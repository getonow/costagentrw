#!/usr/bin/env python3
"""
Startup script for COST ANALYST AI Agent
"""

import os
import sys
import uvicorn
from config import config

def main():
    """Main startup function"""
    print("🚀 Starting COST ANALYST AI Agent...")
    print(f"📊 Database: {config.DATABASE_URL.split('@')[1] if '@' in config.DATABASE_URL else 'Not configured'}")
    print(f"🤖 OpenAI: {'Configured' if config.OPENAI_API_KEY else 'Not configured'}")
    print(f"🌐 Server: http://{config.APP_HOST}:{config.APP_PORT}")
    print(f"🔧 Debug Mode: {config.DEBUG}")
    print("-" * 50)
    
    # Check if OpenAI API key is configured
    if not config.OPENAI_API_KEY:
        print("⚠️  Warning: OpenAI API key not configured. AI analysis will use fallback mode.")
    
    # Start the server
    try:
        uvicorn.run(
            "main:app",
            host=config.APP_HOST,
            port=config.APP_PORT,
            reload=config.DEBUG,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 COST ANALYST AI Agent stopped.")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 