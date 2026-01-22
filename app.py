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
    # Listenizdeki en stabil model ismi
    MODEL_ID = "imagen-4.0-generate-001" 
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
            
            # ANTI-PLASTIC & REALISM ENGINE (Cine Lab Standard)
            realism = (
                "photorealistic, visible skin pores, natural skin texture, "
                "no digital smoothing, authentic lens grain, 8k raw quality, "
                "natural lighting falloff, realistic highlights."
            )
            
            master_prompt = (
                f"Professional Photography, style: {recipe.get('style', 'cinematic')}, "
                f"Shot on {recipe.get('camera', 'full-frame')}, "
                f"Lens: {recipe.get('lens', '85mm prime')}, "
                f"Lighting: {recipe.get('lighting', 'studio')}, {realism}"
            )

            with st.spinner("Imagen 4.0 is rendering..."):
                # GÜNCEL ÜRETİM METODU
                from google.generativeai import ImageGenerationModel
                model = ImageGenerationModel(MODEL_ID)
                
                response = model.generate_images(
                    prompt=master_prompt,
                    number_of_images=1,
                    safety_filter_level="block_only_high",
                    person_generation="allow_adult", # Sanatsal özgürlük için
                    aspect_ratio="1:1"
                )
                
                if response.images:
                    # Görseli göster ve kaydet
                    image = response.images[0]._pil_image
                    st.image(image, use_container_width=True)
                    
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button("DOWNLOAD RAW", data=buf.getvalue(), file_name="output.png")
                else:
                    st.warning("Production halted by safety filters.")

        except ImportError:
            st.error("SDK Error: Please perform a 'Reboot' from the Streamlit Cloud dashboard.")
        except Exception as e:
            if "429" in str(e):
                st.error("Quota Exceeded: Please wait 60 seconds and try again.")
            else:
                st.error(f"Factory Halted: {e}")
    else:
        st.info("System Standby. Awaiting recipe.")
