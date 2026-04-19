"""Tool 1: Get Patient Summary

Fetch comprehensive patient data from FHIR.
"""

from fastmcp import Context
from ..fhir import FHIRClient
from ..fhir.parsers import parse_patient, parse_medications, parse_conditions, parse_allergies
from ..sharp import extract_sharp


async def get_patient_summary(patient_id: str, ctx: Context = None) -> dict:
    """
    Retrieve a structured clinical summary for a patient from the FHIR server.

    Args:
        patient_id: FHIR Patient resource ID (e.g. "patient-001")
        ctx: FastMCP Context with optional SHARP fields

    Returns:
        Structured dict with demographics, conditions, medications, allergies
    """
    sharp = extract_sharp(ctx)
    effective_patient_id = patient_id or sharp.patient_id

    if not effective_patient_id:
        return {"error": "patient_id is required"}

    fhir = FHIRClient(sharp.fhir_base_url, sharp.fhir_access_token or None)

    try:
        patient_raw = await fhir.get_patient(effective_patient_id)
        meds_raw = await fhir.get_medications(effective_patient_id)
        conditions_raw = await fhir.get_conditions(effective_patient_id)
        allergies_raw = await fhir.get_allergies(effective_patient_id)

        result = {
            **parse_patient(patient_raw),
            "current_medications": parse_medications(meds_raw),
            "active_conditions": parse_conditions(conditions_raw),
            "allergies": parse_allergies(allergies_raw),
            "data_source": "FHIR R4",
            "data_classification": "SYNTHETIC"
        }

        # Add mock vitals for demo purposes
        result["recent_vitals"] = {
            "bp": "128/82",
            "hr": 74,
            "temp_f": 98.6,
            "o2_sat": 98,
            "date": "2026-04-18"
        }

        return result
    except Exception as e:
        return {"error": str(e), "patient_id": effective_patient_id}
