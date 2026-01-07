# Frontend for Job Application Bot

## Local Development

1. Make sure backend is running on `http://localhost:8000`
2. Open `index.html` in browser or use a local server:
   ```bash
   python -m http.server 8080
   ```
3. Open `http://localhost:8080`

## Deployment to Vercel

### Option 1: Deploy via Vercel Dashboard

1. Go to https://vercel.com
2. Import your GitHub repository
3. **Important**: Set **Root Directory** to `frontend`
4. Framework Preset: **Other**
5. Build Command: (leave empty - it's static)
6. Output Directory: `.`
7. Add Environment Variable:
   - Key: `VITE_API_URL` or `REACT_APP_API_URL`
   - Value: Your backend URL (e.g., `https://your-backend.railway.app`)

### Option 2: Deploy via CLI

```bash
cd frontend
vercel

# Follow prompts
# Set root directory to: ./
# Add environment variable when prompted
```

### Environment Variables

Set these in Vercel Dashboard → Settings → Environment Variables:

```
VITE_API_URL=https://your-backend-url.railway.app
```

Or if using a different naming convention:

```
REACT_APP_API_URL=https://your-backend-url.railway.app
```

Then update `app.js` to use the correct variable name.

## Manual API URL Configuration

If environment variables don't work, you can manually set the API URL in `app.js`:

```javascript
const API_BASE_URL = 'https://your-actual-backend-url.railway.app';
```

## Custom Domain

1. Go to Vercel Dashboard → Your Project → Settings → Domains
2. Add your custom domain
3. Vercel will provide DNS instructions
4. SSL certificate is automatic!






