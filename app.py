import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import io
import json
from PIL import Image

# --- 1. SETUP & PAGE CONFIG ---
st.set_page_config(page_title="FactoryIR", layout="wide")

# CSS: Gerçek Tek Sayfa (One-Page) Deneyimi İçin Sıkılaştırma
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { padding-top: 0rem; }
    footer {visibility: hidden;}
    .stTextArea textarea { font-family: 'JetBrains Mono', monospace; background-color: #161b22; color: #e6edf3; height: 350px !important; }
    /* Görselin ekrana sığması için max-height ayarı */
    .stImage img { max-height: 65vh; object-fit: contain; border-radius: 10px; }
    .stButton button { height: 3em; font-weight: bold; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API CONFIG (Via Streamlit Secrets) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Error: GOOGLE_API_KEY not found in secrets.")
    st.stop()

# --- 3. 🧠 THE LOGIC BRIDGE (100% FAITHFUL) ---
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
                - NEW DIRECTION: Convert the 'leaning' pose into a strong, self-supporting HIGH-FASHION STANDING stance.
                - CRITICAL RETENTION: Maintain: "Hands tucked in pockets", "Slightly tilted head", "stoic gaze".
                - NO FURNITURE: No blocks, no props.
                """

        refined_prompt = f"ACT AS: Professional Fashion Director.\n{json.dumps(data)}\n{framing_rules}\n{pose_rules}\n- RENDER: Invisible gear.\n- STYLE: Editorial."
        return refined_prompt
    except: return raw_json_prompt

# --- 4. SAFETY & EXTRACTION (100% FAITHFUL) ---
no_filter_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

def safe_extract_response(response):
    try:
        parts = response.parts if hasattr(response, 'parts') else response.candidates[0].content.parts
        for part in parts:
            if hasattr(part, 'inline_data') and part.inline_data.mime_type.startswith('image/'):
                img_bytes = part.inline_data.data
                return (Image.open(io.BytesIO(img_bytes)), img_bytes), part.inline_data.mime_type
            if hasattr(part, 'text') and part.text: return part.text, "text/plain"
        return None, None
    except: return None, None

# --- 5. UI LAYOUT & EXECUTION ---
st.title("FactoryIR")

# API'den canlı model listesini çekme
@st.cache_data
def get_live_models():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # 3.0 modellerini başa getir
        models.sort(key=lambda x: "3.0" in x or "3-pro" in x, reverse=True)
        return models
    except:
        return ["models/gemini-1.5-flash"]

available_models = get_live_models()

# Split Layout (Fixed width for one-page feel)
col_left, col_right = st.columns([1, 1], gap="medium")

with col_left:
    st.write("### Input")
    user_prompt = st.text_area("CineLab JSON:", placeholder="Paste JSON here...", height=400)
    
    # Model seçimi ve Buton alt alta
    selected_model = st.selectbox("Select Active Model:", available_models)
    generate_btn = st.button("🚀 GENERATE RENDER", type="primary", use_container_width=True)

with col_right:
    st.write("### Output")
    if generate_btn and user_prompt:
        try:
            with st.spinner("FactoryIR Engine Rendering..."):
                final_prompt = apply_logic_bridge(user_prompt)
                model = genai.GenerativeModel(selected_model)
                response = model.generate_content(final_prompt, safety_settings=no_filter_settings)
                res, mime = safe_extract_response(response)

            if isinstance(res, tuple):
                img_obj, img_bytes = res
                # Görseli göster
                st.image(img_obj, use_container_width=True)
                # Kaydet butonunu görselin ALTINA koy
                st.download_button("💾 DOWNLOAD RENDER", data=img_bytes, file_name="factory_render.png", mime=mime, use_container_width=True)
            elif res:
                st.info(res)
            else:
                st.error("No image generated.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    elif not generate_btn:
        st.info("Awaiting CineLab JSON...")
