#!/usr/bin/env python3
"""
Test script for COST ANALYST AI Agent
Demonstrates API functionality with example requests
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_root_endpoint():
    """Test root endpoint"""
    print("\n🔍 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")

def test_chat_endpoint(part_number="PA-10197"):
    """Test main chat endpoint"""
    print(f"\n🔍 Testing chat endpoint with part {part_number}...")
    
    message = f"The supplier wants to increase the price of part {part_number} by 10%"
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"message": message},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Chat endpoint working")
            data = response.json()
            print(f"   Part Number: {data.get('part_number')}")
            print(f"   Success: {data.get('success')}")
            print(f"   Message: {data.get('message')}")
            
            # Check if charts were generated
            charts = ['chart1', 'chart2', 'chart3', 'chart4', 'chart5']
            for chart in charts:
                if chart in data and data[chart]:
                    print(f"   ✅ {chart}: Generated")
                else:
                    print(f"   ❌ {chart}: Not generated")
            
            # Check market indices
            indices = data.get('market_indices', {})
            if indices:
                print(f"   📊 Market Indices: {indices}")
            else:
                print("   ❌ Market Indices: Not available")
            
            # Check analysis
            analysis = data.get('analysis', '')
            if analysis:
                print(f"   🤖 Analysis: {len(analysis)} characters generated")
            else:
                print("   ❌ Analysis: Not generated")
                
        elif response.status_code == 404:
            print(f"❌ Part {part_number} not found in database")
        elif response.status_code == 400:
            print(f"❌ Bad request: {response.json().get('detail', 'Unknown error')}")
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")

def test_part_info_endpoint(part_number="PA-10197"):
    """Test part info endpoint"""
    print(f"\n🔍 Testing part info endpoint for {part_number}...")
    try:
        response = requests.get(f"{BASE_URL}/part/{part_number}")
        if response.status_code == 200:
            print("✅ Part info endpoint working")
            data = response.json()
            print(f"   Part Number: {data.get('part_number')}")
            print(f"   Data available: {len(data.get('data', {}))} fields")
        elif response.status_code == 404:
            print(f"❌ Part {part_number} not found")
        else:
            print(f"❌ Part info endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Part info endpoint error: {e}")

def test_market_indices_endpoint():
    """Test market indices endpoint"""
    print("\n🔍 Testing market indices endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/market-indices")
        if response.status_code == 200:
            print("✅ Market indices endpoint working")
            data = response.json()
            print(f"   Current Month: {data.get('current_month')}")
            print(f"   Indices: {data.get('indices')}")
        else:
            print(f"❌ Market indices endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Market indices endpoint error: {e}")

def main():
    """Main test function"""
    print("🧪 COST ANALYST AI Agent - API Test Suite")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Run tests
    test_health_check()
    test_root_endpoint()
    test_chat_endpoint("PA-10197")
    test_chat_endpoint("PA-10181")  # Test another part
    test_part_info_endpoint("PA-10197")
    test_market_indices_endpoint()
    
    print("\n" + "=" * 50)
    print("🏁 Test suite completed!")
    print("\n💡 Tips:")
    print("   - Check the logs for detailed information")
    print("   - Verify database connection if tests fail")
    print("   - Ensure OpenAI API key is configured for AI analysis")
    print("   - Visit http://localhost:8000/docs for interactive API documentation")

if __name__ == "__main__":
    main() 