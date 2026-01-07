import os
import json
from app.services.resume_engine.generator import generate_resume
from app.services.resume_selector import pick_dataset
from app.services.cover_letter_generator import generate_cover_letter


def load_local_dataset(dataset_path: str) -> dict:
    """Load JSON dataset from datasets folder."""
    # Get project root (parent directory of app folder)
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_file_dir))
    
    # If the path already includes 'datasets/', use it as-is
    # Otherwise, prepend 'datasets/'
    if dataset_path.startswith("datasets/"):
        full_path = os.path.join(project_root, dataset_path)
    else:
        full_path = os.path.join(project_root, "datasets", dataset_path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Dataset not found: {full_path}")

    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_resume_pipeline(job_description: str):
    """
    Select dataset → generate resume → generate cover letter.
    """

    print("🟣 Selecting dataset…")
    dataset_name = pick_dataset(job_description)
    print(f"🟣 Using dataset → {dataset_name}")

    master_data = load_local_dataset(dataset_name)

    print("📄 Generating tailored resume…")
    html_path, pdf_path = generate_resume(job_description, master_data)

    print("✉️ Generating tailored cover letter…")
    cover_letter_text = generate_cover_letter(job_description)

    # Save the cover letter
    cover_letter_path = os.path.join("storage", "cover_letters", "cover_letter.txt")
    os.makedirs(os.path.dirname(cover_letter_path), exist_ok=True)

    with open(cover_letter_path, "w", encoding="utf-8") as f:
        f.write(cover_letter_text)

    print(f"📨 Cover letter saved → {cover_letter_path}")

    return {
        "html_resume": html_path,
        "pdf_resume": pdf_path,
        "cover_letter": cover_letter_path
    }
