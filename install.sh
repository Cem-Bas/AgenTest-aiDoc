#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Installing AiDoc - Advanced Web Console Analyzer${NC}"

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo -e "${RED}Error: Python $required_version or higher is required${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install the package in development mode
echo -e "${YELLOW}Installing AiDoc...${NC}"
pip install -e .

# Create reports directory structure
echo -e "${YELLOW}Creating reports directory structure...${NC}"
mkdir -p reports/{screenshots,html,json}

echo -e "${GREEN}Installation complete!${NC}"
echo -e "\nTo use AiDoc, activate the virtual environment and run:"
echo -e "${YELLOW}source venv/bin/activate${NC}"
echo -e "${YELLOW}aidoc https://example.com${NC}"
