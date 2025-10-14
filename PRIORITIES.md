# Priority Action List - Aqumen.ai Project

**Created**: October 2025
**Current State**: Minimal deployment package ready, build fixed, needs production deployment

---

## 🎯 Priority List (Most Important First)

### 🚀 **PRIORITY 1: Deploy to Production** (HIGH - Do First!)
**Why**: Minimal package is ready, build fixed, need to validate it works in production

**Tasks**:
1. **Deploy backend to Render** (~15 mins)
   - Push `minimal` branch to Render
   - Set AWS environment variables
   - Test `/health` endpoint

2. **Deploy frontend to Vercel** (~10 mins)
   - Set Root Directory: `minimal/frontend`
   - Set `VITE_API_URL` to Render backend URL
   - Test all 4 button modes work

3. **End-to-end test** (~10 mins)
   - Student + Demo (10 questions)
   - Dev + Demo (GRPO + pipeline)
   - Dev + Live (generate question with real topic)

**Files**: `DEPLOYMENT_MINIMAL_SET.md`, `minimal/README.md`

---

### 🧪 **PRIORITY 2: Test Minimal Package in Fresh Clone** (HIGH - CRITICAL!)
**Why**: Verify it actually works for someone pulling the repo fresh

**Tasks**:
1. Clone repo in new directory
2. Checkout `minimal` branch
3. Follow `minimal/README.md` exactly
4. Document any missing steps

**Expected time**: 30 mins

**IMPORTANT**: If this works, you can **SKIP cleanup entirely**. Just work from `minimal/` directory going forward and ignore all the old duplicate code in the root. No need to delete anything - just don't touch it.

---

### 💰 **PRIORITY 3: Implement Cost Optimizations** (MEDIUM - Saves $75/day!)
**Why**: Currently spending $97/day, can reduce to ~$20/day

**Tasks**:
1. **Check MCP servers**: `/mcp` → disable unused ones
2. **Use `/compact`** in current session (do this NOW)
3. **Start fresh session** for next feature
4. **Test grep-first workflow**: Practice asking for searches before file reads

**Expected savings**: 75-80% reduction
**Files**: `CLAUDE.md` (already updated with cost-saving rules)

---

### 🧹 **PRIORITY 4: Cleanup Duplicate Code** (LOW - Optional!)
**Why**: Reduces clutter, prevents reading wrong files, saves token costs

**NOTE**: **SKIP THIS if minimal package works in fresh clone!** Just work from `minimal/` directory and ignore the rest.

**Tasks** (only if you really want cleanup):
1. **Delete deprecated directories**:
   - `frontend-dev/`
   - `frontend-main/`
   - `frontend-main-branch/`

2. **Delete old root files**:
   - `demo.jsx`, `demo-modular.jsx`
   - `constants.js`
   - `*.jsonl` session logs

**Expected time**: 20 mins
**Token savings**: ~$40/day (prevents reading duplicates)

**Files**: `FRONTEND_CLEANUP_PLAN.md`, `FILE_AUDIT.md`

---

### 📦 **PRIORITY 5: Modularize App.jsx** (LOW - Future Optimization)
**Why**: Improves maintainability, but not urgent for MVP

**Tasks**:
1. Extract GRPO mock data → `src/data/grpoExample.js`
2. Extract 10 demo questions → `src/data/demoQuestions.js`
3. Split components:
   - `AssessmentView.jsx`
   - `PipelinePanel.jsx`
   - `ModeToggle.jsx`

**Expected time**: 2-3 hours
**Benefits**: Easier to maintain, better code organization
**Risk**: Could introduce bugs, not needed for MVP

**When to do**: After deployment is stable and you're adding new features

---

### 🆕 **PRIORITY 6: New Features** (LOW - After Above)

**Potential features** (from docs):
- Add more gold-standard examples (RAG, RLHF, DPO)
- User authentication
- Question history/favorites
- Export questions as JSON
- Analytics dashboard
- Rotate through multiple demo examples

**When**: After deployment, cost optimization, and fresh clone test are done

---

## 📊 Suggested Order for Next 2-3 Days

### Day 1 (Today):
1. ✅ `/compact` this session (save context)
2. 🧪 **Test fresh clone first** (30 mins) - validates everything works
3. 🚀 Deploy to Vercel + Render (1 hour)
4. 🧪 Test production deployment (30 mins)

### Day 2:
1. 💰 Implement cost optimizations (1 hour)
   - Disable unused MCP servers
   - Practice grep-first workflow
   - Start fresh sessions more frequently
2. 📝 Document any deployment issues found
3. 🔍 Monitor costs for a day

### Day 3:
1. 📊 Review cost improvements
2. 📦 Consider modularizing App.jsx IF adding features
3. 🆕 Start on new features (if needed)

---

## ⚡ Quick Wins (Do These NOW):

1. **Type `/compact`** in this chat → Reduces context, saves money
2. **Fresh clone test** → 30 mins, validates minimal package
3. **Deploy to Render** → Backend live in 15 mins
4. **Set Vercel Root Directory** → Frontend live in 10 mins

---

## 🎯 Success Criteria

**This week:**
- ✅ Minimal package works in fresh clone
- ✅ Deployed and accessible via public URL
- ✅ All 4 button modes working in production
- ✅ Token costs down to <$30/day

**Next week:**
- ✅ Cost monitoring shows sustained reduction
- ✅ Any deployment issues resolved
- ✅ Ready to add new features

---

## 💡 Key Insight

**You asked**: "If we actually check minimal works in a fresh pull then we won't really need the clean-up right? Just build off of that?"

**Answer**: **YES! Exactly right.**

If `minimal/` works in a fresh clone:
- ✅ **Work exclusively from `minimal/` directory**
- ✅ **Ignore all the old duplicate code** (frontend-dev/, frontend-main/, etc.)
- ✅ **No need to delete anything** - just don't touch it
- ✅ **All future work** happens in `minimal/`
- ✅ **Updated CLAUDE.md** already tells me not to read those old directories

**Cleanup is optional** - only do it if the clutter bothers you. Otherwise, just pretend those old directories don't exist.

---

## 📁 Current Working Directory

**Use this**: `minimal/`
```
minimal/
├── frontend/              # Your React frontend
├── backend/               # Your FastAPI backend
├── README.md              # Deployment instructions
└── .gitignore             # Keeps it clean
```

**Ignore these**: Everything else in root (old experiments, duplicates, session logs)

---

## 🔄 Workflow Going Forward

1. **Always work in `minimal/`**
2. **Always ask for `grep` before reading large files**
3. **Start new Claude Code sessions for new features**
4. **Use `/compact` when context feels heavy**
5. **Deploy changes to `minimal` branch**

---

**This is production-ready!** Focus on fresh clone test → deployment → cost optimization.
