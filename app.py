import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import io
import json
from PIL import Image

# --- 1. SETUP ---
st.set_page_config(page_title="FactoryIR: Nano Banana", page_icon="🍌", layout="wide")

st.title("🍌 FactoryIR: Finesse Edition v2.3")
st.markdown("CineLab JSON analizi: Temiz stüdyo, tam boy kadraj ve *estetik* poz düzeltme.")

# --- 2. GÜVENLİK AYARLARI (FULL UNFILTERED) ---
no_filter_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# --- 3. 🧠 THE LOGIC BRIDGE (İNCE İŞÇİLİK KATMANI) ---
def apply_logic_bridge(raw_json_prompt):
    try:
        data = json.loads(raw_json_prompt)
        recipe = data.get("cinematography_recipe", {})
        
        # --- A. KELİME TEMİZLİĞİ (Işık Ekipmanı Avı) ---
        lp = recipe.get("phase_4_lighting_physics", {})
        for key in ["key_light", "fill_light", "back_light", "setup"]:
            if key in lp:
                lp[key] = lp[key].lower().replace("softbox", "diffused volumetric light source") \
                                         .replace("bounce board", "indirect fill reflection") \
                                         .replace("light stand", "invisible point source") \
                                         .replace("setup", "lighting physics")

        # --- B. KADRAJ DİKTE ETME (Extreme Wide Shot Koruması) ---
        framing_rules = """
        - SHOT TYPE: Extreme Wide Shot (EWS).
        - COMPOSITION: The subject must occupy roughly 60-70% of the vertical frame height.
        - HEADROOM & FOOTROOM: Leave clear empty grey space above the head and below the shoes.
        - NO CROPPING: Full body visible, centered against the seamless cyc wall.
        """

        # --- C. POZ VE OBJE ESTETİĞİ (Kritik Güncelleme Burada) ---
        phase1 = recipe.get("phase_1_subject_retention", {})
        location = phase1.get("environment_override", {}).get("location", "").lower()
        notes = lp.get("director_notes", "").lower()
        
        # Orijinal poz detaylarını çekelim (eller cepte, kafa eğik vs.)
        original_pose_details = ", ".join(phase1.get("four_by_four_analysis", {}).get("pose", []))

        pose_rules = ""
        if "studio" in location and "leaning" in original_pose_details.lower():
            # Eğer stüdyo boşsa ve 'leaning' istenmişse:
            if not any(word in notes for word in ["chair", "car", "table", "wall", "prop", "object", "block"]):
                pose_rules = f"""
                - POSE CORRECTION (PHYSICS): The subject cannot 'lean' against air.
                - NEW DIRECTION: Convert the 'leaning' pose into a strong, self-supporting HIGH-FASHION STANDING stance. Do not be robotic.
                - CRITICAL RETENTION: You MUST maintain these specific stylistic details from the original request while standing: "Hands tucked in pockets", "Slightly tilted head", "stoic gaze".
                - NO FURNITURE: No blocks, no props. Just the subject standing confidently.
                """

        refined_prompt = f"""
        ACT AS: Professional Fashion Director of Photography (Kacper Kasprzyk style).
        
        {json.dumps(data)} # Temizlenmiş ve detayları korunmuş JSON
        
        STRICT EXECUTION DIRECTIVES:
        {framing_rules}
        {pose_rules}
        - RENDER RULE: 100% Invisible studio equipment. Only render the light effect.
        - ATMOSPHERE: High-end, minimalist, moody editorial feel.
        """
        return refined_prompt
    except Exception as e:
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

# --- 5. UI ---
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
    user_prompt = st.text_area("📝 CineLab JSON Yapıştır:", height=350)

with col2:
    st.markdown("### ⚙️ Kontrol Paneli")
    generate_btn = st.button("🚀 FİLTRESİZ VE ESTETİK ÜRET", type="primary", use_container_width=True)

# --- 6. EXECUTION ---
st.markdown("---")
if generate_btn:
    if not api_key or not selected_model or not user_prompt:
        st.warning("Eksik alanları doldur.")
    else:
        try:
            with st.spinner("Logic Bridge v2.3: Estetik Poz Düzeltme Uygulanıyor..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(selected_model)
                final_prompt = apply_logic_bridge(user_prompt)
                
                response = model.generate_content(final_prompt, safety_settings=no_filter_settings)
                image_res, text_res, mime = safe_extract_response(response)

                if image_res:
                    img_obj, raw_bytes = image_res
                    st.image(img_obj, caption="FactoryIR Finesse Output", use_container_width=True)
                    st.download_button("💾 Görseli Kaydet", data=raw_bytes, file_name="factory_finesse.png", mime=mime)
                elif text_res: st.info(text_res)
                else: st.error("Görsel üretilemedi.")
        except Exception as e: st.error(f"Hata oluştu: {str(e)}")
