import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import re
import numpy as np
import math

def extract_part_number(message: str) -> Optional[str]:
    """Extract part number from user message"""
    # Common patterns for part numbers
    patterns = [
        r'PA-\d+',  # PA-10197 format
        r'part\s+([A-Z]+-\d+)',  # "part PA-10197"
        r'([A-Z]+-\d+)',  # Any uppercase letters followed by dash and numbers
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1) if len(match.groups()) > 0 else match.group(0)
    
    return None

def get_current_month_format() -> str:
    """Get current month in the format used by the database (e.g., 'jul-25')"""
    now = datetime.now()
    month_names = [
        'ene', 'feb', 'mar', 'abr', 'may', 'jun',
        'jul', 'ago', 'sep', 'oct', 'nov', 'dic'
    ]
    month = month_names[now.month - 1]
    year = str(now.year)[-2:]  # Last 2 digits of year
    return f"{month}-{year}"

def get_last_12_months() -> List[str]:
    """Get list of last 12 months in database format"""
    months = []
    now = datetime.now()
    month_names = [
        'ene', 'feb', 'mar', 'abr', 'may', 'jun',
        'jul', 'ago', 'sep', 'oct', 'nov', 'dic'
    ]
    
    for i in range(12):
        date = now - timedelta(days=30*i)
        month = month_names[date.month - 1]
        year = str(date.year)[-2:]
        months.append(f"{month}-{year}")
    
    return months[::-1]  # Reverse to get chronological order

def map_material_to_index(material: str, for_c3: bool = False) -> Optional[str]:
    """Map material description to index material type. If for_c3 is True, map PPS and related to PP for C3 index."""
    if not material:
        return None
    material_lower = material.lower()
    if for_c3:
        # For C3 index, map PPS and related to PP
        if any(x in material_lower for x in ['pa6', 'polyamide 6', 'nylon 6']):
            return 'PA6'
        elif any(x in material_lower for x in ['pa66', 'polyamide 66', 'nylon 66']):
            return 'PA66'
        elif any(x in material_lower for x in ['pp', 'polypropylene', 'pps', 'polyphenylene sulfide']):
            return 'PP'
    else:
        if any(x in material_lower for x in ['pa6', 'polyamide 6', 'nylon 6']):
            return 'PA6'
        elif any(x in material_lower for x in ['pa66', 'polyamide 66', 'nylon 66']):
            return 'PA66'
        elif any(x in material_lower for x in ['pp', 'polypropylene']):
            return 'PP'
        elif any(x in material_lower for x in ['pps', 'polyphenylene sulfide']):
            return 'PPS'
        elif any(x in material_lower for x in ['ppa', 'polyphthalamide']):
            return 'PPA'
    return None

def create_price_trend_chart(part_data: pd.DataFrame, part_number: str) -> Dict[str, Any]:
    """Create price trend chart for the part"""
    # Extract price columns and convert to time series
    price_columns = [col for col in part_data.columns if col.startswith('price') and 'mkt' not in col]
    
    # Create time series data
    prices = []
    dates = []
    
    for col in price_columns:
        # Extract month and year from column name
        month_year = col.replace('price', '')
        if len(month_year) >= 7:  # e.g., 'jan2023'
            month = month_year[:3]
            year = month_year[3:]
            
            # Convert to datetime
            month_names = {
                'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
            }
            
            if month in month_names:
                try:
                    date = datetime(int(year), month_names[month], 1)
                    price = part_data[col].iloc[0]
                    if pd.notna(price) and price > 0 and not math.isinf(price):
                        clean_price = float(price)
                        prices.append(clean_price)
                        dates.append(date)
                except (ValueError, TypeError):
                    continue
    
    if not prices:
        return {"error": "No valid price data found"}
    
    # Create Plotly figure
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=prices,
        mode='lines+markers',
        name='Part Price',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title=f"Price Trend - {part_number}",
        xaxis_title="Date",
        yaxis_title="Price (EUR)",
        template="plotly_white",
        height=400,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig.to_dict()

def create_cbs_pie_chart(cbs_data: pd.DataFrame, part_number: str, is_suggested: bool = False) -> Dict[str, Any]:
    """Create cost breakdown structure pie chart"""
    # Extract cost components
    cost_components = ['rawmaterial', 'machine', 'labor', 'overhead', 'energy', 'packaginglogistics', 'profit']
    
    labels = []
    values = []
    percentages = []
    
    total = 0
    for component in cost_components:
        if component in cbs_data.columns:
            value = cbs_data[component].iloc[0]
            if pd.notna(value) and value > 0 and not math.isinf(value):
                clean_value = float(value)
                labels.append(component.replace('packaginglogistics', 'Packaging & Logistics').title())
                values.append(clean_value)
                total += clean_value
    
    # Calculate percentages
    if total > 0:
        percentages = [(v/total)*100 for v in values]
    
    # Create Plotly figure
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3,
        textinfo='label+percent+value',
        textposition='inside',
        insidetextorientation='radial'
    )])
    
    title = f"CBS-Suggested for {part_number}" if is_suggested else f"CBS {part_number}"
    
    fig.update_layout(
        title=title,
        template="plotly_white",
        height=400,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig.to_dict()

def create_market_trend_chart(trend_data: pd.DataFrame, title: str, y_axis_title: str) -> Dict[str, Any]:
    """Create market trend chart"""
    if trend_data.empty:
        return {"error": f"No data available for {title}"}
    
    # Convert month strings to datetime for proper ordering
    dates = []
    values = []
    for month_str in trend_data['month']:
        try:
            # Parse month format like 'jul-25'
            month, year = month_str.split('-')
            month_names = {
                'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6,
                'jul': 7, 'ago': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12
            }
            if month in month_names:
                date = datetime(2000 + int(year), month_names[month], 1)
                dates.append(date)
            else:
                dates.append(datetime.now())
        except:
            dates.append(datetime.now())
    
    # Safely extract and clean values
    for value in trend_data['monthlyavgeuro']:
        try:
            if pd.notna(value) and not math.isinf(value):
                clean_value = float(value)
                values.append(clean_value)
            else:
                values.append(0.0)  # Replace NaN/Inf with 0
        except (ValueError, TypeError):
            values.append(0.0)
    
    # Ensure we have valid data
    if not values or len(values) != len(dates):
        return {"error": f"Invalid data for {title}"}
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines+markers',
        name=title,
        line=dict(color='#ff7f0e', width=2),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        y_axis_title=y_axis_title,
        template="plotly_white",
        height=300,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig.to_dict()

def suggest_cbs_structure(part_data: pd.DataFrame) -> Dict[str, float]:
    """Suggest CBS structure based on part information"""
    # This is a simplified suggestion based on typical industry standards
    # In a real implementation, this would be more sophisticated
    
    material = part_data['material'].iloc[0] if 'material' in part_data.columns else 'Unknown'
    currency = part_data['currency'].iloc[0] if 'currency' in part_data.columns else 'EUR'
    
    # Get average price from available price data
    price_columns = [col for col in part_data.columns if col.startswith('price') and 'mkt' not in col]
    prices = []
    for col in price_columns:
        price = part_data[col].iloc[0]
        if pd.notna(price) and price > 0 and not math.isinf(price):
            prices.append(float(price))
    
    # Safe average calculation with fallback
    if prices:
        avg_price = sum(prices) / len(prices)
        # Check for NaN or Infinity
        if pd.isna(avg_price) or math.isinf(avg_price):
            avg_price = 100.0
    else:
        avg_price = 100.0  # Default if no price data
    
    # Suggested breakdown (typical percentages for plastic parts)
    suggested_cbs = {
        'rawmaterial': avg_price * 0.35,  # 35% raw material
        'machine': avg_price * 0.20,      # 20% machine costs
        'labor': avg_price * 0.15,        # 15% labor
        'overhead': avg_price * 0.10,     # 10% overhead
        'energy': avg_price * 0.08,       # 8% energy
        'packaginglogistics': avg_price * 0.07,  # 7% packaging & logistics
        'profit': avg_price * 0.05        # 5% profit
    }
    
    # Ensure all values are valid floats
    for key, value in suggested_cbs.items():
        if pd.isna(value) or math.isinf(value):
            suggested_cbs[key] = 0.0
    
    return suggested_cbs

def format_currency(value: float, currency: str = 'EUR') -> str:
    """Format currency value"""
    if currency == 'EUR':
        return f"€{value:,.2f}"
    elif currency == 'USD':
        return f"${value:,.2f}"
    else:
        return f"{value:,.2f} {currency}" 

def convert_ndarrays_to_lists(obj):
    """Recursively convert numpy.ndarray to list in a nested structure."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_ndarrays_to_lists(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_ndarrays_to_lists(i) for i in obj]
    else:
        return obj 