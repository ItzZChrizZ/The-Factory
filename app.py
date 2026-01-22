import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Cine Lab: Production Factory", layout="wide")

# --- AUTO-THEME & INDUSTRIAL UI CSS ---
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

    .stButton button {{ 
        border-radius: 4px; font-weight: 700; width: 100%; border: none; height: 4em;
        text-transform: uppercase; letter-spacing: 2px; transition: 0.3s;
    }}
    .stButton button:hover {{ opacity: 0.9; transform: scale(0.99); }}
    </style>
    """, unsafe_allow_html=True)

# --- SECURE API CONNECTION ---
try:
    # API Anahtarını Secrets'tan çek
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # DOĞRU MODEL SINIFI: ImageGenerationModel
    # Model adı genellikle 'imagen-3.0-generate-001' veya 'imagen-3.0-generate-002' olur.
    model_name = "imagen-3.0-generate-001" 
except Exception as e:
    st.error("System Error: API Configuration failed.")

# --- PRODUCTION INTERFACE ---
st.title("Cine Lab: Production Factory")
st.markdown("---")

col_in, col_out = st.columns([1, 1.5], gap="large")

with col_in:
    st.subheader("JSON Recipe")
    json_input = st.text_area("Paste Cine Lab technical data:", height=450, placeholder='{"camera": "85mm", ...}')
    generate_btn = st.button("RUN PRODUCTION")

with col_out:
    st.subheader("Factory Output")
    
    if generate_btn and json_input:
        try:
            recipe = json.loads(json_input)
            
            # ANTI-PLASTIC & REALISM ENGINE
            realism_logic = (
                "raw photography, visible skin pores, natural skin texture, subtle imperfections, "
                "no airbrushing, high-frequency details, authentic lens grain, "
                "physically accurate lighting falloff, 8k raw sensor quality, unedited look."
            )
            
            # Master Prompt
            master_prompt = (
                f"Professional Fine Art Photography, style: {recipe.get('style', 'high-end artistic')}, "
                f"Shot on {recipe.get('camera', 'medium format')}, "
                f"Lens: {recipe.get('lens', 'prime lens')}, "
                f"Lighting: {recipe.get('lighting', 'cinematic lighting')}, "
                f"Shadow depth: {recipe.get('shadow_density', 50)}%, "
                f"Quality focus: {realism_logic}"
            )

            with st.spinner("Nano Banana is rendering the raw file..."):
                # GÜNCEL GÖRSEL ÜRETİM METODU
                imagen_model = genai.ImageGenerationModel(model_name)
                response = imagen_model.generate_images(
                    prompt=master_prompt,
                    number_of_images=1,
                    # Güvenlik ayarlarını burada metod içinde yapıyoruz
                    safety_filter_level="block_only_high",
                    person_generation="allow_adult", # Fine Art Nude için kritik
                    aspect_ratio="1:1"
                )
                
                if response.images:
                    image = response.images[0]
                    # Streamlit'te göstermek için PIL Image objesine çeviriyoruz
                    st.image(image._pil_image, use_container_width=True)
                    
                    # Kaydetme butonu
                    buf = io.BytesIO()
                    image._pil_image.save(buf, format="PNG")
                    st.download_button("DOWNLOAD RAW OUTPUT", data=buf.getvalue(), file_name="cine_production.png", mime="image/png")
                else:
                    st.warning("Production halted: No images were generated. Safety filters might be too strict.")
                    
        except json.JSONDecodeError:
            st.error("Error: Input must be a valid JSON format.")
        except Exception as e:
            st.error(f"Factory Halted: {e}")
            st.info("Tip: If model is not found, verify the model name (e.g., 'imagen-3.0-generate-001') in Google AI Studio.")
    else:
        st.info("Production line standby. Please paste a recipe.")
