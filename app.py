import streamlit as st
import requests
import json
import io
from PIL import Image
import urllib.parse
import random

# --- UI AYARLARI ---
st.set_page_config(page_title="Cine Lab: Free Edition", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background-color: #121212; color: #e0e0e0; }
    .stTextArea textarea { background-color: #1e1e1e; color: #fff; border: 1px solid #333; }
    .stButton button { 
        background-color: #00D4FF; 
        color: #000; 
        font-weight: bold; 
        height: 3.5em; 
        border: none;
        transition: 0.3s;
    }
    .stButton button:hover { background-color: #00aabb; color: #fff; }
    h1, h2, h3 { color: #00D4FF; }
    </style>
    """, unsafe_allow_html=True)

# --- ÜCRETSİZ MOTOR FONKSİYONU ---
def generate_free_image(prompt):
    # Google yerine Pollinations (Flux Realism) kullanıyoruz.
    # Bu servis tamamen ücretsizdir ve API Key istemez.
    
    # Promptu URL için güvenli hale getir
    encoded_prompt = urllib.parse.quote(prompt)
    
    # Rastgele bir seed ekle ki her seferinde aynı resim çıkmasın
    seed = random.randint(0, 10000)
    
    # FLUX Modeli: Şu an gerçekçilikte en iyi ücretsiz modellerden biridir
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?model=flux&width=1024&height=1024&seed={seed}&nologo=true"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        return Image.open(io.BytesIO(response.content))
    else:
        raise Exception(f"Sunucu Hatası: {response.status_code}")

# --- ARAYÜZ ---
st.title("🏭 Cine Lab: Free Factory")
st.caption("Motor: FLUX Realism (Ücretsiz & Kartsız)")
st.markdown("---")

col_in, col_out = st.columns([1, 1.5], gap="large")

with col_in:
    st.subheader("JSON Recipe")
    # Kullanıcıya örnek bir reçete gösterelim
    default_json = '{\n "style": "Cinematic Portrait",\n "camera": "Fujifilm GFX 100",\n "lens": "110mm f/2",\n "lighting": "Rembrandt lighting"\n}'
    json_input = st.text_area("Paste technical data:", height=400, value=default_json)
    generate_btn = st.button("ÜRETİMİ BAŞLAT (BEDAVA)")

with col_out:
    st.subheader("Factory Output")
    
    if generate_btn and json_input:
        try:
            recipe = json.loads(json_input)
            
            # Anti-Plastic Prompt (FLUX Modeli için optimize edildi)
            # Flux, doğal dili çok iyi anlar.
            realism_specs = (
                "hyper-realistic photography, raw photo, authentic skin texture, "
                "visible pores, peach fuzz, slight skin imperfections, "
                "depth of field, bokeh, soft studio lighting, 8k uhd, "
                "shot on medium format, no cgi, no 3d render, natural film grain."
            )
            
            master_prompt = (
                f"{recipe.get('style', 'Photo')}, "
                f"Camera: {recipe.get('camera', 'Professional Camera')}, "
                f"Lens: {recipe.get('lens', 'Prime Lens')}, "
                f"Lighting: {recipe.get('lighting', 'Natural')}. "
                f"{realism_specs}"
            )

            with st.spinner("FLUX Motoru çalışıyor (Kredi kartı gerekmez)..."):
                # Ücretsiz fonksiyonu çağırıyoruz
                image = generate_free_image(master_prompt)
                
                if image:
                    st.image(image, use_container_width=True)
                    
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button(
                        label="GÖRSELİ İNDİR",
                        data=buf.getvalue(),
                        file_name="cine_lab_flux.png",
                        mime="image/png"
                    )
                else:
                    st.error("Görsel oluşturulamadı.")

        except json.JSONDecodeError:
            st.error("HATA: JSON formatı bozuk. Lütfen süslü parantezleri kontrol et.")
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
