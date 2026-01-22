import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Cine Lab: Production Factory", layout="wide")

# Theme Selection (Moved from sidebar to main area for a cleaner look)
is_light_mode = st.toggle("Light Mode", value=False)

if is_light_mode:
    main_bg, main_txt, header_col, card_bg, border_col = "#F9FEFF", "#222121", "#F7BE14", "#FFFFFF", "#E0E0E0"
else:
    main_bg, main_txt, header_col, card_bg, border_col = "#222121", "#F9FEFF", "#CCD4D7", "#161b22", "#30363d"

# Custom CSS (No Sidebar Version)
st.markdown(f"""
    <style>
    /* Remove sidebar padding */
    [data-testid="stSidebar"] {{ display: none; }}
    .stApp {{ background-color: {main_bg}; color: {main_txt}; }}
    
    /* Text Area Styling */
    .stTextArea textarea {{ 
        background-color: {card_bg}; 
        color: {main_txt}; 
        border: 1px solid {border_col}; 
        border-radius: 8px;
    }}
    
    /* Headers & Text */
    h1, h2, h3 {{ color: {header_col}; font-family: 'Inter', sans-serif; }}
    
    /* Button Styling */
    .stButton button {{ 
        background-color: {header_col}; 
        color: {main_bg}; 
        border-radius: 4px; 
        font-weight: 600; 
        width: 100%; 
        border: none; 
        height: 3.5em;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .stButton button:hover {{ 
        background-color: {main_txt}; 
        color: {main_bg}; 
    }}
    </style>
    """, unsafe_allow_html=True)

# --- SECURE API CONNECTION ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('imagen-3') # Nano Banana / Imagen 3
except Exception as e:
    st.error("API Key not found or invalid in Secrets.")

# --- MAIN INTERFACE ---
st.title("Cine Lab: Production Factory")
st.markdown("---")

col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.subheader("JSON Recipe")
    json_input = st.text_area("Paste your Cine Lab output here:", height=400, placeholder='{"camera": "85mm", ...}')
    
    generate_btn = st.button("GENERATE")

with col2:
    st.subheader("Production Output")
    
    if generate_btn and json_input:
        try:
            recipe = json.loads(json_input)
            
            # Factory Logic: Converting JSON to technical prompt
            raw_prompt = f"Professional photography, style: {recipe.get('style', 'cinematic')}, " \
                         f"shot on {recipe.get('camera', 'high-end sensor')}, " \
                         f"lens: {recipe.get('lens', '50mm prime')}, " \
                         f"lighting: {recipe.get('lighting', 'studio')}, " \
                         f"detail: ultra-realistic, anti-plastic, natural skin texture."

            with st.spinner("Factory is processing with Nano Banana..."):
                response = model.generate_content(raw_prompt)
                image = response.images[0]
                
                st.image(image, use_container_width=True)
                
                # Download Action
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                st.download_button(
                    label="DOWNLOAD IMAGE",
                    data=buf.getvalue(),
                    file_name="production_output.png",
                    mime="image/png"
                )
        except json.JSONDecodeError:
            st.warning("Invalid JSON format. Please check your recipe.")
        except Exception as e:
            st.error(f"Production error: {e}")
    else:
        st.info("Awaiting recipe... Production line ready.")
