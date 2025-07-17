# COST ANALYST AI Agent - API Documentation

## Base URL
Once deployed on Railway, your API will be available at:
```
https://your-app-name.railway.app
```

## Authentication
Currently, no authentication is required. All endpoints are publicly accessible.

## Endpoints

### 1. Health Check
**GET** `/health`

Check if the service is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "cost-analyst-agent"
}
```

### 2. Root Endpoint
**GET** `/`

Get basic service information.

**Response:**
```json
{
  "message": "COST ANALYST AI Agent is running",
  "version": "1.0.0",
  "endpoints": {
    "chat": "/chat",
    "health": "/health"
  }
}
```

### 3. Main Chat Endpoint
**POST** `/chat`

The primary endpoint for cost analysis. Send a message containing a part number to get comprehensive analysis.

**Request Body:**
```json
{
  "message": "Analyze the cost for part PA-10197"
}
```

**Response:**
```json
{
  "part_number": "PA-10197",
  "chart1": {
    "data": [...],
    "layout": {...}
  },
  "chart2": {
    "data": [...],
    "layout": {...}
  },
  "market_indices": {
    "raw_material": 1121.0,
    "electricity": 85.5,
    "gas": 45.2
  },
  "chart3": {
    "data": [...],
    "layout": {...}
  },
  "chart4": {
    "data": [...],
    "layout": {...}
  },
  "chart5": {
    "data": [...],
    "layout": {...}
  },
  "analysis": "Comprehensive AI-generated analysis and insights...",
  "success": true,
  "message": "Analysis completed successfully for part PA-10197"
}
```

**Charts Description:**
- **chart1**: Price trend chart for the part over time
- **chart2**: Cost Breakdown Structure (CBS) pie chart
- **chart3**: Raw material index trend (last 12 months)
- **chart4**: Electricity index trend (last 12 months)
- **chart5**: Natural gas index trend (last 12 months)

### 4. Part Information
**GET** `/part/{part_number}`

Get basic information about a specific part.

**Response:**
```json
{
  "part_number": "PA-10197",
  "supplier": "Supplier Name",
  "material": "Material Type",
  "current_price": 150.50,
  "currency": "EUR"
}
```

### 5. Market Indices
**GET** `/market-indices`

Get current market indices for raw materials, electricity, and gas.

**Response:**
```json
{
  "raw_material": 1121.0,
  "electricity": 85.5,
  "gas": 45.2,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "No valid part number found in the message. Please include a part number (e.g., PA-10197)."
}
```

### 404 Not Found
```json
{
  "detail": "Part PA-10197 not found in the master file."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error: [error description]"
}
```

## Frontend Integration Examples

### JavaScript/React Example
```javascript
const analyzePart = async (partNumber) => {
  try {
    const response = await fetch('https://your-app.railway.app/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: `Analyze the cost for part ${partNumber}`
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Render charts using Plotly
      Plotly.newPlot('chart1', data.chart1.data, data.chart1.layout);
      Plotly.newPlot('chart2', data.chart2.data, data.chart2.layout);
      Plotly.newPlot('chart3', data.chart3.data, data.chart3.layout);
      Plotly.newPlot('chart4', data.chart4.data, data.chart4.layout);
      Plotly.newPlot('chart5', data.chart5.data, data.chart5.layout);
      
      // Display analysis
      document.getElementById('analysis').innerHTML = data.analysis;
      
      // Display market indices
      document.getElementById('raw-material').textContent = data.market_indices.raw_material;
      document.getElementById('electricity').textContent = data.market_indices.electricity;
      document.getElementById('gas').textContent = data.market_indices.gas;
    }
  } catch (error) {
    console.error('Error:', error);
  }
};
```

### Python Example
```python
import requests
import json

def analyze_part(part_number, base_url="https://your-app.railway.app"):
    url = f"{base_url}/chat"
    payload = {
        "message": f"Analyze the cost for part {part_number}"
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

# Usage
result = analyze_part("PA-10197")
if result and result.get('success'):
    print(f"Analysis for {result['part_number']}:")
    print(result['analysis'])
```

### cURL Example
```bash
curl -X POST "https://your-app.railway.app/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze the cost for part PA-10197"}'
```

## Chart Rendering

All charts are returned as Plotly JSON objects. To render them:

1. **Include Plotly.js** in your frontend:
   ```html
   <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
   ```

2. **Render charts**:
   ```javascript
   Plotly.newPlot('chart-container', chartData.data, chartData.layout);
   ```

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider implementing rate limiting based on your requirements.

## CORS

The API is configured to allow requests from any origin (`*`). For production, you should configure specific allowed origins.

## Testing

You can test the API using:
- The interactive docs at `/docs` (Swagger UI)
- The alternative docs at `/redoc` (ReDoc)
- Direct HTTP requests using the examples above

## Support

For technical support or questions about the API, please refer to the main README.md file or contact the development team. 