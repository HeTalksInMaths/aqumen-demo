# Branch Cleanup Guide - Minimal Branch (Production)

**Date:** October 16, 2025
**Production Branch:** `minimal` (deployed on Vercel)
**Tech Stack:** React (Vercel), Backend (Render), PostgreSQL, FastAPI

## Overview

This guide helps clean up branches in the repository by comparing them against the **`minimal`** branch, which is the production branch deployed on Vercel.

### Key Information

- **Production Branch:** `minimal` (not `main`)
- **Deployment:** Vercel (frontend) + Render (backend)
- **Future Plan:** Will fork to company GitHub as main branch
- **No Streamlit:** Current version is React-based

## Quick Start

### 1. Run Full Analysis

```bash
chmod +x full-branch-analysis.sh
./full-branch-analysis.sh
```

This will:
- Compare all branches against `minimal`
- Analyze PR merge/close history
- Identify branches safe to delete

### 2. Review Results

Check the generated files:
- `minimal-branch-analysis.md` - Branch comparison results
- `pr-analysis.md` - PR history analysis
- `closed-pr-branches.txt` - Branches from closed/denied PRs

### 3. Clean Up Branches

```bash
./cleanup-minimal-branches.sh
```

**Warning:** This will delete remote branches! Review the analysis first.

## Analysis Scripts

### `analyze-minimal-branch.sh`

Compares all branches against the `minimal` production branch.

**Identifies:**
- ✓ Branches fully merged into minimal (safe to delete)
- ⚠️ Branches with diverged commits (needs review)
- ⚡ Branches ahead of minimal (contains newer work)

**Usage:**
```bash
./analyze-minimal-branch.sh
```

**Output:** `minimal-branch-analysis.md`

### `analyze-pr-history.sh`

Analyzes GitHub PR history to identify:
- Merged PRs
- Closed/denied PRs (branches can be deleted)
- Open PRs (do not delete)

**Requirements:** GitHub CLI (`gh`)

**Usage:**
```bash
./analyze-pr-history.sh
```

**Output:** `pr-analysis.md`, `closed-pr-branches.txt`

### `cleanup-minimal-branches.sh`

Safely deletes branches that are fully merged into `minimal`.

**Features:**
- Auto-deletes `codex/*` and `claude/*` automated branches
- Prompts for confirmation on feature branches
- Skips branches with unique commits
- Protects `minimal` and `main` branches

**Usage:**
```bash
./cleanup-minimal-branches.sh
```

### `full-branch-analysis.sh`

Master script that runs all analysis steps in sequence.

**Usage:**
```bash
./full-branch-analysis.sh
```

## Branch Categories

### Safe to Delete

Branches that meet ALL criteria:
- Fully merged into `minimal`
- No unique commits compared to `minimal`
- Associated PR is closed/merged (if applicable)

Examples:
- `codex/*` branches (automated)
- `claude/*` branches (automated)
- Branches from closed PRs

### Needs Review

Branches that:
- Have diverged from `minimal`
- Contain unique commits not in `minimal`
- May have valuable work

Action: Manually review commits to decide merge or delete

### Ahead of Minimal

Branches that:
- Contain newer commits than `minimal`
- May be experimental or work-in-progress

Action: Determine if work should be merged to `minimal`

## Manual Branch Deletion

To manually delete a branch:

```bash
# Delete remote branch
git push origin --delete branch-name

# Delete local branch (if exists)
git branch -D branch-name
```

To delete multiple branches from closed PRs:

```bash
cat closed-pr-branches.txt | xargs -I {} git push origin --delete {}
```

## Understanding the Minimal Branch

The `minimal` branch:
- Is the production branch (deployed on Vercel)
- Contains the stable React application
- Is NOT the same as `main`
- Will eventually become the main branch in a company fork

**Do not delete or modify `minimal` without careful consideration!**

## Merge Strategy

If you need to merge a branch into `minimal`:

```bash
# Checkout minimal
git checkout minimal
git pull origin minimal

# Merge the branch
git merge --no-ff feature-branch-name

# Push to production
git push origin minimal
```

**Note:** This will trigger a deployment on Vercel!

## Common Questions

### Q: Why compare against `minimal` instead of `main`?

**A:** `minimal` is the production branch deployed on Vercel. `main` is not currently used for production.

### Q: Can I delete `codex/*` branches automatically?

**A:** Yes, these are automated branches from Codex CLI and can be safely deleted after review.

### Q: What if a branch has commits not in `minimal`?

**A:** Review the commits first. They may contain:
- Important features to merge
- Experimental work to preserve
- Abandoned work to delete

### Q: Should I delete the `main` branch?

**A:** No! Keep `main` as it may be used for reference or future merging.

## Troubleshooting

### GitHub CLI Not Found

If `analyze-pr-history.sh` fails:

```bash
# Install GitHub CLI
# Visit: https://cli.github.com/

# Authenticate
gh auth login
```

### Branch Already Deleted

If you get "remote ref does not exist" errors:

```bash
# Prune deleted branches
git fetch origin --prune
```

### Merge Conflicts

If merging to `minimal` causes conflicts:

```bash
# Abort the merge
git merge --abort

# Manually resolve
git checkout minimal
git merge branch-name
# Resolve conflicts in editor
git add .
git commit
git push origin minimal
```

## Support

For issues with these scripts, check:
1. Git is properly configured
2. You have push access to the repository
3. GitHub CLI is authenticated (for PR analysis)
4. You're on the correct branch

## Automation Notes

These scripts can be integrated into CI/CD:
- Run analysis weekly to identify stale branches
- Auto-delete `codex/*` branches older than 30 days
- Send reports to team for review

## Next Steps

1. Run `full-branch-analysis.sh` to get current state
2. Review generated markdown files
3. Delete safe branches using cleanup script
4. Manually review branches with unique commits
5. Consider merging valuable work into `minimal`
6. Update this document if you change the strategy

---

**Remember:** Always review before deleting. When in doubt, keep the branch!
