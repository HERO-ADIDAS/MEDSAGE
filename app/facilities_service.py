# app/facilities_service.py
from typing import Dict, List
from urllib.parse import quote


class FacilitiesService:
    """Service to generate medical facility search links"""

    SPECIALIST_KEYWORDS = {
        "Cardiologist": "cardiologist",
        "General Practitioner": "general practitioner",
        "Neurologist": "neurologist",
        "Pulmonologist": "pulmonologist",
        "Gastroenterologist": "gastroenterologist",
        "Orthopedic Surgeon": "orthopedic surgeon",
        "Dermatologist": "dermatologist",
        "Ophthalmologist": "ophthalmologist",
        "ENT Specialist": "ent specialist",
        "Pediatrician": "pediatrician",
        "Psychiatrist": "psychiatrist",
        "Urologist": "urologist",
        "Gynecologist": "gynecologist",
    }

    @staticmethod
    def extract_specialist_from_chat(chat_history: List[dict]) -> str:
        """
        Extract recommended specialist from chat history
        
        Args:
            chat_history: List of chat messages with 'human' and 'ai' keys
        
        Returns:
            Specialist name if found, empty string otherwise
        """
        specialist_patterns = [
            ("primary care physician or cardiologist", "Cardiologist"),
            ("primary care physician", "General Practitioner"),
            ("cardiologist", "Cardiologist"),
            ("neurologist", "Neurologist"),
            ("pulmonologist", "Pulmonologist"),
            ("gastroenterologist", "Gastroenterologist"),
            ("orthopedic surgeon", "Orthopedic Surgeon"),
            ("dermatologist", "Dermatologist"),
            ("ophthalmologist", "Ophthalmologist"),
            ("ent specialist", "ENT Specialist"),
            ("otolaryngologist", "ENT Specialist"),
            ("pediatrician", "Pediatrician"),
            ("psychiatrist", "Psychiatrist"),
            ("urologist", "Urologist"),
            ("gynecologist", "Gynecologist"),
        ]

        for message in chat_history:
            if message.get("ai"):
                ai_text = message["ai"].lower()
                
                if "recommended specialist" in ai_text or "recommend" in ai_text:
                    for pattern, specialist in specialist_patterns:
                        if pattern in ai_text:
                            return specialist
        
        return ""

    @staticmethod
    def get_nearest_facility_links(
        pincode: str,
        specialist: str = "",
        facility_type: str = "all"
    ) -> Dict:
        
        if not pincode or len(pincode) != 6 or not pincode.isdigit():
            return {
                "success": False,
                "error": "Invalid pincode. Must be exactly 6 digits."
            }

        search_links = FacilitiesService._generate_nearest_search_links(
            specialist, facility_type, pincode
        )

        return {
            "success": True,
            "pincode": pincode,
            "specialist": specialist,
            "facility_type": facility_type,
            "search_links": search_links
        }

    @staticmethod
    def _generate_nearest_search_links(
        specialist: str,
        facility_type: str,
        pincode: str
    ) -> Dict:
        
        specialist_keyword = FacilitiesService.SPECIALIST_KEYWORDS.get(
            specialist,
            specialist or "hospital"
        )

        facility_searches = {
            "all": {
                "nearest_hospitals": f"nearest {specialist_keyword} hospital in {pincode}",
                "nearest_clinics": f"nearest {specialist_keyword} clinic in {pincode}",
                "nearest_nursing": f"nearest nursing home in {pincode}"
            },
            "hospital": {
                "nearest_hospitals": f"nearest {specialist_keyword} hospital in {pincode}"
            },
            "clinic": {
                "nearest_clinics": f"nearest {specialist_keyword} clinic in {pincode}"
            },
            "nursing": {
                "nearest_nursing": f"nearest nursing home in {pincode}"
            }
        }

        searches = facility_searches.get(facility_type, facility_searches["all"])
        
        links = {}
        facility_names = {
            "nearest_hospitals": "🏥 Nearest Hospitals",
            "nearest_clinics": "🏢 Nearest Clinics",
            "nearest_nursing": "🏘️ Nearest Nursing Homes"
        }
        
        for key, search_query in searches.items():
            encoded_query = quote(search_query)
            
            links[key] = {
                "name": facility_names.get(key, key),
                "google_maps": f"https://www.google.com/maps/search/{encoded_query}",
                "google_search": f"https://www.google.com/search?q={encoded_query}",
                "display_text": search_query,
                "type": key.replace("nearest_", "")
            }

        return links
