#!/bin/bash

# Branch Cleanup Script - Delete branches that are fully merged into "minimal"
# Run analyze-minimal-branch.sh first to see what will be deleted

set -e

echo "=========================================="
echo "Branch Cleanup for MINIMAL Branch"
echo "=========================================="
echo ""
echo "⚠️  WARNING: This will delete remote branches!"
echo "Make sure you've reviewed minimal-branch-analysis.md first"
echo ""
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "Fetching latest branches..."
git fetch origin --prune
echo ""

# Get branches that are fully merged into minimal
MINIMAL_COMMIT=$(git rev-parse origin/minimal)
echo "Minimal branch is at: $MINIMAL_COMMIT"
echo ""

BRANCHES=$(git branch -r | grep -v 'HEAD' | grep -v 'minimal$' | grep -v 'main$' | sed 's/origin\///' | sort)

DELETED_COUNT=0
KEPT_COUNT=0

for branch in $BRANCHES; do
    # Skip if branch doesn't exist
    if ! git rev-parse "origin/$branch" &>/dev/null; then
        continue
    fi

    # Check if fully merged into minimal
    if git merge-base --is-ancestor "origin/$branch" origin/minimal 2>/dev/null; then
        # Additional check: ensure no unique commits
        UNIQUE_COMMITS=$(git log origin/minimal..origin/$branch --oneline 2>/dev/null | wc -l)

        if [ "$UNIQUE_COMMITS" -eq 0 ]; then
            echo "Deleting: $branch (fully merged)"

            # Auto-delete codex/* and claude/* branches (automated)
            if [[ "$branch" == codex/* ]] || [[ "$branch" == claude/* ]]; then
                git push origin --delete "$branch" 2>/dev/null || echo "  (already deleted)"
                DELETED_COUNT=$((DELETED_COUNT + 1))
            else
                # Ask for confirmation on other branches
                read -p "  Delete $branch? (y/n): " DELETE
                if [ "$DELETE" = "y" ]; then
                    git push origin --delete "$branch" 2>/dev/null || echo "  (already deleted)"
                    DELETED_COUNT=$((DELETED_COUNT + 1))
                else
                    echo "  Kept: $branch"
                    KEPT_COUNT=$((KEPT_COUNT + 1))
                fi
            fi
        else
            echo "Keeping: $branch (has $UNIQUE_COMMITS unique commits)"
            KEPT_COUNT=$((KEPT_COUNT + 1))
        fi
    else
        echo "Keeping: $branch (not fully merged)"
        KEPT_COUNT=$((KEPT_COUNT + 1))
    fi
done

echo ""
echo "=========================================="
echo "Cleanup Complete"
echo "=========================================="
echo "Deleted: $DELETED_COUNT branches"
echo "Kept: $KEPT_COUNT branches"
echo ""
