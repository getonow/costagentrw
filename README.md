# COST ANALYST AI Agent

An AI-powered cost analysis and procurement negotiation assistant that provides comprehensive cost analysis for parts and materials.

## Features

- **Part Analysis**: Extract and analyze part information from master files
- **Cost Breakdown Structure (CBS)**: Generate CBS pie charts and analysis
- **Market Indices**: Real-time market data for raw materials, electricity, and gas
- **Price Trends**: Historical price trend analysis with interactive charts
- **AI Insights**: AI-generated analysis and procurement recommendations

## API Endpoints

- `POST /chat` - Main chat endpoint for cost analysis
- `GET /part/{part_number}` - Get basic part information
- `GET /market-indices` - Get current market indices
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint with API information

## Environment Variables

The following environment variables need to be configured:

```bash
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=False
```

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/getonow/costagentrw.git
cd costagentrw
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your environment variables

4. Run the application:
```bash
uvicorn main:app --host 0.0.0.0 --port 8081 --reload
```

## Cloud Deployment

This application is configured for deployment on Railway:

1. Fork or clone this repository to your GitHub account
2. Connect your GitHub repository to Railway
3. Configure the environment variables in Railway dashboard
4. Deploy!

## API Usage Example

```bash
curl -X POST "https://your-railway-app.railway.app/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze the cost for part PA-10197"}'
```

## Response Format

The API returns comprehensive analysis including:
- Part number
- Price trend charts
- CBS pie charts
- Market indices (raw materials, electricity, gas)
- Market trend charts
- AI-generated analysis and insights

## Technologies Used

- **FastAPI**: Modern web framework for building APIs
- **Supabase**: Database and backend services
- **OpenAI**: AI analysis and insights
- **Plotly**: Interactive charts and visualizations
- **Pandas**: Data manipulation and analysis
- **Uvicorn**: ASGI server for FastAPI

## License

This project is proprietary and confidential. 