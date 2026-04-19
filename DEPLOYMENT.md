# Deployment Guide

## Important Note: MCP Server vs. Vercel

⚠️ **ClinicalBridge is a long-running MCP server, not a traditional web application.**

Vercel is optimized for:
- Stateless serverless functions (max 10 seconds execution)
- Web apps with HTTP request/response cycles
- Frontend deployments

MCP servers need:
- Persistent connections
- WebSocket or stdio transport
- Long-running processes

**Recommendation:** Use **Railway** or **Render** instead (see options below).

---

## Option A: Railway (Recommended ⭐)

Railway is perfect for MCP servers — free tier, persistent connections, easy setup.

### Steps:

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

3. **Login & Initialize**
   ```bash
   railway login
   cd clinicalbridge-mcp
   railway init
   ```

4. **Set Environment Variables**
   ```bash
   railway variables set GROQ_API_KEY=gsk_your_api_key_here
   ```

5. **Deploy**
   ```bash
   railway up
   ```

6. **Get Your URL**
   - After deployment completes, you'll get a URL like:
   - `https://clinicalbridge-mcp-xyz.railway.app`

7. **Set Up with Prompt Opinion**
   - Go to app.promptopinion.ai
   - Add MCP Server → Enter your Railway URL
   - Platform auto-discovers all 5 tools

---

## Option B: Render

Render is also great for MCP servers with a free tier.

### Steps:

1. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/yourusername/clinicalbridge-mcp.git
   git branch -M main
   git push -u origin main
   ```

2. **Connect to Render**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub
   - New Web Service → Select your GitHub repo
   - Build Command: `pip install -e .`
   - Start Command: `python -m clinicalbridge.server`
   - Add environment variable: `GROQ_API_KEY`
   - Deploy

3. **Your URL will be:** `https://clinicalbridge-mcp-xyz.onrender.com`

---

## Option C: Docker (Local or Any Cloud)

### Build & Run Locally

```bash
cd clinicalbridge-mcp

# Build image
docker build -t clinicalbridge-mcp .

# Run container
docker run -e GROQ_API_KEY=gsk_your_key -p 8080:8080 clinicalbridge-mcp

# Test
curl http://localhost:8080/health
```

### Deploy to Any Docker Registry

```bash
# Tag for Docker Hub
docker tag clinicalbridge-mcp yourusername/clinicalbridge-mcp:latest

# Push
docker push yourusername/clinicalbridge-mcp:latest
```

---

## Option D: Vercel (Python Support - Experimental)

⚠️ Vercel Python support is experimental and designed for serverless functions, not long-running servers. This will **not work well** for MCP servers.

If you still want to try:

### Steps:

1. **Create vercel.json**
   ```json
   {
     "buildCommand": "pip install -e .",
     "outputDirectory": ".",
     "devCommand": "python -m clinicalbridge.server",
     "env": {
       "GROQ_API_KEY": "@groq_api_key"
     }
   }
   ```

2. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

3. **Deploy**
   ```bash
   vercel
   ```

4. **Add secret**
   ```bash
   vercel secrets add groq_api_key gsk_your_key_here
   ```

5. **Redeploy**
   ```bash
   vercel deploy --prod
   ```

### Limitations on Vercel:
- Max 10 seconds execution per request
- MCP connections will timeout
- Not suitable for production
- Use Railway/Render instead

---

## Troubleshooting Deployment

### 1. GROQ_API_KEY not found

Add the environment variable to your deployment platform:
- **Railway:** `railway variables set GROQ_API_KEY=gsk_...`
- **Render:** Add in dashboard Environment tab
- **Docker:** `docker run -e GROQ_API_KEY=gsk_...`

### 2. FHIR queries timing out

The public FHIR sandbox (r4.smarthealthit.org) can be slow. Add to your `.env`:
```
FHIR_TIMEOUT=30
```

### 3. Server won't start

Check logs:
- **Railway:** `railway logs`
- **Render:** View in dashboard Logs tab
- **Docker:** `docker logs <container-id>`

Make sure all dependencies installed:
```bash
pip install -e .
```

---

## Registering with Prompt Opinion

Once your server is deployed:

1. **Go to:** app.promptopinion.ai
2. **Sign up** (free builder account)
3. **Add MCP Server:**
   - Paste your deployed URL (e.g., https://clinicalbridge-mcp-xyz.railway.app)
   - Platform auto-discovers your 5 tools
4. **Configure Listing:**
   - Name: ClinicalBridge
   - Category: Clinical Decision Support
   - SHARP Support: ✅ Yes
   - FHIR Version: R4
   - Data: Synthetic only
5. **Publish** — Available on marketplace!

---

## Testing Your Deployment

### Health Check (if implemented)

```bash
curl https://your-deployed-url/health
```

### Test Tool Discovery (MCP)

```bash
curl https://your-deployed-url/mcp
```

### Direct Tool Call (if HTTP transport)

```bash
curl -X POST https://your-deployed-url/tools \
  -H "Content-Type: application/json" \
  -d '{"tool": "get_patient_summary", "patient_id": "87a339d0-8cae-418e-89c7-8651e6aab3c6"}'
```

---

## Environment Variables Reference

| Variable | Required | Default | Notes |
|---|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | - | Get from console.groq.com |
| `FHIR_BASE_URL` | ❌ No | https://r4.smarthealthit.org | Public sandbox |
| `FHIR_TOKEN` | ❌ No | (empty) | For authenticated FHIR servers |
| `PORT` | ❌ No | 8080 | Server port |
| `LOG_LEVEL` | ❌ No | INFO | Logging level |

---

## Recommended Path

**For Agents Assemble Hackathon:**

1. ✅ Deploy to **Railway** (free, supports MCP servers)
2. ✅ Register on **Prompt Opinion** marketplace
3. ✅ Test with agents in the platform
4. ✅ Submit to **Devpost** with:
   - GitHub repo link
   - Railway deployment URL
   - Demo video showing tools in action

---

**Questions?** Check README.md or the AGENTS_ASSEMBLE_SRS.md specification.
