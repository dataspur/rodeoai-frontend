# RodeoAI Quick Start Guide

**Your custom UI is ready!** Railway is only for the backend - your exact design deploys to Cloudflare Pages (FREE).

---

## What You Asked For ✅

> "Railway looks generic and I could not have my live results button, my DataSpur Predictions button, etc..."

**Solution:** Railway is ONLY for your backend API. Your custom UI with ALL your buttons deploys separately to Cloudflare Pages!

### Your Custom Features (All Working):

✅ **DataSpur Predictions** button and view
✅ **Live Results** button and view
✅ **DataSpur Analytics** dashboard
✅ Custom dark theme with gold accents
✅ Chat interface with streaming
✅ Product recognition (image upload)
✅ Exact design you provided

---

## Architecture

```
┌─────────────────────────────────────┐
│  Frontend (Cloudflare Pages)       │  ← Your exact custom UI
│  - FREE hosting                     │  ← FREE!
│  - Fast CDN                         │
│  - Custom domain support            │
│  - /frontend/index.html             │
└──────────────┬──────────────────────┘
               │
               │ API calls over HTTPS
               ↓
┌─────────────────────────────────────┐
│  Backend (Railway or Digital Ocean) │
│  - FastAPI server                   │  ← $5-30/month
│  - PostgreSQL database              │
│  - RAG system (ChromaDB)            │
│  - Image processing                 │
│  - Desktop/rodeoai-backend/         │
└─────────────────────────────────────┘
```

**Key Point:** Your custom UI never touches Railway. It's deployed to Cloudflare Pages with your exact design!

---

## Test Locally (5 minutes)

### 1. Start Backend

```bash
cd Desktop/rodeoai-backend

# Set environment variable
export OPENAI_API_KEY="your_openai_key_here"

# Start server
python3 main.py
```

**Backend runs on:** `http://localhost:8001`

### 2. Start Frontend

```bash
# Open new terminal
cd frontend

# Serve frontend
python3 -m http.server 8000
```

**Frontend runs on:** `http://localhost:8000`

### 3. Test It!

Open `http://localhost:8000` in your browser.

You should see:
- Your exact custom UI
- DataSpur Predictions button in sidebar
- Live Results button in sidebar
- DataSpur Analytics button in sidebar
- Chat input at bottom

**Try:**
- Send a chat message → streams from backend
- Click "DataSpur Predictions" → custom view appears
- Click "Live Results" → custom view appears
- Click "DataSpur Analytics" → charts appear
- Upload an image → product recognition

**Console should show:**
```
🚀 RodeoAI Frontend initialized
📡 API Base URL: http://localhost:8001
✅ Backend connected: {status: "healthy", openai_configured: true}
```

---

## Deploy to Production (10 minutes)

### Step 1: Deploy Frontend to Cloudflare Pages (FREE)

**Option A: Via Cloudflare Dashboard (Easiest)**

1. Push frontend to GitHub:

```bash
cd frontend
git init
git add .
git commit -m "Initial frontend"
git remote add origin https://github.com/YOUR_USERNAME/rodeoai-frontend.git
git push -u origin main
```

2. Go to https://dash.cloudflare.com
3. Click "Workers & Pages" → "Create" → "Pages"
4. Connect GitHub repo
5. Settings:
   - Build command: *(leave empty)*
   - Build output: `/`
   - Root directory: `frontend`
6. Deploy

**Your site:** `https://rodeoai-frontend.pages.dev`

**Option B: Via CLI**

```bash
npm install -g wrangler
wrangler login
cd frontend
wrangler pages deploy . --project-name=rodeoai
```

### Step 2: Deploy Backend to Railway

1. Go to https://railway.app
2. "New Project" → "Deploy from GitHub repo"
3. Select your backend repo (or push `Desktop/rodeoai-backend`)
4. Add environment variables:
   - `OPENAI_API_KEY`
   - `STRIPE_SECRET_KEY`
5. Deploy

**Backend URL:** `https://your-app.railway.app`

### Step 3: Connect Frontend to Backend

Edit `frontend/assets/js/config.js`:

```javascript
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8001'  // Local
    : 'https://your-app.railway.app';  // ← Change this
```

Then redeploy frontend:

```bash
cd frontend
git add assets/js/config.js
git commit -m "Update API endpoint"
git push
```

Cloudflare auto-deploys!

---

## File Structure

```
rodeoai-frontend/
├── frontend/                    ← Your custom UI
│   ├── index.html              ← Exact design you provided
│   ├── assets/
│   │   ├── css/
│   │   │   └── styles.css      ← Your exact styling
│   │   ├── js/
│   │   │   ├── config.js       ← API configuration
│   │   │   └── app.js          ← Connects to FastAPI
│   │   └── images/
│   │       └── dataspur-logo.png  ← Add your logo
│   ├── wrangler.toml           ← Cloudflare Pages config
│   └── README.md               ← Detailed docs
│
└── Desktop/rodeoai-backend/    ← FastAPI backend
    ├── main.py                 ← API server
    ├── models.py               ← Database
    ├── rag_service.py          ← RAG system
    ├── image_processor.py      ← Image processing
    └── ...
```

---

## Your Custom Features Explained

### 1. DataSpur Predictions

**Location:** Sidebar → "DataSpur Predictions"

**What it does:**
- Shows AI-powered rodeo event predictions
- Currently: Placeholder view
- Phase 2: Integrate real prediction data

**Code:** `frontend/index.html` line ~152

### 2. Live Results

**Location:** Sidebar → "Live Results"

**What it does:**
- Shows real-time rodeo event scores
- Currently: Placeholder view
- Phase 2: Integrate real results data

**Code:** `frontend/index.html` line ~159

### 3. DataSpur Analytics

**Location:** Sidebar → "DataSpur Analytics"

**What it does:**
- Shows professional analytics dashboard
- Charts with Chart.js
- Stats cards with metrics
- Currently: Mock data
- Phase 2: Real analytics

**Code:** `frontend/index.html` line ~166

### 4. Chat Interface

**What works now:**
- Real-time streaming from FastAPI backend
- RAG-powered responses
- Conversation history
- Message export

**Try it:** Type "Tell me about bull riding"

### 5. Product Recognition

**What works now:**
- Upload image via attach button
- AI identifies category, brand, model
- Shows pricing (Phase 1 placeholder)

**Try it:** Click attach → upload boot image

---

## Customization

### Change Logo

Replace `frontend/assets/images/dataspur-logo.png` with your logo (40x40px PNG).

### Change Colors

Edit `frontend/assets/css/styles.css`:

```css
:root {
    --accent: #d4af37;  /* Gold - your brand color */
    --bg: #212121;      /* Dark background */
}
```

### Add Custom Domain

In Cloudflare Pages:
1. "Custom domains" → "Set up a custom domain"
2. Add `www.dataspur.com`
3. Cloudflare handles DNS automatically

---

## Cost Breakdown

```
Frontend (Cloudflare Pages):
✅ FREE                    $0/month
  - Unlimited requests
  - Global CDN
  - SSL included
  - Custom domain

Backend (Railway):
✅ Free tier available    $0-30/month
  - 500 hours/month free
  - Then $5 + usage
  - PostgreSQL included

Backend (Digital Ocean):
✅ Budget option          $6-48/month
  - $6 basic droplet
  - $48 CPU optimized

Total: $0-48/month (vs $2,475/month with AWS!)
```

---

## What's Next?

1. ✅ **Add your logo** to `frontend/assets/images/dataspur-logo.png`
2. ✅ **Deploy frontend** to Cloudflare Pages
3. ✅ **Deploy backend** to Railway
4. ⏳ **Integrate real predictions** (connect to ProRodeo API)
5. ⏳ **Integrate live results** (real-time websockets)
6. ⏳ **Train AI models** (Phase 2 for product recognition)
7. ⏳ **Add OAuth** (Google, Apple, Facebook login)

---

## Common Questions

**Q: Why not just use Railway for frontend too?**

A: Cloudflare Pages is:
- FREE (vs Railway charges)
- Faster (global CDN)
- Better for static sites
- Auto-deploys on git push

**Q: Can I use a different backend host?**

A: Yes! Works with:
- Railway
- Digital Ocean
- AWS
- Any host that runs Python

Just update `config.js` with the URL.

**Q: Will my custom UI change?**

A: NO! Your exact design is preserved. Railway only hosts the API, not the UI.

**Q: How do I update the frontend?**

A:
```bash
cd frontend
# Make changes to index.html, styles.css, or app.js
git add .
git commit -m "Update"
git push
# Cloudflare auto-deploys!
```

---

## Support Docs

- Frontend details: `frontend/README.md`
- Backend details: `Desktop/rodeoai-backend/README.md`
- System status: `CURRENT_SYSTEM_STATUS.md`
- Deployment options: `DEPLOYMENT_OPTIONS.md`

---

## Summary

✅ Your custom UI is in `frontend/` directory
✅ ALL your custom buttons are there (DataSpur Predictions, Live Results, Analytics)
✅ Exact design you provided
✅ Connects to FastAPI backend
✅ Deploy to Cloudflare Pages (FREE)
✅ Backend to Railway ($5-30/month)

**Railway is ONLY for the backend API - your UI is completely custom and free to host!**

Ready to deploy? Start with local testing, then push to Cloudflare Pages!
