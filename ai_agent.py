import openai
from config import config
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CostAnalystAgent:
    def __init__(self):
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    
    def generate_analysis_and_insights(
        self,
        part_data: pd.DataFrame,
        cbs_data: pd.DataFrame,
        market_indices: Dict[str, float],
        market_trends: Dict[str, pd.DataFrame],
        part_number: str,
        user_message: str
    ) -> str:
        """Generate comprehensive analysis and insights using OpenAI"""
        
        try:
            # Prepare context for the AI
            context = self._prepare_analysis_context(
                part_data, cbs_data, market_indices, market_trends, part_number, user_message
            )
            
            # Create the prompt for analysis
            prompt = self._create_analysis_prompt(context)
            
            # Generate response using OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are COST ANALYST, an expert AI agent specializing in cost analysis and procurement negotiations. 
                        Your expertise includes:
                        - Analyzing cost structures and market trends
                        - Identifying negotiation opportunities and risks
                        - Providing actionable insights for price negotiations
                        - Understanding market indices and their impact on pricing
                        
                        You provide clear, professional analysis with specific recommendations for procurement professionals."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            return response.choices[0].message.content or "Analysis completed successfully."
            
        except Exception as e:
            logger.error(f"Error generating AI analysis: {e}")
            return self._generate_fallback_analysis(part_data, cbs_data, market_indices, part_number)
    
    def _prepare_analysis_context(
        self,
        part_data: pd.DataFrame,
        cbs_data: pd.DataFrame,
        market_indices: Dict[str, float],
        market_trends: Dict[str, pd.DataFrame],
        part_number: str,
        user_message: str
    ) -> Dict[str, Any]:
        """Prepare context data for AI analysis"""
        
        context = {
            "part_number": part_number,
            "user_message": user_message,
            "part_info": {},
            "cbs_info": {},
            "market_data": {},
            "trends": {}
        }
        
        # Extract part information
        if not part_data.empty:
            supplier_name = part_data.get('suppliername', pd.Series(['Unknown'])).iloc[0]
            part_name = part_data.get('partname', pd.Series(['Unknown'])).iloc[0]
            material = part_data.get('material', pd.Series(['Unknown'])).iloc[0]
            currency = part_data.get('currency', pd.Series(['EUR'])).iloc[0]
            
            context["part_info"] = {
                "supplier_name": supplier_name,
                "part_name": part_name,
                "material": material,
                "currency": currency
            }
            
            # Extract price trend data
            price_columns = [col for col in part_data.columns if col.startswith('price') and 'mkt' not in col]
            prices = []
            for col in price_columns:
                price = part_data[col].iloc[0]
                if pd.notna(price) and price > 0:
                    prices.append(float(price))
            
            if prices:
                context["part_info"]["current_price"] = prices[-1]
                context["part_info"]["avg_price"] = sum(prices) / len(prices)
                context["part_info"]["price_trend"] = "increasing" if prices[-1] > prices[0] else "decreasing" if prices[-1] < prices[0] else "stable"
        
        # Extract CBS information
        if not cbs_data.empty:
            cost_components = ['rawmaterial', 'machine', 'labor', 'overhead', 'energy', 'packaginglogistics', 'profit']
            for component in cost_components:
                if component in cbs_data.columns:
                    value = cbs_data[component].iloc[0]
                    if pd.notna(value) and value > 0:
                        context["cbs_info"][component] = float(value)
        
        # Market indices
        context["market_data"] = market_indices
        
        # Market trends summary
        for trend_type, trend_data in market_trends.items():
            if not trend_data.empty:
                values = trend_data['monthlyavgeuro'].tolist()
                if values:
                    context["trends"][trend_type] = {
                        "current": values[-1],
                        "avg": sum(values) / len(values),
                        "trend": "increasing" if values[-1] > values[0] else "decreasing" if values[-1] < values[0] else "stable"
                    }
        
        return context
    
    def _create_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Create the analysis prompt for OpenAI"""
        
        prompt = f"""
        As COST ANALYST, analyze the following procurement situation and provide comprehensive insights:

        PART INFORMATION:
        - Part Number: {context['part_number']}
        - Supplier: {context['part_info'].get('supplier_name', 'Unknown')}
        - Part Name: {context['part_info'].get('part_name', 'Unknown')}
        - Material: {context['part_info'].get('material', 'Unknown')}
        - Currency: {context['part_info'].get('currency', 'EUR')}
        - Current Price: {context['part_info'].get('current_price', 'Unknown')}
        - Average Price: {context['part_info'].get('avg_price', 'Unknown')}
        - Price Trend: {context['part_info'].get('price_trend', 'Unknown')}

        USER REQUEST: {context['user_message']}

        COST BREAKDOWN STRUCTURE:
        {self._format_cbs_info(context['cbs_info'])}

        CURRENT MARKET INDICES:
        - Raw Material: {context['market_data'].get('raw_material', 'N/A')} €/T
        - Electricity: {context['market_data'].get('electricity', 'N/A')} €/MWh
        - Natural Gas: {context['market_data'].get('gas', 'N/A')} €/MWh

        MARKET TRENDS (Last 12 months):
        {self._format_trends_info(context['trends'])}

        Please provide a comprehensive analysis including:

        1. **EXECUTIVE SUMMARY**: Brief overview of the situation and key findings
        2. **COST STRUCTURE ANALYSIS**: Analysis of the part's cost breakdown and efficiency
        3. **MARKET TREND ANALYSIS**: How market indices have evolved and their impact
        4. **PRICE COMPARISON**: Comparison between part price trends and market trends
        5. **NEGOTIATION OPPORTUNITIES**: Specific opportunities for price improvement
        6. **RISK ASSESSMENT**: Potential risks and mitigation strategies
        7. **RECOMMENDATIONS**: Actionable recommendations for the procurement team

        Focus on providing specific, data-driven insights that can be used in negotiations.
        """
        
        return prompt
    
    def _format_cbs_info(self, cbs_info: Dict[str, float]) -> str:
        """Format CBS information for the prompt"""
        if not cbs_info:
            return "No CBS data available"
        
        formatted = []
        for component, value in cbs_info.items():
            formatted.append(f"- {component.replace('packaginglogistics', 'Packaging & Logistics').title()}: {value:.2f} €")
        
        return "\n".join(formatted)
    
    def _format_trends_info(self, trends: Dict[str, Any]) -> str:
        """Format trends information for the prompt"""
        if not trends:
            return "No trend data available"
        
        formatted = []
        for trend_type, data in trends.items():
            formatted.append(f"- {trend_type.replace('_', ' ').title()}: Current {data['current']:.2f}, Avg {data['avg']:.2f}, Trend {data['trend']}")
        
        return "\n".join(formatted)
    
    def _generate_fallback_analysis(
        self,
        part_data: pd.DataFrame,
        cbs_data: pd.DataFrame,
        market_indices: Dict[str, float],
        part_number: str
    ) -> str:
        """Generate a fallback analysis when AI is not available"""
        
        analysis = f"""
        # COST ANALYSIS REPORT - {part_number}

        ## Executive Summary
        Analysis completed for part {part_number}. The system has processed available data to provide insights for negotiation purposes.

        ## Key Findings
        - Part identified in master file: {'Yes' if not part_data.empty else 'No'}
        - CBS data available: {'Yes' if not cbs_data.empty else 'No'}
        - Market indices retrieved: {len(market_indices)} out of 3 expected

        ## Market Conditions
        """
        
        if market_indices:
            analysis += f"""
        - Raw Material Index: {market_indices.get('raw_material', 'N/A')} €/T
        - Electricity Index: {market_indices.get('electricity', 'N/A')} €/MWh
        - Natural Gas Index: {market_indices.get('gas', 'N/A')} €/MWh
            """
        
        analysis += f"""

        ## Recommendations
        1. Review the provided charts for visual analysis of trends
        2. Compare part price evolution with market indices
        3. Identify negotiation opportunities based on market vs. supplier price movements
        4. Consider requesting detailed cost breakdown from supplier if not available

        ## Next Steps
        - Schedule supplier meeting to discuss pricing
        - Prepare negotiation strategy based on market analysis
        - Monitor market trends for future negotiations
        """
        
        return analysis 