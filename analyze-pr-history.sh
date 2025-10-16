#!/bin/bash

# PR History Analysis Script
# Identifies branches from closed/denied PRs that can be deleted

set -e

echo "=========================================="
echo "Pull Request History Analysis"
echo "=========================================="
echo ""

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

echo "Fetching PR information..."
echo ""

# Get all PRs
gh pr list --state all --limit 100 --json number,title,state,headRefName,baseRefName,mergedAt,closedAt,url > pr-data.json

# Parse PR data and categorize
echo "# Pull Request Analysis" > pr-analysis.md
echo "" >> pr-analysis.md
echo "**Analysis Date:** $(date)" >> pr-analysis.md
echo "" >> pr-analysis.md

# Analyze PRs
echo "## PRs Merged into Main" >> pr-analysis.md
echo "" >> pr-analysis.md
jq -r '.[] | select(.state == "MERGED" and .mergedAt != null) | "- PR #\(.number): \(.title) (branch: `\(.headRefName)`)"' pr-data.json >> pr-analysis.md || echo "None" >> pr-analysis.md
echo "" >> pr-analysis.md

echo "## PRs Closed Without Merging (SAFE TO DELETE)" >> pr-analysis.md
echo "" >> pr-analysis.md
jq -r '.[] | select(.state == "CLOSED" and .mergedAt == null) | "- PR #\(.number): \(.title) (branch: `\(.headRefName)`)"' pr-data.json >> pr-analysis.md || echo "None" >> pr-analysis.md
echo "" >> pr-analysis.md

echo "## Open PRs (DO NOT DELETE)" >> pr-analysis.md
echo "" >> pr-analysis.md
jq -r '.[] | select(.state == "OPEN") | "- PR #\(.number): \(.title) (branch: `\(.headRefName)`)"' pr-data.json >> pr-analysis.md || echo "None" >> pr-analysis.md
echo "" >> pr-analysis.md

# Get branches from closed PRs
echo "## Branches from Closed PRs (Candidates for Deletion)" >> pr-analysis.md
echo "" >> pr-analysis.md
echo "These branches had PRs that were closed without merging:" >> pr-analysis.md
echo "" >> pr-analysis.md
jq -r '.[] | select(.state == "CLOSED" and .mergedAt == null) | .headRefName' pr-data.json | sort -u | while read branch; do
    echo "- \`$branch\`" >> pr-analysis.md
done
echo "" >> pr-analysis.md

# Summary statistics
MERGED_COUNT=$(jq '[.[] | select(.state == "MERGED")] | length' pr-data.json)
CLOSED_COUNT=$(jq '[.[] | select(.state == "CLOSED" and .mergedAt == null)] | length' pr-data.json)
OPEN_COUNT=$(jq '[.[] | select(.state == "OPEN")] | length' pr-data.json)

echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""
echo "✓ Merged PRs: $MERGED_COUNT"
echo "✗ Closed (not merged) PRs: $CLOSED_COUNT"
echo "⏳ Open PRs: $OPEN_COUNT"
echo ""
echo "Analysis saved to: pr-analysis.md"
echo ""

# Create a list of branches to delete from closed PRs
jq -r '.[] | select(.state == "CLOSED" and .mergedAt == null) | .headRefName' pr-data.json | sort -u > closed-pr-branches.txt

echo "Branches from closed PRs saved to: closed-pr-branches.txt"
echo ""
echo "To delete these branches, run:"
echo "  cat closed-pr-branches.txt | xargs -I {} git push origin --delete {}"
