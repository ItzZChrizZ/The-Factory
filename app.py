import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import io
import json # JSON analizi için eklendi
from PIL import Image

# --- SİSTEM AYARLARI ---
st.set_page_config(page_title="FactoryIR: Nano Banana", page_icon="🍌", layout="wide")

# --- 🧠 THE LOGIC BRIDGE (MANTIK KÖPRÜSÜ) ---
def apply_logic_bridge(raw_json_prompt):
    """Cinelab JSON'unu analiz eder ve fiziksel tutarsızlıkları düzeltir."""
    try:
        data = json.loads(raw_json_prompt)
        recipe = data.get("cinematography_recipe", {})
        
        # 1. Değişkenleri Çek
        phase1 = recipe.get("phase_1_subject_retention", {})
        env = phase1.get("environment_override", {})
        pose_list = phase1.get("four_by_four_analysis", {}).get("pose", [])
        pose_str = ", ".join(pose_list).lower()
        
        location = env.get("location", "").lower()
        notes = recipe.get("phase_4_lighting_physics", {}).get("director_notes", "")

        # 2. Yaslanma (Leaning) ve Obje Mantığı
        prop_logic = ""
        if "leaning" in pose_str:
            if "studio" in location:
                # Eğer kullanıcı notlarda bir obje belirtmediyse varsayılan bir destek ekle
                if not any(word in notes.lower() for word in ["chair", "car", "table", "wall", "prop"]):
                    prop_logic = "\n- PHYSICAL CORRECTION: Subject is leaning. Add a minimalist, neutral studio prop (like a white geometric block) for support to prevent floating."
                else:
                    prop_logic = f"\n- PHYSICAL CORRECTION: Ensure the subject is realistically leaning on the mentioned prop with contact shadows."

        # 3. Görünmez Ekipman Şerhi
        invisible_gear = ""
        if "studio" in location:
            invisible_gear = "\n- RENDER RULE: 100% Invisible equipment. Do NOT show light stands, softboxes, cables, or flags. Only render the resulting light physics on the subject and environment."

        # 4. Promptu Yeniden Sentezle (High-Fidelity)
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
    except:
        # Eğer giriş JSON değilse, ham promptu gönder (güvenlik önlemi)
        return raw_json_prompt

# --- (Buradan sonrası mevcut FactoryIR kodunla entegre) ---
# ... (no_filter_settings ve safe_extract_response fonksiyonların aynı kalıyor) ...

# --- Üretim Mantığı Güncellemesi ---
# generate_btn basıldığında yapılacak işlem:
if generate_btn:
    if not api_key or not selected_model or not user_prompt:
        st.warning("Eksik alanları doldur.")
    else:
        try:
            with st.spinner("Logic Bridge Aktif: Görsel Fizik Kuralları Denetleniyor..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(selected_model)
                
                # MANTIK KÖPRÜSÜ BURADA DEVREYE GİRİYOR
                final_refined_prompt = apply_logic_bridge(user_prompt)
                
                response = model.generate_content(
                    final_refined_prompt,
                    safety_settings=no_filter_settings
                )
                
                # Sonuçları işle...
                image_res, text_res, mime = safe_extract_response(response)
                # ... (Görsel gösterim kodların)
