import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Map abstract domain labels to dataset names in Supabase / local
DOMAIN_TO_DATASET = {
    "cybersecurity": "master_cyber",
    "software_engineering": "master_swe",
    "it_support": "master_it",
    "cloud": "master_cloud",
    "data_analytics": "master_data_analytics",
    "general": "master_data"
}


def classify_job(job_description: str) -> dict:
    """
    Use OpenAI to classify a job description into a domain and return
    a structured JSON result with confidence and reasoning.
    """
    if not job_description or not job_description.strip():
        return {
            "domain": "general",
            "confidence": 0.4,
            "secondary_domains": [],
            "reason": "Empty or missing description, falling back to general dataset."
        }

    system_prompt = (
        "You are a job classification engine. "
        "Given a job description, choose the SINGLE best primary domain and optional secondary domains.\n\n"
        "Allowed primary domains:\n"
        "- cybersecurity\n"
        "- software_engineering\n"
        "- it_support\n"
        "- cloud\n"
        "- data_analytics\n"
        "- general\n\n"
        "Return STRICT JSON with the following keys ONLY:\n"
        "{\n"
        '  \"domain\": \"one of the allowed domains\",\n'
        "  \"confidence\": number between 0 and 1,\n"
        "  \"secondary_domains\": [list of zero or more allowed domains],\n"
        "  \"reason\": \"short explanation of why you picked this\"\n"
        "}\n"
        "Do not include any extra text, just raw JSON."
    )

    user_prompt = (
        "Classify the following job description:\n\n"
        f"{job_description}\n"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1
    )

    content = response.choices[0].message.content

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # Fallback if the model returns something weird
        return {
            "domain": "general",
            "confidence": 0.5,
            "secondary_domains": [],
            "reason": f"Failed to parse JSON from model output: {content[:150]}"
        }

    # Safety: normalize / validate domain
    domain = str(data.get("domain", "general")).strip().lower()
    if domain not in DOMAIN_TO_DATASET:
        domain = "general"

    confidence = float(data.get("confidence", 0.6))
    secondary = data.get("secondary_domains", [])
    reason = data.get("reason", "")

    return {
        "domain": domain,
        "confidence": confidence,
        "secondary_domains": secondary,
        "reason": reason
    }


def select_dataset_for_job(job_description: str) -> dict:
    """
    High-level helper:
    - Classify the job
    - Map to dataset name
    - Return everything needed by the resume generator
    """
    classification = classify_job(job_description)
    domain = classification["domain"]
    dataset_name = DOMAIN_TO_DATASET.get(domain, "master_data")

    return {
        "dataset_name": dataset_name,
        "domain": domain,
        "confidence": classification["confidence"],
        "secondary_domains": classification["secondary_domains"],
        "reason": classification["reason"]
    }
