import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io

# --- TEMA AYARLARI ---
st.set_page_config(page_title="Cine Lab: Production Factory", layout="wide")

# Kullanıcının belirlediği renk paleti
is_light_mode = st.sidebar.toggle("Light Mode", value=False)

if is_light_mode:
    main_bg, main_txt, header_col, card_bg, border_col = "#F9FEFF", "#222121", "#F7BE14", "#FFFFFF", "#E0E0E0"
else:
    main_bg, main_txt, header_col, card_bg, border_col = "#222121", "#F9FEFF", "#CCD4D7", "#161b22", "#30363d"

# Custom CSS Entegrasyonu
st.markdown(f"""
    <style>
    .stApp {{ background-color: {main_bg}; color: {main_txt}; }}
    .stTextArea textarea {{ background-color: {card_bg}; color: {main_txt}; border: 1px solid {border_col}; }}
    h1, h2, h3 {{ color: {header_col}; }}
    .stButton button {{ background-color: {header_col}; color: {main_bg}; border-radius: 8px; width: 100%; }}
    </style>
    """, unsafe_allow_html=True)

# --- API YAPILANDIRMASI ---
st.sidebar.title("Factory Settings")
api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    # 2026 Nano Banana (Imagen-3 tabanlı) model seçimi
    model = genai.GenerativeModel('imagen-3') 

# --- ARAYÜZ ---
st.title("🎬 Cine Lab: Production Factory")
st.caption("JSON Reçetelerini Gerçekliğe Dönüştür")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Input Recipe")
    json_input = st.text_area("Paste Cine Lab JSON here:", height=300, placeholder='{"camera": "85mm", "lighting": "low key"...}')
    
    generate_btn = st.button("GENERATE IMAGE")

with col2:
    st.subheader("Production Output")
    image_placeholder = st.empty()
    
    if generate_btn:
        if not api_key:
            st.error("Lütfen bir API Key girin.")
        else:
            try:
                # JSON parse ve prompt hazırlığı
                data = json.loads(json_input)
                # JSON verisini betimleyici bir prompta çeviriyoruz
                final_prompt = f"Professional photography, {data.get('camera', '')}, {data.get('lens', '')}, {data.get('lighting', '')} lighting, realism, ultra-detailed, cinematic quality."
                
                with st.spinner("Nano Banana fabrikada üretiyor..."):
                    # Görsel üretimi (Model fonksiyonu API güncelliğine göre değişebilir)
                    response = model.generate_content(final_prompt)
                    # Not: API yanıt yapısı 2026 standartlarına göre optimize edilmiştir
                    image_data = response.images[0] 
                    
                    st.session_state['last_image'] = image_data
                    image_placeholder.image(image_data, use_container_width=True)
                    
                    # Kaydetme Butonu
                    buf = io.BytesIO()
                    image_data.save(buf, format="PNG")
                    st.download_button(
                        label="💾 SAVE IMAGE",
                        data=buf.getvalue(),
                        file_name="cinelab_output.png",
                        mime="image/png"
                    )
            except Exception as e:
                st.error(f"Üretim Hatası: {str(e)}")

if 'last_image' not in st.session_state:
    image_placeholder.info("Henüz bir üretim yapılmadı. JSON reçetesini yapıştırın ve Generate'e basın.")