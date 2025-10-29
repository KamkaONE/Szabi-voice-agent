#!/bin/bash
#
# Deploy script for Szabi Voice Agent
# This script syncs your local changes to GitHub and Hetzner server
#
# Usage: ./deploy.sh "commit message"
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SERVER="root@37.27.247.64"
SERVER_PATH="/opt/agent"

echo -e "${GREEN}=== Szabi Voice Agent Deployment ===${NC}\n"

# Check if commit message provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Please provide a commit message${NC}"
    echo "Usage: ./deploy.sh \"your commit message\""
    exit 1
fi

COMMIT_MSG="$1"

# Step 1: Check git status
echo -e "${YELLOW}Step 1: Checking git status...${NC}"
if [[ -n $(git status -s) ]]; then
    echo "Changes detected:"
    git status -s
else
    echo "No changes to commit"
    exit 0
fi

# Step 2: Stage changes (excluding sensitive files)
echo -e "\n${YELLOW}Step 2: Staging changes...${NC}"
git add -A
git reset HEAD .env 2>/dev/null || true  # Unstage .env if accidentally added
git reset HEAD .claude/settings.local.json 2>/dev/null || true  # Unstage Claude settings
echo "✓ Changes staged (excluding .env and Claude settings)"

# Step 3: Commit locally
echo -e "\n${YELLOW}Step 3: Committing changes locally...${NC}"
git commit -m "$COMMIT_MSG"
echo "✓ Committed: $COMMIT_MSG"

# Step 4: Push to GitHub
echo -e "\n${YELLOW}Step 4: Pushing to GitHub...${NC}"
git push
echo "✓ Pushed to GitHub"

# Step 5: Deploy to Hetzner server
echo -e "\n${YELLOW}Step 5: Deploying to Hetzner server...${NC}"

# Pull latest changes on server
ssh $SERVER << 'EOF'
cd /opt/agent
echo "Pulling latest changes from GitHub..."
git pull origin main

echo "Restarting services..."
docker-compose pull livekit  # Pull new LiveKit image if version changed
docker-compose up -d --build

echo "✓ Services restarted"
EOF

echo -e "\n${GREEN}=== Deployment Complete ===${NC}"
echo -e "\nYour changes are now live on:"
echo "  • Local machine: /Users/szabolcs.levai/Desktop/agent"
echo "  • GitHub: https://github.com/KamkaONE/Szabi-voice-agent"
echo "  • Hetzner server: $SERVER:$SERVER_PATH"
echo ""
echo "To view logs: ssh $SERVER 'docker logs agent_voiceagent_1 -f'"
