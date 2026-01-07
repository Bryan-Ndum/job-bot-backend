import json
import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Path to datasets folder
DATASETS_DIR = "resume_engine/datasets"

# List of dataset files
FILES = [
    "master_data.json",
    "master_cyber.json",
    "master_swe.json",
    "master_it.json",
    "master_cloud.json",
    "master_data_analytics.json"
]


def upload_dataset(filename):
    """Upload a single dataset to Supabase using UPSERT."""
    path = os.path.join(DATASETS_DIR, filename)
    
    # Make sure file exists
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        return
    
    # Load JSON file
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    dataset_name = filename.replace(".json", "")

    # UPSERT so duplicates do NOT crash
    response = supabase.table("resume_data").upsert(
        {
            "dataset_name": dataset_name,
            "content": data
        },
        on_conflict="dataset_name"
    ).execute()

    print(f"✅ Uploaded (or updated): {dataset_name}")


def main():
    print("\n=== Uploading Resume Datasets to Supabase ===\n")

    for file in FILES:
        upload_dataset(file)

    print("\n=== Done! All datasets uploaded successfully. ===\n")


if __name__ == "__main__":
    main()
