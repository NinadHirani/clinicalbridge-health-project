"""Local Testing Script - Test all tools without MCP server running"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from clinicalbridge.tools import get_patient_summary
from clinicalbridge.tools.drug_interactions import check_drug_interactions
from clinicalbridge.tools.icd10_suggestions import get_icd10_suggestions
from clinicalbridge.tools.followup_slots import find_followup_slots
from clinicalbridge.tools.discharge_summary import generate_discharge_summary


async def test_all():
    """Test all five tools sequentially."""

    print("=" * 60)
    print("🏥 ClinicalBridge Tool Testing")
    print("=" * 60)

    # Use a known test patient from the public FHIR sandbox
    test_patient_id = "87a339d0-8cae-418e-89c7-8651e6aab3c6"

    print("\n[1/5] Testing get_patient_summary...")
    try:
        result = await get_patient_summary(test_patient_id, ctx=None)
        print(f"✅ Patient summary retrieved:")
        print(f"   Name: {result.get('name', 'N/A')}")
        print(f"   Age: {result.get('age', 'N/A')}")
        print(f"   Conditions: {len(result.get('active_conditions', []))} found")
        print(f"   Medications: {len(result.get('current_medications', []))} found")
        patient_summary = result
    except Exception as e:
        print(f"❌ Error: {e}")
        patient_summary = {}

    print("\n[2/5] Testing check_drug_interactions...")
    try:
        test_meds = ["warfarin", "ibuprofen", "metformin"]
        result = await check_drug_interactions(test_meds, test_patient_id, ctx=None)
        print(f"✅ Drug interactions checked:")
        print(f"   Medications: {', '.join(test_meds)}")
        print(f"   Overall Risk: {result.get('overall_risk', 'UNKNOWN')}")
        print(f"   Interactions Found: {len(result.get('interactions_found', []))}")
        if result.get('interactions_found'):
            for interaction in result.get('interactions_found', []):
                print(f"   - {interaction['pair'][0]} + {interaction['pair'][1]}: {interaction.get('severity', 'UNKNOWN')}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n[3/5] Testing get_icd10_suggestions...")
    try:
        test_conditions = ["type 2 diabetes", "hypertension"]
        result = await get_icd10_suggestions(test_conditions, "inpatient", ctx=None)
        print(f"✅ ICD-10 suggestions generated:")
        print(f"   Conditions: {', '.join(test_conditions)}")
        print(f"   Principal DX: {result.get('principal_dx_recommendation', 'N/A')}")
        print(f"   Suggestions Count: {len(result.get('suggestions', []))}")
        for sugg in result.get('suggestions', []):
            print(f"   - {sugg['condition_input']}: {sugg.get('primary_code', 'N/A')} ({sugg.get('description', 'N/A')})")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n[4/5] Testing find_followup_slots...")
    try:
        result = await find_followup_slots("endocrinology", "94102", days_from_now=14, ctx=None)
        print(f"✅ Follow-up slots found:")
        print(f"   Specialty: {result.get('specialty', 'N/A')}")
        print(f"   ZIP Code: {result.get('zip_code', 'N/A')}")
        print(f"   Available Slots: {result.get('total_available', 0)}")
        for slot in result.get('slots', [])[:2]:
            print(f"   - {slot.get('provider', 'N/A')} on {slot.get('date', 'N/A')} at {slot.get('time', 'N/A')} ({slot.get('type', 'N/A')})")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n[5/5] Testing generate_discharge_summary...")
    try:
        result = await generate_discharge_summary(test_patient_id, tone="clinical", ctx=None)
        print(f"✅ Discharge summary generated:")
        print(f"   Patient ID: {result.get('patient_id', 'N/A')}")
        print(f"   Generated At: {result.get('generated_at', 'N/A')}")
        print(f"   Audit ID: {result.get('audit_id', 'N/A')}")
        if result.get('summary'):
            summary_preview = result['summary'][:200] + "..." if len(result['summary']) > 200 else result['summary']
            print(f"   Summary Preview: {summary_preview}")
        print(f"   Interaction Flags: {len(result.get('interaction_flags', []))}")
        print(f"   ICD-10 Codes: {len(result.get('icd10_codes', []))}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 60)
    print("✅ Testing Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_all())
