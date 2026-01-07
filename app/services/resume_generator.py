import json
from jinja2 import Template
import pdfkit
import uuid
from app.core.supabase_client import supabase

TEMPLATE_PATH = "resume_engine/template.html"

def generate_resume(dataset_path: str, job_description: str):
    # Load dataset
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    # Add job description to dataset
    dataset["job_description"] = job_description

    # Load template
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template_html = f.read()

    template = Template(template_html)
    resume_html = template.render(dataset=dataset)

    output_pdf = f"generated_resumes/resume_{uuid.uuid4()}.pdf"

    # Convert to PDF
    pdfkit.from_string(resume_html, output_pdf)

    # Upload to Supabase
    with open(output_pdf, "rb") as f:
        file_bytes = f.read()

    supabase.storage.from_("resumes").upload(output_pdf.split("/")[-1], file_bytes)

    print(f"📄 Generated & uploaded resume → {output_pdf}")

    return output_pdf
