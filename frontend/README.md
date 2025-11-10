# RodeoAI Frontend

**Custom UI for RodeoAI with DataSpur branding**

This is your completely custom frontend with:
- ✅ DataSpur Predictions button
- ✅ Live Results button
- ✅ DataSpur Analytics view
- ✅ Custom dark theme design
- ✅ Chat interface
- ✅ Product recognition (image upload)

---

## Architecture

```
Frontend (Cloudflare Pages - FREE)
     ↓
     ↓  API Calls
     ↓
Backend (Railway/Digital Ocean)
├── FastAPI
├── PostgreSQL
├── ChromaDB (RAG)
└── Image Processing
```

**KEY POINT:** Railway is ONLY for your backend API. Your custom UI is deployed separately to Cloudflare Pages (which is FREE and fast).

---

## Local Development

### 1. Start the Backend

```bash
cd Desktop/rodeoai-backend

# Set environment variables
export OPENAI_API_KEY="your_key_here"
export STRIPE_SECRET_KEY="your_key_here"

# Start backend
python main.py
# Backend runs on http://localhost:8001
```

### 2. Open the Frontend

```bash
cd frontend

# Option A: Use Python's built-in server
python3 -m http.server 8000

# Option B: Use npx serve
npx serve .

# Open http://localhost:8000 in your browser
```

### 3. Test the Connection

- Open browser console (F12)
- You should see:
  ```
  🚀 RodeoAI Frontend initialized
  📡 API Base URL: http://localhost:8001
  ✅ Backend connected: {status: "healthy", openai_configured: true}
  ```

- Try sending a chat message
- Try uploading an image (product recognition)

---

## Deploy to Cloudflare Pages (FREE)

### Option 1: Via Cloudflare Dashboard (Easiest)

1. **Push Frontend to GitHub**

```bash
cd frontend
git init
git add .
git commit -m "Initial frontend"
git remote add origin https://github.com/YOUR_USERNAME/rodeoai-frontend.git
git push -u origin main
```

2. **Create Cloudflare Pages Project**

- Go to https://dash.cloudflare.com
- Click "Workers & Pages" → "Create Application" → "Pages"
- Click "Connect to Git"
- Select your `rodeoai-frontend` repository
- **Build settings:**
  - Build command: *(leave empty)*
  - Build output directory: `/`
  - Root directory: `frontend`
- Click "Save and Deploy"

3. **Your site is LIVE!**
   - URL: `https://rodeoai-frontend.pages.dev`
   - Custom domain: Add your own domain in Pages settings

### Option 2: Via Wrangler CLI

```bash
# Install Wrangler
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Deploy
cd frontend
wrangler pages deploy . --project-name=rodeoai-frontend

# Your site: https://rodeoai-frontend.pages.dev
```

---

## Deploy Backend

### Option A: Railway (Easiest)

1. **Push Backend to GitHub**

```bash
cd Desktop/rodeoai-backend
git init
git add .
git commit -m "Initial backend"
git remote add origin https://github.com/YOUR_USERNAME/rodeoai-backend.git
git push -u origin main
```

2. **Deploy to Railway**

- Go to https://railway.app
- Click "New Project" → "Deploy from GitHub repo"
- Select `rodeoai-backend`
- Railway auto-detects Python and deploys
- Add environment variables:
  - `OPENAI_API_KEY`
  - `STRIPE_SECRET_KEY`
  - `STRIPE_WEBHOOK_SECRET`
  - `DATABASE_URL` (Railway provides PostgreSQL)

3. **Get Backend URL**
   - Railway gives you: `https://your-app.railway.app`

### Option B: Digital Ocean

1. **Create Droplet**
   - Ubuntu 22.04
   - $6/month plan is fine for start

2. **SSH and Setup**

```bash
ssh root@your-droplet-ip

# Install dependencies
apt update && apt upgrade -y
apt install python3-pip postgresql redis-server nginx -y

# Clone repo
git clone https://github.com/YOUR_USERNAME/rodeoai-backend
cd rodeoai-backend

# Install Python packages
pip3 install -r requirements.txt

# Setup PostgreSQL
sudo -u postgres createdb rodeoai
sudo -u postgres createuser rodeoai

# Create systemd service
nano /etc/systemd/system/rodeoai.service
```

**Service file:**

```ini
[Unit]
Description=RodeoAI FastAPI Backend
After=network.target

[Service]
User=root
WorkingDirectory=/root/rodeoai-backend
Environment="OPENAI_API_KEY=your_key"
Environment="STRIPE_SECRET_KEY=your_key"
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
systemctl daemon-reload
systemctl enable rodeoai
systemctl start rodeoai

# Setup Nginx
nano /etc/nginx/sites-available/rodeoai
```

**Nginx config:**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/rodeoai /etc/nginx/sites-enabled/
systemctl restart nginx

# Install SSL (free)
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your-domain.com
```

---

## Connect Frontend to Backend

After deploying backend, update the frontend config:

**Edit `frontend/assets/js/config.js`:**

```javascript
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8001'  // Local development
    : 'https://your-backend.railway.app';  // ← CHANGE THIS to your deployed backend URL
```

**Then redeploy frontend:**

```bash
cd frontend
git add assets/js/config.js
git commit -m "Update API endpoint"
git push

# Cloudflare Pages auto-deploys on git push!
```

---

## File Structure

```
frontend/
├── index.html              # Main HTML with your exact UI
├── assets/
│   ├── css/
│   │   └── styles.css      # Your exact dark theme design
│   ├── js/
│   │   ├── config.js       # API configuration
│   │   └── app.js          # App logic (connects to FastAPI)
│   └── images/
│       └── dataspur-logo.png  # Your logo (add this)
├── wrangler.toml           # Cloudflare Pages config
└── README.md               # This file
```

---

## Features

### ✅ Currently Working

1. **Chat Interface**
   - Real-time streaming from FastAPI backend
   - Conversation history
   - RAG-powered responses

2. **Product Recognition**
   - Upload images via attach button
   - AI identifies category, brand, model
   - Shows pricing (Phase 1 placeholder data)

3. **DataSpur Predictions**
   - Custom view (ready for data integration)

4. **Live Results**
   - Custom view (ready for data integration)

5. **DataSpur Analytics**
   - Custom charts with Chart.js
   - Stats dashboard

### ⏳ Coming Soon

- OAuth login (Google, Apple, Facebook)
- Real prediction data integration
- Real live results data integration
- Payment integration (Stripe)
- Phase 2: Real AI models for product recognition

---

## Customization

### Change Logo

Replace `assets/images/dataspur-logo.png` with your logo.

### Change Colors

Edit `assets/css/styles.css`:

```css
:root {
    --accent: #d4af37;  /* Gold - change this */
    --bg: #212121;      /* Dark background */
    --surface: #2f2f2f; /* Cards */
}
```

### Add New Views

1. Add nav item in `index.html`:

```html
<div class="nav-item" data-view="my-new-view">
    <span>My New Feature</span>
</div>
```

2. Add panel view:

```html
<div class="panel-view" id="myNewView">
    <div class="panel-header">
        <h1 class="panel-title">My New Feature</h1>
        <p class="panel-subtitle">Description</p>
    </div>
    <!-- Your content -->
</div>
```

3. Add to `assets/js/app.js`:

```javascript
const titles = {
    'chat': 'Chat',
    'predictions': 'DataSpur Predictions',
    'live-results': 'Live Results',
    'analytics': 'DataSpur Analytics',
    'my-new-view': 'My New Feature'  // Add this
};
```

---

## Troubleshooting

### Frontend can't connect to backend

**Error in console:** `⚠️ Backend not reachable`

**Fix:**
1. Make sure backend is running (`python main.py` locally)
2. Check `config.js` has correct API_BASE_URL
3. Check CORS in backend `main.py` (already configured to allow all origins)

### Chat not streaming

**Fix:** FastAPI backend must support streaming. Check that `main.py` returns `StreamingResponse`.

### Image upload fails

**Error:** `Image recognition failed`

**Fix:**
1. Backend must have image processing dependencies installed
2. Check `pip install pillow opencv-python imagehash`
3. Verify `product_recognition_service.py` exists

### Cloudflare Pages build fails

**Fix:** No build needed! Just deploy static files:
- Build command: *(leave empty)*
- Output directory: `/`

---

## Cost Breakdown

```
Frontend (Cloudflare Pages):  FREE
├── Unlimited bandwidth
├── Free SSL
├── CDN included
└── Custom domain support

Backend (Railway):           $5-30/month
├── Free tier: 500 hours/month
├── Paid: $5/month + usage
└── PostgreSQL included

Backend (Digital Ocean):     $6-48/month
├── Basic Droplet: $6/month
├── CPU Optimized: $48/month
└── Add PostgreSQL: +$15/month
```

---

## Next Steps

1. ✅ Frontend deployed to Cloudflare Pages
2. ✅ Backend deployed to Railway or Digital Ocean
3. ✅ Update `config.js` with backend URL
4. ⏳ Add your logo to `assets/images/`
5. ⏳ Set up custom domain
6. ⏳ Enable OAuth
7. ⏳ Integrate real prediction/results data

---

## Support

Questions? Check:
- Backend docs: `../Desktop/rodeoai-backend/README.md`
- System status: `../CURRENT_SYSTEM_STATUS.md`
- Deployment options: `../DEPLOYMENT_OPTIONS.md`

Your UI is **exactly as designed** - Railway doesn't change it at all!
