import os
from openai import OpenAI

# Load API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Path to universal cover letter template
TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__),
    "resume_engine",
    "templates",
    "cover_letter_universal.txt"
)


def load_base_cover_letter() -> str:
    """Load the universal cover letter template text."""
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Cover letter template not found: {TEMPLATE_PATH}")

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()


def generate_cover_letter(job_description: str) -> str:
    """
    Generate tailored cover letter using GPT-4o-mini based on:
    - Universal cover letter template
    - Job description
    """

    base_letter = load_base_cover_letter()

    prompt = f"""
    You are a professional cover letter writer.

    Rewrite the base cover letter so that it matches the job description.
    
    CRITICAL REQUIREMENTS:
    - EXACTLY 200-250 words total (not including greeting and closing)
    - Maximum 3 short paragraphs for the body
    - One paragraph referencing the company, product, or market
    - One paragraph explaining role alignment and relevant experience
    - Optional short closing paragraph if word count allows
    - Use a short, clear, professional tone
    - No filler, no generic buzzwords
    - Metrics in the first bullets when possible
    
    FORMAT:
    - Keep the greeting "Good day Sir/Ma'am," at the beginning
    - Keep the closing "Sincerely," followed by "Bryan Ndum" at the end
    - Body should start with "I am writing..." or similar

    BASE COVER LETTER:
    {base_letter}

    JOB DESCRIPTION:
    {job_description}

    Return ONLY the final cover letter text with the same greeting and closing format. Ensure the body is exactly 200-250 words.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    cover_letter = response.choices[0].message.content.strip()
    
    # Verify word count (excluding greeting and closing)
    word_count = count_body_words(cover_letter)
    
    # If outside range, adjust
    if word_count < 200 or word_count > 250:
        cover_letter = adjust_word_count(cover_letter, job_description, word_count)
    
    return cover_letter


def count_body_words(text: str) -> int:
    """Count words in the body (excluding greeting and closing)."""
    lines = text.split('\n')
    body_started = False
    body_lines = []
    
    for line in lines:
        line_lower = line.lower().strip()
        # Skip greeting
        if "good day" in line_lower or "dear" in line_lower:
            continue
        # Mark start of body
        if line.strip() and not body_started:
            body_started = True
        # Stop at closing
        if "sincerely" in line_lower or "best regards" in line_lower:
            break
        if body_started:
            body_lines.append(line)
    
    body_text = ' '.join(body_lines)
    return len(body_text.split())


def adjust_word_count(cover_letter: str, job_description: str, current_count: int) -> str:
    """Adjust cover letter to be within 200-250 word range."""
    if current_count > 250:
        # Truncate intelligently
        target = 225
        prompt = f"""
        Shorten this cover letter to exactly {target} words in the body (excluding greeting and closing).
        Keep the greeting "Good day Sir/Ma'am," and closing "Sincerely,\\nBryan Ndum".
        Maintain all key information about role alignment.

        COVER LETTER:
        {cover_letter}
        """
    else:
        # Expand intelligently
        target = 225
        prompt = f"""
        Expand this cover letter to exactly {target} words in the body (excluding greeting and closing).
        Add relevant details from the job description. Keep the greeting "Good day Sir/Ma'am," and closing "Sincerely,\\nBryan Ndum".

        COVER LETTER:
        {cover_letter}

        JOB DESCRIPTION:
        {job_description}
        """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except:
        return cover_letter  # Return original if adjustment fails
