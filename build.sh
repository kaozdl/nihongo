#!/bin/bash

# JLPT Test Manager - Build and Tag Script
# This script creates a git tag and prepares deployment package

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   JLPT Test Manager - Build & Tag Script            ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if git repo
if [ ! -d .git ]; then
    echo -e "${RED}❌ Error: Not a git repository${NC}"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}⚠️  Warning: You have uncommitted changes${NC}"
    echo -e "${YELLOW}   Please commit or stash your changes first${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Build cancelled${NC}"
        exit 1
    fi
fi

# Get current version or prompt for new one
echo -e "${BLUE}📦 Current tags:${NC}"
git tag -l | tail -5 || echo "  No tags yet"
echo ""

# Prompt for version
read -p "Enter new version tag (e.g., v1.0.0): " VERSION

if [ -z "$VERSION" ]; then
    echo -e "${RED}❌ Error: Version tag cannot be empty${NC}"
    exit 1
fi

# Check if tag already exists
if git rev-parse "$VERSION" >/dev/null 2>&1; then
    echo -e "${RED}❌ Error: Tag '$VERSION' already exists${NC}"
    exit 1
fi

# Optional: Add tag message
read -p "Enter tag message (optional): " TAG_MESSAGE

# Create the tag
echo -e "${GREEN}🏷️  Creating tag '$VERSION'...${NC}"
if [ -z "$TAG_MESSAGE" ]; then
    git tag "$VERSION"
else
    git tag -a "$VERSION" -m "$TAG_MESSAGE"
fi

echo -e "${GREEN}✅ Tag '$VERSION' created successfully${NC}"
echo ""

# Ask if user wants to push tag
read -p "Push tag to remote? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}📤 Pushing tag to remote...${NC}"
    git push origin "$VERSION"
    echo -e "${GREEN}✅ Tag pushed to remote${NC}"
fi
echo ""

# Create deployment package
echo -e "${BLUE}📦 Creating deployment package...${NC}"

PACKAGE_NAME="nihongo-${VERSION}-pythonanywhere.zip"

# Files to include in deployment package
FILES=(
    "*.py"
    "*.md"
    "*.txt"
    "*.json"
    "*.ini"
    "*.cfg"
    "*.sh"
    "*.bat"
    "models/"
    "templates/"
    "translations/"
    "admin/"
    "alembic/"
    "docs/"
    "env.production.example"
)

# Create temporary directory for packaging
TEMP_DIR=$(mktemp -d)
PACKAGE_DIR="$TEMP_DIR/package_contents"
mkdir -p "$PACKAGE_DIR"

echo -e "${BLUE}   Copying files...${NC}"

# Copy files preserving structure
for pattern in "${FILES[@]}"; do
    if [[ "$pattern" == */ ]]; then
        # Directory - copy recursively preserving structure
        dir_name="${pattern%/}"
        if [ -d "$dir_name" ]; then
            echo -e "     📁 $dir_name/"
            cp -r "$dir_name" "$PACKAGE_DIR/"
        fi
    else
        # Files - use find to handle glob patterns
        found_files=$(find . -maxdepth 1 -name "$pattern" -type f)
        if [ -n "$found_files" ]; then
            echo "$found_files" | while read -r file; do
                echo -e "     📄 $(basename "$file")"
                cp "$file" "$PACKAGE_DIR/"
            done
        fi
    fi
done

# Create the zip from inside the package directory (files at root of zip)
echo -e "${BLUE}   Creating archive...${NC}"
cd "$PACKAGE_DIR"
zip -r "$PACKAGE_NAME" . > /dev/null
cd - > /dev/null

# Move to current directory
mv "$PACKAGE_DIR/$PACKAGE_NAME" .

# Cleanup
rm -rf "$TEMP_DIR"

# Get package size
PACKAGE_SIZE=$(du -h "$PACKAGE_NAME" | cut -f1)

echo -e "${GREEN}✅ Deployment package created: $PACKAGE_NAME ($PACKAGE_SIZE)${NC}"
echo ""

# Display deployment instructions
echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   📋 DEPLOYMENT INSTRUCTIONS                         ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ Build completed successfully!${NC}"
echo ""
echo -e "${YELLOW}📦 Package: $PACKAGE_NAME${NC}"
echo -e "${YELLOW}🏷️  Version: $VERSION${NC}"
echo ""
echo -e "${BLUE}Next steps for PythonAnywhere deployment:${NC}"
echo ""
echo -e "  1️⃣  Log in to https://www.pythonanywhere.com"
echo -e "  2️⃣  Go to the ${GREEN}Files${NC} tab"
echo -e "  3️⃣  Upload ${YELLOW}$PACKAGE_NAME${NC}"
echo -e "  4️⃣  Open a ${GREEN}Bash console${NC} and run:"
echo ""
echo -e "${GREEN}     cd ~"
echo -e "     rm -rf nihongo  # Remove old deployment if exists"
echo -e "     mkdir nihongo"
echo -e "     cd nihongo"
echo -e "     unzip ../$PACKAGE_NAME"
echo -e "     python3.11 -m venv venv"
echo -e "     source venv/bin/activate"
echo -e "     pip install --upgrade pip"
echo -e "     pip install -r requirements.txt${NC}"
echo ""
echo -e "  5️⃣  Verify directory structure: ${GREEN}ls -la models/${NC}"
echo -e "      ${YELLOW}Should see: __init__.py, user.py, exam.py, etc.${NC}"
echo -e "  6️⃣  Create ${YELLOW}.env${NC} file with production settings"
echo -e "  7️⃣  Initialize database: ${GREEN}flask init-db${NC}"
echo -e "  8️⃣  Configure WSGI file (see PYTHONANYWHERE_DEPLOYMENT.md)"
echo -e "  9️⃣  Reload web app"
echo ""
echo -e "${BLUE}📖 For detailed instructions, see:${NC}"
echo -e "   ${GREEN}PYTHONANYWHERE_DEPLOYMENT.md${NC}"
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🎉 Happy Deploying!                                ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}"

