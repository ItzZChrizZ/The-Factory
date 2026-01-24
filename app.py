import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io
# Görsel üretimi için gerekli özel sınıf
from google.generativeai import ImageGenerationModel

# --- UI AYARLARI ---
st.set_page_config(page_title="Cine Lab: Production Factory", layout="wide")

# --- CSS TEMA ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    @media (prefers-color-scheme: dark) {
        .stApp { background-color: #222121; color: #F9FEFF; }
        .stTextArea textarea { background-color: #161b22; color: #F9FEFF; border: 1px solid #30363d; border-radius: 8px; }
        h1, h2, h3 { color: #CCD4D7; }
        .stButton button { background-color: #CCD4D7; color: #222121; }
    }
    @media (prefers-color-scheme: light) {
        .stApp { background-color: #F9FEFF; color: #222121; }
        .stTextArea textarea { background-color: #FFFFFF; color: #222121; border: 1px solid #E0E0E0; border-radius: 8px; }
        h1, h2, h3 { color: #F7BE14; }
        .stButton button { background-color: #F7BE14; color: #F9FEFF; }
    }
    .stButton button { border-radius: 4px; font-weight: 700; width: 100%; height: 4em; text-transform: uppercase; letter-spacing: 2px; }
    </style>
    """, unsafe_allow_html=True)

# --- API BAĞLANTISI ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("API Key 'Secrets' içinde bulunamadı.")
except Exception as e:
    st.error(f"Bağlantı Hatası: {e}")

# --- KRİTİK AYAR: LİSTENDEN SEÇİLEN MODEL ---
# Senin paylaştığın listedeki en kararlı model
MODEL_ID = "imagen-4.0-generate-001"

# --- ARAYÜZ ---
st.title("Cine Lab: Production Factory (v4.0)")
st.markdown("---")

col_in, col_out = st.columns([1, 1.5], gap="large")

with col_in:
    st.subheader("JSON Recipe")
    json_input = st.text_area(
        "Paste technical data:", 
        height=450, 
        placeholder='{"camera": "Sony A7R V", "lens": "85mm", "style": "Cinematic"}'
    )
    generate_btn = st.button("RUN PRODUCTION")

with col_out:
    st.subheader("Factory Output")
    
    if generate_btn and json_input:
        try:
            # 1. Reçete Analizi
            recipe = json.loads(json_input)
            
            # 2. Anti-Plastic Motoru (Imagen 4.0 için optimize edildi)
            realism_specs = (
                "photorealistic, visible skin pores, natural skin texture, "
                "no digital smoothing, authentic lens grain, 8k raw quality, "
                "imperfect skin details, realistic lighting falloff, masterpiece."
            )
            
            master_prompt = (
                f"Professional Fine Art Photography, style: {recipe.get('style', 'cinematic')}, "
                f"Shot on {recipe.get('camera', 'medium format')}, "
                f"Lens: {recipe.get('lens', 'prime lens')}, "
                f"Lighting: {recipe.get('lighting', 'studio lighting')}, {realism_specs}"
            )

            with st.spinner(f"Imagen 4.0 is rendering..."):
                # 3. Görsel Üretimi
                model = ImageGenerationModel(MODEL_ID)
                
                response = model.generate_images(
                    prompt=master_prompt,
                    number_of_images=1,
                    # Güvenlik Filtreleri (Sanatsal üretim için esnek)
                    safety_filter_level="block_only_high", 
                    person_generation="allow_adult",
                    aspect_ratio="1:1"
                )
                
                # 4. Sonuç
                if response.images:
                    image = response.images[0]._pil_image
                    st.image(image, use_container_width=True)
                    
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button("DOWNLOAD RAW", data=buf.getvalue(), file_name="production_v4.png", mime="image/png")
                else:
                    st.warning("Üretim durduruldu (Güvenlik filtresi).")

        except json.JSONDecodeError:
            st.error("HATA: JSON formatı bozuk.")
        except Exception as e:
            # Hata Yakalama
            if "429" in str(e):
                st.info("⏳ Limit aşıldı (Quota Exceeded). Model çok güçlü olduğu için Google bekletiyor. Lütfen 1 dakika bekleyip tekrar deneyin.")
            elif "404" in str(e):
                st.error(f"Model Bulunamadı hatası: {MODEL_ID}. Ancak listede bu model var, geçici bir sunucu hatası olabilir.")
            else:
                st.error(f"SİSTEM HATASI: {e}")
    else:
        st.info(f"Sistem Hazır. Aktif Motor: {MODEL_ID}")
