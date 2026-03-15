import os
from supabase import create_client, Client
from core.config import settings

def get_supabase_client() -> Client | None:
    """Create and return a Supabase client connection."""
    url: str = settings.SUPABASE_URL
    key: str = settings.SUPABASE_KEY
    if not url or not key:
        print("Error: SUPABASE_URL or SUPABASE_KEY is missing in environment variables.")
        return None
    try:
        supabase: Client = create_client(url, key)
        return supabase
    except Exception as e:
        print(f"Error while connecting to Supabase: {e}")
        return None
