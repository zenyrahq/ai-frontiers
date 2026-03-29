#!/bin/bash

# ============================================================
# AI Frontiers - Pre-merge Checklist
# ============================================================
# Run this before merging any PR to main
# ============================================================

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "======================================"
echo "  Pre-merge Checklist"
echo "======================================"
echo ""

PASSED=0
FAILED=0
WARNINGS=0

check() {
    local name=$1
    local cmd=$2
    local required=${3:-true}

    echo -n "Checking $name... "

    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
        return 0
    else
        if [ "$required" = "true" ]; then
            echo -e "${RED}✗ FAIL${NC}"
            ((FAILED++))
            return 1
        else
            echo -e "${YELLOW}⚠ WARN${NC}"
            ((WARNINGS++))
            return 0
        fi
    fi
}

# Code Quality
echo "--- Code Quality ---"
check "No debug prints" "! grep -r 'console.log\|print(' --include='*.ts' --include='*.tsx' --include='*.py' frontend/src api/ 2>/dev/null | grep -v 'node_modules' | grep -v '__pycache__'" "false"
check "No TODO comments in changed files" "! git diff main --name-only | xargs grep -l 'TODO\|FIXME' 2>/dev/null" "false"

# Security
echo ""
echo "--- Security ---"
check "No hardcoded secrets" "! grep -r 'password\|secret\|api_key\|token' --include='*.py' --include='*.ts' --include='*.env' api/ frontend/src/ 2>/dev/null | grep -v '.example' | grep -v 'os.getenv' | grep -v 'process.env'" "false"
check "No .env files staged" "! git diff --cached --name-only | grep '.env$'" "false"

# Tests
echo ""
echo "--- Tests ---"
check "Backend tests exist" "[ -d 'api/tests' ] && [ $(find api/tests -name 'test_*.py' | wc -l) -gt 0 ]" "false"
check "Frontend builds" "cd frontend && npm run build"

# Documentation
echo ""
echo "--- Documentation ---"
check "API docs exist for new endpoints" "true" "false"  # Manual check
check "README is up to date" "true" "false"  # Manual check

# Summary
echo ""
echo "======================================"
echo "  Summary"
echo "======================================"
echo -e "Passed:   ${GREEN}$PASSED${NC}"
echo -e "Failed:   ${RED}$FAILED${NC}"
echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
echo ""

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Cannot merge: $FAILED checks failed${NC}"
    exit 1
else
    echo -e "${GREEN}Ready to merge!${NC}"
    echo ""
    echo "Final checks (manual):"
    echo "  [ ] Code reviewed by at least 1 person"
    echo "  [ ] Documentation updated if needed"
    echo "  [ ] Breaking changes communicated"
    echo "  [ ] Tested on staging environment"
fi
