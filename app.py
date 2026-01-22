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
    .stButton button { border-radius: 4px; font-weight: 700; width: 100%; height: 4em; text-transform: uppercase; letter-spacing: 2px; transition: 0.3s; }
    .stButton button:hover { opacity: 0.8; transform: translateY(-1px); }
    </style>
    """, unsafe_allow_html=True)

# --- SECURE API SETUP ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # Senin listendeki en güncel Imagen 4.0 modeli
    MODEL_ID = "imagen-4.0-generate-001" 
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
            
            # ANTI-PLASTIC ENGINE (Cine Lab Standards)
            realism = (
                "photorealistic, visible skin pores, natural skin micro-texture, "
                "subtle imperfections, no digital airbrushing, high-frequency details, "
                "authentic lens grain, physically accurate lighting falloff, 8k raw sensor quality."
            )
            
            master_prompt = (
                f"Professional Fine Art Photography, style: {recipe.get('style', 'cinematic')}, "
                f"Shot on {recipe.get('camera', 'medium format')}, "
                f"Lens: {recipe.get('lens', 'prime lens')}, "
                f"Lighting: {recipe.get('lighting', 'studio lighting')}, {realism}"
            )

            with st.spinner("Imagen 4.0 is processing the raw file..."):
                # GÜNCEL SDK METODU
                from google.generativeai import ImageGenerationModel
                model = ImageGenerationModel(MODEL_ID)
                
                response = model.generate_images(
                    prompt=master_prompt,
                    number_of_images=1,
                    safety_filter_level="block_only_high",
                    person_generation="allow_adult",
                    aspect_ratio="1:1"
                )
                
                if response.images:
                    # PIL formatına çevirip gösteriyoruz
                    image = response.images[0]._pil_image
                    st.image(image, use_container_width=True)
                    
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button("DOWNLOAD RAW", data=buf.getvalue(), file_name="factory_output.png", mime="image/png")
                else:
                    st.warning("Production halted: Safety engine flagged the recipe.")

        except ImportError:
            st.error("SDK Error: Please perform a 'Reboot' from the Streamlit Cloud dashboard.")
        except Exception as e:
            if "429" in str(e):
                st.error("Quota Exceeded: Please wait 60 seconds and try again.")
            else:
                st.error(f"Factory Halted: {e}")
    else:
        st.info("System Standby. Awaiting recipe for production.")
