#!/bin/bash

# ClinicalBridge Railway Deployment Script
# This script deploys your MCP server to Railway

set -e

echo "🚀 ClinicalBridge Railway Deployment"
echo "===================================="
echo ""

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please log in to Railway..."
    railway login
fi

cd "$(dirname "$0")/.." || exit 1

echo ""
echo "📦 Initializing Railway project..."
railway init --name clinicalbridge-health-project

echo ""
echo "🔑 Setting environment variables..."
echo "Please enter your Groq API key (from console.groq.com):"
read -r GROQ_API_KEY
railway variables set GROQ_API_KEY="$GROQ_API_KEY"
railway variables set FHIR_BASE_URL="https://r4.smarthealthit.org"
railway variables set PORT="8080"

echo ""
echo "📤 Deploying to Railway..."
railway up

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 Your MCP server is now live!"
railway status

echo ""
echo "Next steps:"
echo "1. Go to app.promptopinion.ai"
echo "2. Add MCP Server with your Railway URL"
echo "3. Platform will auto-discover all 5 tools"
echo "4. Submit to Devpost: https://devpost.com"

