"""Tool 4: Find Follow-up Slots

Generate realistic synthetic appointment availability.
"""

from fastmcp import Context
from ..data import generate_follow_up_slots


async def find_followup_slots(
    specialty: str,
    zip_code: str,
    days_from_now: int = 14,
    ctx: Context = None
) -> dict:
    """
    Find available follow-up appointment slots by specialty and location.

    Args:
        specialty: Medical specialty (e.g., "endocrinology", "cardiology")
        zip_code: Patient's home ZIP code
        days_from_now: Target follow-up window in days
        ctx: FastMCP Context

    Returns:
        List of available appointment slots with provider info
    """
    slots = generate_follow_up_slots(specialty, zip_code, days_from_now)

    return {
        "specialty": specialty,
        "zip_code": zip_code,
        "slots": slots,
        "total_available": len(slots),
        "data_classification": "SYNTHETIC"
    }
