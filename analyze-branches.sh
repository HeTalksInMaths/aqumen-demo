#!/bin/bash
# Branch Analysis Script
# This script helps analyze which branches need to be merged to main

set -e

echo "=========================================="
echo "Branch Cleanup Analysis Tool"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fetch all branches
echo "Fetching all remote branches..."
git fetch --all

echo ""
echo "=========================================="
echo "PHASE 1: Analyzing 'minimal' branch"
echo "=========================================="
echo ""

# Check minimal branch relationship with main
echo "Commits in minimal but not in main:"
MINIMAL_AHEAD=$(git log main..origin/minimal --oneline | wc -l)
if [ "$MINIMAL_AHEAD" -gt 0 ]; then
    echo -e "${YELLOW}minimal is $MINIMAL_AHEAD commits ahead of main${NC}"
    git log main..origin/minimal --oneline --decorate
else
    echo -e "${GREEN}minimal has no commits ahead of main${NC}"
fi

echo ""
echo "Commits in main but not in minimal:"
MINIMAL_BEHIND=$(git log origin/minimal..main --oneline | wc -l)
if [ "$MINIMAL_BEHIND" -gt 0 ]; then
    echo -e "${YELLOW}minimal is $MINIMAL_BEHIND commits behind main${NC}"
    git log origin/minimal..main --oneline --decorate
else
    echo -e "${GREEN}minimal has no commits behind main${NC}"
fi

echo ""
echo "File differences between minimal and main:"
git diff --stat origin/minimal main

echo ""
echo "=========================================="
echo "PHASE 2: Analyzing minimal2 branch"
echo "=========================================="
echo ""

MINIMAL2_AHEAD=$(git log main..origin/minimal2 --oneline | wc -l)
if [ "$MINIMAL2_AHEAD" -gt 0 ]; then
    echo -e "${YELLOW}minimal2 is $MINIMAL2_AHEAD commits ahead of main${NC}"
    git log main..origin/minimal2 --oneline --decorate | head -10
else
    echo -e "${GREEN}minimal2 has no commits ahead of main${NC}"
fi

echo ""
echo "=========================================="
echo "PHASE 3: Analyzing minimal-scaffold branch"
echo "=========================================="
echo ""

SCAFFOLD_AHEAD=$(git log main..origin/minimal-scaffold --oneline | wc -l)
if [ "$SCAFFOLD_AHEAD" -gt 0 ]; then
    echo -e "${YELLOW}minimal-scaffold is $MINIMAL_SCAFFOLD_AHEAD commits ahead of main${NC}"
    git log main..origin/minimal-scaffold --oneline --decorate | head -10
else
    echo -e "${GREEN}minimal-scaffold has no commits ahead of main${NC}"
fi

echo ""
echo "=========================================="
echo "PHASE 4: Analyzing Feature Branches"
echo "=========================================="
echo ""

FEATURE_BRANCHES=(
    "feat/question-playground-revamp"
    "feature/automate-dataset-creation"
    "feature/automate-dataset-creation-2"
    "feature/batch-pipeline-improvements"
    "refactor-backend-pipeline"
)

for branch in "${FEATURE_BRANCHES[@]}"; do
    echo "--- $branch ---"
    AHEAD=$(git log main..origin/$branch --oneline 2>/dev/null | wc -l)
    if [ "$AHEAD" -gt 0 ]; then
        echo -e "${YELLOW}Has $AHEAD commits not in main${NC}"
        git log main..origin/$branch --oneline --decorate | head -5
    else
        echo -e "${GREEN}No unique commits - can be deleted${NC}"
    fi
    echo ""
done

echo ""
echo "=========================================="
echo "PHASE 5: Analyzing Fix Branches"
echo "=========================================="
echo ""

FIX_BRANCHES=(
    "fix/css-color-rendering-issue"
    "password-modal-upgrades"
    "render"
)

for branch in "${FIX_BRANCHES[@]}"; do
    echo "--- $branch ---"
    AHEAD=$(git log main..origin/$branch --oneline 2>/dev/null | wc -l)
    if [ "$AHEAD" -gt 0 ]; then
        echo -e "${YELLOW}Has $AHEAD commits not in main${NC}"
        git log main..origin/$branch --oneline --decorate | head -5
    else
        echo -e "${GREEN}No unique commits - can be deleted${NC}"
    fi
    echo ""
done

echo ""
echo "=========================================="
echo "PHASE 6: Checking Codex Branches"
echo "=========================================="
echo ""

echo "All codex/* branches (automated tasks):"
git branch -r | grep "codex/" | wc -l
echo "These are typically safe to delete after review."

echo ""
echo "=========================================="
echo "Summary: Branches Merged to Main"
echo "=========================================="
echo ""

git branch -r --merged main | grep -v "HEAD\|main"

echo ""
echo "=========================================="
echo "Summary: Branches NOT Merged to Main"
echo "=========================================="
echo ""

git branch -r --no-merged main | grep -v "HEAD\|claude/"

echo ""
echo "=========================================="
echo "Analysis Complete!"
echo "=========================================="
echo ""
echo "Review the output above to determine:"
echo "1. Whether 'minimal' should be merged to main"
echo "2. Which feature branches have valuable unmerged work"
echo "3. Which branches can be safely deleted"
echo ""
echo "See BRANCH_CLEANUP_ANALYSIS.md for detailed recommendations."
