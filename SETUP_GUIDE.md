# Setup & GitHub Deployment Guide

## 🎯 Project Complete!

Your ClinicalBridge MCP server is fully implemented with all 5 tools. Now let's get it on GitHub and deployed.

---

## Step 1: Create GitHub Repository

### Option A: Using GitHub Web UI

1. **Go to** [github.com/new](https://github.com/new)
2. **Repository name:** `clinicalbridge-mcp`
3. **Description:** "AI-powered clinical decision support MCP server for discharge planning"
4. **Visibility:** Public (for hackathon judges)
5. **Initialize:** Leave unchecked (we already have git history)
6. Click **"Create repository"**

### Option B: Using GitHub CLI

```bash
gh repo create clinicalbridge-mcp --public --source=. --remote=origin --push
```

---

## Step 2: Push Code to GitHub

```bash
cd /Users/ninadhirani/Desktop/clinicalbridge-mcp

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/clinicalbridge-mcp.git

# Rename branch to main (if not already)
git branch -M main

# Push code
git push -u origin main
```

**Expected output:**
```
Enumerating objects: 27, done.
Counting objects: 100% (27/27), done.
...
To https://github.com/YOUR_USERNAME/clinicalbridge-mcp.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

### Verify

Visit: `https://github.com/YOUR_USERNAME/clinicalbridge-mcp`

You should see all your code!

---

## Step 3: Deploy to Railway (Recommended)

Railway is perfect for MCP servers and has a free tier.

### 3.1 Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub (recommended)

### 3.2 Install Railway CLI

```bash
npm install -g @railway/cli
# or
brew install railway  # macOS
```

### 3.3 Login to Railway

```bash
railway login
```

### 3.4 Deploy from Your Project

```bash
cd /Users/ninadhirani/Desktop/clinicalbridge-mcp
railway init
```

**Prompts:**
- "Create a new project?" → Yes
- "Environment to deploy to?" → Select default or create new

### 3.5 Set Environment Variables

```bash
railway variables set GROQ_API_KEY=gsk_your_api_key_here
```

Get your free Groq API key:
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Create API key
4. Copy and paste above

### 3.6 Deploy

```bash
railway up
```

**Expected output:**
```
✓ Deploying...
✓ Build complete
✓ Deployment live at: https://clinicalbridge-mcp-xyz.railway.app
```

### 3.7 Get Your URL

After deployment, your server is live at:
```
https://clinicalbridge-mcp-xyz.railway.app
```

Test it:
```bash
curl https://clinicalbridge-mcp-xyz.railway.app/health
```

---

## Step 4: Register with Prompt Opinion

1. **Go to:** [app.promptopinion.ai](https://app.promptopinion.ai)
2. **Sign up** (free account for builders)
3. Click **"Add MCP Server"**
4. **Paste your Railway URL:** `https://clinicalbridge-mcp-xyz.railway.app`
5. **Platform discovers tools automatically**
6. **Fill in marketplace listing:**
   - **Name:** ClinicalBridge
   - **Tagline:** AI-powered discharge planning tools
   - **Category:** Clinical Decision Support
   - **SHARP Support:** ✅ Yes
   - **FHIR Version:** R4
   - **Data Classification:** Synthetic only
7. Click **"Publish"**

Your server is now discoverable by any agent on Prompt Opinion!

---

## Step 5: Submit to Agents Assemble (Devpost)

1. **Go to:** [devpost.com](https://devpost.com) → Search "Agents Assemble"
2. **Create submission:**
   - **Title:** ClinicalBridge
   - **Tagline:** AI-Powered Discharge Planning MCP Server
   - **Description:**
     ```
     ClinicalBridge is an MCP server providing 5 specialized healthcare tools:
     
     ✅ Tool 1: get_patient_summary - FHIR R4 patient data retrieval
     ✅ Tool 2: check_drug_interactions - FDA-based interaction checking + LLM synthesis
     ✅ Tool 3: get_icd10_suggestions - Billing code mapping
     ✅ Tool 4: find_followup_slots - Appointment scheduling
     ✅ Tool 5: generate_discharge_summary - AI-powered document generation
     
     - 100% synthetic data (no PHI)
     - SHARP context aware for Prompt Opinion integration
     - Uses Groq API (llama3-70b) for clinical text synthesis
     - Deployed on Railway with public accessibility
     - Published to Prompt Opinion Marketplace
     
     Addresses hackathon challenge: Healthcare AI with clear feasibility and impact.
     Reduces hospital readmissions by automating discharge planning (saves $26B annually in US).
     ```
   
   - **GitHub Link:** `https://github.com/YOUR_USERNAME/clinicalbridge-mcp`
   - **Deployment:** `https://clinicalbridge-mcp-xyz.railway.app`
   - **Demo Video:** (create and upload - see demo script in SRS)
   - **Team:** Solo builder
   - **Category:** AI/ML
   - **Technologies:** Python, FastMCP, FHIR R4, Groq API, Railway

3. **Submit**

---

## Step 6: Create Demo Video (Optional but Recommended)

Use the demo script from AGENTS_ASSEMBLE_SRS.md (Section 14).

### Quick Demo Recording

1. **Tool & Software:**
   - OBS Studio (free) or Loom
   - Terminal + Prompt Opinion platform UI

2. **Structure (< 3 min):**
   - [0:00-0:20] Hook: Readmission problem
   - [0:20-0:40] What is ClinicalBridge
   - [0:40-1:00] Tool discovery in Prompt Opinion
   - [1:00-1:30] Live demo of tools
   - [1:30-2:10] AI factor - discharge summary
   - [2:10-2:30] Architecture & SHARP context
   - [2:30-2:45] Close

3. **Upload:**
   - YouTube (unlisted)
   - Paste link in Devpost submission

---

## Troubleshooting

### Git push fails

```bash
# Check remote
git remote -v

# Should show:
# origin  https://github.com/YOUR_USERNAME/clinicalbridge-mcp.git (fetch)
# origin  https://github.com/YOUR_USERNAME/clinicalbridge-mcp.git (push)

# If wrong, fix:
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/clinicalbridge-mcp.git
```

### Railway deployment fails

Check logs:
```bash
railway logs
```

Common issues:
- Missing GROQ_API_KEY → `railway variables set GROQ_API_KEY=gsk_...`
- Python version → Should be 3.11+
- Dependencies → Check pyproject.toml

### Groq API key not working

1. Verify key is valid at [console.groq.com](https://console.groq.com)
2. Verify set in Railway: `railway variables`
3. Redeploy: `railway up`

### Tools not discovered by Prompt Opinion

1. Verify deployment URL is correct
2. Check endpoint: `https://your-url/mcp`
3. Ensure MCP server is running
4. Try re-adding server in platform

---

## File Checklist

✅ All code files created:
- ✅ `src/clinicalbridge/server.py` - Main server
- ✅ `src/clinicalbridge/tools/` - All 5 tools
- ✅ `src/clinicalbridge/fhir/` - FHIR client
- ✅ `src/clinicalbridge/llm/` - Groq integration
- ✅ `src/clinicalbridge/sharp/` - SHARP context
- ✅ `.env.example` - Environment variables
- ✅ `README.md` - Documentation
- ✅ `DEPLOYMENT.md` - Deployment guide
- ✅ `pyproject.toml` - Dependencies
- ✅ `Dockerfile` - Docker support
- ✅ `.github/workflows/tests.yml` - CI/CD
- ✅ `scripts/test_tools_locally.py` - Local testing

---

## Next Steps

1. **Get Groq API Key**
   - [console.groq.com](https://console.groq.com) → Sign up → Create key

2. **Create GitHub Repo**
   - Use Option A or B above

3. **Push Code**
   - Follow "Step 2" above

4. **Deploy to Railway**
   - Follow "Step 3" above

5. **Register on Prompt Opinion**
   - Follow "Step 4" above

6. **Submit to Devpost**
   - Follow "Step 5" above

---

## Questions?

- **For setup:** Check README.md
- **For deployment:** Check DEPLOYMENT.md
- **For technical details:** Check AGENTS_ASSEMBLE_SRS.md
- **For testing:** Run `python scripts/test_tools_locally.py`

---

**You're ready to go! 🚀**

Submit before **May 11, 2026** for Agents Assemble Hackathon.

Good luck. Build the hammer. 🔨
