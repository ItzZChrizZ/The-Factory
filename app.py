import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import io
import json
from PIL import Image
import re

# 1. PAGE CONFIG
st.set_page_config(page_title="FactoryIR", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    div[data-testid="column"] { overflow: hidden; }
    .stTextArea textarea { font-family: 'JetBrains Mono', monospace; }
    .main { padding-top: 2rem; }
    .stButton > button { width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 2. SECRETS & API SETUP
@st.cache_resource
def setup_genai():
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            api_key = st.secrets["GOOGLE_API_KEY"]
            genai.configure(api_key=api_key)
            return True
        return False
    except Exception:
        return False

api_ready = setup_genai()

# 3. MODEL FILTERING FUNCTION
@st.cache_data(ttl=3600) # Cache results for 1 hour to avoid repeated API calls
def get_filtered_models():
    try:
        if not api_ready:
            return ["models/gemini-3.0-pro-latest"] # Fallback if API not ready

        # List models and filter for those supporting generateContent (likely image models)
        all_models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Filter for "gemini-3.0" and above using regex
        # Pattern matches "gemini-" followed by a version number >= 3 (e.g., 3.0, 3.5, 4.0)
        filtered_models = []
        version_pattern = re.compile(r"gemini-(\d+)\.(\d+)")
        
        for m in all_models:
            match = version_pattern.search(m.name)
            if match:
                major_version = int(match.group(1))
                if major_version >= 3:
                    filtered_models.append(m.name)
        
        if not filtered_models:
             # Fallback if no models match >= 3.0
            return ["models/gemini-3.0-pro-latest"] 
            
        return filtered_models
    except Exception as e:
        # Fallback in case of any API error during listing
        # print(f"Error fetching models: {e}") # For debugging
        return ["models/gemini-3.0-pro-latest"]

# 4. SECURITY SETTINGS (100% FAITHFUL)
no_filter_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# 5. THE LOGIC BRIDGE (100% FAITHFUL)
def apply_logic_bridge(raw_json_prompt):
    try:
        data = json.loads(raw_json_prompt)
        recipe = data.get("cinematography_recipe", {})
        lp = recipe.get("phase_4_lighting_physics", {})
        
        for key in ["key_light", "fill_light", "back_light", "setup"]:
            if key in lp:
                lp[key] = lp[key].lower().replace("softbox", "diffused volumetric light source") \
                                         .replace("bounce board", "indirect fill reflection") \
                                         .replace("light stand", "invisible point source") \
                                         .replace("setup", "lighting physics")

        framing_rules = """
        - SHOT TYPE: Extreme Wide Shot (EWS).
        - COMPOSITION: The subject must occupy roughly 60-70% of the vertical frame height.
        - HEADROOM & FOOTROOM: Leave clear empty grey space above the head and below the shoes.
        - NO CROPPING: Full body visible, centered against the seamless cyc wall.
        """

        phase1 = recipe.get("phase_1_subject_retention", {})
        location = phase1.get("environment_override", {}).get("location", "").lower()
        notes = lp.get("director_notes", "").lower()
        original_pose_details = ", ".join(phase1.get("four_by_four_analysis", {}).get("pose", []))

        pose_rules = ""
        if "studio" in location and "leaning" in original_pose_details.lower():
            if not any(word in notes for word in ["chair", "car", "table", "wall", "prop", "object", "block"]):
                pose_rules = f"""
                - POSE CORRECTION (PHYSICS): The subject cannot 'lean' against air.
                - NEW DIRECTION: Convert the 'leaning' pose into a strong, self-supporting HIGH-FASHION STANDING stance. Do not be robotic.
                - CRITICAL RETENTION: You MUST maintain these specific stylistic details from the original request while standing: "Hands tucked in pockets", "Slightly tilted head", "stoic gaze".
                - NO FURNITURE: No blocks, no props. Just the subject standing confidently.
                """

        refined_prompt = f"ACT AS: Professional Fashion Director (Kacper Kasprzyk style).\n{json.dumps(data)}\n{framing_rules}\n{pose_rules}\n- RENDER: 100% Invisible studio equipment.\n- ATMOSPHERE: High-end editorial."
        return refined_prompt
    except: return raw_json_prompt

def safe_extract_response(response):
    try:
        parts = response.parts if hasattr(response, 'parts') else response.candidates[0].content.parts
        for part in parts:
            if hasattr(part, 'inline_data') and part.inline_data.mime_type.startswith('image/'):
                img_bytes = part.inline_data.data
                return (Image.open(io.BytesIO(img_bytes)), img_bytes), part.inline_data.mime_type
            if hasattr(part, 'text') and part.text:
                return part.text, "text/plain"
        return None, None
    except: return None, None

# 6. UI LAYOUT
st.title("FactoryIR")
st.markdown("---")

if not api_ready:
    st.error("🔑 API Key Missing! Please add GOOGLE_API_KEY to your Streamlit Secrets.")
    st.info("Local: Create .streamlit/secrets.toml | Cloud: App Settings > Secrets")
    st.stop()

# Get filtered model list
filtered_models = get_filtered_models()

# Main Interface Split
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.write("### Input")
    user_prompt = st.text_area("CineLab JSON:", height=400, placeholder="Paste your JSON here...")
    
    st.write("### Model Selection")
    # Dropdown for models >= 3.0
    selected_model_name = st.selectbox("Select Model:", filtered_models, label_visibility="collapsed")
    
    generate_btn = st.button("🚀 GENERATE RENDER", type="primary", use_container_width=True)

with col_right:
    st.write("### Output")
    if generate_btn and user_prompt:
        try:
            # Using spinner instead of status for a cleaner look in the column
            with st.spinner("FactoryIR Engine Running..."):
                # 1. Apply Logic Bridge
                final_prompt = apply_logic_bridge(user_prompt)
                
                # 2. Request Render
                model = genai.GenerativeModel(selected_model_name)
                response = model.generate_content(final_prompt, safety_settings=no_filter_settings)
                
                # 3. Extract Result
                res, mime = safe_extract_response(response)

            if isinstance(res, tuple): # Image returned
                img_obj, img_bytes = res
                # SAVE BUTTON AT THE TOP OF THE IMAGE
                st.download_button("💾 DOWNLOAD IMAGE", data=img_bytes, file_name="render.png", mime=mime, use_container_width=True)
                st.image(img_obj, use_container_width=True)
            elif res:
                st.info(res)
            else:
                st.error("Model could not generate an image.")
                
        except Exception as e:
            st.error(f"Error: {e}")
    elif not generate_btn:
        st.info("Ready for input. The render will appear here.")
