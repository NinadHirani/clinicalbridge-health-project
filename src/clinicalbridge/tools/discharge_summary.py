"""Tool 5: Generate Discharge Summary

AI-powered discharge summary generation - the centerpiece tool.
"""

import uuid
from datetime import datetime
from fastmcp import Context
from ..sharp import extract_sharp
from ..llm import synthesize
from . import get_patient_summary
from .drug_interactions import check_drug_interactions
from .icd10_suggestions import get_icd10_suggestions


async def generate_discharge_summary(
    patient_id: str,
    include_sections: list[str] = None,
    tone: str = "clinical",
    ctx: Context = None
) -> dict:
    """
    Generate a complete AI-synthesized discharge summary.

    This is the primary AI tool — synthesizes patient data, drug interactions,
    ICD-10 codes, and follow-up plans into a clinician-ready document.
    Cannot be replicated by rule-based systems.

    Args:
        patient_id: Patient FHIR ID
        include_sections: Sections to include (default: all)
        tone: "clinical" | "patient_friendly"
        ctx: FastMCP Context with optional SHARP fields

    Returns:
        Structured discharge summary with all sections
    """
    sharp = extract_sharp(ctx)
    effective_id = patient_id or sharp.patient_id

    if not effective_id:
        return {"error": "patient_id is required"}

    try:
        # Gather all context
        patient = await get_patient_summary(effective_id, ctx)
        if "error" in patient:
            return patient

        meds = [m["name"] for m in patient.get("current_medications", [])]
        conditions = [c["display"] for c in patient.get("active_conditions", [])]

        interactions = await check_drug_interactions(meds, effective_id, ctx)
        icd10 = await get_icd10_suggestions(conditions, "inpatient", ctx)

        # Build context for LLM
        context_str = f"""
Patient: {patient.get('name', 'Unknown')}, {patient.get('age', '?')}yo {patient.get('gender', '')}
Conditions: {', '.join(conditions) if conditions else 'None documented'}
Medications: {', '.join(meds) if meds else 'None'}
Drug Interaction Flags: {interactions.get('overall_risk', 'UNKNOWN')} risk
{interactions.get('llm_summary', '')}
ICD-10 Principal Dx: {icd10.get('principal_dx_recommendation', 'Unspecified')}
Allergies: {', '.join([a.get('substance','') for a in patient.get('allergies', [])]) if patient.get('allergies') else 'NKDA'}
Recent Vitals: BP {patient.get('recent_vitals', {}).get('bp', 'N/A')}, HR {patient.get('recent_vitals', {}).get('hr', 'N/A')}
        """.strip()

        tone_instruction = (
            "Use precise clinical language suitable for physician review."
            if tone == "clinical" else
            "Use plain language a patient can understand. Avoid jargon."
        )

        summary_text = await synthesize(
            system_prompt=(
                f"You are an AI clinical documentation assistant. {tone_instruction} "
                "Generate a structured discharge summary. Include: discharge diagnosis, "
                "discharge medications (with warnings), patient instructions, and follow-up plan. "
                "Be concise, accurate, and flag any safety concerns prominently."
            ),
            user_content=context_str,
            max_tokens=1200
        )

        return {
            "patient_id": effective_id,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "tone": tone,
            "summary": summary_text,
            "interaction_flags": interactions.get("interactions_found", []),
            "icd10_codes": icd10.get("suggestions", []),
            "llm_model": "llama3-70b-8192",
            "data_classification": "SYNTHETIC",
            "audit_id": f"audit-{uuid.uuid4().hex[:8]}"
        }
    except Exception as e:
        return {"error": str(e), "patient_id": effective_id}
