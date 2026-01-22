import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io
# Güvenlik ve Görsel Modelleri için gerekli kütüphaneler
from google.generativeai import ImageGenerationModel
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Cine Lab: Production Factory", layout="wide")

# --- INDUSTRIAL UI CSS ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    @media (prefers-color-scheme: dark) {
        .stApp { background-color: #222121; color: #F9FEFF; }
        .stTextArea textarea { background-color: #161b22; color: #F9FEFF; border: 1px solid #30363d; border-radius: 8px; }
        h1, h2, h3 { color: #CCD4D7; }
        .stButton button { background-color: #CCD4D7; color: #222121; }
    }
    @media (prefers-color-scheme: light) {
        .stApp { background-color: #F9FEFF; color: #222121; }
        .stTextArea textarea { background-color: #FFFFFF; color: #222121; border: 1px solid #E0E0E0; border-radius: 8px; }
        h1, h2, h3 { color: #F7BE14; }
        .stButton button { background-color: #F7BE14; color: #F9FEFF; }
    }
    .stButton button { border-radius: 4px; font-weight: 700; width: 100%; height: 4em; text-transform: uppercase; letter-spacing: 2px; }
    </style>
    """, unsafe_allow_html=True)

# --- SECURE API SETUP ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # Listenizdeki en kararlı Imagen 3 modeli
    MODEL_ID = "imagen-3.0-generate-001" 
except Exception as e:
    st.error("API Key missing. Please check Streamlit Secrets.")

# --- PRODUCTION INTERFACE ---
st.title("Cine Lab: Production Factory")
st.markdown("---")

col_in, col_out = st.columns([1, 1.5], gap="large")

with col_in:
    st.subheader("JSON Recipe")
    json_input = st.text_area("Paste technical data:", height=450, placeholder='{"camera": "Sony A7R V", ...}')
    generate_btn = st.button("RUN PRODUCTION")

with col_out:
    st.subheader("Factory Output")
    
    if generate_btn and json_input:
        try:
            recipe = json.loads(json_input)
            
            # ANTI-PLASTIC ENGINE (Cine Lab Standartları)
            realism = (
                "photorealistic, visible skin pores, natural skin micro-texture, "
                "no digital airbrushing, high-frequency details, "
                "authentic lens grain, physically accurate lighting falloff, 8k raw sensor quality."
            )
            
            master_prompt = (
                f"Professional Fine Art Photography, style: {recipe.get('style', 'cinematic')}, "
                f"Shot on {recipe.get('camera', 'medium format')}, "
                f"Lens: {recipe.get('lens', 'prime lens')}, "
                f"Lighting: {recipe.get('lighting', 'studio lighting')}, {realism}"
            )

            with st.spinner("Imagen 3.0 is rendering the raw file..."):
                # --- DOĞRU METOT: ImageGenerationModel ÇAĞRISI ---
                # Artık generate_content değil, generate_images kullanıyoruz
                model = ImageGenerationModel(MODEL_ID)
                
                response = model.generate_images(
                    prompt=master_prompt,
                    number_of_images=1,
                    safety_filter_level="block_only_high",
                    person_generation="allow_adult", # Fine Art Nude için izin
                    aspect_ratio="1:1"
                )
                
                if response.images:
                    # Gelen görsel PIL formatında olduğu için doğrudan gösteriyoruz
                    image = response.images[0]._pil_image
                    st.image(image, use_container_width=True)
                    
                    # Kaydetme Butonu
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button("DOWNLOAD RAW", data=buf.getvalue(), file_name="factory_output.png", mime="image/png")
                else:
                    st.warning("Production halted: Safety engine flagged the recipe.")

        except Exception as e:
            # 429 hatası (quota) kontrolü
            if "429" in str(e):
                st.error("Quota Exceeded: Lütfen 60 saniye bekleyip tekrar deneyin.")
            else:
                st.error(f"Factory Halted (System Error): {e}")
                st.info("İpucu: Eğer 'cannot import' hatası alırsan 'from google.generativeai import ImageGenerationModel' satırını kontrol et.")
    else:
        st.info("System Standby. Awaiting recipe for production.")
