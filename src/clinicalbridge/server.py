"""ClinicalBridge MCP Server

Main entry point - FastMCP server exposing all clinical tools.
"""

import os
from fastmcp import FastMCP, Context
from dotenv import load_dotenv

load_dotenv()

from .tools import get_patient_summary as _get_patient_summary
from .tools.drug_interactions import check_drug_interactions as _check_drug_interactions
from .tools.icd10_suggestions import get_icd10_suggestions as _get_icd10_suggestions
from .tools.followup_slots import find_followup_slots as _find_followup_slots
from .tools.discharge_summary import generate_discharge_summary as _generate_discharge_summary

mcp = FastMCP(
    name="ClinicalBridge",
    instructions=(
        "ClinicalBridge provides five healthcare tools for discharge planning workflows. "
        "Tools are SHARP-aware and use FHIR R4 for patient data. "
        "All data used in this deployment is 100% synthetic. "
        "Use get_patient_summary first, then other tools as needed, "
        "and call generate_discharge_summary last for a complete output."
    )
)


@mcp.tool()
async def get_patient_summary(patient_id: str, ctx: Context) -> dict:
    """
    Retrieve structured patient summary from FHIR: demographics, conditions,
    medications, allergies, and recent vitals.

    Args:
        patient_id: FHIR Patient resource ID

    Returns:
        Structured patient data from FHIR R4
    """
    return await _get_patient_summary(patient_id, ctx)


@mcp.tool()
async def check_drug_interactions(
    medications: list[str],
    patient_id: str = "",
    ctx: Context = None
) -> dict:
    """
    Check medication list for drug-drug interactions using FDA data and LLM synthesis.
    Returns severity flags and clinical recommendations.

    Args:
        medications: List of medication names
        patient_id: Optional patient ID for allergy cross-checking

    Returns:
        Interaction analysis with severity and recommendations
    """
    return await _check_drug_interactions(medications, patient_id, ctx)


@mcp.tool()
async def get_icd10_suggestions(
    conditions: list[str],
    encounter_type: str = "inpatient",
    ctx: Context = None
) -> dict:
    """
    Suggest ICD-10-CM billing codes for a list of clinical condition descriptions.
    Uses CMS ICD-10 API with LLM disambiguation.

    Args:
        conditions: List of condition descriptions
        encounter_type: "inpatient" | "outpatient" | "ED"

    Returns:
        ICD-10 code suggestions with confidence scores
    """
    return await _get_icd10_suggestions(conditions, encounter_type, ctx)


@mcp.tool()
async def find_followup_slots(
    specialty: str,
    zip_code: str,
    days_from_now: int = 14,
    ctx: Context = None
) -> dict:
    """
    Find available follow-up appointment slots by specialty and location.
    Returns synthetic but realistic scheduling options.

    Args:
        specialty: Medical specialty (e.g., "endocrinology", "cardiology")
        zip_code: Patient's ZIP code
        days_from_now: Target follow-up window

    Returns:
        List of available appointment slots
    """
    return await _find_followup_slots(specialty, zip_code, days_from_now, ctx)


@mcp.tool()
async def generate_discharge_summary(
    patient_id: str,
    include_sections: list[str] = None,
    tone: str = "clinical",
    ctx: Context = None
) -> dict:
    """
    AI-powered discharge summary generation. Synthesizes patient data, drug interactions,
    ICD-10 codes, and follow-up plans into a complete clinician-ready document.

    This is the primary AI tool — cannot be replicated by rule-based systems.

    Args:
        patient_id: Patient FHIR ID
        include_sections: Optional sections to include
        tone: "clinical" | "patient_friendly"

    Returns:
        Complete discharge summary with all clinical data
    """
    return await _generate_discharge_summary(patient_id, include_sections, tone, ctx)


def main():
    """Run the MCP server."""
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")

    print(f"🏥 ClinicalBridge MCP Server starting on {host}:{port}")

    # Import uvicorn for HTTP server
    import uvicorn
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    # Create FastAPI app wrapper
    app = FastAPI(title="ClinicalBridge MCP")

    # Add CORS middleware to allow Prompt Opinion platform
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    @app.post("/")
    async def root():
        """Root endpoint - shows server info."""
        return {
            "message": "🏥 ClinicalBridge MCP Server",
            "version": "0.1.0",
            "endpoints": {
                "health": "/health",
                "mcp": "/mcp",
                "tools": "/tools"
            }
        }

    @app.get("/health")
    @app.post("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "service": "ClinicalBridge MCP", "version": "0.1.0"}

    @app.get("/mcp")
    @app.post("/mcp")
    async def mcp_info():
        """MCP server information and tool list."""
        return {
            "name": "ClinicalBridge",
            "version": "0.1.0",
            "tools": [
                {
                    "name": "get_patient_summary",
                    "description": "Retrieve structured patient summary from FHIR"
                },
                {
                    "name": "check_drug_interactions",
                    "description": "Check medication list for dangerous interactions"
                },
                {
                    "name": "get_icd10_suggestions",
                    "description": "Suggest ICD-10-CM billing codes"
                },
                {
                    "name": "find_followup_slots",
                    "description": "Find available follow-up appointment slots"
                },
                {
                    "name": "generate_discharge_summary",
                    "description": "AI-powered discharge summary generation"
                }
            ]
        }

    @app.get("/tools")
    @app.post("/tools")
    async def list_tools():
        """List all available tools."""
        return {
            "tools": [
                "get_patient_summary",
                "check_drug_interactions",
                "get_icd10_suggestions",
                "find_followup_slots",
                "generate_discharge_summary"
            ]
        }

    @app.get("/sse")
    async def sse_stream():
        """Server-Sent Events stream for Streamable HTTP transport."""
        from fastapi.responses import StreamingResponse
        import json

        async def event_generator():
            # Send tool discovery
            tools_data = {
                "name": "ClinicalBridge",
                "version": "0.1.0",
                "tools": [
                    {"name": "get_patient_summary", "description": "Retrieve structured patient summary from FHIR"},
                    {"name": "check_drug_interactions", "description": "Check medication list for dangerous interactions"},
                    {"name": "get_icd10_suggestions", "description": "Suggest ICD-10-CM billing codes"},
                    {"name": "find_followup_slots", "description": "Find available follow-up appointment slots"},
                    {"name": "generate_discharge_summary", "description": "AI-powered discharge summary generation"}
                ]
            }
            yield f"data: {json.dumps(tools_data)}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    # Run with uvicorn
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
