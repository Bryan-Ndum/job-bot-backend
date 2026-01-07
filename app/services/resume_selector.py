from openai import OpenAI
from app.core.config import settings

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Maps domain → dataset file
DATASET_MAP = {
    "cyber": "datasets/master_cyber.json",
    "swe": "datasets/master_swe.json",
    "data": "datasets/master_data_analytics.json",
    "it": "datasets/master_it.json",
    "cloud": "datasets/master_cloud.json",
    "general": "datasets/master_data.json"
}


# ---------------------------------------------------------
# CLASSIFY JOB DESCRIPTION USING GPT-4o-mini
# ---------------------------------------------------------

def classify_job_description(text: str) -> str:
    """
    Uses GPT-4o-mini to classify job descriptions into:
    cyber, swe, it, data, cloud, general
    """

    if not text or text.strip().lower() == "skip":
        return "general"

    prompt = f"""
    You are a job classification model.

    Classify the job description into EXACTLY one of:
    - cyber
    - swe
    - it
    - data
    - cloud
    - general

    Respond ONLY with the label. No punctuation, no sentences.

    JOB DESCRIPTION:
    {text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    label = response.choices[0].message.content.strip().lower()

    # fallback safety
    return label if label in DATASET_MAP else "general"


# ---------------------------------------------------------
# PICK THE BEST DATASET BASED ON JOB CLASSIFICATION
# ---------------------------------------------------------

def pick_dataset(job_description: str) -> str:
    label = classify_job_description(job_description)
    print(f"🟣 Dataset selected → {label}")
    return DATASET_MAP[label]
