# Render Deployment Guide

## Prerequisites
1. GitHub account
2. Render account (free at render.com)

## Deployment Steps

### 1. Push to GitHub
```bash
# Initialize git repository (if not already done)
git add .
git commit -m "Add deployment configuration"
git push origin main
```

### 2. Deploy on Render
1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: smart-tourist-safety
   - **Root Directory**: `backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

### 3. Environment Variables (if needed)
No additional environment variables required for this prototype.

### 4. Access Your Deployed App
After deployment, Render will provide a URL like:
`https://smart-tourist-safety-xxxx.onrender.com`

## Deployed Endpoints
Replace `YOUR_RENDER_URL` with your actual Render URL:

- **Tourist App**: `https://YOUR_RENDER_URL/tourist`
- **Police Dashboard**: `https://YOUR_RENDER_URL/dashboard`
- **API Documentation**: `https://YOUR_RENDER_URL/docs`
- **Ledger Verification**: `https://YOUR_RENDER_URL/ledger/verify`

## Notes
- Free tier may have cold starts (first request after inactivity takes longer)
- Free tier has limited monthly hours
- WebSocket connections work on Render free tier
- HTTPS is automatically provided