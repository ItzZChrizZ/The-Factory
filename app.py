import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io
from google.generativeai import ImageGenerationModel

st.set_page_config(page_title="Cine Lab: Diagnostic Mode", layout="wide")
st.title("🛠️ Cine Lab: Hata Tespit Modu")

# 1. API Bağlantısı
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        st.success("✅ API Anahtarı Algılandı")
    else:
        st.error("❌ API Anahtarı Secrets içinde yok!")
        st.stop()
except Exception as e:
    st.error(f"❌ API Bağlantı Hatası: {e}")
    st.stop()

# 2. Test Arayüzü
col1, col2 = st.columns(2)

with col1:
    st.subheader("Model Seçimi")
    # Listendeki modelleri manuel ekledim
    selected_model = st.selectbox(
        "Test edilecek modeli seç:",
        [
            "imagen-4.0-generate-001",
            "imagen-3.0-generate-001",
            "imagen-4.0-generate-preview-06-06"
        ]
    )
    
    st.subheader("Prompt")
    test_prompt = st.text_area("Test Prompt", "A cinematic apple on a table, 8k lighting, photorealistic")
    
    run_btn = st.button("TEST ÜRETİMİ YAP")

with col2:
    st.subheader("Sonuç / Hata Kaydı")
    
    if run_btn:
        status_container = st.empty()
        status_container.info(f"⏳ {selected_model} ile bağlanılıyor...")
        
        try:
            # En yalın haliyle çağırıyoruz (Parametre hatası varsa elemeyi sağlar)
            model = ImageGenerationModel(selected_model)
            
            response = model.generate_images(
                prompt=test_prompt,
                number_of_images=1,
                # Hata ihtimalini düşürmek için bunları varsayılan bırakıyorum
                # safety_filter_level="block_only_high", 
                # person_generation="allow_adult",
                aspect_ratio="1:1"
            )
            
            if response.images:
                st.success(f"✅ BAŞARILI! Model: {selected_model}")
                st.image(response.images[0]._pil_image, caption="Üretilen Görsel")
                status_container.empty()
            else:
                st.warning("⚠️ Yanıt boş döndü (Görsel oluşturulamadı).")

        except Exception as e:
            # İŞTE BURASI: Hatayı ekrana tam olarak yazdıracak
            st.error("🚨 ÜRETİM HATASI OLUŞTU!")
            st.code(str(e), language="bash")
            
            st.markdown("### Hata Analizi:")
            err_msg = str(e)
            if "404" in err_msg:
                st.write("👉 **Sebep:** Model ismi bulunamadı veya API anahtarının bu modele yetkisi yok.")
            elif "400" in err_msg:
                st.write("👉 **Sebep:** Gönderilen parametreler hatalı (örn: aspect_ratio veya safety ayarları).")
            elif "429" in err_msg:
                st.write("👉 **Sebep:** Kota doldu (Quota Exceeded).")
            elif "500" in err_msg:
                st.write("👉 **Sebep:** Google sunucularında geçici hata.")
            else:
                st.write("👉 **Sebep:** Beklenmeyen bir kütüphane veya yetki hatası.")
