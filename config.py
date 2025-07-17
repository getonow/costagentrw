import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@db.btwbudemzcbaqxnpcgtf.supabase.co:5432/database_name")
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Application Configuration
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT = int(os.getenv("APP_PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    # Database table names
    MASTER_FILE_TABLE = "MASTER_FILE"
    CBS_PARTS_TABLE = "CBS_PARTS"
    BASELINE_INDEX_TABLE = "BASELINE_INDEX"

config = Config() 