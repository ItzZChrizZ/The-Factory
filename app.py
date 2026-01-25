import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import io
import json
from PIL import Image

# --- 1. SETUP & PAGE CONFIG ---
st.set_page_config(page_title="FactoryIR", layout="wide")

# CSS: Sidebar'ı gizle, Fontları ayarla ve Paddingleri optimize et
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .stTextArea textarea { font-family: 'JetBrains Mono', monospace; background-color: #161b22; color: #e6edf3; }
    .stButton button { height: 3em; font-weight: bold; border-radius: 8px; }
    h1 { margin-bottom: 0.5rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API CONFIG (Via Streamlit Secrets) ---
# Secrets kontrolü ve API kurulumu
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Error: GOOGLE_API_KEY not found in secrets. Please check your .streamlit/secrets.toml file.")
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
                - NEW DIRECTION: Convert the 'leaning' pose into a strong, self-supporting HIGH-FASHION STANDING stance. Do not be robotic.
                - CRITICAL RETENTION: You MUST maintain these specific stylistic details from the original request while standing: "Hands tucked in pockets", "Slightly tilted head", "stoic gaze".
                - NO FURNITURE: No blocks, no props. Just the subject standing confidently.
                """

        refined_prompt = f"""
        ACT AS: Professional Fashion Director of Photography (Kacper Kasprzyk style).
        
        {json.dumps(data)}
        
        STRICT EXECUTION DIRECTIVES:
        {framing_rules}
        {pose_rules}
        - RENDER RULE: 100% Invisible studio equipment. Only render the light effect.
        - ATMOSPHERE: High-end, minimalist, moody editorial feel.
        """
        return refined_prompt
    except Exception:
        return raw_json_prompt

# --- 4. SAFETY & EXTRACTION (CORRECTED) ---
no_filter_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

def safe_extract_response(response):
    """
    Returns: ((img_obj, img_bytes), text_content, mime_type)
    """
    try:
        # Candidate kontrolü
        if not hasattr(response, 'candidates') or not response.candidates:
            return None, "No candidates returned", None
            
        parts = response.parts if hasattr(response, 'parts') else response.candidates[0].content.parts
        
        for part in parts:
            # GÖRSEL YAKALAMA
            if hasattr(part, 'inline_data') and part.inline_data.mime_type.startswith('image/'):
                img_bytes = part.inline_data.data
                img = Image.open(io.BytesIO(img_bytes))
                return (img, img_bytes), None, part.inline_data.mime_type
            
            # TEXT YAKALAMA (Hata mesajı veya modelin reddi olabilir)
            if hasattr(part, 'text') and part.text:
                return None, part.text, "text/plain"
                
        return None, None, None
    except Exception as e: 
        return None, str(e), None

# --- 5. UI LAYOUT & EXECUTION ---
st.title("FactoryIR")

@st.cache_data
def get_available_models():
    try:
        # Sadece generateContent destekleyenleri listele
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Eğer liste boşsa veya istenen modeller yoksa manuel ekleme yapabiliriz (Opsiyonel)
        return models
    except:
        return ["models/gemini-1.5-pro-latest"] # Fallback

available_models = get_available_models()

# Layout: İki Sütun
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.write("### Input")
    user_prompt = st.text_area("CineLab JSON Input:", height=380, placeholder="Paste JSON code here...")
    
    st.write("### Settings")
    # Model listesi boş gelirse diye önlem
    if available_models:
        selected_model = st.selectbox("Select Active Model:", available_models, index=0)
    else:
        selected_model = st.text_input("Enter Model Name (e.g., gemini-1.5-pro):", "gemini-1.5-pro")

    generate_btn = st.button("🚀 GENERATE RENDER", type="primary", use_container_width=True)

with col_right:
    st.write("### Output")
    if generate_btn and user_prompt:
        try:
            with st.spinner("Processing Logic Bridge & Rendering..."):
                # 1. Prompt'u işle
                final_prompt = apply_logic_bridge(user_prompt)
                
                # 2. Modeli çağır
                model = genai.GenerativeModel(selected_model)
                response = model.generate_content(final_prompt, safety_settings=no_filter_settings)
                
                # 3. Yanıtı ayrıştır (DÜZELTİLDİ: 3 Değişken)
                img_res, text_res, mime = safe_extract_response(response)

            # 4. Sonucu Göster
            if img_res:
                img_obj, img_bytes = img_res
                st.image(img_obj, use_container_width=True)
                
                # İndirme Butonu
                st.download_button(
                    label="💾 DOWNLOAD RENDER", 
                    data=img_bytes, 
                    file_name="factory_render.png", 
                    mime=mime, 
                    use_container_width=True
                )
            elif text_res:
                # Eğer model metin döndürdüyse (Hata veya açıklama)
                st.warning("Model responded with text instead of an image:")
                st.code(text_res, language="text")
            else:
                st.error("Model did not return any usable content (Blocked or Empty).")
                
        except Exception as e:
            st.error(f"System Error: {str(e)}")
            
    elif not generate_btn:
        st.info("System ready. Waiting for CineLab JSON...")
