"""
KrushiSetu Location Privacy Protection Engine
Ensures farmer exact home addresses, plot GPS coordinates, and private landmarks
are not publicly exposed across marketplace listings, search results, or public APIs.
"""

from typing import Dict, Any, Optional

def mask_location_for_public(location_input: Any) -> Dict[str, str]:
    """
    Sanitize location to high-level administrative boundaries (City, District, State).
    Withholds exact house numbers, survey numbers, coordinates, and private street details.
    """
    if isinstance(location_input, str):
        import re
        # Clean string location and strip any trailing 6-digit PIN codes
        clean_input = re.sub(r'\b\d{5,6}\b', '', location_input).strip()
        parts = [p.strip() for p in clean_input.split(",") if p.strip()]
        if len(parts) >= 2:
            return {
                "display_location": f"{parts[-2]}, {parts[-1]}",
                "district": parts[-2],
                "state": parts[-1],
                "privacy_level": "anonymized_regional"
            }
        elif len(parts) == 1:
            return {
                "display_location": parts[0],
                "district": parts[0],
                "state": "India",
                "privacy_level": "anonymized_regional"
            }
        return {
            "display_location": "Maharashtra, India",
            "district": "General Mandi Region",
            "state": "Maharashtra",
            "privacy_level": "anonymized_regional"
        }

    if isinstance(location_input, dict):
        city = location_input.get("city") or location_input.get("district") or ""
        state = location_input.get("state") or location_input.get("region") or ""
        district = location_input.get("district") or city

        if city and state and city.lower() != state.lower():
            display = f"{city}, {state}"
        elif city:
            display = city
        elif state:
            display = state
        else:
            display = "Verified Agricultural Region"

        return {
            "display_location": display,
            "district": district or "District Hub",
            "state": state or "State",
            "privacy_level": "anonymized_regional"
        }

    return {
        "display_location": "Verified Agricultural Region",
        "district": "District Hub",
        "state": "State",
        "privacy_level": "anonymized_regional"
    }

def format_public_region(user_or_dict: Dict[str, Any]) -> str:
    """Convenience helper returning formatted public region string (e.g. 'Nashik, Maharashtra')."""
    masked = mask_location_for_public(user_or_dict)
    return masked["display_location"]

def is_exact_location_permitted(requester_user: Optional[Dict[str, Any]], target_user_id: str, order_status: Optional[str] = None) -> bool:
    """
    Verify if the requesting user has legitimate business authorization to view
    the exact physical pickup/dispatch address (e.g. confirmed order logistics, or same user).
    """
    if not requester_user:
        return False
    
    req_id = str(requester_user.get("id") or requester_user.get("_id") or "")
    req_role = str(requester_user.get("role", "")).lower()

    # User viewing their own address or Admin
    if req_id == str(target_user_id) or req_role == "admin":
        return True

    # Counterparties can only see exact address if the transaction/order is Confirmed/In-Transit
    if order_status and order_status.lower() in ("accepted", "confirmed", "in-transit", "dispatched", "delivered"):
        return True

    return False
