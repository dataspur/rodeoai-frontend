# Railway Deployment Guide for RodeoAI Backend

## Prerequisites

1. Railway account (https://railway.app)
2. GitHub account
3. Supabase project set up
4. OpenAI API key

## Step 1: Create GitHub Repository

### Option A: Using GitHub CLI
```bash
cd Desktop/rodeoai-backend
git init
git add .
git commit -m "Initial commit: RodeoAI backend with TAURUS routing"
gh repo create rodeoai-backend --private --source=. --remote=origin --push
```

### Option B: Using GitHub Web UI
1. Go to https://github.com/new
2. Repository name: `rodeoai-backend`
3. Visibility: Private
4. Do NOT initialize with README (we already have files)
5. Click "Create repository"
6. Run these commands in the backend directory:
```bash
cd Desktop/rodeoai-backend
git init
git add .
git commit -m "Initial commit: RodeoAI backend with TAURUS routing"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/rodeoai-backend.git
git push -u origin main
```

## Step 2: Connect Railway to GitHub

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. If first time: Click "Configure GitHub App" and authorize Railway
4. Select your `rodeoai-backend` repository
5. Railway will detect it as a Python project

## Step 3: Configure Environment Variables

In Railway dashboard, go to your project > Variables tab and add:

### Required Variables

```
OPENAI_API_KEY=sk-...your-key-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_JWT_SECRET=your-supabase-jwt-secret
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=generate-a-random-32-character-string
```

### Get Supabase Credentials

1. Go to your Supabase project dashboard
2. Click on "Project Settings" (gear icon)
3. Go to "API" section:
   - `SUPABASE_URL` = Project URL
   - `SUPABASE_KEY` = Project API keys > anon/public
4. Go to "Database" section:
   - Copy the connection string for `DATABASE_URL`
   - Format: `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres`

### Generate SECRET_KEY

Run this in Python:
```python
import secrets
print(secrets.token_urlsafe(32))
```

## Step 4: Add PostgreSQL Database (Optional - if not using Supabase DB)

1. In Railway dashboard, click "+ New"
2. Select "Database" > "PostgreSQL"
3. Railway will auto-create `DATABASE_URL` variable
4. Reference it in your app: `${{Postgres.DATABASE_URL}}`

**Note:** If using Supabase PostgreSQL, skip this step and use Supabase's DATABASE_URL instead.

## Step 5: Deploy

Railway will automatically deploy when you:
- Push to the main branch
- The deployment will use `railway.json` configuration
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Monitor Deployment

1. Watch the "Deployments" tab in Railway
2. Check logs for errors
3. Once deployed, Railway will provide a URL: `https://your-app.up.railway.app`

## Step 6: Test Deployment

```bash
# Test health endpoint
curl https://your-app.up.railway.app/

# Expected response:
{"status":"ok","message":"RodeoAI API is running"}

# Test chat endpoint
curl -X POST https://your-app.up.railway.app/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What is team roping?", "model": "taurus"}'
```

## Step 7: Update Frontend Environment

In your frontend `.env.local` or Cloudflare Pages environment variables:
```
NEXT_PUBLIC_API_URL=https://your-app.up.railway.app
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

## Automatic Deployments

Railway is now configured for automatic deployments:
- Every push to `main` branch triggers a new deployment
- Railway builds using `railway.json` configuration
- Environment variables persist across deployments
- Zero-downtime deployments

## Troubleshooting

### Build Fails

Check Railway logs:
1. Click on deployment
2. View "Build Logs"
3. Common issues:
   - Missing dependencies in `requirements.txt`
   - Python version mismatch (Railway uses Python 3.11 by default)
   - Missing environment variables

### Runtime Errors

Check Railway logs:
1. Click on deployment
2. View "Deploy Logs"
3. Common issues:
   - Database connection failures (check `DATABASE_URL`)
   - Missing environment variables
   - Port binding (Railway sets `$PORT` automatically)

### Database Connection Issues

Ensure `DATABASE_URL` format is correct:
```
postgresql://user:password@host:port/database
```

For Supabase:
```
postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
```

## Useful Railway Commands

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# View logs
railway logs

# Open dashboard
railway open

# Run commands in Railway environment
railway run python manage.py migrate
```

## Cost Optimization

Railway pricing:
- Starter plan: $5/month (500 hours of usage)
- Hobby plan: Usage-based ($0.000231/GB-hour RAM)

Tips:
- Use Supabase free tier for database (save $15/month)
- Scale down when not in use
- Monitor usage in Railway dashboard

## Next Steps

1. Set up custom domain (optional)
2. Configure CORS for production
3. Set up monitoring/alerts
4. Enable Railway metrics
5. Configure backup strategy

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Supabase Docs: https://supabase.com/docs
