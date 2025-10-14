# 🚀 Deployment Guide - 3-Component Architecture

This guide covers local testing and production deployment of all three components:
1. **FastAPI Backend** (Render)
2. **Streamlit Dev Mode** (Streamlit Cloud)
3. **React Frontend** (Vercel)

---

## 🏗️ Architecture Overview

```
┌────────────────────────────────────┐
│  FastAPI Backend (Render)          │
│  https://aqumen-api.onrender.com   │
│  ├── GET  /health                  │
│  ├── GET  /api/models               │
│  ├── GET  /api/generate-stream (SSE)│
│  └── POST /api/generate (blocking) │
└────────────────────────────────────┘
         ↓                    ↓
┌─────────────────┐  ┌──────────────────────┐
│ Streamlit Cloud │  │  Vercel              │
│ dev.aqumen.ai   │  │  demo.aqumen.ai      │
│ (Dev/Debug UI)  │  │  (Student Game)      │
│ - SSE stream    │  │  - API calls         │
│ - Full prompts  │  │  - Hardcoded toggle  │
│ - LLM responses │  │  - Clean UX          │
└─────────────────┘  └──────────────────────┘
```

---

## 🧪 Local Testing

### 1. Test FastAPI Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"

# Run server
uvicorn api_server:app --reload --port 8000

# Test in another terminal
curl http://localhost:8000/health

# Test SSE streaming (should see events in real-time)
curl -N http://localhost:8000/api/generate-stream?topic=GRPO%20in%20Multi-Task%20RL
```

**Expected output:**
```
event: start
data: {"event":"start","topic":"GRPO in Multi-Task RL","timestamp":"..."}

event: step
data: {"type":"step","step_number":1,"description":"Generate difficulty categories",...}

event: step
data: {"type":"step","step_number":2,...}
...
```

### 2. Test Streamlit Dev Mode

```bash
cd frontend-dev

# Install dependencies
pip install -r requirements.txt

# Run Streamlit
streamlit run streamlit_app.py

# Opens browser at http://localhost:8501
```

**In the UI:**
1. Make sure API endpoint is `http://localhost:8000`
2. Enter a topic
3. Click "Generate Question"
4. Watch steps complete in real-time!

### 3. Test Pipeline Streaming Directly

```bash
cd backend

# Test the streaming generator
python -c "
from corrected_7step_pipeline import AdversarialPipeline

p = AdversarialPipeline()
for item in p.run_full_pipeline_streaming('GRPO in Multi-Task RL', max_attempts=3):
    if isinstance(item, dict):
        print(f'FINAL: {item}')
    else:
        print(f'Step {item.step_number}: {item.description} - Success: {item.success}')
"
```

---

## 🌐 Production Deployment

### 1. Deploy FastAPI to Render

#### Option A: Via Dashboard (Easiest)

1. **Sign up at [render.com](https://render.com)**

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repo

3. **Configure Service**
   ```
   Name: aqumen-api
   Region: Oregon (US West)
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn api_server:app --host 0.0.0.0 --port $PORT
   ```

4. **Add Environment Variables**
   - `AWS_ACCESS_KEY_ID`: Your AWS key
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret
   - `AWS_DEFAULT_REGION`: `us-east-1`
   - `PYTHON_VERSION`: `3.11.0`

5. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for build
   - Your API will be at: `https://aqumen-api.onrender.com`

6. **Test Deployment**
   ```bash
   curl https://aqumen-api.onrender.com/health
   ```

#### Option B: Via render.yaml (Infrastructure as Code)

Create `render.yaml` in repo root:

```yaml
services:
  - type: web
    name: aqumen-api
    runtime: python
    region: oregon
    plan: starter  # $7/month, or 'free' for testing
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn api_server:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: AWS_ACCESS_KEY_ID
        sync: false  # Set in dashboard
      - key: AWS_SECRET_ACCESS_KEY
        sync: false
      - key: AWS_DEFAULT_REGION
        value: us-east-1
      - key: PYTHON_VERSION
        value: 3.11.0
```

Then connect repo in Render dashboard.

#### Render Free Tier Caveats

- **Spins down after 15 min of inactivity**
- **50-60 second cold start** on first request
- For production, use $7/month Starter plan (no spin-down)

### 2. Deploy Streamlit to Streamlit Cloud

1. **Sign up at [streamlit.io/cloud](https://streamlit.io/cloud)**

2. **Deploy App**
   - Click "New app"
   - Connect GitHub repo
   - Configure:
     ```
     Repository: your-repo
     Branch: main
     Main file path: frontend-dev/streamlit_app.py
     ```

3. **Custom Domain (Optional)**
   - In Streamlit Cloud dashboard, go to Settings → Custom Domain
   - Add `dev.aqumen.ai`
   - In your DNS provider (e.g., Vercel DNS, Cloudflare):
     ```
     CNAME  dev  →  your-app.streamlit.app
     ```

4. **Update API Endpoint**
   - In Streamlit app sidebar, change default API endpoint to:
     `https://aqumen-api.onrender.com`
   - Or better: Add Streamlit Secrets in dashboard:
     ```toml
     [api]
     endpoint = "https://aqumen-api.onrender.com"
     ```
   - Update code to read: `st.secrets["api"]["endpoint"]`

### 3. Update React Frontend on Vercel

Already deployed at `demo.aqumen.ai`! Just need to add API integration.

#### Update React Code

In `aqumen-demo-frontend/src/App.jsx`, add:

```javascript
// Add to state
const [apiMode, setApiMode] = useState(false);
const [apiEndpoint] = useState('https://aqumen-api.onrender.com');
const [isGenerating, setIsGenerating] = useState(false);

// Add API generation function
const generateFromAPI = async (topic) => {
  setIsGenerating(true);
  try {
    const response = await fetch(`${apiEndpoint}/api/generate`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({topic})
    });

    if (!response.ok) {
      throw new Error('Generation failed');
    }

    const data = await response.json();
    const newQuestion = parseQuestion(data.question);

    // Add to questions array
    setParsedQuestions([...parsedQuestions, newQuestion]);
    setCurrentQuestion(parsedQuestions.length);

  } catch (error) {
    console.error('API generation error:', error);
    alert('Failed to generate question. Using hardcoded examples.');
  } finally {
    setIsGenerating(false);
  }
};

// Add toggle UI in your app
<div>
  <label>
    <input
      type="checkbox"
      checked={apiMode}
      onChange={(e) => setApiMode(e.target.checked)}
    />
    Use API-generated questions
  </label>

  {apiMode && (
    <div>
      <input
        type="text"
        placeholder="Enter topic"
        onKeyPress={(e) => {
          if (e.key === 'Enter') {
            generateFromAPI(e.target.value);
          }
        }}
      />
      {isGenerating && <div>Generating... (30-60s)</div>}
    </div>
  )}
</div>
```

#### Deploy to Vercel

```bash
cd aqumen-demo-frontend
git add .
git commit -m "Add API integration with toggle"
git push origin main
```

Vercel auto-deploys on push!

---

## 🔧 Environment Variables Summary

### Backend (Render)
```
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_DEFAULT_REGION=us-east-1
PYTHON_VERSION=3.11.0
```

### Streamlit (Streamlit Cloud)
```toml
# .streamlit/secrets.toml (add via dashboard)
[api]
endpoint = "https://aqumen-api.onrender.com"
```

### React (Vercel)
No env vars needed - API endpoint can be hardcoded or use Vercel env vars:
```
REACT_APP_API_ENDPOINT=https://aqumen-api.onrender.com
```

---

## 📊 Monitoring & Debugging

### Check Backend Health

```bash
# Health check
curl https://aqumen-api.onrender.com/health

# Model info
curl https://aqumen-api.onrender.com/api/models

# Test generation (blocking)
curl -X POST https://aqumen-api.onrender.com/api/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "GRPO in Multi-Task RL"}'
```

### Check Streamlit

Visit: `https://dev.aqumen.ai` or `https://your-app.streamlit.app`

### Check React

Visit: `https://demo.aqumen.ai`

---

## 🐛 Troubleshooting

### Backend Issues

**Problem: Timeout on Render**
- Solution: Upgrade from free to Starter plan ($7/month)
- Free tier spins down, causing 60s cold starts

**Problem: AWS Credentials Error**
- Check environment variables in Render dashboard
- Verify AWS keys have Bedrock permissions
- Test locally first with same keys

**Problem: CORS Error**
- Check `allow_origins` in `api_server.py`
- Make sure your frontend domain is listed

### Streamlit Issues

**Problem: Can't connect to API**
- Check API endpoint URL in sidebar
- Try with `http://localhost:8000` for local testing
- Verify backend is running

**Problem: SSE events not showing**
- Check browser console for errors
- Verify `sseclient-py` is installed
- Try simple curl test first

### React Issues

**Problem: API calls failing**
- Check CORS configuration in backend
- Verify API endpoint URL
- Check browser console for errors

---

## 💰 Cost Estimate

### Infrastructure
- **Render Starter**: $7/month (no spin-down, 512MB RAM)
- **Streamlit Cloud**: Free (or $20/month for custom domain)
- **Vercel**: Free for hobby projects

### AWS Bedrock (pay-per-use)
- **Sonnet 4.5**: ~$0.003 per 1K input tokens, ~$0.015 per 1K output tokens
- **Sonnet 4**: ~$0.003 per 1K input tokens, ~$0.015 per 1K output tokens
- **Haiku 3**: ~$0.00025 per 1K input tokens, ~$0.00125 per 1K output tokens

**Per question generation (7 steps):**
- Input tokens: ~10K tokens = $0.03
- Output tokens: ~5K tokens = $0.075
- **Total: ~$0.10 per question**

**Monthly estimate (100 questions):**
- Infrastructure: $7
- AWS: $10
- **Total: ~$17/month**

---

## 🎯 Next Steps

1. ✅ Test everything locally
2. ✅ Deploy backend to Render
3. ✅ Deploy Streamlit to Streamlit Cloud
4. ✅ Update React to call API
5. ✅ Test end-to-end
6. 📊 Monitor costs and performance
7. 🔄 Iterate on prompts using dev mode

---

## 📚 Additional Resources

- [Render Docs](https://render.com/docs)
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Vercel Docs](https://vercel.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SSE Guide](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

---

**Questions?** Check logs in each platform's dashboard or test locally first!
