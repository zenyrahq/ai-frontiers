#!/bin/bash
# Deploy AI Frontiers to Cloud Server
# 部署 AI Frontiers 到云服务器

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  AI Frontiers - Cloud Deployment Script${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env file with your configuration${NC}"
    exit 1
fi

# Load environment variables
source .env

# Function to check command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}Error: $1 is not installed${NC}"
        exit 1
    fi
}

# Check required commands
echo -e "${BLUE}Checking prerequisites...${NC}"
check_command docker
check_command docker-compose

# Create necessary directories
echo -e "${BLUE}Creating directories...${NC}"
mkdir -p deployment/nginx/ssl
mkdir -p data/postgres
mkdir -p data/redis

# Pull latest images
echo -e "${BLUE}Pulling Docker images...${NC}"
docker-compose -f docker-compose.prod.yml pull

# Build images
echo -e "${BLUE}Building Docker images...${NC}"
docker-compose -f docker-compose.prod.yml build

# Stop existing containers
echo -e "${BLUE}Stopping existing containers...${NC}"
docker-compose -f docker-compose.prod.yml down

# Start services
echo -e "${BLUE}Starting services...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo -e "${BLUE}Waiting for services to start...${NC}"
sleep 10

# Check service health
echo -e "${BLUE}Checking service health...${NC}"

# Check API
if curl -sf http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ API is healthy${NC}"
else
    echo -e "${YELLOW}⚠ API health check failed${NC}"
fi

# Check Frontend
if curl -sf http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}✓ Frontend is healthy${NC}"
else
    echo -e "${YELLOW}⚠ Frontend health check failed${NC}"
fi

# Show status
echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "Services running:"
docker-compose -f docker-compose.prod.yml ps
echo ""
echo -e "Access the application:"
echo -e "  Frontend: ${GREEN}http://localhost${NC}"
echo -e "  API Docs: ${GREEN}http://localhost/api/docs${NC}"
echo ""
echo -e "Useful commands:"
echo -e "  View logs: ${BLUE}docker-compose -f docker-compose.prod.yml logs -f${NC}"
echo -e "  Stop:      ${BLUE}docker-compose -f docker-compose.prod.yml down${NC}"
echo -e "  Restart:   ${BLUE}docker-compose -f docker-compose.prod.yml restart${NC}"
