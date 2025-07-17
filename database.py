from dotenv import load_dotenv
load_dotenv()
import os
import requests
from typing import Optional, Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

HEADERS = {
    "apikey": SUPABASE_ANON_KEY,
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    "Content-Type": "application/json"
}

# MASTER_FILE queries
def get_part_from_master_file(part_number: str) -> Optional[Dict[str, Any]]:
    try:
        url = f"{SUPABASE_URL}/rest/v1/MASTER_FILE"
        params = {"PartNumber": f"eq.{part_number}"}
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 200 and response.json():
            return response.json()[0]
        return None
    except Exception as e:
        logger.error(f"Error querying MASTER_FILE: {e}")
        return None

# CBS_PARTS queries
def get_cbs_for_part(part_number: str) -> Optional[Dict[str, Any]]:
    try:
        url = f"{SUPABASE_URL}/rest/v1/CBS_PARTS"
        params = {"partnumber": f"eq.{part_number}"}
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 200 and response.json():
            return response.json()[0]
        return None
    except Exception as e:
        logger.error(f"Error querying CBS_PARTS: {e}")
        return None

# BASELINE_INDEX queries
def get_baseline_index(index: str, material: Optional[str], month: Optional[str]) -> Optional[List[Dict[str, Any]]]:
    try:
        url = f"{SUPABASE_URL}/rest/v1/BASELINE_INDEX"
        params = {"index": f"eq.{index}"}
        if material:
            params["material"] = f"eq.{material}"
        if month:
            params["month"] = f"eq.{month}"
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 200 and response.json():
            return response.json()
        return None
    except Exception as e:
        logger.error(f"Error querying BASELINE_INDEX: {e}")
        return None

# Example: get all months for a given index/material
def get_baseline_index_trend(index: str, material: Optional[str], months: List[str]) -> Optional[List[Dict[str, Any]]]:
    try:
        url = f"{SUPABASE_URL}/rest/v1/BASELINE_INDEX"
        params = {"index": f"eq.{index}"}
        if material:
            params["material"] = f"eq.{material}"
        if months:
            # Use 'in' filter for months
            months_str = ','.join(months)
            params["month"] = f"in.({months_str})"
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 200 and response.json():
            return response.json()
        return None
    except Exception as e:
        logger.error(f"Error querying BASELINE_INDEX trend: {e}")
        return None 