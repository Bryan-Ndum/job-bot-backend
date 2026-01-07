import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

_supabase: Client | None = None


def get_supabase() -> Client:
    """
    Returns a singleton Supabase client so the app always uses only one instance.
    Prevents 'duplicate connection' errors and import loops.
    """
    global _supabase

    if _supabase is None:
        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            raise ValueError("❌ Missing Supabase environment variables.")
        _supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    return _supabase

