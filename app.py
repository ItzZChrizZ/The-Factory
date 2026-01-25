import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import io
import json
from PIL import Image

# --- 1. SETUP ---
st.set_page_config(page_title="FactoryIR: Nano Banana", page_icon="🍌", layout="wide")

st.title("🍌 FactoryIR: Nano Banana")
st.markdown("CineLab JSON reçetesini yapıştır, Logic Bridge ile kusursuz fizik ve filtresiz üretim al.")

# --- 2. GÜVENLİK AYARLARI (FİLTRELERİ KALDIRMA) ---
no_filter_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# --- 3. 🧠 THE LOGIC BRIDGE (MANTIK KÖPRÜSÜ) ---
def apply_logic_bridge(raw_json_prompt):
    """Cinelab JSON'unu analiz eder ve fiziksel tutarsızlıkları düzeltir."""
    try:
        data = json.loads(raw_json_prompt)
        recipe = data.get("cinematography_recipe", {})
        
        phase1 = recipe.get("phase_1_subject_retention", {})
        env = phase1.get("environment_override", {})
        pose_list = phase1.get("four_by_four_analysis", {}).get("pose", [])
        pose_str = ", ".join(pose_list).lower()
        
        location = env.get("location", "").lower()
        notes = recipe.get("phase_4_lighting_physics", {}).get("director_notes", "")

        prop_logic = ""
        # Yaslanma (Leaning) Kontrolü
        if "leaning" in pose_str:
            if "studio" in location:
                if not any(word in notes.lower() for word in ["chair", "car", "table", "wall", "prop"]):
                    prop_logic = "\n- PHYSICAL CORRECTION: Subject is leaning. Add a minimalist, neutral studio prop (like a white geometric block) for support to prevent floating."
                else:
                    prop_logic = f"\n- PHYSICAL CORRECTION: Ensure the subject is realistically leaning on the mentioned prop with contact shadows."

        invisible_gear = ""
        if "studio" in location:
            invisible_gear = "\n- RENDER RULE: 100% Invisible equipment. Do NOT show light stands, softboxes, cables, or flags. Only render the resulting light physics on the subject."

        refined_prompt = f"""
        ACT AS: Professional Technical Director of Photography.
        STRICT COMPLIANCE: Follow the JSON recipe with 100% fidelity.
        
        {raw_json_prompt}
        
        FINAL EXECUTION RULES:
        - WEIGHTING: Technical specs (Phase 2) and Subject DNA (Phase 1) take 80% priority.
        - OPTICAL CHARACTER: Apply exact f-stop depth of field and sensor grain.
        {prop_logic}
        {invisible_gear}
        - OUTPUT: High-resolution cinematic visual.
        """
        return refined_prompt
    except Exception:
        return raw_json_prompt

# --- 4. YARDIMCI FONKSİYON: VERİ AYIKLAMA ---
def safe_extract_response(response):
    image_data = None
    text_data = None
    mime_type = None
    
    try:
        if hasattr(response, 'parts') and response.parts:
            parts = response.parts
        elif hasattr(response, 'candidates') and response.candidates:
            parts = response.candidates[0].content.parts
        else:
            return None, None, None

        for part in parts:
            if hasattr(part, 'inline_data') and part.inline_data.mime_type.startswith('image/'):
                img_bytes = part.inline_data.data
                img = Image.open(io.BytesIO(img_bytes))
                image_data = (img, img_bytes)
                mime_type = part.inline_data.mime_type
                return image_data, None, mime_type
            
            if hasattr(part, 'text') and part.text:
                text_data = part.text
        return None, text_data, "text/plain"
    except:
        return None, None, None

# --- 5. SIDEBAR: AYARLAR ---
with st.sidebar:
    st.header("🔑 Bağlantı")
    api_key = st.text_input("Google API Key", type="password")
    fetch_models_btn = st.button("Modelleri Listele")
    
    if 'model_list' not in st.session_state:
        st.session_state.model_list = []

    if fetch_models_btn and api_key:
        try:
            genai.configure(api_key=api_key)
            models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            st.session_state.model_list = [m.name for m in models]
            st.success("Modeller listelendi.")
        except Exception as e:
            st.error(f"Hata: {e}")

    selected_model = st.selectbox("Model Seç:", st.session_state.model_list) if st.session_state.model_list else None

# --- 6. ANA EKRAN ---
col1, col2 = st.columns([2, 1])
with col1:
    user_prompt = st.text_area("📝 CineLab Prompt Girişi:", height=350, placeholder="JSON reçetesini buraya yapıştır...")

with col2:
    st.markdown("### ⚙️ Kontrol")
    st.write("Aktif Model:", selected_model if selected_model else "Seçilmedi")
    generate_btn = st.button("🚀 FİLTRESİZ ÜRET", type="primary", use_container_width=True)

# --- 7. ÜRETİM MANTIĞI ---
st.markdown("---")
if generate_btn:
    if not api_key or not selected_model or not user_prompt:
        st.warning("Lütfen tüm alanları doldur.")
    else:
        try:
            with st.spinner("Logic Bridge Denetleniyor & Üretiliyor..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(selected_model)
                
                # Logic Bridge Uygula
                final_prompt = apply_logic_bridge(user_prompt)
                
                response = model.generate_content(final_prompt, safety_settings=no_filter_settings)
                image_res, text_res, mime = safe_extract_response(response)

                if image_res:
                    img_obj, raw_bytes = image_res
                    st.image(img_obj, caption="FactoryIR Output", use_container_width=True)
                    st.download_button("💾 Kaydet", data=raw_bytes, file_name="output.png", mime=mime)
                elif text_res:
                    st.info("Model metin yanıtı döndürdü:")
                    st.write(text_res)
                else:
                    st.error("Görsel oluşturulamadı. Filtreye takılmış veya model desteklemiyor olabilir.")
        except Exception as e:
            st.error(f"Üretim hatası: {e}")
