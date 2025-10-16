#!/bin/bash

# Master Branch Analysis Script
# Analyzes all branches against "minimal" production branch and PR history
# Provides comprehensive cleanup recommendations

set -e

echo "=========================================="
echo "Full Branch Cleanup Analysis"
echo "=========================================="
echo ""
echo "This script will:"
echo "1. Analyze all branches vs minimal branch"
echo "2. Check PR merge/close history"
echo "3. Generate cleanup recommendations"
echo ""

# Make scripts executable
chmod +x analyze-minimal-branch.sh
chmod +x analyze-pr-history.sh
chmod +x cleanup-minimal-branches.sh

# Run branch analysis
echo "Step 1: Analyzing branches against minimal..."
echo "=========================================="
./analyze-minimal-branch.sh

echo ""
echo "Step 2: Analyzing PR history..."
echo "=========================================="
./analyze-pr-history.sh || echo "⚠️  PR analysis failed (gh CLI may not be available)"

echo ""
echo "=========================================="
echo "Analysis Complete!"
echo "=========================================="
echo ""
echo "Review these files:"
echo "  📄 minimal-branch-analysis.md - Branch comparison results"
echo "  📄 pr-analysis.md - PR merge/close history"
echo "  📄 closed-pr-branches.txt - Branches from closed PRs"
echo ""
echo "To clean up branches, run:"
echo "  ./cleanup-minimal-branches.sh"
echo ""
