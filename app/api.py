# ============================================================
# Imports
# ============================================================

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from app.models import Turn, UserDetails
from app.engine import DiagnosticEngine
from app.report_generator import generate_report_pdf
from app.facilities_service import FacilitiesService
import datetime
import traceback

# ============================================================
# Pydantic Models for API Requests/Responses
# ============================================================

class ChatRequest(BaseModel):
    query: str
    history: List[Turn]

class ChatResponse(BaseModel):
    ai_response: str
    history: List[Turn]
    search_query: Optional[str] = None
    retrieved_context: Optional[str] = None

class ReportRequest(BaseModel):
    user_details: Optional[UserDetails] = None
    chat_history: List[dict]

class PatientInfo(BaseModel):
    name: str
    age: int
    gender: str
    symptoms: str

class GetNearestFacilitiesRequest(BaseModel):
    pincode: str
    specialist: str = ""
    facility_type: str = "all"

class ExtractSpecialistRequest(BaseModel):
    chat_history: List[dict]

# ============================================================
# Initialize Router and Diagnostic Engine
# ============================================================

router = APIRouter()

try:
    engine = DiagnosticEngine()
    chain = engine.get_chain()
except Exception as e:
    # Fatal error during engine initialization
    print(f"FATAL: Failed to initialize DiagnosticEngine: {e}")
    raise RuntimeError(f"Engine initialization failed: {e}") from e

# ============================================================
# Endpoint: Extract Specialist from Chat History
# Route: /api/extract_specialist
# Method: POST
# ============================================================

@router.post("/extract_specialist",
             summary="Extract recommended specialist from chat history")
async def extract_specialist(request: ExtractSpecialistRequest):
    """
    Extracts the recommended specialist from the chat history.
    Example:
      {
          "chat_history": [
              {"human": "I have fever", "ai": "Based on your symptoms...Recommended Specialist: Cardiologist"}
          ]
      }
    """
    print(f"[API /extract_specialist] Extracting specialist from {len(request.chat_history)} messages")
    try:
        specialist = FacilitiesService.extract_specialist_from_chat(request.chat_history)
        if specialist:
            print(f"[API /extract_specialist] Found specialist: {specialist}")
            return {
                "success": True,
                "specialist": specialist
            }
        else:
            print(f"[API /extract_specialist] No specialist found in chat")
            return {
                "success": True,
                "specialist": "",
                "message": "No specialist found in chat history"
            }
    except Exception as e:
        print(f"Error in /extract_specialist endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# Endpoint: Receive and Store Patient Info
# Route: /api/patient
# Method: POST
# ============================================================

@router.post("/patient", summary="Receive and store patient information")
async def patient_info(request: PatientInfo):
    """
    Accepts patient details and returns a success message.
    First step before diagnosis begins.
    """
    try:
        print(f"[API /patient] Received: {request.dict()}")
        return JSONResponse(content={
            "message": "Patient info received successfully.",
            "data": request.dict()
        })
    except Exception as e:
        print(f"Error in /patient endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process patient info: {e}")

# ============================================================
# Endpoint: Diagnostic Conversation (AI Chat)
# Route: /api/chat
# Method: POST
# ============================================================

@router.post("/chat",
             response_model=ChatResponse,
             summary="Process one turn of the diagnostic chat")
async def chat(request: ChatRequest):
    """
    Handles one turn of the diagnostic chat between patient and AI.
    """
    print(f"[API /chat] Received query: '{request.query}' with history length: {len(request.history)}")
    try:
        current_turn_input = Turn(human=request.query, ai="")
        input_data = {"history": request.history + [current_turn_input]}
        chain_output = await chain.ainvoke(input_data)
        ai_response = chain_output.get("ai_response", "Error: No response generated.")
        search_query = chain_output.get("search_query", "N/A")
        retrieved_context = chain_output.get("retrieved_context", "N/A")
        final_turn = Turn(human=request.query, ai=ai_response)
        updated_history = request.history + [final_turn]
        print(f"[API /chat] Sending response: '{ai_response[:60]}...'")
        return ChatResponse(
            ai_response=ai_response,
            history=updated_history,
            search_query=search_query,
            retrieved_context=retrieved_context
        )
    except Exception as e:
        print(f"Error in /chat endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error processing chat: {e}")

# ============================================================
# Endpoint: Generate PDF Summary of Chat Session
# Route: /api/generate_report
# Method: POST
# ============================================================

@router.post("/generate_report",
             summary="Generate a PDF summary of the chat session",
             responses={
                 200: {"content": {"application/pdf": {}}},
                 400: {"description": "Bad Request"},
                 500: {"description": "Internal Server Error"},
             })
async def generate_report(request: ReportRequest):
    """
    Generates a PDF report summarizing patient info and chat history.
    Uses LLM to create a clinical summary.
    """
    print(f"[API /generate_report] Received request. History length: {len(request.chat_history)}")
    try:
        pdf_bytes = generate_report_pdf(request.user_details, request.chat_history)
        print(f"[API /generate_report] PDF generated, size: {len(pdf_bytes)} bytes.")
        return Response(
            content=bytes(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=MedSage_Report_{datetime.date.today().strftime('%Y%m%d')}.pdf"
            }
        )
    except ValueError as ve:
        print(f"Value Error generating report: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error in /generate_report endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {e}")

# ============================================================
# Endpoint: Get Nearest Medical Facilities
# Route: /api/get_nearest_facilities
# Method: POST
# ============================================================

@router.post("/get_nearest_facilities",
             summary="Get nearest medical facilities by pincode")
async def get_nearest_facilities(request: GetNearestFacilitiesRequest):
    """
    Get Google Maps search links for NEAREST medical facilities.
    Returns links to find nearest hospitals, clinics, or nursing homes.
    Example:
      {
          "pincode": "110051",
          "specialist": "Cardiologist",
          "facility_type": "hospital"
      }
    """
    print(f"[API /get_nearest_facilities] Pincode: {request.pincode}, Specialist: {request.specialist}, Type: {request.facility_type}")
    try:
        result = FacilitiesService.get_nearest_facility_links(
            pincode=request.pincode,
            specialist=request.specialist,
            facility_type=request.facility_type
        )
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to fetch facilities")
            )
        print(f"[API /get_nearest_facilities] Generated links for pincode: {result['pincode']}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in /get_nearest_facilities endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# Endpoint: List Available Pincodes
# Route: /api/available_pincodes
# Method: GET
# ============================================================

@router.get("/available_pincodes",
            summary="Get list of available pincodes")
async def available_pincodes():
    """
    Returns list of available pincodes for facility search.
    """
    print("[API /available_pincodes] Request received")
    try:
        return {
            # Potentially list pincodes here
        }
    except Exception as e:
        print(f"Error in /available_pincodes endpoint: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# Endpoint: API Health Check
# Route: /api/health
# Method: GET
# ============================================================

@router.get("/health", summary="Health check endpoint")
async def health_check():
    """
    Simple health check to verify API is running.
    """
    return {
        "status": "healthy",
        "service": "MedSage API",
        "version": "1.0.0",
        "message": "All systems operational"
    }

