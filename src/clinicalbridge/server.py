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
        """Root endpoint - serves HTML dashboard."""
        from fastapi.responses import HTMLResponse

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
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
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
                .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 40px; }
                .card {
                    background: rgba(255,255,255,0.05);
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 12px;
                    padding: 20px;
                    backdrop-filter: blur(10px);
                }
                .card h3 {
                    color: #60a5fa;
                    margin-bottom: 10px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                .card p { color: #cbd5e1; font-size: 0.95em; line-height: 1.6; }
                .tools-section {
                    background: rgba(255,255,255,0.05);
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 12px;
                    padding: 30px;
                    backdrop-filter: blur(10px);
                }
                .tools-section h2 {
                    color: #60a5fa;
                    margin-bottom: 20px;
                    font-size: 1.8em;
                }
                .tool {
                    background: rgba(0,0,0,0.3);
                    border-left: 4px solid #34d399;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-radius: 6px;
                }
                .tool h4 {
                    color: #34d399;
                    margin-bottom: 5px;
                    font-size: 1.1em;
                }
                .tool p { color: #cbd5e1; font-size: 0.9em; }
                .links {
                    display: flex;
                    gap: 10px;
                    margin-top: 10px;
                    flex-wrap: wrap;
                }
                a {
                    display: inline-block;
                    padding: 8px 16px;
                    background: #3b82f6;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    font-size: 0.9em;
                    transition: background 0.3s;
                }
                a:hover { background: #2563eb; }
                .code {
                    background: rgba(0,0,0,0.5);
                    padding: 12px;
                    border-radius: 6px;
                    font-family: 'Monaco', 'Courier New', monospace;
                    font-size: 0.85em;
                    overflow-x: auto;
                    margin-top: 10px;
                }
                footer {
                    text-align: center;
                    padding: 20px;
                    color: #64748b;
                    margin-top: 40px;
                    font-size: 0.9em;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>🏥 ClinicalBridge MCP</h1>
                    <p>AI-Powered Clinical Decision Support for Discharge Planning</p>
                    <div class="status">✅ Service Healthy</div>
                </header>

                <div class="grid">
                    <div class="card">
                        <h3>📊 Version</h3>
                        <p><strong>0.1.0</strong><br/>Agents Assemble Hackathon</p>
                    </div>
                    <div class="card">
                        <h3>🛠️ Tools</h3>
                        <p><strong>5 Clinical Tools</strong><br/>FHIR R4 + LLM-Powered</p>
                    </div>
                    <div class="card">
                        <h3>📋 Data</h3>
                        <p><strong>100% Synthetic</strong><br/>No real PHI</p>
                    </div>
                </div>

                <div class="tools-section">
                    <h2>📚 Available Tools</h2>

                    <div class="tool">
                        <h4>1️⃣ get_patient_summary</h4>
                        <p>Retrieve structured patient data from FHIR R4 (demographics, conditions, medications, allergies)</p>
                        <div class="code">
                            curl -X POST https://clinicalbridge-health-project-production.up.railway.app/mcp \\<br/>
                            &nbsp;&nbsp;-H "Content-Type: application/json" \\<br/>
                            &nbsp;&nbsp;-d '{"patient_id": "patient-001"}'
                        </div>
                    </div>

                    <div class="tool">
                        <h4>2️⃣ check_drug_interactions</h4>
                        <p>Check medications for dangerous interactions using FDA data + LLM synthesis</p>
                        <div class="code">
                            curl -X POST https://clinicalbridge-health-project-production.up.railway.app/mcp \\<br/>
                            &nbsp;&nbsp;-H "Content-Type: application/json" \\<br/>
                            &nbsp;&nbsp;-d '{"medications": ["warfarin", "ibuprofen"]}'
                        </div>
                    </div>

                    <div class="tool">
                        <h4>3️⃣ get_icd10_suggestions</h4>
                        <p>Suggest ICD-10-CM billing codes for clinical conditions</p>
                        <div class="code">
                            curl -X POST https://clinicalbridge-health-project-production.up.railway.app/mcp \\<br/>
                            &nbsp;&nbsp;-H "Content-Type: application/json" \\<br/>
                            &nbsp;&nbsp;-d '{"conditions": ["type 2 diabetes", "hypertension"]}'
                        </div>
                    </div>

                    <div class="tool">
                        <h4>4️⃣ find_followup_slots</h4>
                        <p>Find available follow-up appointment slots by specialty and location</p>
                        <div class="code">
                            curl -X POST https://clinicalbridge-health-project-production.up.railway.app/mcp \\<br/>
                            &nbsp;&nbsp;-H "Content-Type: application/json" \\<br/>
                            &nbsp;&nbsp;-d '{"specialty": "endocrinology", "zip_code": "94102"}'
                        </div>
                    </div>

                    <div class="tool">
                        <h4>5️⃣ generate_discharge_summary</h4>
                        <p><strong>⭐ AI-Powered:</strong> Synthesizes all data into complete discharge document</p>
                        <div class="code">
                            curl -X POST https://clinicalbridge-health-project-production.up.railway.app/mcp \\<br/>
                            &nbsp;&nbsp;-H "Content-Type: application/json" \\<br/>
                            &nbsp;&nbsp;-d '{"patient_id": "patient-001", "tone": "clinical"}'
                        </div>
                    </div>
                </div>

                <div style="margin-top: 40px; text-align: center;">
                    <h2 style="color: #60a5fa; margin-bottom: 20px;">🚀 Quick Links</h2>
                    <div class="links" style="justify-content: center;">
                        <a href="/health">Health Check</a>
                        <a href="/mcp">MCP Info</a>
                        <a href="/tools">Tools List</a>
                        <a href="https://github.com/NinadHirani/clinicalbridge-health-project" target="_blank">GitHub</a>
                    </div>
                </div>

                <footer>
                    <p>🏥 ClinicalBridge • Agents Assemble Hackathon • Built by NinadHirani</p>
                    <p>Using: FastMCP • Groq API • FHIR R4 • Railway</p>
                </footer>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

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
