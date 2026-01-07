import os
import json
from supabase import create_client
from dotenv import load_dotenv

# -------------------------------------------------
# LOAD ENVIRONMENT (.env)
# -------------------------------------------------
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ Missing Supabase credentials in .env")
    exit()

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# -------------------------------------------------
# ALL DATASETS YOU WANT TO UPLOAD
# Add/remove freely
# -------------------------------------------------

DATASETS = {
    "master_general": "datasets/master_general.json",
    "master_senior_cyber": "datasets/master_senior_cyber.json",
    "master_remote": "datasets/master_remote.json",

    # If you later add more datasets:
    "master_it": "datasets/master_it.json",
    "master_data_analytics": "datasets/master_data_analytics.json",
    "master_cloud": "datasets/master_cloud.json",
    "master_swe": "datasets/master_swe.json",
    "master_cyber": "datasets/master_cyber.json",
    "master_admin": "datasets/master_admin.json"
}

# -------------------------------------------------
# FUNCTION TO UPLOAD A SINGLE DATASET
# -------------------------------------------------
def upload_dataset(dataset_name, file_path):
    print(f"\n📤 Uploading: {dataset_name}")

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # UPSERT → Insert OR Update if it already exists
    response = (
        supabase.table("resume_data")
        .upsert(
            {
                "dataset_name": dataset_name,
                "content": data
            },
            on_conflict="dataset_name"
        )
        .execute()
    )

    print(f"✅ Uploaded: {dataset_name}")


# -------------------------------------------------
# MAIN EXECUTION
# -------------------------------------------------
def main():
    print("\n🚀 Uploading all resume datasets to Supabase...\n")

    for dataset_name, file_path in DATASETS.items():
        upload_dataset(dataset_name, file_path)

    print("\n🎉 FINISHED — All datasets uploaded to Supabase!")


if __name__ == "__main__":
    main()
