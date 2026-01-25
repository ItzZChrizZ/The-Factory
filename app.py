import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import io
import json
from PIL import Image

# --- 1. SETUP ---
st.set_page_config(page_title="FactoryIR: Nano Banana", page_icon="🍌", layout="wide")

st.title("🍌 FactoryIR: Nano Banana v2.1")
st.markdown("CineLab JSON reçetesini analiz eder, hatalı poz ve kadraj seçimlerini otomatik düzeltir.")

# --- 2. GÜVENLİK AYARLARI ---
no_filter_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# --- 3. 🧠 THE LOGIC BRIDGE (GÜNCELLENMİŞ MANTIK) ---
def apply_logic_bridge(raw_json_prompt):
    try:
        data = json.loads(raw_json_prompt)
        recipe = data.get("cinematography_recipe", {})
        phase1 = recipe.get("phase_1_subject_retention", {})
        env = phase1.get("environment_override", {})
        location = env.get("location", "").lower()
        notes = recipe.get("phase_4_lighting_physics", {}).get("director_notes", "")

        # --- KURAL 1: KADRAJ (FULL-BODY) KORUMASI ---
        framing_fix = """
        - FRAMING RULE: MUST be a strict FULL-BODY shot. 
        - Camera is positioned 5-7 meters away. 
        - Show the subject from the bottom of their shoes to the top of their head. 
        - DO NOT zoom in for textures; maintain a wide fashion editorial distance."""

        # --- KURAL 2: POZ VE OBJE KORUMASI ---
        pose_fix = ""
        if "studio" in location:
            # Kullanıcı notlarda bir obje (car, chair, wall vb) belirtmediyse
            if not any(word in notes.lower() for word in ["chair", "car", "table", "wall", "prop", "object"]):
                pose_fix = """
                - POSE OVERRIDE: Ignore the 'leaning' pose from the reference. 
                - New Pose: The model must stand STRAIGHT and UPRIGHT in the center. 
                - NO blocks, NO props, NO furniture. 100% empty space around the subject."""
            else:
                pose_fix = "- POSE RULE: Maintain leaning pose against the specified prop in the notes."

        # --- KURAL 3: GÖRÜNMEZ EKİPMAN ---
        invisible_gear = "\n- RENDER RULE: 100% Invisible studio equipment (no stands, no softbox edges)."

        refined_prompt = f"""
        ACT AS: Professional Technical Director of Photography.
        {raw_json_prompt}
        
        CRITICAL REVISIONS FOR THIS RENDER:
        {framing_fix}
        {pose_fix}
        {invisible_gear}
        - STICK TO: Neutral minimalist grey cyclorama background as requested.
        """
        return refined_prompt
    except:
        return raw_json_prompt

# --- 4. YARDIMCI FONKSİYONLAR ---
def safe_extract_response(response):
    try:
        parts = response.parts if hasattr(response, 'parts') else response.candidates[0].content.parts
        for part in parts:
            if hasattr(part, 'inline_data') and part.inline_data.mime_type.startswith('image/'):
                img_bytes = part.inline_data.data
                img = Image.open(io.BytesIO(img_bytes))
                return (img, img_bytes), None, part.inline_data.mime_type
            if hasattr(part, 'text') and part.text:
                return None, part.text, "text/plain"
        return None, None, None
    except: return None, None, None

# --- 5. SIDEBAR & UI ---
with st.sidebar:
    st.header("🔑 Bağlantı")
    api_key = st.text_input("Google API Key", type="password")
    fetch_models_btn = st.button("Modelleri Listele")
    if 'model_list' not in st.session_state: st.session_state.model_list = []
    if fetch_models_btn and api_key:
        try:
            genai.configure(api_key=api_key)
            models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            st.session_state.model_list = [m.name for m in models]
        except Exception as e: st.error(f"Hata: {e}")
    selected_model = st.selectbox("Model Seç:", st.session_state.model_list) if st.session_state.model_list else None

col1, col2 = st.columns([2, 1])
with col1:
    user_prompt = st.text_area("📝 CineLab Prompt Girişi:", height=350)

with col2:
    st.markdown("### ⚙️ Kontrol")
    generate_btn = st.button("🚀 FİLTRESİZ ÜRET", type="primary", use_container_width=True)

# --- 6. EXECUTION ---
st.markdown("---")
if generate_btn:
    if not api_key or not selected_model or not user_prompt:
        st.warning("Eksik alanlar var.")
    else:
        try:
            with st.spinner("Logic Bridge Zorlanıyor: Tam Boy & Dik Duruş..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(selected_model)
                final_prompt = apply_logic_bridge(user_prompt)
                
                response = model.generate_content(final_prompt, safety_settings=no_filter_settings)
                image_res, text_res, mime = safe_extract_response(response)

                if image_res:
                    img_obj, raw_bytes = image_res
                    st.image(img_obj, caption="FactoryIR Fixed Output", use_container_width=True)
                    st.download_button("💾 Kaydet", data=raw_bytes, file_name="fixed_output.png", mime=mime)
                elif text_res: st.info(text_res)
                else: st.error("Sonuç alınamadı.")
        except Exception as e: st.error(f"Hata: {e}")
