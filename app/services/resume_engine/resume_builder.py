import os
import json
from openai import OpenAI
from supabase import create_client
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# -----------------------------
# LOAD ENVIRONMENT
# -----------------------------
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# -----------------------------
# LOAD DATASET FROM SUPABASE
# -----------------------------
def load_dataset_from_supabase(dataset_name: str) -> dict:
    """Fetch a resume dataset from Supabase"""
    result = (
        supabase.table("resume_data")
        .select("content")
        .eq("dataset_name", dataset_name)
        .single()
        .execute()
    )

    return result.data["content"]


# -----------------------------
# GENERATE RAW RESUME SECTIONS
# -----------------------------
def generate_resume_sections(job_description: str, dataset: dict) -> dict:
    """Use OpenAI to merge dataset + job description into tailored sections."""

    prompt = f"""
You are a professional resume writer.
Use the provided dataset and job description to generate tailored resume content.

Dataset:
{json.dumps(dataset, indent=2)}

Job Description:
{job_description}

Return STRICT JSON with the following:

{{
  "summary": "...",
  "skills": [...],
  "experience": [
    {{
      "title": "...",
      "bullets": [...]
    }}
  ]
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You generate highly tailored resume content."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    try:
        data = json.loads(response.choices[0].message.content)
        return data
    except:
        return {
            "summary": "Results could not be parsed.",
            "skills": [],
            "experience": []
        }


# -----------------------------
# LOAD HTML TEMPLATE
# -----------------------------
def load_html_template() -> str:
    path = "resume_engine/template.html"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# -----------------------------
# MERGE TEMPLATE + CONTENT
# -----------------------------
def build_html_resume(content: dict) -> str:
    """Fill your template.html with the generated content."""

    html = load_html_template()
    soup = BeautifulSoup(html, "html.parser")

    # Replace SUMMARY
    summary_tag = soup.find(id="summary_block")
    if summary_tag:
        summary_tag.string = content["summary"]

    # Replace SKILLS
    skills_tag = soup.find(id="skills_block")
    if skills_tag:
        skills_tag.string = " | ".join(content["skills"])

    # Replace EXPERIENCE
    exp_section = soup.find(id="experience_block")
    if exp_section:
        exp_section.clear()
        for exp in content["experience"]:
            div = soup.new_tag("div")
            div.string = f"{exp['title']}: " + " ; ".join(exp["bullets"])
            exp_section.append(div)

    return str(soup)


# -----------------------------
# SAVE HTML TO PDF or DOCX
# -----------------------------
def save_as_pdf(html: str, output_path: str):
    """Exports the resume to a PDF."""
    from weasyprint import HTML
    HTML(string=html).write_pdf(output_path)


# -----------------------------
# HIGH-LEVEL BUILDER
# -----------------------------
def build_resume(job_description: str, dataset_name: str) -> str:
    print(f"🔄 Loading dataset: {dataset_name}")
    dataset = load_dataset_from_supabase(dataset_name)

    print("🤖 Generating tailored resume content...")
    content = generate_resume_sections(job_description, dataset)

    print("📝 Building HTML resume...")
    html = build_html_resume(content)

    output_path = f"generated_resume_{dataset_name}.pdf"
    print(f"📄 Saving PDF as {output_path}")
    save_as_pdf(html, output_path)

    return output_path
