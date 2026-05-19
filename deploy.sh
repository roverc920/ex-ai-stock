#!/bin/bash

# AI Stock Analyzer - Automated Deployment Script
# This script automates deployment to Render and Supabase

set -e

echo "🚀 AI Stock Analyzer - Automated Deployment"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check dependencies
check_dependency() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${RED}❌ $1 is not installed. Please install it first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ $1 found${NC}"
}

echo ""
echo "Step 1: Checking dependencies..."
check_dependency git
check_dependency curl

# GitHub check
echo ""
echo "Step 2: Checking GitHub repository..."
if ! git remote -v > /dev/null 2>&1; then
    echo -e "${RED}❌ No git remote configured${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Git repository configured${NC}"

# Render CLI check
echo ""
echo "Step 3: Checking Render..."
if command -v render &> /dev/null; then
    echo -e "${GREEN}✅ Render CLI found${NC}"
    RENDER_CLI=true
else
    echo -e "${YELLOW}⚠️  Render CLI not found. Will use dashboard deployment.${NC}"
    RENDER_CLI=false
fi

# Function to create Supabase project
create_supabase_project() {
    echo ""
    echo "Step 4: Creating Supabase Project..."
    echo "-------------------------------------"
    echo -e "${YELLOW}Please create a Supabase project manually:${NC}"
    echo ""
    echo "1. Visit: https://supabase.com/dashboard"
    echo "2. Click 'New Project'"
    echo "3. Organization: (your organization)"
    echo "4. Project name: stock-analyzer"
    echo "5. Database password: (set a strong password)"
    echo "6. Region: Singapore (or closest to you)"
    echo ""
    echo "After creation, go to SQL Editor and run:"
    echo ""
    cat << 'SQL'
CREATE TABLE stock_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(50) NOT NULL,
    raw_data JSONB NOT NULL,
    analysis JSONB NOT NULL,
    sentiment VARCHAR(20) NOT NULL CHECK (sentiment IN ('Bullish', 'Neutral', 'Bearish')),
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('Low', 'Medium', 'High')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_stock_analyses_code ON stock_analyses(stock_code);
CREATE INDEX idx_stock_analyses_created_at ON stock_analyses(created_at DESC);
CREATE INDEX idx_stock_analyses_sentiment ON stock_analyses(sentiment);
SQL
    echo ""
    echo "Then get your credentials from Project Settings → API:"
    echo "  - Project URL"
    echo "  - anon public API Key"
    echo ""
    read -p "Press Enter when you've completed this step..."
}

# Function to deploy to Render
deploy_to_render() {
    echo ""
    echo "Step 5: Deploying to Render..."
    echo "------------------------------"

    if [ "$RENDER_CLI" = true ]; then
        echo -e "${GREEN}Using Render CLI...${NC}"

        # Check if already logged in
        if ! render whoami > /dev/null 2>&1; then
            echo -e "${YELLOW}Please login to Render:${NC}"
            render login
        fi

        # Create blueprint
        echo "Creating services from render.yaml..."
        render blueprint apply
    else
        echo -e "${YELLOW}Manual Render deployment:${NC}"
        echo ""
        echo "1. Visit: https://dashboard.render.com/blueprint"
        echo "2. Click 'New Blueprint Instance'"
        echo "3. Connect your GitHub repository: roverc920/ex-ai-stock"
        echo "4. Click 'Apply' to create both services"
        echo ""
        echo "Or manually create services:"
        echo ""
        echo "Backend (Web Service):"
        echo "  - Name: stock-analyzer-api"
        echo "  - Runtime: Python 3"
        echo "  - Build Command: pip install -r requirements.txt"
        echo "  - Start Command: uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
        echo "  - Root Directory: backend"
        echo ""
        echo "Frontend (Static Site):"
        echo "  - Name: stock-analyzer-web"
        echo "  - Runtime: Node"
        echo "  - Build Command: npm install && npm run build"
        echo "  - Publish Directory: dist"
        echo "  - Root Directory: frontend"
        echo ""
        read -p "Press Enter when you've completed this step..."
    fi
}

# Function to configure environment variables
configure_env_vars() {
    echo ""
    echo "Step 6: Configuring Environment Variables..."
    echo "--------------------------------------------"
    echo -e "${YELLOW}Please configure the following in Render Dashboard:${NC}"
    echo ""
    echo "Backend Service (stock-analyzer-api) - Environment Variables:"
    echo "  - SUPABASE_URL: (your Supabase project URL)"
    echo "  - SUPABASE_KEY: (your Supabase anon key)"
    echo "  - DEEPSEEK_API_KEY: sk-a42acb2d63de47b891f63243822d18c0"
    echo "  - DEEPSEEK_API_URL: https://api.deepseek.com"
    echo ""
    echo "Frontend Service (stock-analyzer-web) - Environment Variables:"
    echo "  - VITE_API_BASE_URL: (will be auto-populated after backend deploys)"
    echo ""
    read -p "Press Enter when you've completed this step..."
}

# Main execution
main() {
    echo ""
    read -p "Do you want to start deployment? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 0
    fi

    create_supabase_project
    deploy_to_render
    configure_env_vars

    echo ""
    echo "=============================================="
    echo -e "${GREEN}🎉 Deployment setup complete!${NC}"
    echo ""
    echo "Your application should be available at:"
    echo "  - Frontend: https://stock-analyzer-web.onrender.com"
    echo "  - Backend:  https://stock-analyzer-api.onrender.com"
    echo ""
    echo "Note: It may take a few minutes for the services to start."
    echo ""
    echo "Next steps:"
    echo "  1. Visit Render dashboard to monitor deployment"
    echo "  2. Test the frontend URL in your browser"
    echo "  3. Run 'git push' to trigger automatic redeployments"
}

main
