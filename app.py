import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Cine Lab: Production Factory", layout="wide")

# --- AUTO-THEME INDUSTRIAL CSS ---
# This CSS handles everything: Sidebar removal, No icons, and Automatic light/dark switching.
st.markdown(f"""
    <style>
    /* 1. Hide Sidebar & Streamlit Branding */
    [data-testid="stSidebar"] {{ display: none; }}
    header {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    
    /* 2. Automatic Theme Detection (No Buttons Needed) */
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

    /* 3. Production Button Styling */
    .stButton button {{ 
        border-radius: 4px; 
        font-weight: 700; 
        width: 100%; 
        border: none; 
        height: 3.5em;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: 0.3s;
    }}
    
    .stButton button:hover {{ 
        opacity: 0.9;
        transform: scale(0.99);
    }}

    /* Clean Input Fields */
    .stTextArea label {{ font-size: 1.1rem; font-weight: 600; opacity: 0.8; }}
    </style>
    """, unsafe_allow_html=True)

# --- SECURE API CONNECTION ---
try:
    # Use the key you saved in Streamlit Secrets
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('imagen-3') 
except Exception as e:
    st.error("Critical System Error: Check API Secrets.")

# --- PRODUCTION INTERFACE ---
st.title("Cine Lab: Production Factory")
st.markdown("---")

col_input, col_output = st.columns([1, 1.5], gap="large")

with col_input:
    st.subheader("JSON Recipe")
    json_input = st.text_area(
        "Input technical data:", 
        height=450, 
        placeholder='{"camera": "85mm", "lighting": "low key", "shadows": 80...}'
    )
    
    # The only button - purely functional
    generate_btn = st.button("GENERATE")

with col_output:
    st.subheader("Production Output")
    
    if generate_btn and json_input:
        try:
            recipe = json.loads(json_input)
            
            # Internal Factory Logic: Translating JSON to High-End Photography Language
            # This is where we ensure the "Anti-Plastic" look
            master_prompt = (
                f"High-end professional photography, style: {recipe.get('style', 'cinematic')}, "
                f"camera: {recipe.get('camera', 'professional full-frame')}, "
                f"lens: {recipe.get('lens', 'prime lens')}, "
                f"lighting setup: {recipe.get('lighting', 'studio lighting')}, "
                f"technical quality: natural skin texture, 8k resolution, realistic details, "
                f"no plastic skin, natural lighting falloff."
            )

            with st.spinner("Factory processing..."):
                response = model.generate_content(master_prompt)
                image = response.images[0]
                
                st.image(image, use_container_width=True)
                
                # Simple Download Button
                buf = io.BytesIO()
                image.save(buf, format="PNG")
                st.download_button(
                    label="DOWNLOAD IMAGE",
                    data=buf.getvalue(),
                    file_name="cine_lab_factory_output.png",
                    mime="image/png"
                )
        except json.JSONDecodeError:
            st.error("Error: Invalid JSON input format.")
        except Exception as e:
            st.error(f"Production Halted: {e}")
    else:
        st.info("System Ready. Paste a recipe to start production.")
