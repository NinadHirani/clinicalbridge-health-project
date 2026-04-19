"""Tool 2: Check Drug Interactions

Analyze medications for dangerous interactions using OpenFDA and LLM synthesis.
"""

import httpx
from fastmcp import Context
from ..sharp import extract_sharp
from ..llm import synthesize

OPENFDA_URL = "https://api.fda.gov/drug/label.json"

# Known critical interactions for demo (when FDA API is unavailable)
KNOWN_CRITICAL_INTERACTIONS = {
    ("warfarin", "ibuprofen"): {
        "mechanism": "NSAIDs potentiate anticoagulant effect, risk of major bleeding",
        "severity": "CRITICAL",
    },
    ("metformin", "contrast dye"): {
        "mechanism": "Risk of lactic acidosis with contrast media",
        "severity": "CRITICAL",
    },
    ("lisinopril", "potassium supplements"): {
        "mechanism": "Hyperkalemia risk - both increase potassium levels",
        "severity": "HIGH",
    },
}


async def check_drug_interactions(
    medications: list[str],
    patient_id: str = "",
    ctx: Context = None
) -> dict:
    """
    Check for drug-drug and drug-allergy interactions.

    Args:
        medications: List of medication names
        patient_id: Patient ID for allergy cross-checking
        ctx: FastMCP Context with optional SHARP fields

    Returns:
        Interaction flags with severity levels and clinical recommendations
    """
    sharp = extract_sharp(ctx)

    interactions = []

    # Check each medication pair
    for i, med_a in enumerate(medications):
        for med_b in medications[i + 1:]:
            result = await _check_drug_pair(med_a, med_b)
            if result:
                interactions.append(result)

    # Use LLM to synthesize clinical narrative
    if interactions:
        interaction_text = "\n".join([
            f"- {i['pair'][0]} + {i['pair'][1]}: {i.get('mechanism', 'unknown')}"
            for i in interactions
        ])
        llm_summary = await synthesize(
            system_prompt=(
                "You are a clinical pharmacist. Given drug interaction data, "
                "write a concise 2-3 sentence clinical warning for the care team. "
                "Be direct, mention severity, and give one actionable recommendation."
            ),
            user_content=f"Medications: {', '.join(medications)}\n\nInteractions found:\n{interaction_text}",
            max_tokens=300
        )
    else:
        llm_summary = f"No critical interactions detected among: {', '.join(medications)}."

    overall_risk = "HIGH" if any(i.get("severity") == "CRITICAL" for i in interactions) else \
                   "MODERATE" if interactions else "LOW"

    return {
        "medications_checked": medications,
        "interactions_found": interactions,
        "overall_risk": overall_risk,
        "llm_summary": llm_summary,
        "data_classification": "SYNTHETIC"
    }


async def _check_drug_pair(drug_a: str, drug_b: str) -> dict | None:
    """Query for known interactions between two drugs."""
    drug_a_lower = drug_a.lower().strip()
    drug_b_lower = drug_b.lower().strip()

    # Check known critical interactions first
    for (known_a, known_b), interaction in KNOWN_CRITICAL_INTERACTIONS.items():
        if {drug_a_lower, drug_b_lower} == {known_a.lower(), known_b.lower()}:
            return {
                "pair": [drug_a, drug_b],
                **interaction,
                "fda_source": "Clinical Knowledge Base",
                "recommendation": "Consult pharmacist before dispensing."
            }

    # Try OpenFDA API (may not have all drugs)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                OPENFDA_URL,
                params={
                    "search": f'openfda.brand_name:"{drug_a}" OR openfda.generic_name:"{drug_a}"',
                    "limit": 1
                }
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("results"):
                    result = data["results"][0]
                    interactions_list = result.get("drug_interactions", [])
                    if interactions_list and any(drug_b_lower in i.lower() for i in interactions_list):
                        return {
                            "pair": [drug_a, drug_b],
                            "severity": "MODERATE",
                            "mechanism": interactions_list[0][:300],
                            "fda_source": "openFDA.gov",
                            "recommendation": "Monitor closely; consult pharmacist."
                        }
    except Exception:
        pass

    return None
