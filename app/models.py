# Imports
from pydantic import BaseModel
from typing import List, Optional

# Chat Turn Model
class Turn(BaseModel):
    """
    Represents a single turn in the conversation (Human <-> AI).
    """
    human: str  # Human/user message
    ai: str     # AI response

# User Details Model
class UserDetails(BaseModel):
    name: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    known_conditions: Optional[str] = None
    current_medications: Optional[str] = None
    allergies: Optional[str] = None

# Report Request Model
class ReportRequest(BaseModel):
    user_details: Optional[UserDetails] = None
    chat_history: List[Turn]  # Use List[Turn]; List[Dict] if using simple JS objects
