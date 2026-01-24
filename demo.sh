#!/bin/bash
# Run Athena demo with sample data
#
# The demo will be accessible at:
#   - http://localhost:3000 (this machine)
#   - http://<your-ip>:3000 (other machines on network)

set -e
cd "$(dirname "$0")"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Initialize sample data git repo if needed
if [ ! -d ".screenshot-data/athena/.git" ]; then
    echo "Initializing sample data..."
    bash .screenshot-data/init-git.sh
fi

# Get local IP address
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo -e "${BLUE}Starting Athena demo...${NC}"
echo ""

# Build and start
docker compose -f docker-compose.demo.yml up --build -d

echo ""
echo -e "${GREEN}Athena demo is starting!${NC}"
echo ""
echo "Access the app at:"
echo -e "  Local:   ${BLUE}http://localhost:3000${NC}"
echo -e "  Network: ${BLUE}http://${LOCAL_IP}:3000${NC}"
echo ""
echo "API available at:"
echo -e "  Local:   ${BLUE}http://localhost:8000${NC}"
echo -e "  Network: ${BLUE}http://${LOCAL_IP}:8000${NC}"
echo ""
echo "To view logs:  docker compose -f docker-compose.demo.yml logs -f"
echo "To stop:       docker compose -f docker-compose.demo.yml down"
echo ""

# Wait for health check
echo "Waiting for services to be ready..."
timeout 60 bash -c 'until curl -sf http://localhost:3000 > /dev/null 2>&1; do sleep 2; echo -n "."; done' && echo -e " ${GREEN}Ready!${NC}" || echo " Timeout - check logs"
