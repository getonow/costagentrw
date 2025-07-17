# Deployment Guide: Migrating to Railway

This guide will help you migrate your local COST ANALYST AI Agent to Railway cloud platform.

## Prerequisites

1. **GitHub Account**: You need a GitHub account
2. **Railway Account**: Sign up at [railway.app](https://railway.app)
3. **Environment Variables**: Your current `.env` file with:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `OPENAI_API_KEY`

## Step 1: Push to GitHub

1. **Initialize Git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Railway deployment"
   ```

2. **Add your GitHub repository as remote**:
   ```bash
   git remote add origin https://github.com/getonow/costagentrw.git
   git branch -M main
   git push -u origin main
   ```

## Step 2: Deploy to Railway

1. **Go to Railway Dashboard**:
   - Visit [railway.app](https://railway.app)
   - Sign in with your GitHub account

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository: `getonow/costagentrw`

3. **Configure Environment Variables**:
   - In your Railway project dashboard, go to "Variables" tab
   - Add the following environment variables:
     ```
     SUPABASE_URL=your_supabase_url
     SUPABASE_ANON_KEY=your_supabase_anon_key
     OPENAI_API_KEY=your_openai_api_key
     APP_HOST=0.0.0.0
     APP_PORT=8000
     DEBUG=False
     ```

4. **Deploy**:
   - Railway will automatically detect the Python project
   - It will install dependencies from `requirements.txt`
   - The app will start using the `Procfile`

## Step 3: Verify Deployment

1. **Check Deployment Status**:
   - In Railway dashboard, check the "Deployments" tab
   - Ensure the deployment is successful (green status)

2. **Test Your API**:
   - Get your Railway app URL from the dashboard
   - Test the health endpoint: `https://your-app.railway.app/health`
   - Test the main chat endpoint with a sample request

3. **Update Your Frontend**:
   - Replace `http://localhost:8081` with your Railway URL
   - Example: `https://your-app.railway.app/chat`

## Step 4: Configure Custom Domain (Optional)

1. **Add Custom Domain**:
   - In Railway dashboard, go to "Settings" → "Domains"
   - Add your custom domain
   - Configure DNS records as instructed

## Troubleshooting

### Common Issues:

1. **Build Failures**:
   - Check Railway logs for dependency issues
   - Ensure all packages in `requirements.txt` are compatible

2. **Environment Variables**:
   - Verify all required variables are set in Railway
   - Check for typos in variable names

3. **Database Connection**:
   - Ensure Supabase URL and key are correct
   - Check if Supabase allows connections from Railway's IP ranges

4. **Port Issues**:
   - Railway automatically sets the `PORT` environment variable
   - The app is configured to use `$PORT` in the Procfile

### Monitoring:

- **Logs**: Check Railway logs for any errors
- **Metrics**: Monitor CPU, memory usage in Railway dashboard
- **Health Checks**: Use the `/health` endpoint to verify service status

## Cost Optimization

Railway pricing is based on usage:
- **Free Tier**: Limited hours per month
- **Pro Plan**: Pay for actual usage
- **Team Plan**: For multiple developers

Monitor your usage in the Railway dashboard to optimize costs.

## Security Considerations

1. **Environment Variables**: Never commit sensitive data to Git
2. **CORS**: Update CORS settings for production domains
3. **Rate Limiting**: Consider adding rate limiting for production
4. **API Keys**: Rotate API keys regularly

## Next Steps

After successful deployment:

1. **Set up monitoring** and alerting
2. **Configure CI/CD** for automatic deployments
3. **Set up staging environment** for testing
4. **Document API** for team members
5. **Set up backup strategies** for your data

Your API will now be accessible from anywhere on the internet at:
`https://your-app.railway.app` 