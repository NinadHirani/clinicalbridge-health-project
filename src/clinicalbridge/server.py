"""ClinicalBridge MCP Server

Main entry point - FastAPI HTTP server exposing all clinical tools via MCP protocol.
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

    import uvicorn
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse

    app = FastAPI(title="ClinicalBridge MCP")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Keep informational endpoints ──────────────────────────
    @app.get("/health")
    @app.post("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "service": "ClinicalBridge MCP", "version": "0.1.0"}

    @app.get("/agent_card.json")
    async def agent_card():
        """Prompt Opinion Marketplace discovery manifest."""
        return {
            "name": "ClinicalBridge",
            "description": (
                "AI-powered clinical decision support for discharge planning. "
                "Tools: patient summary, drug interactions, ICD-10 coding, "
                "follow-up scheduling, and AI discharge summary generation. "
                "All data is 100% synthetic."
            ),
            "version": "0.1.0",
            "protocol": "mcp",
            "transport": "sse",
            "mcp_endpoint": "/sse",
            "tools": [
                "get_patient_summary",
                "check_drug_interactions",
                "get_icd10_suggestions",
                "find_followup_slots",
                "generate_discharge_summary",
            ],
            "sharp_supported": True,
            "data_classification": "SYNTHETIC",
            "tags": ["healthcare", "discharge-planning", "fhir", "clinical-decision-support"],
        }

    @app.get("/")
    @app.post("/")
    async def root():
        """Root endpoint - serves HTML dashboard."""
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🏥 ClinicalBridge MCP Server</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                    color: #e2e8f0;
                    min-height: 100vh;
                    padding: 20px;
                }
                .container { max-width: 1200px; margin: 0 auto; }
                header {
                    text-align: center;
                    padding: 40px 20px;
                    background: rgba(255,255,255,0.05);
                    border-radius: 12px;
                    border: 1px solid rgba(255,255,255,0.1);
                    margin-bottom: 40px;
                }
                h1 {
                    font-size: 2.5em;
                    margin-bottom: 10px;
                    background: linear-gradient(135deg, #60a5fa, #34d399);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
                .status {
                    display: inline-block;
                    padding: 8px 16px;
                    background: #10b981;
                    color: white;
                    border-radius: 20px;
                    font-size: 0.9em;
                    margin-top: 10px;
                }
                .links {
                    display: flex;
                    gap: 10px;
                    justify-content: center;
                    margin-top: 20px;
                    flex-wrap: wrap;
                }
                a {
                    display: inline-block;
                    padding: 8px 16px;
                    background: #3b82f6;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    transition: background 0.3s;
                }
                a:hover { background: #2563eb; }
                .tool-list {
                    background: rgba(255,255,255,0.05);
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 12px;
                    padding: 30px;
                    margin-top: 30px;
                }
                .tool {
                    background: rgba(0,0,0,0.3);
                    border-left: 4px solid #34d399;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-radius: 6px;
                }
                .tool h4 { color: #34d399; margin-bottom: 5px; }
                .tool p { color: #cbd5e1; font-size: 0.9em; }
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>🏥 ClinicalBridge MCP</h1>
                    <p>AI-Powered Clinical Decision Support for Discharge Planning</p>
                    <div class="status">✅ Service Healthy</div>
                    <div class="links">
                        <a href="/health">Health</a>
                        <a href="/agent_card.json">Manifest</a>
                        <a href="/sse">MCP Stream</a>
                    </div>
                </header>
                <div class="tool-list">
                    <h2>📚 5 Clinical Tools Available</h2>
                    <div class="tool">
                        <h4>1. get_patient_summary</h4>
                        <p>Retrieve FHIR R4 patient data (demographics, conditions, medications, allergies)</p>
                    </div>
                    <div class="tool">
                        <h4>2. check_drug_interactions</h4>
                        <p>FDA-based interaction checking + LLM clinical synthesis</p>
                    </div>
                    <div class="tool">
                        <h4>3. get_icd10_suggestions</h4>
                        <p>Suggest ICD-10-CM billing codes for clinical conditions</p>
                    </div>
                    <div class="tool">
                        <h4>4. find_followup_slots</h4>
                        <p>Find available follow-up appointments by specialty and location</p>
                    </div>
                    <div class="tool">
                        <h4>5. generate_discharge_summary</h4>
                        <p>⭐ AI-powered complete discharge document generation</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    # ── MOUNT THE REAL MCP ASGI APP ──────────────────────────
    # FastMCP exports as an ASGI app for HTTP transports
    mcp_asgi = mcp.app()
    app.mount("/", mcp_asgi)

    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
