"""ClinicalBridge MCP Server

HTTP wrapper for Railway deployment.
Exposes MCP tools as HTTP endpoints.
"""

import os
import json
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

load_dotenv()

# FastMCP for real MCP protocol
from fastmcp import FastMCP, Context

# Import all tools
from .tools import get_patient_summary
from .tools.drug_interactions import check_drug_interactions
from .tools.icd10_suggestions import get_icd10_suggestions
from .tools.followup_slots import find_followup_slots
from .tools.discharge_summary import generate_discharge_summary

# ── Real MCP server (what Prompt Opinion connects to) ─────────────────────
mcp = FastMCP(
    name="ClinicalBridge",
    instructions=(
        "ClinicalBridge provides five healthcare tools for discharge planning. "
        "All data is 100% synthetic. "
        "Call get_patient_summary first, then generate_discharge_summary last."
    )
)

@mcp.tool()
async def get_patient_summary(patient_id: str, ctx: Context) -> dict:
    """Retrieve structured patient summary from FHIR: demographics, conditions, medications, allergies."""
    from .tools import get_patient_summary as _fn
    return await _fn(patient_id, ctx)

@mcp.tool()
async def check_drug_interactions(medications: list[str], patient_id: str = "", ctx: Context = None) -> dict:
    """Check medication list for drug-drug interactions using FDA data and LLM synthesis."""
    from .tools.drug_interactions import check_drug_interactions as _fn
    return await _fn(medications, patient_id, ctx)

@mcp.tool()
async def get_icd10_suggestions(conditions: list[str], encounter_type: str = "inpatient", ctx: Context = None) -> dict:
    """Suggest ICD-10-CM billing codes for a list of clinical condition descriptions."""
    from .tools.icd10_suggestions import get_icd10_suggestions as _fn
    return await _fn(conditions, encounter_type, ctx)

@mcp.tool()
async def find_followup_slots(specialty: str, zip_code: str, days_from_now: int = 14, ctx: Context = None) -> dict:
    """Find available follow-up appointment slots by specialty and location."""
    from .tools.followup_slots import find_followup_slots as _fn
    return await _fn(specialty, zip_code, days_from_now, ctx)

@mcp.tool()
async def generate_discharge_summary(patient_id: str, include_sections: list[str] = None, tone: str = "clinical", ctx: Context = None) -> dict:
    """AI-powered discharge summary: synthesizes patient data, drug interactions, ICD-10 codes into a complete document."""
    from .tools.discharge_summary import generate_discharge_summary as _fn
    return await _fn(patient_id, include_sections, tone, ctx)

app = FastAPI(title="ClinicalBridge MCP")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy", "service": "ClinicalBridge MCP", "version": "0.1.0"}


@app.get("/agent_card.json")
async def agent_card():
    """Marketplace discovery manifest."""
    return {
        "name": "ClinicalBridge",
        "description": "AI-powered clinical decision support for discharge planning",
        "version": "0.1.0",
        "protocol": "mcp",
        "transport": "sse",
        "endpoint": "/sse",
        "tools": [
            {
                "name": "get_patient_summary",
                "description": "Retrieve structured patient summary from FHIR: demographics, conditions, medications, allergies."
            },
            {
                "name": "check_drug_interactions",
                "description": "Check medication list for drug-drug interactions using FDA data and LLM synthesis."
            },
            {
                "name": "get_icd10_suggestions",
                "description": "Suggest ICD-10-CM billing codes for a list of clinical condition descriptions."
            },
            {
                "name": "find_followup_slots",
                "description": "Find available follow-up appointment slots by specialty and location."
            },
            {
                "name": "generate_discharge_summary",
                "description": "AI-powered discharge summary: synthesizes patient data, drug interactions, ICD-10 codes into a complete document."
            },
        ],
        "sharp_supported": True,
        "data_classification": "SYNTHETIC",
    }


@app.post("/tools/get_patient_summary")
async def call_get_patient_summary(patient_id: str):
    """Get patient summary from FHIR."""
    return await get_patient_summary(patient_id, ctx=None)


@app.post("/tools/check_drug_interactions")
async def call_check_drug_interactions(medications: list[str], patient_id: str = ""):
    """Check drug interactions."""
    return await check_drug_interactions(medications, patient_id, ctx=None)


@app.post("/tools/get_icd10_suggestions")
async def call_get_icd10_suggestions(conditions: list[str], encounter_type: str = "inpatient"):
    """Get ICD-10 suggestions."""
    return await get_icd10_suggestions(conditions, encounter_type, ctx=None)


@app.post("/tools/find_followup_slots")
async def call_find_followup_slots(specialty: str, zip_code: str, days_from_now: int = 14):
    """Find follow-up slots."""
    return await find_followup_slots(specialty, zip_code, days_from_now, ctx=None)


@app.post("/tools/generate_discharge_summary")
async def call_generate_discharge_summary(patient_id: str, tone: str = "clinical"):
    """Generate discharge summary."""
    return await generate_discharge_summary(patient_id, tone=tone, ctx=None)


@app.get("/")
async def root():
    """HTML dashboard."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🏥 ClinicalBridge MCP</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #e2e8f0;
                min-height: 100vh;
                padding: 40px 20px;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            h1 {
                background: linear-gradient(135deg, #60a5fa, #34d399);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 2.5em;
                text-align: center;
            }
            .status {
                text-align: center;
                padding: 20px;
                background: rgba(16, 185, 129, 0.1);
                border-radius: 12px;
                margin: 20px 0;
            }
            .tools {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 40px;
            }
            .tool {
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 12px;
                padding: 20px;
            }
            .tool h3 { color: #60a5fa; margin-top: 0; }
            .tool p { color: #cbd5e1; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 ClinicalBridge MCP</h1>
            <div class="status">
                ✅ Service Running<br/>
                <small>AI-Powered Clinical Decision Support</small>
            </div>
            <div class="tools">
                <div class="tool">
                    <h3>1. get_patient_summary</h3>
                    <p>Retrieve FHIR R4 patient data</p>
                    <code>POST /tools/get_patient_summary</code>
                </div>
                <div class="tool">
                    <h3>2. check_drug_interactions</h3>
                    <p>FDA-based interaction checking + LLM synthesis</p>
                    <code>POST /tools/check_drug_interactions</code>
                </div>
                <div class="tool">
                    <h3>3. get_icd10_suggestions</h3>
                    <p>Suggest ICD-10-CM billing codes</p>
                    <code>POST /tools/get_icd10_suggestions</code>
                </div>
                <div class="tool">
                    <h3>4. find_followup_slots</h3>
                    <p>Find available appointments</p>
                    <code>POST /tools/find_followup_slots</code>
                </div>
                <div class="tool">
                    <h3>5. generate_discharge_summary</h3>
                    <p>⭐ AI-powered discharge generation</p>
                    <code>POST /tools/generate_discharge_summary</code>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(html)


def main():
    """Run the HTTP server."""
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")

    print(f"🏥 ClinicalBridge HTTP Server on {host}:{port}")

    # Mount real MCP protocol at /sse
    app.mount("/sse", mcp.app())

    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
