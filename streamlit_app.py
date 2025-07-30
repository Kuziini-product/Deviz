
import streamlit as st
import pandas as pd
import base64
from pathlib import Path
from PIL import Image
from ai_generator import genereaza_deviz_AI
from image_utils import extrage_dimensiuni_din_imagine
from deviz_exporter import export_excel_pdf, lista_oferte_istoric
import os
from dotenv import load_dotenv
import json
import time

load_dotenv()
st.set_page_config(page_title="Kuziini | Configurator Devize", layout="wide")
st.image("Kuziini_logo_negru.png", width=320)

logo_path = Path("assets/Kuziini_logo_negru.png")
if logo_path.exists():
    st.image(str(logo_path), width=300)
else:
    st.markdown("### 🪑 Kuziini | Configurator")

st.markdown("### Adauga Devize nou")

nume_client = st.text_input("Nume client", value=st.session_state.get("nume_client", ""))
telefon_client = st.text_input("Telefon client", value=st.session_state.get("telefon_client", ""))

poza = st.file_uploader("Încarcă o imagine (jpg/png)", type=["jpg", "png"])
if poza:
    with st.spinner("🔍 Se extrag dimensiunile din imagine..."):
        dim_text = extrage_dimensiuni_din_imagine(poza)
        time.sleep(1)
        if dim_text and "x" in dim_text:
            try:
                h, L, a = dim_text.strip().split("x")
                st.session_state["inaltime"] = h
                st.session_state["latime"] = L
                st.session_state["adancime"] = a
                st.success(f"Dimensiuni extrase: {dim_text}")
            except:
                st.warning("⚠️ Format necunoscut.")

col1, col2, col3 = st.columns(3)
with col1:
    inaltime = st.text_input("Înălțime (mm)", value=st.session_state.get("inaltime", ""))
with col2:
    latime = st.text_input("Lățime (mm)", value=st.session_state.get("latime", ""))
with col3:
    adancime = st.text_input("Adâncime (mm)", value=st.session_state.get("adancime", ""))

descriere = st.text_area("Descriere corp mobilier", height=150, value=st.session_state.get("descriere", ""))

st.session_state.update({
    "inaltime": inaltime,
    "latime": latime,
    "adancime": adancime,
    "descriere": descriere,
    "nume_client": nume_client,
    "telefon_client": telefon_client
})

dimensiuni = f"{inaltime}x{latime}x{adancime}"

col_db, col_val = st.columns([2, 1])
try:
    df = pd.read_csv("Accesorii.csv", encoding="latin1")
    col_db.success("Baza de date a fost încărcată cu succes.")
except Exception as e:
    col_db.error(f"Eroare: {e}")
    st.stop()

# 📊 Contor devize generate
istoric_json = [f for f in os.listdir("output/istoric") if f.endswith(".json")]
contor = len(istoric_json)
col_val.info(f"📊 Devize generate: {contor}")

deviz_df = pd.DataFrame()
total = 0.0

if st.button("🔧 Generează deviz"):
    with st.spinner("Se generează devizul..."):
        raspuns, deviz_df = genereaza_deviz_AI(descriere, dimensiuni, df)
        poza_path = None
        if poza:
            ext = Path(poza.name).suffix
            poza_path = f"assets/uploads/{nume_client.replace(' ', '')}_{int(time.time())}{ext}"
            Path("assets/uploads").mkdir(parents=True, exist_ok=True)
            with open(poza_path, "wb") as f:
                f.write(poza.getbuffer())

        pdf_path, total, nume_fisier_base = export_excel_pdf(
            deviz_df, descriere, nume_client, dimensiuni, telefon_client, poza_path)

        st.success("✅ Devizul a fost generat cu succes!")
        st.info(f"💰 Total deviz generat: {total:.2f} lei")

        with open(pdf_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(pdf_path)}">📥 Descarcă PDF</a>'
            st.markdown(href, unsafe_allow_html=True)

if not deviz_df.empty and st.button("👁️ Afișează devizul în aplicație"):
    st.dataframe(deviz_df)
    try:
        total_vizual = pd.to_numeric(deviz_df["Total"], errors="coerce").sum()
        st.success(f"💵 Total vizual deviz: {total_vizual:.2f} lei")
    except:
        st.warning("⚠️ Nu am putut calcula totalul vizual.")

# 📂 Istoric + buton regenerare cu precompletare
st.markdown("### 📂 Istoric devize existente")
json_files = sorted([f for f in os.listdir("output/istoric") if f.endswith(".json")])
select = st.selectbox("Selectează un deviz vechi", options=json_files if json_files else ["-"])

if select != "-" and select:
    path_json = os.path.join("output/istoric", select)
    with open(path_json, encoding="utf-8") as f:
        meta = json.load(f)
        st.markdown(f"**🔖 {select[:-5]}**")
        st.markdown(f"👤 Client: {meta.get('nume_client', '-')}")
        st.markdown(f"📏 Dimensiuni: {meta.get('dimensiuni', '-')}")
        st.markdown(f"✍️ Descriere: {meta.get('descriere', '-')}")
        st.markdown(f"💰 Total: {meta.get('valoare_total', 0):.2f} lei")
        if meta.get("poza_path") and os.path.exists(meta["poza_path"]):
            st.image(meta["poza_path"], width=200)

        if st.button("✏️ Folosește ca șablon"):
            st.session_state["nume_client"] = meta.get("nume_client", "")
            st.session_state["telefon_client"] = meta.get("telefon_client", "")
            dims = meta.get("dimensiuni", "x").split("x")
            if len(dims) == 3:
                st.session_state["inaltime"], st.session_state["latime"], st.session_state["adancime"] = dims
            st.session_state["descriere"] = meta.get("descriere", "")
            st.rerun()
        