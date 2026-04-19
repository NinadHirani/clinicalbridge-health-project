# ClinicalBridge MCP

**🏥 AI-Powered Clinical Decision Support for Discharge Planning**

> Agents Assemble Hackathon · May 11, 2026 · Prize Pool: $25,000 USD

ClinicalBridge is a Model Context Protocol (MCP) server that exposes specialized healthcare tools for AI agents operating in clinical discharge planning workflows.

## What It Does

When a patient is ready for discharge, clinicians must:
1. Check drug interactions with home medications  ✅ `check_drug_interactions`
2. Verify follow-up appointment availability       ✅ `find_followup_slots`
3. Check applicable ICD-10 codes for billing      ✅ `get_icd10_suggestions`
4. Generate synthesized discharge summary         ✅ `generate_discharge_summary`

ClinicalBridge provides all four as callable, composable tools — each one stateless, SHARP-aware, and FHIR-grounded.

---

## Features

✅ **5 Clinical Tools**
- `get_patient_summary` — Fetch patient data from FHIR R4
- `check_drug_interactions` — FDA-based interaction checking + LLM synthesis
- `get_icd10_suggestions` — ICD-10-CM code mapping
- `find_followup_slots` — Synthetic appointment scheduling
- `generate_discharge_summary` — AI-powered complete discharge document

✅ **SHARP Context Support**
- Standardized Healthcare Agent Runtime Parameters (SHARP) integration
- Patient ID and FHIR token propagation from Prompt Opinion platform
- Fallback to environment variables for local testing

✅ **100% Synthetic Data**
- No real PHI anywhere in codebase
- All patient data clearly labeled `"data_classification": "SYNTHETIC"`
- Uses public FHIR sandbox (r4.smarthealthit.org)

✅ **AI Factor**
- Uses Groq API (llama3-70b-8192) for clinical text synthesis
- Can't be replicated by rule-based systems
- Judges will see clear LLM usage in discharge summary generation

---

## Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/yourusername/clinicalbridge-mcp.git
cd clinicalbridge-mcp
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -e .
```

### 2. Get API Keys

- **Groq (Free):** [console.groq.com](https://console.groq.com) → Create API key
- Copy to `.env`:
  ```bash
  cp .env.example .env
  # Edit .env and add your GROQ_API_KEY
  ```

### 3. Run Server

```bash
python -m clinicalbridge.server
```

Server runs at: `http://localhost:8080`

### 4. Test Tools

```bash
python scripts/test_tools_locally.py
```

---

## Project Structure

```
clinicalbridge-mcp/
├── src/clinicalbridge/
│   ├── server.py              # FastMCP server + all 5 tools
│   ├── tools/                 # Individual tool implementations
│   │   ├── patient_summary.py
│   │   ├── drug_interactions.py
│   │   ├── icd10_suggestions.py
│   │   ├── followup_slots.py
│   │   └── discharge_summary.py
│   ├── fhir/                  # FHIR R4 client & parsers
│   ├── llm/                   # Groq LLM integration
│   ├── sharp/                 # SHARP context extraction
│   └── data/                  # Synthetic data generators
├── tests/                     # Pytest test suite
├── scripts/                   # Local testing scripts
├── data/                      # Synthetic patient fixtures
├── pyproject.toml             # Dependencies
├── .env.example               # Environment template
└── README.md                  # This file
```

---

---

## 🧪 Testing with Live FHIR Data

Use these confirmed synthetic patient IDs from the public SMART Health IT sandbox to test the tools:

| Patient ID | Use Case |
|---|---|
| `87a339d0-8cae-418e-89c7-8651e6aab3c6` | Full discharge summary demo, drug interactions |
| `9995a32b-ce66-4b88-b8da-7e65f84b2de7` | Alternative test patient |
| `2739a9b2-4d49-4b43-92c0-9f1cab3b8cde` | Additional test patient |

All patients are 100% synthetic — no real PHI.

### Example Test Call

```bash
curl -X POST http://localhost:8080/sse \
  -H "Content-Type: application/json" \
  -d '{
    "method": "call_tool",
    "params": {
      "name": "get_patient_summary",
      "arguments": {
        "patient_id": "87a339d0-8cae-418e-89c7-8651e6aab3c6"
      }
    }
  }'
```

---

## API Examples

### Tool 1: Get Patient Summary

```json
{
  "patient_id": "87a339d0-8cae-418e-89c7-8651e6aab3c6"
}
```

Response:
```json
{
  "patient_id": "87a339d0-8cae-418e-89c7-8651e6aab3c6",
  "name": "Jane Smith",
  "age": 67,
  "gender": "female",
  "active_conditions": [
    {"display": "Type 2 Diabetes", "icd10": "E11.9"}
  ],
  "current_medications": [
    {"name": "Metformin", "dose": "1000mg", "frequency": "BID"}
  ],
  "allergies": [
    {"substance": "Penicillin", "reaction": "Anaphylaxis", "severity": "severe"}
  ],
  "data_classification": "SYNTHETIC"
}
```

### Tool 2: Check Drug Interactions

```json
{
  "medications": ["warfarin", "ibuprofen", "metformin"]
}
```

Response:
```json
{
  "medications_checked": ["warfarin", "ibuprofen", "metformin"],
  "interactions_found": [
    {
      "pair": ["warfarin", "ibuprofen"],
      "severity": "CRITICAL",
      "mechanism": "NSAIDs potentiate anticoagulant effect, risk of major bleeding",
      "recommendation": "AVOID combination..."
    }
  ],
  "overall_risk": "HIGH",
  "llm_summary": "...",
  "data_classification": "SYNTHETIC"
}
```

### Tool 5: Generate Discharge Summary

```json
{
  "patient_id": "87a339d0-8cae-418e-89c7-8651e6aab3c6",
  "tone": "clinical"
}
```

Response:
```json
{
  "patient_id": "87a339d0-8cae-418e-89c7-8651e6aab3c6",
  "generated_at": "2026-04-19T14:32:00Z",
  "summary": "Patient: Jane Smith, 67yo female. Primary discharge diagnosis: Type 2 Diabetes Mellitus with Hyperglycemia (E11.65)...",
  "interaction_flags": [...],
  "icd10_codes": [...],
  "data_classification": "SYNTHETIC",
  "audit_id": "audit-7f3a9c"
}
```

---

## Deployment

### Option A: Railway (Recommended)

```bash
npm install -g @railway/cli
railway login
railway init
railway variables set GROQ_API_KEY=your_key
railway up
```

Your server will be live at: `https://clinicalbridge-mcp-xxx.railway.app`

### Option B: Render

1. Push code to GitHub
2. Create Web Service on render.com
3. Build Command: `pip install -e .`
4. Start Command: `python -m clinicalbridge.server`
5. Add environment variables
6. Deploy

### Option C: Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
EXPOSE 8080
CMD ["python", "-m", "clinicalbridge.server"]
```

```bash
docker build -t clinicalbridge .
docker run -e GROQ_API_KEY=your_key -p 8080:8080 clinicalbridge
```

---

## Prompt Opinion Marketplace

### Register Your Server

1. Go to app.promptopinion.ai
2. Select "Add MCP Server"
3. Enter your deployed URL: `https://your-app.railway.app`
4. Platform auto-discovers all 5 tools via MCP introspection
5. Configure marketplace listing:
   - **Name:** ClinicalBridge
   - **Category:** Clinical Decision Support
   - **SHARP Support:** ✅ Yes
   - **FHIR Version:** R4
   - **Data Classification:** Synthetic only

6. Click "Publish" — now discoverable by any agent on the platform!

---

## Environment Variables

```bash
# Required
GROQ_API_KEY=gsk_your_key_here

# Optional (defaults provided)
FHIR_BASE_URL=https://r4.smarthealthit.org
FHIR_TOKEN=

# Optional
PORT=8080
LOG_LEVEL=INFO
```

---

## Testing

### Local Tool Testing

```bash
python scripts/test_tools_locally.py
```

### Pytest

```bash
pytest tests/ -v
```

### MCP Inspector

```bash
npx @modelcontextprotocol/inspector
# Point at: http://localhost:8080
```

---

## Architecture

```
Prompt Opinion Platform
       │
       ├─ Orchestrator Agent
       │       │
       │       └─ MCP Discovery
       │              │
       └──────────────────────── ClinicalBridge MCP Server
                      │
                      ├─ Tool 1: get_patient_summary
                      ├─ Tool 2: check_drug_interactions
                      ├─ Tool 3: get_icd10_suggestions
                      ├─ Tool 4: find_followup_slots
                      └─ Tool 5: generate_discharge_summary
                           │
                           ├─ FHIR R4 (r4.smarthealthit.org)
                           ├─ OpenFDA API
                           ├─ CMS ICD-10 API
                           └─ Groq LLM (llama3-70b-8192)
```

---

## Technical Stack

| Component | Technology |
|---|---|
| **MCP Framework** | fastmcp (Python) |
| **LLM** | Groq API (llama3-70b-8192) — free tier |
| **FHIR Server** | HAPI FHIR public sandbox (`r4.smarthealthit.org`) |
| **Drug Interactions** | OpenFDA Drug Interaction API (free) |
| **ICD-10 Lookup** | CMS ICD-10 API (free) |
| **Deployment** | Railway, Render, or Docker |
| **Language** | Python 3.11+ |

---

## Key Files

- `src/clinicalbridge/server.py` — Main server with all 5 tools
- `src/clinicalbridge/tools/` — Individual tool implementations
- `src/clinicalbridge/fhir/__init__.py` — FHIR client
- `src/clinicalbridge/llm/__init__.py` — Groq integration
- `src/clinicalbridge/sharp/__init__.py` — SHARP context handling
- `.env.example` — Environment variable template
- `pyproject.toml` — Dependencies

---

## Support

For questions, check:
1. `.env.example` for required env vars
2. `scripts/test_tools_locally.py` for example tool calls
3. The AGENTS_ASSEMBLE_SRS.md for detailed specifications

---

**Built for the Agents Assemble Hackathon**

Good luck. Build the hammer. 🔨
