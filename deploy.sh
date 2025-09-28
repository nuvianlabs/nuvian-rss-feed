#!/bin/bash

# RSS Feed Analyzer - Railway Deployment Script

echo "🚀 Deploying RSS Feed Analyzer to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if user is logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway:"
    railway login
fi

# Initialize Railway project if not already done
if [ ! -f ".railway/project.json" ]; then
    echo "📦 Initializing Railway project..."
    railway init
fi

# Set environment variables
echo "🔧 Setting environment variables..."
echo "Please enter your OpenAI API key:"
read -p "OPENAI_API_KEY: " openai_key
railway variables set OPENAI_API_KEY="$openai_key"

echo "Enter your email configuration (optional, press Enter to skip):"
read -p "SMTP_USERNAME (email): " smtp_user
if [ ! -z "$smtp_user" ]; then
    railway variables set SMTP_USERNAME="$smtp_user"
    read -p "SMTP_PASSWORD (app password): " smtp_pass
    railway variables set SMTP_PASSWORD="$smtp_pass"
fi

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo "🌐 Your app will be available at: https://your-app-name.railway.app"
echo "📊 Check the Railway dashboard for logs and monitoring"

