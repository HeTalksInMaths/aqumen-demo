#!/bin/bash
# Branch Cleanup Script
# WARNING: This script will DELETE branches. Review carefully before running!

set -e

echo "=========================================="
echo "Branch Cleanup Script"
echo "=========================================="
echo ""
echo "WARNING: This script will delete branches from the remote repository."
echo "Please review BRANCH_CLEANUP_ANALYSIS.md before proceeding."
echo ""
read -p "Have you reviewed the analysis and want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo "=========================================="
echo "PHASE 1: Delete Codex Automated Branches"
echo "=========================================="
echo ""
echo "These branches were created by automated tools and are typically safe to delete."
echo ""

CODEX_BRANCHES=(
    "codex/analyze-button-functionality-in-recent-commits"
    "codex/analyze-button-functionality-in-recent-commits-gfxqos"
    "codex/analyze-button-functionality-in-recent-commits-sfzf3h"
    "codex/debug-vercel-build-error-b4r2e7"
    "codex/determine-minimal-files-for-gpt-5-nano"
    "codex/fix-color-scheme-rendering-issue"
    "codex/fix-color-scheme-rendering-issue-437kdu"
    "codex/fix-color-scheme-rendering-issue-qn1wla"
    "codex/fix-non-clickable-dev-mode-button"
    "codex/review-relevant-.md-files-in-codebase"
    "codex/review-relevant-.md-files-in-codebase-yjn0p9"
)

read -p "Delete ${#CODEX_BRANCHES[@]} codex/* branches? (yes/no): " DELETE_CODEX

if [ "$DELETE_CODEX" == "yes" ]; then
    for branch in "${CODEX_BRANCHES[@]}"; do
        echo "Deleting $branch..."
        git push origin --delete "$branch" || echo "Failed to delete $branch (may not exist)"
    done
    echo "✓ Codex branches deleted"
else
    echo "Skipped codex branch deletion"
fi

echo ""
echo "=========================================="
echo "PHASE 2: Delete Duplicate Branches"
echo "=========================================="
echo ""

echo "feat/refactor-prompt-pipeline is identical to original-aqumen-streamlit"
read -p "Delete feat/refactor-prompt-pipeline? (yes/no): " DELETE_DUP1

if [ "$DELETE_DUP1" == "yes" ]; then
    git push origin --delete feat/refactor-prompt-pipeline || echo "Failed to delete"
    echo "✓ Deleted feat/refactor-prompt-pipeline"
fi

echo ""
echo "Checking if feature/automate-dataset-creation and feature/automate-dataset-creation-2 are identical..."
git fetch origin feature/automate-dataset-creation feature/automate-dataset-creation-2
DIFF_COUNT=$(git diff origin/feature/automate-dataset-creation origin/feature/automate-dataset-creation-2 | wc -l)

if [ "$DIFF_COUNT" -eq 0 ]; then
    echo "The branches are identical."
    read -p "Delete feature/automate-dataset-creation-2? (yes/no): " DELETE_DUP2
    if [ "$DELETE_DUP2" == "yes" ]; then
        git push origin --delete feature/automate-dataset-creation-2 || echo "Failed to delete"
        echo "✓ Deleted feature/automate-dataset-creation-2"
    fi
else
    echo "The branches differ. Manual review needed."
fi

echo ""
echo "=========================================="
echo "PHASE 3: Delete hardcoded-examples (if obsolete)"
echo "=========================================="
echo ""

echo "hardcoded-examples points to commit 16e7063 (old main before PR #4)"
echo "Current main is at 9323692 (after PR #4)"
read -p "Delete hardcoded-examples branch? (yes/no): " DELETE_HARDCODED

if [ "$DELETE_HARDCODED" == "yes" ]; then
    git push origin --delete hardcoded-examples || echo "Failed to delete"
    echo "✓ Deleted hardcoded-examples"
fi

echo ""
echo "=========================================="
echo "PHASE 4: Minimal Branches (REQUIRES MANUAL REVIEW)"
echo "=========================================="
echo ""

echo "⚠️  IMPORTANT: Review the minimal branch analysis before deleting!"
echo "Run ./analyze-branches.sh first to understand the relationship."
echo ""
echo "Minimal branches found:"
echo "  - minimal (commit b7a18d4)"
echo "  - minimal2 (commit 6d033f1)"
echo "  - minimal-scaffold (commit 5eb19ef)"
echo ""
echo "These branches are NOT deleted by this script."
echo "After reviewing the analysis, you can delete them manually:"
echo ""
echo "  git push origin --delete minimal"
echo "  git push origin --delete minimal2"
echo "  git push origin --delete minimal-scaffold"
echo ""

echo ""
echo "=========================================="
echo "Cleanup Complete!"
echo "=========================================="
echo ""
echo "Branches that still need manual review:"
echo "  - minimal, minimal2, minimal-scaffold (need diff analysis)"
echo "  - feature/automate-dataset-creation (may have valuable work)"
echo "  - feature/batch-pipeline-improvements (may have valuable work)"
echo "  - refactor-backend-pipeline (may have valuable work)"
echo "  - feat/question-playground-revamp (may have valuable work)"
echo "  - fix/css-color-rendering-issue (check if fix is in main)"
echo "  - password-modal-upgrades (check if merged)"
echo "  - render (unknown purpose)"
echo ""
echo "Next steps:"
echo "1. Run ./analyze-branches.sh to check feature branches"
echo "2. Merge any valuable unmerged work"
echo "3. Delete branches after confirming they're merged or obsolete"
echo "4. Update BRANCH_HISTORY.md with cleanup results"
