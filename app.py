import streamlit as st
import google.generativeai as genai
import importlib.metadata

st.set_page_config(page_title="Cine Lab: System Check", layout="wide")

st.title("🛠️ Cine Lab: Sistem ve Yetki Kontrolü")

# 1. Kütüphane Sürüm Kontrolü
try:
    version = importlib.metadata.version("google-generativeai")
    st.write(f"**Yüklü SDK Sürümü:** `{version}`")
    
    # Sürüm 0.8.3'ten küçükse uyarı ver
    if tuple(map(int, version.split('.'))) < (0, 8, 3):
        st.error("❌ SÜRÜM ESKİ! Lütfen Streamlit panelinden uygulamayı SİLİP (Delete App) tekrar kurun.")
    else:
        st.success("✅ Kütüphane Sürümü Güncel (Görsel üretimi destekliyor).")
except:
    st.error("Kütüphane sürümü okunamadı.")

st.markdown("---")

# 2. API ve Model Yetki Kontrolü
st.subheader("🔑 API Anahtarı ve Model Erişimi")

try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        st.success("API Anahtarı 'Secrets' içinden alındı.")
        
        # Kullanılabilir Modelleri Listele
        st.write("Bu anahtarla erişilebilen **Imagen/Görsel** modelleri aranıyor...")
        
        all_models = list(genai.list_models())
        imagen_models = [m.name for m in all_models if "imagen" in m.name or "generate" in m.supported_generation_methods]
        
        if imagen_models:
            st.success(f"🎉 Bulunan Görsel Modelleri ({len(imagen_models)}):")
            st.code(imagen_models)
            
            # TEST ÜRETİMİ BUTONU
            if st.button("TEST: Basit Bir Kare Üret (Imagen 3)"):
                try:
                    # Listeden en iyisini seç
                    target_model = "imagen-3.0-generate-001"
                    if "models/imagen-3.0-generate-001" not in [m.name for m in all_models]:
                        # Eğer 3.0 yoksa listedeki ilkini al
                        target_model = imagen_models[0].name.replace("models/", "")
                    
                    st.info(f"Test ediliyor: {target_model}")
                    from google.generativeai import ImageGenerationModel
                    model = ImageGenerationModel(target_model)
                    response = model.generate_images(prompt="A cinematic apple, 8k lighting", number_of_images=1)
                    st.image(response.images[0]._pil_image)
                    st.balloons()
                except Exception as e:
                    st.error(f"Test Üretim Hatası: {e}")
        else:
            st.warning("⚠️ Bu API anahtarı ile hiçbir 'Imagen' (Görsel) modeline erişim yok. Sadece metin modelleri (Gemini Pro/Flash) açık olabilir.")
            st.write("Tüm açık modeller:", [m.name for m in all_models])
            
    else:
        st.error("❌ Secrets ayarlanmamış. Lütfen ayarlardan GEMINI_API_KEY ekleyin.")

except Exception as e:
    st.error(f"Bağlantı Hatası: {e}")
