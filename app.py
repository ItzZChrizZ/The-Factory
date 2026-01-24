import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io
# Görsel üretimi için gerekli özel sınıf
from google.generativeai import ImageGenerationModel

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Cine Lab: Production Factory", layout="wide")

# --- CSS / TEMA ---
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

# --- API AYARLARI ---
# Hata oluşursa loading ekranında kalmaması için try-except bloğu
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("API Key bulunamadı! Lütfen Streamlit Secrets ayarlarını kontrol et.")
except Exception as e:
    st.error(f"API Bağlantı Hatası: {e}")

# Model İsmi (Listendeki en kararlı model)
MODEL_ID = "imagen-3.0-generate-001"

# --- ARAYÜZ ---
st.title("Cine Lab: Production Factory")
st.markdown("---")

col_in, col_out = st.columns([1, 1.5], gap="large")

with col_in:
    st.subheader("JSON Recipe")
    # Örnek JSON ile başla ki kullanıcı ne yapıştıracağını bilsin
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
            # 1. JSON Analizi
            recipe = json.loads(json_input)
            
            # 2. Anti-Plastic Prompt Motoru
            realism_specs = (
                "photorealistic, visible skin pores, natural skin texture, "
                "no digital smoothing, authentic lens grain, 8k raw quality, "
                "imperfect skin details, realistic lighting falloff."
            )
            
            master_prompt = (
                f"Professional Fine Art Photography, style: {recipe.get('style', 'cinematic')}, "
                f"Shot on {recipe.get('camera', 'medium format')}, "
                f"Lens: {recipe.get('lens', 'prime lens')}, "
                f"Lighting: {recipe.get('lighting', 'studio lighting')}, {realism_specs}"
            )

            with st.spinner(f"Rendering with {MODEL_ID}..."):
                # 3. Görsel Üretimi (Doğru Sınıf ve Metot)
                model = ImageGenerationModel(MODEL_ID)
                
                response = model.generate_images(
                    prompt=master_prompt,
                    number_of_images=1,
                    # Güvenlik Filtreleri (Fine Art için ayarlı)
                    safety_filter_level="block_only_high", 
                    person_generation="allow_adult",
                    aspect_ratio="1:1"
                )
                
                # 4. Sonuç Gösterimi
                if response.images:
                    image = response.images[0]._pil_image
                    st.image(image, use_container_width=True)
                    
                    # İndirme
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button("DOWNLOAD RAW", data=buf.getvalue(), file_name="factory_output.png", mime="image/png")
                else:
                    st.warning("Üretim durduruldu (Güvenlik filtresi veya boş yanıt).")

        except json.JSONDecodeError:
            st.error("HATA: Geçersiz JSON formatı. Lütfen Cine Lab çıktısını kontrol et.")
        except Exception as e:
            # Hata detayını gösterelim ki loading'de kalmasın
            st.error(f"SİSTEM HATASI: {e}")
            if "429" in str(e):
                st.info("Limit aşıldı (Quota Exceeded). Lütfen 1 dakika bekleyip tekrar dene.")
            elif "404" in str(e):
                st.info(f"Model bulunamadı: {MODEL_ID}. API Key yetkilerini kontrol et.")
    else:
        st.info("Sistem Hazır. Reçete bekleniyor.")
