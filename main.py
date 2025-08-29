from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import math

from database import (
    get_part_from_master_file,
    get_cbs_for_part,
    get_baseline_index,
    get_baseline_index_trend
)
from utils import (
    extract_part_number, get_current_month_format, get_last_12_months,
    map_material_to_index, create_price_trend_chart, create_cbs_pie_chart,
    create_market_trend_chart, suggest_cbs_structure, format_currency,
    convert_ndarrays_to_lists
)
from ai_agent import CostAnalystAgent
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="COST ANALYST AI Agent",
    description="AI-powered cost analysis and procurement negotiation assistant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for production
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type", 
        "Authorization", 
        "X-Requested-With",
        "Accept",
        "Origin"
    ],
    expose_headers=["*"],
    max_age=86400,  # Cache preflight requests for 24 hours
)

# Initialize AI agent
ai_agent = CostAnalystAgent()

# Pydantic models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    part_number: str
    chart1: Dict[str, Any]  # Price trend chart
    chart2: Dict[str, Any]  # CBS pie chart
    market_indices: Dict[str, float]  # Current market indices
    chart3: Dict[str, Any]  # Raw material trend
    chart4: Dict[str, Any]  # Electricity trend
    chart5: Dict[str, Any]  # Gas trend
    analysis: str  # AI-generated analysis and insights
    success: bool
    message: str

def safe_float(val):
    """Safely convert value to float, handling None, NaN, and Infinity"""
    try:
        if val is None:
            return 0.0
        float_val = float(val)
        # Check for NaN or Infinity
        if pd.isna(float_val) or math.isinf(float_val):
            return 0.0
        return float_val
    except Exception:
        return 0.0

def clean_for_json(obj):
    """Recursively clean data structure to ensure JSON serialization compatibility"""
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(item) for item in obj]
    elif isinstance(obj, float):
        # Handle NaN and Infinity
        if pd.isna(obj) or math.isinf(obj):
            return 0.0
        return obj
    elif isinstance(obj, (int, str, bool)) or obj is None:
        return obj
    else:
        # Convert any other types to string to ensure JSON compatibility
        return str(obj)

@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return {
        "message": "COST ANALYST AI Agent is running",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint accessed")
    return {"status": "healthy", "service": "cost-analyst-agent"}

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """Handle preflight OPTIONS requests for all endpoints"""
    return {
        "message": "OK",
        "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allowed_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"]
    }

@app.options("/chat")
async def chat_options():
    """Handle preflight OPTIONS requests for the chat endpoint"""
    return {
        "message": "OK",
        "allowed_methods": ["POST"],
        "allowed_headers": ["Content-Type", "Authorization", "X-Requested-With"]
    }

@app.get("/test-cors")
async def test_cors():
    """Test endpoint to verify CORS is working"""
    logger.info("CORS test endpoint accessed")
    return {
        "message": "CORS test successful",
        "timestamp": "2024-01-15T10:30:00Z",
        "cors_enabled": True,
        "status": "working"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint for the COST ANALYST agent.
    Processes user messages and returns comprehensive cost analysis.
    """
    logger.info(f"Received chat request: {request.message}")
    try:
        market_indices_clean = {"raw_material": 0.0, "electricity": 0.0, "gas": 0.0}
        # Step 1: Extract part number from user message
        part_number = extract_part_number(request.message)
        if not part_number:
            raise HTTPException(
                status_code=400,
                detail="No valid part number found in the message. Please include a part number (e.g., PA-10197)."
            )
        
        logger.info(f"Processing request for part: {part_number}")
        
        # Step 2: Get part information from MASTER_FILE
        part_data_dict = get_part_from_master_file(part_number)
        if part_data_dict is None:
            raise HTTPException(
                status_code=404,
                detail=f"Part {part_number} not found in the master file."
            )
        part_data = pd.DataFrame([part_data_dict])
        
        # Step 3: Generate price trend chart (Chart 1)
        chart1 = create_price_trend_chart(part_data, part_number)
        
        # Step 4: Get CBS information and generate pie chart (Chart 2)
        cbs_data_dict = get_cbs_for_part(part_number)
        is_suggested_cbs = False
        
        if cbs_data_dict is None:
            # Generate suggested CBS structure
            suggested_cbs = suggest_cbs_structure(part_data)
            # Convert to DataFrame format for chart generation
            cbs_data = pd.DataFrame([suggested_cbs])
            is_suggested_cbs = True
        else:
            cbs_data = pd.DataFrame([cbs_data_dict])
        
        chart2 = create_cbs_pie_chart(cbs_data, part_number, is_suggested_cbs)
        
        # Step 5: Get current market indices
        material = part_data['material'].iloc[0] if 'material' in part_data.columns else "Unknown"
        # For C3 index, use the special mapping
        index_material_c3 = map_material_to_index(material, for_c3=True)
        index_material = map_material_to_index(material)
        current_month = get_current_month_format()
        
        logger.info(f"Material: {material}, C3 Index Material: {index_material_c3}, Regular Index Material: {index_material}")
        logger.info(f"Current month: {current_month}")
        
        # Raw material index (C3 index) - only query if we have a valid material mapping
        raw_material_value = None
        if index_material_c3:
            raw_material_data = get_baseline_index(
                index="C3",
                material=index_material_c3,
                month=current_month
            )
            logger.info(f"Raw material data for C3 index: {raw_material_data}")
            # Safe extraction with proper null checks
            if raw_material_data and len(raw_material_data) > 0:
                try:
                    monthly_avg = raw_material_data[0].get('monthlyavgeuro')
                    if monthly_avg is not None:
                        raw_material_value = float(monthly_avg)
                except (ValueError, TypeError, KeyError):
                    raw_material_value = None
        else:
            logger.warning(f"No valid C3 index material mapping found for material: {material}")
        
        # Electricity index
        electricity_data = get_baseline_index(
            index="European Wholesale Electricity Prices",
            material=None,
            month=current_month
        )
        logger.info(f"Electricity data: {electricity_data}")
        # Safe extraction with proper null checks
        electricity_value = None
        if electricity_data and len(electricity_data) > 0:
            try:
                monthly_avg = electricity_data[0].get('monthlyavgeuro')
                if monthly_avg is not None:
                    electricity_value = float(monthly_avg)
            except (ValueError, TypeError, KeyError):
                electricity_value = None
        
        # Gas index
        gas_data = get_baseline_index(
            index="Natural Gas EU Dutch TTF (EUR/MWh)",
            material=None,
            month=current_month
        )
        logger.info(f"Gas data: {gas_data}")
        # Safe extraction with proper null checks
        gas_value = None
        if gas_data and len(gas_data) > 0:
            try:
                monthly_avg = gas_data[0].get('monthlyavgeuro')
                if monthly_avg is not None:
                    gas_value = float(monthly_avg)
            except (ValueError, TypeError, KeyError):
                gas_value = None
        
        market_indices = {
            "raw_material": raw_material_value,
            "electricity": electricity_value,
            "gas": gas_value
        }
        
        logger.info(f"Final market indices values: {market_indices}")
        
        # Step 6: Get market trends and generate charts (Charts 3, 4, 5)
        last_12_months = get_last_12_months()
        # Raw material trend (C3 index) - only query if we have a valid material mapping
        raw_material_trend_df = pd.DataFrame()
        if index_material_c3:
            raw_material_trend = get_baseline_index_trend(
                index="C3",
                material=index_material_c3,
                months=last_12_months
            )
            raw_material_trend_df = pd.DataFrame(raw_material_trend) if raw_material_trend else pd.DataFrame()
        
        chart3 = create_market_trend_chart(
            raw_material_trend_df,
            "Raw Material Index Trend",
            "Price (€/T)"
        )
        # Electricity trend
        electricity_trend = get_baseline_index_trend(
            index="European Wholesale Electricity Prices",
            material=None,
            months=last_12_months
        )
        electricity_trend_df = pd.DataFrame(electricity_trend) if electricity_trend else pd.DataFrame()
        chart4 = create_market_trend_chart(
            electricity_trend_df,
            "Energy Index Electricity Trend",
            "Price (€/MWh)"
        )
        # Gas trend
        gas_trend = get_baseline_index_trend(
            index="Natural Gas EU Dutch TTF (EUR/MWh)",
            material=None,
            months=last_12_months
        )
        gas_trend_df = pd.DataFrame(gas_trend) if gas_trend else pd.DataFrame()
        chart5 = create_market_trend_chart(
            gas_trend_df,
            "Energy Index Gas Trend",
            "Price (€/MWh)"
        )
        
        # Step 7: Generate AI analysis and insights
        try:
            analysis = ai_agent.generate_analysis_and_insights(
                part_data, cbs_data, market_indices_clean, {
                    'raw_material': raw_material_trend_df,
                    'electricity': electricity_trend_df,
                    'gas': gas_trend_df
                }, part_number, request.message
            )
        except Exception as e:
            logger.warning(f"AI analysis failed, using fallback: {e}")
            analysis = f"Analysis completed for part {part_number}. AI insights temporarily unavailable."
        
        # Prepare response
        # Ensure market_indices has only float values
        market_indices_clean = {k: safe_float(v) for k, v in market_indices.items()}
        # Ensure all charts are dicts (not lists)
        def ensure_dict(x):
            return x if isinstance(x, dict) else {}
        
        # Clean all response data for JSON serialization
        cleaned_chart1 = clean_for_json(ensure_dict(convert_ndarrays_to_lists(chart1)))
        cleaned_chart2 = clean_for_json(ensure_dict(convert_ndarrays_to_lists(chart2)))
        cleaned_chart3 = clean_for_json(ensure_dict(convert_ndarrays_to_lists(chart3)))
        cleaned_chart4 = clean_for_json(ensure_dict(convert_ndarrays_to_lists(chart4)))
        cleaned_chart5 = clean_for_json(ensure_dict(convert_ndarrays_to_lists(chart5)))
        
        response = ChatResponse(
            part_number=part_number,
            chart1=cleaned_chart1,
            chart2=cleaned_chart2,
            market_indices=market_indices_clean,
            chart3=cleaned_chart3,
            chart4=cleaned_chart4,
            chart5=cleaned_chart5,
            analysis=analysis,
            success=True,
            message=f"Analysis completed successfully for part {part_number}"
        )
        
        logger.info(f"Successfully processed analysis for part {part_number}")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/part/{part_number}")
async def get_part_info(part_number: str):
    """Get basic part information"""
    try:
        part_data_dict = get_part_from_master_file(part_number)
        if part_data_dict is None:
            raise HTTPException(status_code=404, detail="Part not found")
        return {
            "part_number": part_number,
            "data": part_data_dict
        }
    except Exception as e:
        logger.error(f"Error getting part info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market-indices")
async def get_market_indices():
    """Get current market indices"""
    try:
        current_month = get_current_month_format()
        # Raw material index
        raw_material_data = get_baseline_index(
            index="Tecnon Engineering Resin €/T (low)",
            material=None,
            month=current_month
        )
        # Safe extraction with proper null checks
        raw_material_value = None
        if raw_material_data and len(raw_material_data) > 0:
            try:
                monthly_avg = raw_material_data[0].get('monthlyavgeuro')
                if monthly_avg is not None:
                    raw_material_value = float(monthly_avg)
            except (ValueError, TypeError, KeyError):
                raw_material_value = None
        
        # Electricity index
        electricity_data = get_baseline_index(
            index="European Wholesale Electricity Prices",
            material=None,
            month=current_month
        )
        # Safe extraction with proper null checks
        electricity_value = None
        if electricity_data and len(electricity_data) > 0:
            try:
                monthly_avg = electricity_data[0].get('monthlyavgeuro')
                if monthly_avg is not None:
                    electricity_value = float(monthly_avg)
            except (ValueError, TypeError, KeyError):
                electricity_value = None
        
        # Gas index
        gas_data = get_baseline_index(
            index="Natural Gas EU Dutch TTF (EUR/MWh)",
            material=None,
            month=current_month
        )
        # Safe extraction with proper null checks
        gas_value = None
        if gas_data and len(gas_data) > 0:
            try:
                monthly_avg = gas_data[0].get('monthlyavgeuro')
                if monthly_avg is not None:
                    gas_value = float(monthly_avg)
            except (ValueError, TypeError, KeyError):
                gas_value = None
        
        indices = {
            "raw_material": raw_material_value,
            "electricity": electricity_value,
            "gas": gas_value
        }
        return {
            "current_month": current_month,
            "indices": indices
        }
    except Exception as e:
        logger.error(f"Error getting market indices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8081,
        reload=True
    ) 