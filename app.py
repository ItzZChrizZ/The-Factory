import streamlit as st
import subprocess
import sys

# --- 1. KABA KUVVET: Kütüphaneyi Zorla Güncelleme ---
# Streamlit önbelleğini delmek için uygulama başlarken pip install çalıştırıyoruz.
try:
    # Bu komut terminalde 'pip install --upgrade google-generativeai' yazmakla aynıdır
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "google-generativeai>=0.8.3"])
except Exception as e:
    st.error(f"Güncelleme Hatası: {e}")

# Kütüphane güncellendikten sonra import ediyoruz
import google.generativeai as genai
import json
from PIL import Image
import io

# --- UI AYARLARI ---
st.set_page_config(page_title="Cine Lab: Force Fix", layout="wide")

# --- CSS ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #222121; color: #F9FEFF; }
    .stButton button { background-color: #F7BE14; color: #222121; font-weight: bold; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- API BAĞLANTISI ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("API Key bulunamadı.")
except Exception as e:
    st.error(f"Bağlantı Hatası: {e}")

# Listendeki en güçlü model (Bunu teyit etmiştik)
MODEL_ID = "imagen-4.0-generate-001"

st.title("🏭 Cine Lab: Fabrika (Force Update Modu)")
st.caption(f"Aktif Model: {MODEL_ID}")

col_in, col_out = st.columns([1, 1.5], gap="large")

with col_in:
    json_input = st.text_area("JSON Reçetesi:", height=300, value='{"style": "Cinematic", "camera": "Sony A7R", "lens": "85mm"}')
    generate_btn = st.button("ÜRETİMİ BAŞLAT")

with col_out:
    if generate_btn:
        try:
            recipe = json.loads(json_input)
            
            # Anti-Plastic Prompt
            master_prompt = (
                f"Professional Fine Art Photography, {recipe.get('style', '')}, "
                f"{recipe.get('camera', '')}, {recipe.get('lens', '')}, "
                f"photorealistic, visible skin pores, natural texture, 8k raw quality, no airbrushing."
            )

            with st.spinner("Kütüphane kontrol ediliyor ve görsel üretiliyor..."):
                # --- KRİTİK DEĞİŞİKLİK ---
                # Hata veren 'from google... import ImageGenerationModel' satırını sildik.
                # Yerine, güncellenmiş ana kütüphane içinden çağırıyoruz.
                try:
                    # Yeni sürümde bu sınıf genai'nin altında olmalı
                    if hasattr(genai, "ImageGenerationModel"):
                        model = genai.ImageGenerationModel(MODEL_ID)
                    else:
                        # Eğer hala bulamazsa manuel import deneriz
                        from google.generativeai import ImageGenerationModel
                        model = ImageGenerationModel(MODEL_ID)

                    response = model.generate_images(
                        prompt=master_prompt,
                        number_of_images=1,
                        # Güvenlik parametrelerini şimdilik kapattım, önce çalıştığını görelim
                        aspect_ratio="1:1"
                    )
                    
                    if response.images:
                        image = response.images[0]._pil_image
                        st.image(image, use_container_width=True)
                        
                        buf = io.BytesIO()
                        image.save(buf, format="PNG")
                        st.download_button("İNDİR", data=buf.getvalue(), file_name="output.png", mime="image/png")
                    else:
                        st.warning("Görsel üretilemedi (Boş yanıt).")

                except ImportError:
                    st.error("Kütüphane hala eski sürümde! 'Force Update' işe yaramadı.")
                except Exception as inner_e:
                    st.error(f"Model Hatası: {inner_e}")
                    if "404" in str(inner_e):
                        st.info("İpucu: Model ID hatası. Lütfen API Key yetkilerini kontrol et.")

        except json.JSONDecodeError:
            st.error("HATA: JSON bozuk.")
        except Exception as e:
            st.error(f"SİSTEM HATASI: {e}")
