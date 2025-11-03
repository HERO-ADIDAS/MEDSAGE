# ============================================================
# Imports
# ============================================================

from fpdf import FPDF, XPos, YPos
import datetime
from app.nim_client import get_nim_llm
from app import prompts
from langchain_core.output_parsers import StrOutputParser

# ============================================================
# PDF Report Class Extending FPDF
# ============================================================

class PDF(FPDF):
    def header(self):
        """
        Create a custom header for each PDF page with branding.
        """
        self.set_fill_color(14, 165, 233)  # Blue background fill
        self.set_text_color(255, 255, 255)  # White text
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 12, 'MedSage', border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L', fill=True)
        self.set_font('Helvetica', '', 10)
        self.cell(0, 8, 'AI-Powered Diagnostic Summary Report', border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L', fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def footer(self):
        """
        Custom footer showing page number and disclaimer.
        """
        self.set_y(-20)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 4, f'Page {self.page_no()}', border=0, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font('Helvetica', 'I', 7)
        self.multi_cell(
            w=0, h=3,
            text='[DISCLAIMER] AI-generated summary for informational purposes only. Not a medical diagnosis. Consult a healthcare provider.',
            border=0, align='C'
        )
        self.set_text_color(0, 0, 0)

    def section_title(self, title):
        """
        Adds a styled section title to the PDF.
        """
        self.ln(2)
        self.set_font('Helvetica', 'B', 13)
        self.set_fill_color(230, 240, 250)  # Light blue background
        self.cell(0, 8, title, border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L', fill=True)
        self.ln(3)

    def clean_text(self, text):
        """
        Remove markdown markers like ** for clean display.
        """
        return text.replace('**', '')

    def section_body(self, text):
        """
        Adds paragraph text body to the PDF, cleaned from markdown.
        """
        clean = self.clean_text(text)
        self.set_font('Helvetica', '', 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(w=0, h=6, text=clean, border=0, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def key_value(self, key, value):
        """
        Prints a key-value pair with styled keys for patient info.
        """
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(14, 165, 233)  # Blue keys
        self.cell(w=50, h=6, text=key + ":", border=0, new_x=XPos.RIGHT, new_y=YPos.TOP, align='L')

        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        value_str = str(value) if value is not None else "Not provided"
        self.multi_cell(w=0, h=6, text=value_str, border=0, align='L', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

# ============================================================
# Function to Generate PDF Report Bytes from Chat History and User Details
# ============================================================

def generate_report_pdf(user_details: dict | None, chat_history: list) -> bytes:
    """
    Generate a polished PDF report summarizing the diagnostic session.

    Args:
        user_details: Optional dict or Pydantic model with patient info.
        chat_history: List of chat turns containing human and AI messages.

    Returns:
        bytes representing the PDF file content.

    Raises:
        ValueError: If chat history is empty.
    """

    # Build full conversation string from chat history
    full_history_str = ""
    for turn in chat_history:
        human_msg = getattr(turn, 'human', turn.get('human', ''))
        ai_msg = getattr(turn, 'ai', turn.get('ai', ''))
        if human_msg:
            full_history_str += f"Patient: {human_msg}\n\n"
        if ai_msg:
            full_history_str += f"MedSage Assistant: {ai_msg}\n\n"
    full_history_str = full_history_str.strip()

    if not full_history_str:
        raise ValueError("Chat history is empty.")

    # Generate clinical summary using LLM and prompt
    print("[Report Gen] Generating clinical summary...")
    try:
        llm = get_nim_llm()
        summary_chain = prompts.SUMMARY_PROMPT | llm | StrOutputParser()
        clinical_summary = summary_chain.invoke({"full_history": full_history_str})
        print("[Report Gen] Summary generated successfully.")
    except Exception as e:
        print(f"[Report Gen] Error: {e}")
        clinical_summary = "Clinical summary could not be generated at this time."

    # Initialize PDF document
    pdf = PDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Title Header
    pdf.ln(5)
    pdf.set_font('Helvetica', 'B', 18)
    pdf.set_text_color(14, 165, 233)
    pdf.cell(0, 10, 'Diagnostic Session Report', border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f'Generated: {datetime.date.today().strftime("%B %d, %Y")}', border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    # Patient Information Section (if provided)
    if user_details:
        user_dict = user_details.model_dump() if hasattr(user_details, 'model_dump') else user_details
    else:
        user_dict = {}

    if user_dict:
        pdf.section_title('PATIENT INFORMATION')
        pdf.key_value("Name", user_dict.get('name'))
        if user_dict.get('age'):
            pdf.key_value("Age", f"{user_dict.get('age')} years")
        gender = user_dict.get('gender') or user_dict.get('gender_assigned')
        if gender:
            pdf.key_value("Gender", gender)
        if user_dict.get('dob'):
            pdf.key_value("Date of Birth", user_dict.get('dob'))
        if user_dict.get('symptoms'):
            pdf.key_value("Initial Symptoms", user_dict.get('symptoms'))

    # Clinical Summary Section
    pdf.section_title('CLINICAL SUMMARY')
    pdf.section_body(clinical_summary)

    # Disclaimer Section
    pdf.ln(3)
    pdf.set_fill_color(255, 243, 224)  # Light orange background
    pdf.set_draw_color(255, 152, 0)    # Orange border
    pdf.set_line_width(0.7)
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(230, 124, 0)
    pdf.cell(
        0, 8, 'IMPORTANT DISCLAIMER', border=1,
        new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L', fill=True
    )

    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(0, 0, 0)
    disclaimer = (
        "This report contains an AI-generated analysis for informational purposes only. "
        "It is NOT a medical diagnosis or treatment recommendation. "
        "Always consult with a qualified healthcare professional before making healthcare decisions."
    )
    pdf.multi_cell(w=0, h=5, text=disclaimer, border=1, align='L', fill=True)

    # Output PDF as bytes
    return pdf.output()
