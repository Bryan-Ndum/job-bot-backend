import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

DATASETS = [
    "master_general",
    "master_senior_cyber",
    "master_remote",
    "master_admin"
]

for name in DATASETS:
    print(f"\n🔍 Checking dataset: {name}")

    result = (
        supabase.table("resume_data")
        .select("content")
        .eq("dataset_name", name)
        .execute()
    )

    if not result.data:
        print(f"❌ Not found in Supabase: {name}")
    else:
        print(f"✅ Found → Keys: {list(result.data[0]['content'].keys())}")
