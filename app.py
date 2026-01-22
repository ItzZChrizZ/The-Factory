import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Cine Lab: Production Factory", layout="wide")

# --- AUTO-THEME INDUSTRIAL UI ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    @media (prefers-color-scheme: dark) {
        .stApp { background-color: #222121; color: #F9FEFF; }
        .stTextArea textarea { background-color: #161b22; color: #F9FEFF; border: 1px solid #30363d; }
        h1, h2, h3 { color: #CCD4D7; }
        .stButton button { background-color: #CCD4D7; color: #222121; }
    }
    @media (prefers-color-scheme: light) {
        .stApp { background-color: #F9FEFF; color: #222121; }
        .stTextArea textarea { background-color: #FFFFFF; color: #222121; border: 1px solid #E0E0E0; }
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
    # Listendeki tam ismi kullanıyoruz
    MODEL_NAME = "nano-banana-pro-preview" 
except Exception as e:
    st.error("API Key error. Check Streamlit Secrets.")

# --- PRODUCTION INTERFACE ---
st.title("Cine Lab: Production Factory")
st.markdown("---")

col_in, col_out = st.columns([1, 1.5], gap="large")

with col_in:
    st.subheader("JSON Recipe")
    json_input = st.text_area("Paste technical data:", height=450)
    generate_btn = st.button("RUN PRODUCTION")

with col_out:
    st.subheader("Factory Output")
    
    if generate_btn and json_input:
        try:
            recipe = json.loads(json_input)
            
            # ANTI-PLASTIC ENGINE
            realism = "photorealistic, visible skin pores, natural skin texture, subtle imperfections, 8k raw sensor quality, no airbrushing."
            master_prompt = (
                f"Professional Fine Art Photography, style: {recipe.get('style', 'high-end')}, "
                f"Shot on {recipe.get('camera', 'medium format')}, "
                f"Lens: {recipe.get('lens', 'prime')}, "
                f"Lighting: {recipe.get('lighting', 'cinematic')}, "
                f"Technical details: {realism}"
            )

            with st.spinner("Nano Banana is rendering..."):
                # En sağlam metot: Doğrudan GenerativeModel ile çağırıyoruz
                model = genai.GenerativeModel(MODEL_NAME)
                
                response = model.generate_content(
                    master_prompt,
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    }
                )
                
                # Görseli yanıttan çekme (2026 SDK yapısı)
                found_image = False
                if response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        # Eğer part içinde image verisi varsa
                        if hasattr(part, 'inline_data') and part.inline_data:
                            img_bytes = part.inline_data.data
                            image = Image.open(io.BytesIO(img_bytes))
                            st.image(image, use_container_width=True)
                            
                            buf = io.BytesIO()
                            image.save(buf, format="PNG")
                            st.download_button("DOWNLOAD RAW", data=buf.getvalue(), file_name="output.png")
                            found_image = True
                            break
                        # Bazı sürümlerde doğrudan .image olarak gelir
                        elif hasattr(part, 'image') and part.image:
                            st.image(part.image, use_container_width=True)
                            found_image = True
                            break

                if not found_image:
                    st.warning("Production halted: No image found in response. Possible safety block.")

        except json.JSONDecodeError:
            st.error("Error: Invalid JSON.")
        except Exception as e:
            st.error(f"Factory Halted: {e}")
    else:
        st.info("System Standby. Awaiting recipe.")
