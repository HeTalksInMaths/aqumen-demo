#!/bin/bash

# Branch Analysis Script - Compare all branches against "minimal" (production branch)
# This script identifies which branches can be safely deleted

set -e

echo "=========================================="
echo "Branch Analysis vs MINIMAL (Production)"
echo "=========================================="
echo ""

# Fetch all branches
echo "Fetching all branches from remote..."
git fetch origin --prune
echo ""

# Get the minimal branch commit
MINIMAL_COMMIT=$(git rev-parse origin/minimal)
echo "Minimal branch is at: $MINIMAL_COMMIT"
echo ""

# Create output file
OUTPUT_FILE="minimal-branch-analysis.md"
echo "# Branch Analysis Against MINIMAL Branch" > "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "**Analysis Date:** $(date)" >> "$OUTPUT_FILE"
echo "**Minimal Branch Commit:** $MINIMAL_COMMIT" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Get all remote branches except HEAD
BRANCHES=$(git branch -r | grep -v 'HEAD' | grep -v 'minimal$' | sed 's/origin\///' | sort)

echo "Analyzing branches..."
echo ""

# Arrays to categorize branches
SAFE_TO_DELETE=()
NEEDS_REVIEW=()
HAS_UNIQUE_COMMITS=()

# Analyze each branch
for branch in $BRANCHES; do
    echo "Checking: $branch"

    # Get the commit hash
    BRANCH_COMMIT=$(git rev-parse "origin/$branch" 2>/dev/null || echo "INVALID")

    if [ "$BRANCH_COMMIT" = "INVALID" ]; then
        echo "  ⚠️  Branch not found"
        continue
    fi

    # Check if this branch is an ancestor of minimal (fully merged)
    if git merge-base --is-ancestor "origin/$branch" origin/minimal 2>/dev/null; then
        echo "  ✓ Fully merged into minimal - SAFE TO DELETE"
        SAFE_TO_DELETE+=("$branch")
    else
        # Check if minimal is an ancestor of this branch (branch is ahead)
        if git merge-base --is-ancestor origin/minimal "origin/$branch" 2>/dev/null; then
            echo "  ⚡ Branch is AHEAD of minimal - contains newer commits"
            HAS_UNIQUE_COMMITS+=("$branch")
        else
            # Branches have diverged
            UNIQUE_COMMITS=$(git log origin/minimal..origin/$branch --oneline 2>/dev/null | wc -l)
            if [ "$UNIQUE_COMMITS" -eq 0 ]; then
                echo "  ✓ No unique commits - SAFE TO DELETE"
                SAFE_TO_DELETE+=("$branch")
            else
                echo "  ⚠️  Has $UNIQUE_COMMITS unique commits - NEEDS REVIEW"
                NEEDS_REVIEW+=("$branch")
            fi
        fi
    fi
done

echo ""
echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo ""
echo "✓ Safe to delete (fully merged): ${#SAFE_TO_DELETE[@]}"
echo "⚠️  Needs review (diverged): ${#NEEDS_REVIEW[@]}"
echo "⚡ Ahead of minimal (newer): ${#HAS_UNIQUE_COMMITS[@]}"
echo ""

# Write detailed analysis to file
echo "## Summary" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "- **Safe to Delete:** ${#SAFE_TO_DELETE[@]} branches" >> "$OUTPUT_FILE"
echo "- **Needs Review:** ${#NEEDS_REVIEW[@]} branches" >> "$OUTPUT_FILE"
echo "- **Ahead of Minimal:** ${#HAS_UNIQUE_COMMITS[@]} branches" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Safe to delete section
echo "## ✓ Safe to Delete (Fully Merged into Minimal)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
if [ ${#SAFE_TO_DELETE[@]} -eq 0 ]; then
    echo "None" >> "$OUTPUT_FILE"
else
    for branch in "${SAFE_TO_DELETE[@]}"; do
        COMMIT=$(git rev-parse "origin/$branch")
        echo "- \`$branch\` (commit: ${COMMIT:0:7})" >> "$OUTPUT_FILE"
    done
fi
echo "" >> "$OUTPUT_FILE"

# Needs review section
echo "## ⚠️  Needs Review (Diverged from Minimal)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
if [ ${#NEEDS_REVIEW[@]} -eq 0 ]; then
    echo "None" >> "$OUTPUT_FILE"
else
    for branch in "${NEEDS_REVIEW[@]}"; do
        COMMIT=$(git rev-parse "origin/$branch")
        UNIQUE=$(git log origin/minimal..origin/$branch --oneline 2>/dev/null | wc -l)
        echo "- \`$branch\` (commit: ${COMMIT:0:7}, $UNIQUE unique commits)" >> "$OUTPUT_FILE"

        # Show first 5 unique commits
        echo "  \`\`\`" >> "$OUTPUT_FILE"
        git log origin/minimal..origin/$branch --oneline --max-count=5 >> "$OUTPUT_FILE" 2>/dev/null || true
        echo "  \`\`\`" >> "$OUTPUT_FILE"
    done
fi
echo "" >> "$OUTPUT_FILE"

# Ahead of minimal section
echo "## ⚡ Ahead of Minimal (Contains Newer Commits)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
if [ ${#HAS_UNIQUE_COMMITS[@]} -eq 0 ]; then
    echo "None" >> "$OUTPUT_FILE"
else
    for branch in "${HAS_UNIQUE_COMMITS[@]}"; do
        COMMIT=$(git rev-parse "origin/$branch")
        AHEAD=$(git log origin/minimal..origin/$branch --oneline 2>/dev/null | wc -l)
        echo "- \`$branch\` (commit: ${COMMIT:0:7}, $AHEAD commits ahead)" >> "$OUTPUT_FILE"

        # Show first 5 commits ahead
        echo "  \`\`\`" >> "$OUTPUT_FILE"
        git log origin/minimal..origin/$branch --oneline --max-count=5 >> "$OUTPUT_FILE" 2>/dev/null || true
        echo "  \`\`\`" >> "$OUTPUT_FILE"
    done
fi
echo "" >> "$OUTPUT_FILE"

echo "Analysis complete! Results saved to: $OUTPUT_FILE"
echo ""
echo "To delete safe branches, run:"
echo "  ./cleanup-minimal-branches.sh"
