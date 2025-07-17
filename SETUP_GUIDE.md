# 🚀 Quick Setup Guide - COST ANALYST AI Agent

## Immediate Start (Windows)

1. **Double-click** `start.bat` to automatically:
   - Create virtual environment
   - Install dependencies
   - Start the server

## Immediate Start (Linux/Mac)

1. **Run** `./start.sh` in terminal to automatically:
   - Create virtual environment
   - Install dependencies
   - Start the server

## Manual Setup

### 1. Create Environment File
Create `.env` file in the root directory:
```env
DATABASE_URL=postgresql://username:password@db.btwbudemzcbaqxnpcgtf.supabase.co:5432/database_name
OPENAI_API_KEY=your_openai_api_key_here
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Server
```bash
python start.py
```

## Test the Application

1. **Health Check**: Visit `http://localhost:8000/health`
2. **API Docs**: Visit `http://localhost:8000/docs`
3. **Test Script**: Run `python test_example.py`

## Example API Call

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "The supplier wants to increase the price of part PA-10197 by 10%"}'
```

## What You Get

✅ **5 Interactive Charts** (Plotly JSON format)
✅ **Market Indices** (Raw material, electricity, gas)
✅ **AI Analysis** (Comprehensive insights and recommendations)
✅ **Cost Breakdown Structure** (Pie chart visualization)
✅ **Price Trend Analysis** (Historical data visualization)

## Troubleshooting

- **Database Connection**: Check DATABASE_URL in `.env`
- **OpenAI API**: Verify API key is valid
- **Port Issues**: Change APP_PORT in `.env` if 8000 is busy
- **Dependencies**: Run `pip install -r requirements.txt`

## Next Steps

1. Configure your database connection
2. Add your OpenAI API key
3. Test with your frontend application
4. Customize charts and analysis as needed

---

**🎯 Ready to analyze costs and negotiate better prices!** 