"""Tool 3: ICD-10 Suggestions

Map clinical conditions to ICD-10-CM billing codes.
"""

import httpx
from fastmcp import Context
from ..llm import synthesize

CMS_ICD10_URL = "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"

# Fallback mapping for common conditions
COMMON_ICD10_MAP = {
    "type 2 diabetes": {"code": "E11.9", "description": "Type 2 diabetes mellitus without complications"},
    "hypertension": {"code": "I10", "description": "Essential (primary) hypertension"},
    "asthma": {"code": "J45.9", "description": "Asthma, unspecified"},
    "heart failure": {"code": "I50.9", "description": "Heart failure, unspecified"},
    "pneumonia": {"code": "J18.9", "description": "Pneumonia, unspecified"},
    "covid-19": {"code": "U07.1", "description": "COVID-19, virus identified"},
}


async def get_icd10_suggestions(
    conditions: list[str],
    encounter_type: str = "inpatient",
    ctx: Context = None
) -> dict:
    """
    Suggest ICD-10-CM codes for a patient's active conditions.

    Args:
        conditions: List of condition descriptions
        encounter_type: "inpatient" | "outpatient" | "ED"
        ctx: FastMCP Context

    Returns:
        Ranked ICD-10 code suggestions with confidence scores
    """
    suggestions = []

    for condition in conditions:
        codes = await _lookup_icd10(condition)
        if codes:
            primary = codes[0]
            suggestions.append({
                "condition_input": condition,
                "primary_code": primary["code"],
                "description": primary["description"],
                "alternatives": [c["code"] for c in codes[1:3]],
                "confidence": 0.90 if len(codes) > 1 else 0.75,
            })

    principal_dx = suggestions[0]["primary_code"] if suggestions else ""

    return {
        "suggestions": suggestions,
        "principal_dx_recommendation": principal_dx,
        "encounter_type": encounter_type,
        "data_classification": "SYNTHETIC"
    }


async def _lookup_icd10(condition: str) -> list[dict]:
    """Query CMS or fallback mapping for ICD-10 codes."""
    condition_lower = condition.lower().strip()

    # Try fallback mapping first
    if condition_lower in COMMON_ICD10_MAP:
        return [COMMON_ICD10_MAP[condition_lower]]

    # Try CMS API
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                CMS_ICD10_URL,
                params={
                    "terms": condition,
                    "maxList": 3,
                    "sf": "code,name",
                    "df": "code,name"
                }
            )
            if resp.status_code == 200:
                data = resp.json()
                codes = data[3] if len(data) > 3 else []
                return [{"code": c[0], "description": c[1]} for c in codes]
    except Exception:
        pass

    # Final fallback
    return [{
        "code": "R99",
        "description": "Ill-defined and unspecified cause of mortality (fallback)"
    }]
