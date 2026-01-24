import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import io
from PIL import Image

# --- Sayfa Ayarları ---
st.set_page_config(
    page_title="Nano Banana: Unfiltered Lab",
    page_icon="🍌",
    layout="wide"
)

st.title("🍌 Nano Banana: Filtresiz Üretim İstasyonu")
st.markdown("Cinelab promptunu yapıştır, filtresiz (BLOCK_NONE) olarak üret.")

# --- Güvenlik Ayarları (FİLTRELERİ KALDIRMA) ---
# Tüm güvenlik kategorileri için eşiği "BLOCK_NONE" yapıyoruz.
no_filter_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# --- Yardımcı Fonksiyon: Görsel Verisi Kontrolü ---
def try_extract_image(response_obj):
    """Yanıtta görsel verisi varsa ayıklar (Geleceğe yönelik hazırlık)."""
    try:
        # Bu yapı modelden modele değişebilir, genel bir deneme yapıyoruz.
        if hasattr(response_obj, 'parts'):
             for part in response_obj.parts:
                 if hasattr(part, 'inline_data') and part.inline_data.mime_type.startswith('image/'):
                     image_bytes = part.inline_data.data
                     img = Image.open(io.BytesIO(image_bytes))
                     # MIME type (örn: image/png) ve raw bytes döndür
                     return img, image_bytes, part.inline_data.mime_type
    except Exception:
        return None, None, None
    return None, None, None

# --- Sidebar: Ayarlar ---
with st.sidebar:
    st.header("🔑 Bağlantı")
    api_key = st.text_input("Google API Key", type="password")
    
    fetch_models_btn = st.button("Modelleri Listele")
    
    if 'model_list' not in st.session_state:
        st.session_state.model_list = []

    if fetch_models_btn and api_key:
        try:
            genai.configure(api_key=api_key)
            models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            st.session_state.model_list = [m.name for m in models]
            st.success(f"{len(st.session_state.model_list)} model listelendi.")
        except Exception as e:
            st.error(f"Modeller listelenirken hata: {e}")

    if st.session_state.model_list:
        selected_model = st.selectbox("Model Seç:", st.session_state.model_list)
        st.caption("⚠️ Seçili model 'BLOCK_NONE' güvenlik ayarıyla çalıştırılacak.")
    else:
        selected_model = None
        st.info("API Key gir ve listele.")

# --- Ana Ekran ---
col1, col2 = st.columns([2, 1])

with col1:
    user_prompt = st.text_area(
        "📝 Cinelab Prompt Girişi:", 
        height=350, 
        placeholder="Promptunu buraya yapıştır..."
    )

with col2:
    st.markdown("### ⚙️ Kontrol")
    st.write("Aktif Model:")
    st.code(selected_model if selected_model else "Seçilmedi")
    
    generate_btn = st.button("🚀 FİLTRESİZ ÜRET", type="primary", use_container_width=True)

# --- Üretim Mantığı ---
st.markdown("---")
st.header("Sonuç Alanı")

if generate_btn:
    if not api_key or not selected_model or not user_prompt:
        st.warning("Lütfen API Key, Model ve Prompt alanlarını doldur.")
    else:
        # Hata yakalama bloğu
        try:
            with st.spinner(f"{selected_model} filtresiz çalışıyor..."):
                # Yapılandırma
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(selected_model)
                
                # Üretim İsteği (Güvenlik ayarları eklendi)
                response = model.generate_content(
                    user_prompt,
                    safety_settings=no_filter_settings
                )
                
                # --- SONUÇ İŞLEME ---
                
                # 1. Görsel Kontrolü Yap
                generated_image_obj, raw_bytes, mime_type = try_extract_image(response)

                if generated_image_obj:
                    st.success("Görsel başarıyla oluşturuldu!")
                    # Görseli göster
                    st.image(generated_image_obj, caption="Nano Banana Çıktısı", use_column_width=True)
                    
                    # Kaydetme Butonu (Dosya uzantısını MIME type'tan tahmin et)
                    ext = mime_type.split('/')[-1] if mime_type else "png"
                    st.download_button(
                        label=f"💾 Görseli Kaydet ({ext.upper()})",
                        data=raw_bytes,
                        file_name=f"nano_banana_result.{ext}",
                        mime=mime_type
                    )

                # 2. Görsel yoksa, Metin Kontrolü Yap
                elif hasattr(response, 'text') and response.text:
                    st.success("Metin başarıyla oluşturuldu.")
                    st.markdown("### 📄 Metin Çıktısı:")
                    st.write(response.text)
                    st.download_button(
                        label="💾 Metni İndir (TXT)",
                        data=response.text,
                        file_name="nano_banana_text.txt",
                        mime="text/plain"
                    )
                
                # 3. Ne görsel ne metin varsa ham yanıtı göster
                else:
                    st.warning("Model bir çıktı döndürdü ancak standart metin veya görsel formatında değil. Ham yanıt aşağıdadır:")
                    st.write(response)

        except Exception as e:
            # İstenilen HAM HATA GÖSTERİMİ
            st.error("🚨 KRİTİK HATA OLUŞTU!")
            st.markdown("Aşağıdaki hata mesajını inceleyin:")
            st.code(str(e), language="bash") # Hatayı kod bloğu içinde ham olarak göster
