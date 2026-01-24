import streamlit as st
import google.generativeai as genai

# --- Sayfa Ayarları ---
st.set_page_config(
    page_title="Nano Banana Generator",
    page_icon="🍌",
    layout="centered"
)

# --- Başlık ve Açıklama ---
st.title("🍌 Nano Banana: Prompt İşleyici")
st.markdown("""
**Cinelab** üzerinden hazırladığın promptu aşağıya yapıştır ve üretimi başlat.
""")

# --- Sidebar: API Key Girişi ---
with st.sidebar:
    st.header("Ayarlar")
    api_key = st.text_input("Google API Key", type="password", help="API anahtarını buraya gir.")
    
    # Model Seçimi (İstersen değiştirebilirsin)
    model_type = st.selectbox("Model Seç", ["gemini-1.5-flash", "gemini-1.5-pro"])

# --- Ana Arayüz ---
# Cinelab'den gelen promptu buraya alıyoruz
user_prompt = st.text_area("Cinelab Promptunu Buraya Yapıştır:", height=200, placeholder="Örn: Nano Banana için fütüristik bir şehir tasviri...")

generate_btn = st.button("✨ Üretimi Başlat", type="primary")

# --- Mantık Kısmı ---
if generate_btn:
    if not api_key:
        st.error("Lütfen önce sol menüden API Key girişini yap.")
    elif not user_prompt:
        st.warning("Lütfen işlenecek bir prompt gir.")
    else:
        try:
            with st.spinner("Nano Banana çalışıyor, lütfen bekle..."):
                # API Yapılandırması
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_type)
                
                # İsteği Gönder
                response = model.generate_content(user_prompt)
                
                # Sonucu Göster
                st.success("İşlem Tamamlandı!")
                st.markdown("### 📝 Sonuç:")
                st.write(response.text)
                
                # İstersen sonucu kopyalamak veya indirmek için buton ekleyebiliriz
                st.download_button(
                    label="Sonucu İndir (TXT)",
                    data=response.text,
                    file_name="nano_banana_output.txt",
                    mime="text/plain"
                )
                
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")

# --- Alt Bilgi ---
st.markdown("---")
st.caption("Nano Banana Project | Powered by Cinelab Logic")
