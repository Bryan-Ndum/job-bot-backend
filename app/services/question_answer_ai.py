import time
import openai
from selenium.webdriver.common.by import By
from app.core.config import settings

openai.api_key = settings.OPENAI_API_KEY

def ai_generate_answer(question: str) -> str:
    """Generate a strong job-specific answer."""
    prompt = f"""
    You are Bryan Ndum, a cybersecurity and software engineer.
    Use his resume context to answer professionally.

    Question:
    "{question}"

    Provide a clear, confident, short answer.
    """

    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return completion.choices[0].message["content"].strip()

def answer_question(driver):
    """Detects LinkedIn questions and answers them with AI."""
    print("🤖 Checking for questions to answer…")

    textareas = driver.find_elements(By.CSS_SELECTOR, "textarea")

    for area in textareas:
        label = area.get_attribute("aria-label") or ""
        
        if not label:
            continue

        print(f"🟣 AI answering: {label}")
        try:
            answer = ai_generate_answer(label)
            area.clear()
            time.sleep(0.4)
            area.send_keys(answer)
            time.sleep(0.5)
        except Exception as e:
            print("❌ Error answering question:", e)
            continue
