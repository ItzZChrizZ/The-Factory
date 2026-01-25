import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import io
import json
from PIL import Image

# --- 1. SETUP & STRICT UI LOCKING ---
st.set_page_config(page_title="FactoryIR", layout="wide", initial_sidebar_state="collapsed")

# CSS: Ekranı dikeyde kilitleyen ve scroll'u yok eden "Finesse" katmanı
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { padding-top: 0rem; overflow: hidden; }
    .stTextArea textarea { font-family: 'JetBrains Mono', monospace; height: 45vh !important; }
    /* Görselin ekrana sığması için dikey kilit */
    .stImage img { max-height: 60vh !important; width: auto; object-fit: contain; margin: 0 auto; display: block; border-radius: 8px; }
    .stButton button { height: 3.5em; font-weight: bold; }
    div[data-testid="column"] { height: 90vh; }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. API CONFIG ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("API Key missing in secrets.")
    st.stop()

# --- 3. THE LOGIC BRIDGE (100% FAITHFUL) ---
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
        - NO CROPPING: Full body visible.
        """

        phase1 = recipe.get("phase_1_subject_retention", {})
        location = phase1.get("environment_override", {}).get("location", "").lower()
        original_pose_details = ", ".join(phase1.get("four_by_four_analysis", {}).get("pose", []))

        pose_rules = ""
        if "studio" in location and "leaning" in original_pose_details.lower():
            pose_rules = """
            - POSE CORRECTION: Self-supporting high-fashion standing stance. No leaning against air.
            - RETENTION: "Hands in pockets", "Slightly tilted head", "stoic gaze".
            """

        # Modelin metin üretmesini zorlaştıran, direkt görsel üretimini tetikleyen prompt
        return f"IMAGE_GENERATION_TASK: {json.dumps(data)}\n{framing_rules}\n{pose_rules}\nRENDER: 100% Photo-realistic, invisible gear, Kacper Kasprzyk style."
    except: return raw_json_prompt

# --- 4. SAFETY & EXTRACTION ---
no_filter_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

def safe_extract_response(response):
    try:
        # Önce görsel var mı ona bak, metni görmezden gel
        parts = response.parts if hasattr(response, 'parts') else response.candidates[0].content.parts
        for part in parts:
            if hasattr(part, 'inline_data') and part.inline_data.mime_type.startswith('image/'):
                return (Image.open(io.BytesIO(part.inline_data.data)), part.inline_data.data), part.inline_data.mime_type
        return None, None
    except: return None, None

# --- 5. UI LAYOUT ---
st.title("FactoryIR")

@st.cache_data
def get_live_models():
    try: return [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except: return ["models/gemini-1.5-flash"]

available_models = get_live_models()

col_in, col_out = st.columns([1, 1], gap="large")

with col_in:
    st.write("### Input")
    user_prompt = st.text_area("CineLab JSON Input:", placeholder="Paste JSON...", label_visibility="collapsed")
    
    st.write("### Settings")
    selected_model = st.selectbox("Model:", available_models, label_visibility="collapsed")
    gen_btn = st.button("🚀 GENERATE RENDER", type="primary", use_container_width=True)

with col_out:
    st.write("### Output")
    if gen_btn and user_prompt:
        try:
            with st.spinner("Rendering..."):
                model = genai.GenerativeModel(selected_model)
                final_prompt = apply_logic_bridge(user_prompt)
                response = model.generate_content(final_prompt, safety_settings=no_filter_settings)
                res, mime = safe_extract_response(response)

            if res:
                img_obj, img_bytes = res
                st.image(img_obj, use_container_width=True)
                # İNDİR BUTONU GÖRSELİN ALTINDA
                st.download_button("💾 DOWNLOAD RENDER", data=img_bytes, file_name="factory_render.png", mime=mime, use_container_width=True)
            else:
                st.error("Model did not return an image. Check if the selected model supports image generation.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.info("System ready. Waiting for JSON...")
