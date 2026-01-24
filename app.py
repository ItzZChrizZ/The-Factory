import streamlit as st
import requests
import json
import base64
from PIL import Image
import io

# --- UI AYARLARI ---
st.set_page_config(page_title="Cine Lab: Direct Link", layout="wide")

# --- CSS ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #222121; color: #F9FEFF; }
    .stButton button { background-color: #F7BE14; color: #222121; font-weight: bold; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- API BAĞLANTISI ---
# Burada SDK kullanmıyoruz, sadece anahtarı alıyoruz.
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("🚨 API Key bulunamadı! Secrets ayarlarını kontrol et.")
    st.stop()

# --- BYPASS FONKSİYONU (REST API) ---
def generate_image_bypass(prompt, model_id, key):
    # Google'ın ham API adresi (SDK kullanmadan direkt erişim)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:predict?key={key}"
    
    headers = {"Content-Type": "application/json"}
    
    # İstek paketi (JSON)
    payload = {
        "instances": [
            {"prompt": prompt}
        ],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "1:1"
        }
    }
    
    # Postacıya veriyoruz (Requests)
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code != 200:
        raise Exception(f"Google Reddedildi ({response.status_code}): {response.text}")
    
    # Gelen paketi açıyoruz
    result = response.json()
    
    # Görsel verisini (Base64) çözüyoruz
    try:
        predictions = result.get('predictions', [])
        if predictions:
            # Base64 string'i görsel verisine çevir
            b64_data = predictions[0]['bytesBase64Encoded']
            image_data = base64.b64decode(b64_data)
            return Image.open(io.BytesIO(image_data))
        else:
            return None
    except Exception as e:
        raise Exception(f"Paket Açma Hatası: {e} - Yanıt: {result}")

# --- ARAYÜZ ---
st.title("🏭 Cine Lab: Direct Uplink (SDK-Free)")
st.caption("Aracı kütüphane devre dışı. Doğrudan Google sunucularına bağlanılıyor.")

col_in, col_out = st.columns([1, 1.5], gap="large")

with col_in:
    # Model Seçimi (Listendeki modeller)
    model_choice = st.selectbox("Model Seç:", ["imagen-3.0-generate-001", "imagen-4.0-generate-001"])
    
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

            with st.spinner(f"{model_choice} ile doğrudan bağlantı kuruluyor..."):
                # BYPASS FONKSİYONUNU ÇAĞIRIYORUZ
                image = generate_image_bypass(master_prompt, model_choice, api_key)
                
                if image:
                    st.image(image, use_container_width=True)
                    
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button("İNDİR", data=buf.getvalue(), file_name="output.png", mime="image/png")
                else:
                    st.warning("Görsel oluşturulamadı (Boş yanıt).")

        except json.JSONDecodeError:
            st.error("HATA: JSON bozuk.")
        except Exception as e:
            st.error("🚨 BAĞLANTI HATASI:")
            st.code(str(e))
            if "404" in str(e):
                st.info("İpucu: Model ismi bu API endpoint'inde farklı olabilir. Listeden diğer modeli dene.")
