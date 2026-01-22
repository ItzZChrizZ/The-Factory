import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io
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
    # Listenizdeki en güçlü ve stabil model
    MODEL_ID = "imagen-4.0-generate-001" 
except Exception as e:
    st.error("API Key error. Check Streamlit Secrets.")

# --- PRODUCTION INTERFACE ---
st.title("Cine Lab: Production Factory")
st.markdown("---")

col_in, col_out = st.columns([1, 1.5], gap="large")

with col_in:
    st.subheader("JSON Recipe")
    json_input = st.text_area("Paste technical data:", height=450, placeholder='{"camera": "85mm", ...}')
    generate_btn = st.button("RUN PRODUCTION")

with col_out:
    st.subheader("Factory Output")
    
    if generate_btn and json_input:
        try:
            recipe = json.loads(json_input)
            
            # ANTI-PLASTIC ENGINE
            realism = (
                "photorealistic, authentic skin texture, visible pores, "
                "no digital smoothing, cinematic lighting, 8k raw resolution, "
                "natural highlights, real lens grain."
            )
            
            master_prompt = (
                f"Professional Photography, style: {recipe.get('style', 'high-end')}, "
                f"Shot on {recipe.get('camera', 'medium format')}, "
                f"Lens: {recipe.get('lens', 'prime lens')}, "
                f"Lighting: {recipe.get('lighting', 'studio')}, {realism}"
            )

            with st.spinner("Factory is rendering with Imagen 4.0..."):
                # ÇÖZÜM: Hiçbir özel sınıfa (ImageGenerationModel vb.) gerek duymayan ana metod
                model = genai.GenerativeModel(MODEL_ID)
                
                # Görsel üretimini standart içerik üretimi üzerinden tetikliyoruz
                response = model.generate_content(
                    master_prompt,
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    }
                )
                
                # Görsel verisini blob (byte) olarak çekiyoruz
                img_found = False
                if response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        # Blob verisini kontrol et (inline_data)
                        if hasattr(part, 'inline_data') and part.inline_data:
                            img_bytes = part.inline_data.data
                            image = Image.open(io.BytesIO(img_bytes))
                            st.image(image, use_container_width=True)
                            
                            buf = io.BytesIO()
                            image.save(buf, format="PNG")
                            st.download_button("DOWNLOAD RAW OUTPUT", data=buf.getvalue(), file_name="production.png")
                            img_found = True
                            break
                
                if not img_found:
                    st.warning("Production halted: The safety engine or model response did not return a valid image.")

        except Exception as e:
            # 429 hatası gelirse kullanıcıyı bilgilendir
            if "429" in str(e):
                st.error("Quota Exceeded (429): Please wait 60 seconds. The factory is cooling down.")
            else:
                st.error(f"Factory Halted (System Error): {e}")
    else:
        st.info("System Standby. Awaiting recipe for production.")
