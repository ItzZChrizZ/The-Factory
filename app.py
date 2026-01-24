import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Cine Lab: Production Factory", layout="wide")

# --- CSS ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    @media (prefers-color-scheme: dark) {
        .stApp { background-color: #222121; color: #F9FEFF; }
        .stTextArea textarea { background-color: #161b22; color: #F9FEFF; border: 1px solid #30363d; border-radius: 8px; }
        .stButton button { background-color: #CCD4D7; color: #222121; }
    }
    @media (prefers-color-scheme: light) {
        .stApp { background-color: #F9FEFF; color: #222121; }
        .stTextArea textarea { background-color: #FFFFFF; color: #222121; border: 1px solid #E0E0E0; border-radius: 8px; }
        .stButton button { background-color: #F7BE14; color: #F9FEFF; }
    }
    .stButton button { border-radius: 4px; font-weight: 700; width: 100%; height: 4em; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- API BAĞLANTISI (GÜVENLİ MOD) ---
api_status = "ok"
try:
    # Secrets kontrolü
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        api_status = "missing_key"
except Exception as e:
    api_status = f"error: {str(e)}"

# Model ID (Listendeki en sağlam model)
MODEL_ID = "imagen-3.0-generate-001"

# --- ARAYÜZ ---
st.title("Cine Lab: Production Factory")
st.markdown("---")

if api_status == "missing_key":
    st.error("🚨 HATA: API Key bulunamadı! 'Secrets' ayarlarında 'GEMINI_API_KEY' ismini kullandığından emin ol.")
elif api_status.startswith("error"):
    st.error(f"🚨 SİSTEM HATASI: {api_status}")

col_in, col_out = st.columns([1, 1.5], gap="large")

with col_in:
    st.subheader("JSON Recipe")
    json_input = st.text_area("Paste technical data:", height=450, placeholder='{"camera": "Sony A7R V", ...}')
    generate_btn = st.button("RUN PRODUCTION")

with col_out:
    st.subheader("Factory Output")
    
    if generate_btn and json_input:
        if api_status != "ok":
            st.error("API Bağlantısı olmadığı için üretim yapılamıyor.")
        else:
            try:
                recipe = json.loads(json_input)
                
                # --- IMPORT KONTROLÜ (Çökme Engelleyici) ---
                # Import işlemini butonun içine taşıdık ki uygulama açılırken patlamasın.
                try:
                    from google.generativeai import ImageGenerationModel
                except ImportError:
                    st.error("⚠️ KRİTİK HATA: Kütüphane güncellenemedi.")
                    st.info("Lütfen Streamlit panelinden 'Reboot App' yapın. (Requirements.txt: google-generativeai>=0.8.3 olmalı)")
                    st.stop()

                realism = "photorealistic, visible pores, natural texture, 8k raw quality, no airbrushing."
                master_prompt = f"Professional Photo, {recipe.get('style','')}, {recipe.get('camera','')}, {recipe.get('lens','')}, {realism}"

                with st.spinner(f"Rendering with {MODEL_ID}..."):
                    model = ImageGenerationModel(MODEL_ID)
                    
                    response = model.generate_images(
                        prompt=master_prompt,
                        number_of_images=1,
                        safety_filter_level="block_only_high",
                        person_generation="allow_adult",
                        aspect_ratio="1:1"
                    )
                    
                    if response.images:
                        image = response.images[0]._pil_image
                        st.image(image, use_container_width=True)
                        
                        buf = io.BytesIO()
                        image.save(buf, format="PNG")
                        st.download_button("DOWNLOAD RAW", data=buf.getvalue(), file_name="output.png", mime="image/png")
                    else:
                        st.warning("Üretim durduruldu (Güvenlik filtresi).")

            except Exception as e:
                st.error(f"ÜRETİM HATASI: {e}")
                if "404" in str(e):
                    st.info("Model bulunamadı. API Key'in 'Imagen 3' yetkisi olduğundan emin ol.")
    else:
        st.info("Sistem Hazır.")
