import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io

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
except Exception as e:
    st.error("API Key not found in Streamlit Secrets.")

# --- PRODUCTION INTERFACE ---
st.title("Cine Lab: Production Factory")
st.markdown("---")

col_in, col_out = st.columns([1, 1.5], gap="large")

with col_in:
    st.subheader("JSON Recipe")
    json_input = st.text_area("Paste technical data:", height=450)
    generate_btn = st.button("RUN PRODUCTION")
    
    # DEBUG: Mevcut modelleri listele (Hata alırsak kontrol için)
    if st.checkbox("Show Available Models (Debug)"):
        models = [m.name for m in genai.list_models()]
        st.write(models)

with col_out:
    st.subheader("Factory Output")
    
    if generate_btn and json_input:
        try:
            recipe = json.loads(json_input)
            
            # ANTI-PLASTIC ENGINE
            realism = "photorealistic, visible skin pores, natural skin texture, subtle imperfections, 8k raw quality, no airbrushing."
            master_prompt = f"Professional Fine Art Photography, {recipe.get('style', '')}, {recipe.get('camera', '')}, {recipe.get('lens', '')}, {realism}"

            with st.spinner("Factory is rendering..."):
                # ÇÖZÜM: ImageGenerationModel'i güvenli bir şekilde çağırıyoruz
                try:
                    from google.generativeai import ImageGenerationModel
                    # Model ismini 'imagen-3.0-generate-001' olarak deniyoruz
                    model = ImageGenerationModel("imagen-3.0-generate-001")
                    
                    response = model.generate_images(
                        prompt=master_prompt,
                        number_of_images=1,
                        safety_filter_level="block_only_high",
                        person_generation="allow_adult",
                        aspect_ratio="1:1"
                    )
                    
                    if response.images:
                        image = response.images[0]._pil_image #
                        st.image(image, use_container_width=True)
                        
                        buf = io.BytesIO()
                        image.save(buf, format="PNG")
                        st.download_button("DOWNLOAD RAW", data=buf.getvalue(), file_name="output.png")
                    else:
                        st.warning("Production halted by safety filters.")
                        
                except ImportError:
                    st.error("SDK version error. Please ensure requirements.txt has google-generativeai>=0.8.3")
                except Exception as inner_e:
                    st.error(f"Model Error: {inner_e}")
                    st.info("Check 'Show Available Models' to see if 'imagen-3.0-generate-001' is listed.")

        except json.JSONDecodeError:
            st.error("Error: Invalid JSON.")
        except Exception as e:
            st.error(f"Factory Halted: {e}")
    else:
        st.info("System Standby. Awaiting recipe.")
