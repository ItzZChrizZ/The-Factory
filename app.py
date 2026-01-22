import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Cine Lab: Production Factory", layout="wide")

# --- AUTO-THEME INDUSTRIAL UI ---
st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    header {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    @media (prefers-color-scheme: dark) {{
        .stApp {{ background-color: #222121; color: #F9FEFF; }}
        .stTextArea textarea {{ background-color: #161b22; color: #F9FEFF; border: 1px solid #30363d; }}
        h1, h2, h3 {{ color: #CCD4D7; }}
        .stButton button {{ background-color: #CCD4D7; color: #222121; }}
    }}
    @media (prefers-color-scheme: light) {{
        .stApp {{ background-color: #F9FEFF; color: #222121; }}
        .stTextArea textarea {{ background-color: #FFFFFF; color: #222121; border: 1px solid #E0E0E0; }}
        h1, h2, h3 {{ color: #F7BE14; }}
        .stButton button {{ background-color: #F7BE14; color: #F9FEFF; }}
    }}
    .stButton button {{ border-radius: 4px; font-weight: 700; width: 100%; height: 4em; text-transform: uppercase; letter-spacing: 2px; }}
    </style>
    """, unsafe_allow_html=True)

# --- SECURE CONNECTION & MODEL SETUP ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Imagen 3'ün en kararlı üretim ismi
    MODEL_ID = "imagen-3.0-generate-001" 
except Exception as e:
    st.error("Configuration Error: Check your API Secrets.")

# --- INTERFACE ---
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
            realism = (
                "photorealistic, visible skin pores, natural skin texture, "
                "subtle imperfections, no airbrushing, high-frequency details, "
                "8k raw sensor quality, unedited look, natural lighting falloff."
            )
            
            master_prompt = (
                f"Professional Fine Art Photography, {recipe.get('style', 'high-end')}, "
                f"Shot on {recipe.get('camera', 'medium format')}, "
                f"Lens: {recipe.get('lens', 'prime')}, "
                f"Lighting: {recipe.get('lighting', 'cinematic')}, "
                f"Shadow depth: {recipe.get('shadow_density', 50)}%, {realism}"
            )

            with st.spinner("Factory is rendering..."):
                # GÜNCEL METOT: ImageGenerationModel kullanımı
                # Eğer kütüphanen güncelse bu özellik çalışacaktır
                from google.generativeai import ImageGenerationModel
                
                img_model = ImageGenerationModel(MODEL_ID)
                response = img_model.generate_images(
                    prompt=master_prompt,
                    number_of_images=1,
                    safety_filter_level="block_only_high",
                    person_generation="allow_adult", # Sanatsal özgürlük için
                    aspect_ratio="1:1"
                )
                
                if response.images:
                    # Gelen görseli PIL formatına çevirip gösteriyoruz
                    image = response.images[0]._pil_image
                    st.image(image, use_container_width=True)
                    
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button("DOWNLOAD RAW OUTPUT", data=buf.getvalue(), file_name="production.png", mime="image/png")
                else:
                    st.warning("Production halted: Content flagged by safety filters.")
                    
        except json.JSONDecodeError:
            st.error("Error: Invalid JSON.")
        except AttributeError:
            st.error("Error: 'ImageGenerationModel' not found. Please update google-generativeai to 0.8.3 or higher.")
        except Exception as e:
            st.error(f"Factory Halted: {e}")
            st.info("Tip: Verify 'Imagen 3' access in your Google AI Studio account.")
    else:
        st.info("System Standby. Awaiting recipe.")
