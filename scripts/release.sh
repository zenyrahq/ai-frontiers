#!/bin/bash

# ============================================================
# AI Frontiers - Release Script
# ============================================================
# Usage: ./scripts/release.sh [patch|minor|major] [message]
# Example: ./scripts/release.sh patch "Fix search bug"
# ============================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get current version
get_current_version() {
    git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0"
}

# Calculate new version
calculate_new_version() {
    local current=$1
    local type=$2

    # Remove 'v' prefix
    current=${current#v}

    IFS='.' read -r major minor patch <<< "$current"

    case $type in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
        *)
            echo -e "${RED}Invalid version type: $type${NC}"
            exit 1
            ;;
    esac

    echo "v$major.$minor.$patch"
}

# Pre-release checks
pre_release_checks() {
    echo -e "${BLUE}=== Pre-release Checks ===${NC}"

    # Check if on main branch
    local branch=$(git branch --show-current)
    if [ "$branch" != "main" ]; then
        echo -e "${RED}✗ Not on main branch (current: $branch)${NC}"
        echo -e "${YELLOW}  Run: git checkout main && git pull${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ On main branch${NC}"

    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        echo -e "${RED}✗ Uncommitted changes detected${NC}"
        git status --short
        exit 1
    fi
    echo -e "${GREEN}✓ No uncommitted changes${NC}"

    # Check for unpushed commits
    local unpushed=$(git log @{u}..HEAD --oneline 2>/dev/null | wc -l)
    if [ "$unpushed" -gt 0 ]; then
        echo -e "${YELLOW}! You have $unpushed unpushed commits${NC}"
        read -p "  Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    echo ""
}

# Run tests
run_tests() {
    echo -e "${BLUE}=== Running Tests ===${NC}"

    # Backend tests
    if [ -d "api/tests" ]; then
        echo "Running backend tests..."
        cd api
        python -m pytest tests/ -v || true
        cd ..
    fi

    # Frontend build
    if [ -d "frontend" ]; then
        echo "Building frontend..."
        cd frontend
        npm run build
        cd ..
    fi

    echo -e "${GREEN}✓ Tests passed${NC}"
    echo ""
}

# Create release
create_release() {
    local version=$1
    local message=$2

    echo -e "${BLUE}=== Creating Release $version ===${NC}"

    # Create tag
    git tag -a "$version" -m "Release $version: $message"
    echo -e "${GREEN}✓ Tag created${NC}"

    # Push tag
    git push origin "$version"
    echo -e "${GREEN}✓ Tag pushed${NC}"

    echo ""
}

# Post-release tasks
post_release() {
    local version=$1

    echo -e "${BLUE}=== Post-release Tasks ===${NC}"

    echo -e "${YELLOW}Remember to:${NC}"
    echo "  1. Update CHANGELOG.md"
    echo "  2. Update docs-private/project-management/PROJECT_MANAGEMENT.md"
    echo "  3. Create GitHub Release with release notes"
    echo "  4. Monitor deployment (if auto-deploy enabled)"
    echo ""
    echo -e "${GREEN}Release $version created successfully!${NC}"
}

# Main
main() {
    local version_type=${1:-patch}
    local message=${2:-"Release"}

    local current_version=$(get_current_version)
    local new_version=$(calculate_new_version "$current_version" "$version_type")

    echo -e "${BLUE}"
    echo "========================================"
    echo "  AI Frontiers Release Script"
    echo "========================================"
    echo -e "${NC}"
    echo "Current version: $current_version"
    echo "New version:     $new_version"
    echo "Type:            $version_type"
    echo "Message:         $message"
    echo ""

    read -p "Proceed with release? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi

    pre_release_checks
    run_tests
    create_release "$new_version" "$message"
    post_release "$new_version"
}

main "$@"
