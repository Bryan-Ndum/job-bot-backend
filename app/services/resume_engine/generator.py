import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from app.core.supabase_client import get_supabase
from .pdf_converter import html_to_pdf

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
sb = get_supabase()

# 100% reliable Windows-safe path resolution
TEMPLATE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "template.html")
)

HTML_OUTPUT_DIR = os.path.abspath("storage/resumes/html")
PDF_OUTPUT_DIR = os.path.abspath("storage/resumes/pdf")


# --------------------------------------------
# LOAD HTML TEMPLATE
# --------------------------------------------
def load_template():
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"template.html NOT FOUND at: {TEMPLATE_PATH}")

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()


# --------------------------------------------
# FORCE CONTENT INTO SAFE STRUCTURE
# --------------------------------------------
def ensure_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [value]
    return []


# --------------------------------------------
# FORMAT CONTENT INTO HTML TEMPLATE
# --------------------------------------------
def fill_template(template: str, summary, education, experience, projects, skills, certs):

    if isinstance(skills, list):
        skills = " | ".join(skills)

    if isinstance(certs, list):
        certs = ", ".join(certs)

    # EXPERIENCE → HTML blocks
    if isinstance(experience, list):
        blocks = []
        for exp in experience:
            title = exp.get("title", "")
            bullets = ensure_list(exp.get("bullets", []))
            bullet_html = "<br>- " + "<br>- ".join(bullets)
            blocks.append(f"<b>{title}</b><br>{bullet_html}")
        experience = "<br><br>".join(blocks)

    # PROJECTS → HTML blocks
    if isinstance(projects, list):
        blocks = []
        for proj in projects:
            title = proj.get("title", "")
            bullets = ensure_list(proj.get("bullets", []))
            bullet_html = "<br>- " + "<br>- ".join(bullets)
            blocks.append(f"<b>{title}</b><br>{bullet_html}")
        projects = "<br><br>".join(blocks)

    # Insert into template
    return (
        template.replace("{{SUMMARY}}", str(summary))
                .replace("{{EDUCATION}}", str(education))
                .replace("{{EXPERIENCE}}", str(experience))
                .replace("{{PROJECTS}}", str(projects))
                .replace("{{SKILLS}}", str(skills))
                .replace("{{CERTIFICATIONS}}", str(certs))
    )


# --------------------------------------------
# GPT SECTION GENERATOR
# --------------------------------------------
def generate_section(prompt: str):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system",
             "content": "Write clean, concise, ATS-optimized resume bullets."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=350
    )
    return response.choices[0].message.content.strip()


# --------------------------------------------
# MAIN RESUME GENERATOR
# --------------------------------------------
def generate_resume(job_description: str, master_data: dict):

    print("📄 Loading template...")
    template = load_template()

    # Generate each section
    summary = generate_section(
        f"Rewrite my summary to match this job:\n\nJD:\n{job_description}\n\nSummary:\n{master_data['summary']}"
    )

    skills = ensure_list(master_data["skills"])
    experience = ensure_list(master_data["experience"])
    projects = ensure_list(master_data["projects"])
    education = master_data["education"]
    certs = ensure_list(master_data["certifications"])

    # Build final HTML
    final_html = fill_template(
        template,
        summary,
        education,
        experience,
        projects,
        skills,
        certs
    )

    # Ensure folders exist
    os.makedirs(HTML_OUTPUT_DIR, exist_ok=True)
    os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

    html_path = os.path.join(HTML_OUTPUT_DIR, "resume.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"✅ HTML resume saved → {html_path}")

    # Convert HTML → PDF
    pdf_path = html_to_pdf(html_path, PDF_OUTPUT_DIR)

    if not pdf_path:
        raise RuntimeError("❌ PDF generation failed.")

    print(f"📄 PDF resume saved → {pdf_path}")

    return html_path, pdf_path
