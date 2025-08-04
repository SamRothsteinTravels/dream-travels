# Dream Travels Deployment Guide

## Backend Deployment (Railway)

### Step 1: Connect to Railway
1. Go to [railway.app](https://railway.app)
2. Click "Login with GitHub"
3. Authorize Railway to access your repositories

### Step 2: Deploy Backend
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your Dream Travels repository
4. Select the `/backend` folder as root
5. Railway will auto-detect Python and deploy using the Dockerfile

### Step 3: Set Environment Variables
In Railway dashboard:
- `MONGO_URL`: mongodb+srv://65willswat:rodxa4-hebdoc-qiwFyz@cluster0.yin7cfx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
- `DB_NAME`: dream_travels_db
- `PORT`: 8001

### Step 4: Get Backend URL
After deployment, Railway will provide a URL like:
`https://your-project-name.railway.app`

## Frontend Deployment (Vercel)

### Step 1: Connect to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click "Continue with GitHub"
3. Authorize Vercel

### Step 2: Deploy Frontend
1. Click "New Project"
2. Import your GitHub repository
3. Select `/frontend` as root directory
4. Framework Preset: "Create React App"
5. Build Command: `yarn build`
6. Output Directory: `build`

### Step 3: Set Environment Variable
In Vercel dashboard:
- `REACT_APP_BACKEND_URL`: Your Railway backend URL (from Step 4 above)

## Testing Your Deployed App

1. Frontend URL: Provided by Vercel
2. Backend URL: Provided by Railway
3. Database: MongoDB Atlas (already set up)

Your Dream Travels app will be live with:
- ✅ 178 theme parks (Queue Times + WaitTimesApp)
- ✅ Travel blog scraping
- ✅ Real-time wait times
- ✅ Custom domain support
- ✅ Global CDN

## Costs
- MongoDB Atlas: Free (512MB)
- Railway: ~$0-5/month (free credits)
- Vercel: Free (unlimited personal projects)

Total: Essentially FREE for testing!