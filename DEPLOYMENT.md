# Railway Deployment Guide

## Deploying to Railway

### Method 1: Railway CLI (Recommended)

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize Railway project**:
   ```bash
   railway init
   ```

4. **Set environment variables**:
   ```bash
   railway variables set OPENAI_API_KEY=your_openai_api_key_here
   railway variables set SMTP_SERVER=smtp.gmail.com
   railway variables set SMTP_PORT=587
   railway variables set SMTP_USERNAME=your_email@gmail.com
   railway variables set SMTP_PASSWORD=your_app_password
   ```

5. **Deploy**:
   ```bash
   railway up
   ```

### Method 2: GitHub Integration

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Connect to Railway**:
   - Go to [Railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Set environment variables in Railway dashboard**:
   - Go to your project settings
   - Add the following variables:
     - `OPENAI_API_KEY`
     - `SMTP_SERVER`
     - `SMTP_PORT`
     - `SMTP_USERNAME`
     - `SMTP_PASSWORD`

4. **Deploy**:
   - Railway will automatically detect the Python app
   - It will install dependencies from `requirements.txt`
   - The app will start using the `Procfile`

## Environment Variables for Railway

Set these in your Railway project dashboard:

### Required
- `OPENAI_API_KEY` - Your OpenAI API key for AI analysis

### Optional (for email integration)
- `SMTP_SERVER` - SMTP server (default: smtp.gmail.com)
- `SMTP_PORT` - SMTP port (default: 587)
- `SMTP_USERNAME` - Your email username
- `SMTP_PASSWORD` - Your email app password

### Railway will automatically set:
- `PORT` - Railway sets this automatically
- `RAILWAY_ENVIRONMENT` - Set by Railway

## Troubleshooting

### Common Issues

1. **Build fails**: Check that all dependencies are in `requirements.txt`
2. **App crashes**: Check Railway logs for error messages
3. **Environment variables not working**: Ensure they're set in Railway dashboard
4. **Port issues**: Railway automatically sets the PORT environment variable

### Checking Logs

```bash
railway logs
```

### Local Testing

Test your app locally before deploying:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your_key_here
export PORT=5000

# Run the app
python app.py
```

## Railway-Specific Features

### Automatic Deployments
- Railway automatically deploys when you push to your main branch
- You can also trigger manual deployments from the dashboard

### Custom Domains
- Railway provides a default domain: `your-app-name.railway.app`
- You can add custom domains in the Railway dashboard

### Scaling
- Railway automatically scales based on traffic
- You can set resource limits in the dashboard

## Monitoring

Railway provides built-in monitoring:
- View logs in real-time
- Monitor resource usage
- Set up alerts for errors

## Cost Optimization

- Railway offers a free tier with generous limits
- Monitor your usage in the dashboard
- Upgrade to paid plans for production use

