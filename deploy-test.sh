#!/bin/bash
#
# Test Deploy Script - Upload to Hetzner WITHOUT GitHub
# Use this to test changes on the server before committing to GitHub
#
# Usage: ./deploy-test.sh
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SERVER="root@37.27.247.64"
SERVER_PATH="/opt/agent"
LOCAL_PATH="/Users/szabolcs.levai/Desktop/agent"

echo -e "${BLUE}=== Test Deployment to Hetzner (Skip GitHub) ===${NC}\n"

# Step 1: Show what will be uploaded
echo -e "${YELLOW}Step 1: Checking for changes...${NC}"
if [[ -n $(git status -s) ]]; then
    echo "Local changes detected:"
    git status -s
    echo ""
else
    echo "No local changes detected"
fi

# Step 2: Sync code files to server (excluding sensitive files and git)
echo -e "${YELLOW}Step 2: Uploading files to Hetzner...${NC}"

rsync -avz --progress \
  --exclude='.git/' \
  --exclude='.env' \
  --exclude='__pycache__/' \
  --exclude='*.pyc' \
  --exclude='.DS_Store' \
  --exclude='node_modules/' \
  --exclude='*.log' \
  --exclude='.claude/' \
  --exclude='livekit_data/' \
  --exclude='caddy_data/' \
  --exclude='caddy_config/' \
  --exclude='*.db' \
  --exclude='*.sqlite' \
  --exclude='deploy.sh' \
  --exclude='deploy-test.sh' \
  --exclude='DEPLOYMENT.md' \
  "${LOCAL_PATH}/" "${SERVER}:${SERVER_PATH}/"

echo -e "\n✓ Files uploaded"

# Step 3: Rebuild and restart services
echo -e "\n${YELLOW}Step 3: Restarting services on Hetzner...${NC}"

ssh $SERVER << 'EOF'
cd /opt/agent

echo "Stopping services..."
docker-compose down

echo "Rebuilding containers..."
docker-compose build --no-cache voiceagent

echo "Starting services..."
docker-compose up -d

echo "✓ Services restarted"
EOF

echo -e "\n${GREEN}=== Test Deployment Complete ===${NC}"
echo -e "\n${BLUE}Next steps:${NC}"
echo "  1. Test on Hetzner: https://szabolcslevai.com"
echo "  2. View logs: ssh $SERVER 'docker logs agent_voiceagent_1 -f'"
echo "  3. If it works, commit & push to GitHub: ./deploy.sh \"your message\""
echo "  4. If it doesn't work, make more changes and run ./deploy-test.sh again"
echo ""
echo -e "${YELLOW}Note: .env file is NOT synced (for security). Sync manually if needed:${NC}"
echo "  scp .env ${SERVER}:${SERVER_PATH}/.env"
