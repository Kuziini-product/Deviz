import os
from openai import OpenAI
from dotenv import load_dotenv

# Încarcă variabilele din .env
load_dotenv()

# Obține cheia API din variabila de mediu
import os
print("DEBUG - API KEY:", os.getenv("OPENAI_API_KEY"))

# Verifică dacă este setată cheia
if not API_KEY:
    raise ValueError("🔑 OPENAI_API_KEY nu este setată. Verifică fișierul .env sau Streamlit Secrets.")

# Creează clientul GPT
client = OpenAI(api_key=API_KEY)

# Exemplu funcție de generare deviz
def genereaza_deviz_AI(prompt_user: str):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ești un expert în mobilier care generează devize detaliate."},
                {"role": "user", "content": prompt_user}
            ],
            temperature=0.5,
            max_tokens=1500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Eroare la generarea devizului: {e}"
