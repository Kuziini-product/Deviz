mport os
from openai import OpenAI
from dotenv import load_dotenv

# Încarcă variabilele din fișierul .env
load_dotenv()

# Definim API_KEY imediat după ce încărcăm .env
API_KEY = os.getenv("OPENAI_API_KEY")

# Verificăm dacă este setată
if not API_KEY:
    raise ValueError("🔑 OPENAI_API_KEY nu este setată. Verifică fișierul .env sau Streamlit Secrets.")

# Inițializăm clientul GPT
client = OpenAI(api_key=API_KEY)

# Funcția AI de generare deviz
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
