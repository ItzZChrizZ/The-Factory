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
no_filter_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# --- Yardımcı Fonksiyon: Güvenli Veri Ayıklama ---
def safe_extract_response(response):
    """Yanıttan metin veya görseli hatasız çıkarmaya çalışır."""
    image_data = None
    text_data = None
    mime_type = None
    
    # 1. Parça (Parts) kontrolü
    if not hasattr(response, 'parts') or not response.parts:
        # Bazen parts boş olabilir ama candidates dolu olabilir
        if hasattr(response, 'candidates') and response.candidates:
            parts = response.candidates[0].content.parts
        else:
            return None, None, None
    else:
        parts = response.parts

    # 2. Parçaları Tara
    for part in parts:
        # GÖRSEL KONTROLÜ
        if hasattr(part, 'inline_data') and hasattr(part.inline_data, 'mime_type'):
            if part.inline_data.mime_type.startswith('image/'):
                try:
                    img_bytes = part.inline_data.data
                    img = Image.open(io.BytesIO(img_bytes))
                    image_data = (img, img_bytes)
                    mime_type = part.inline_data.mime_type
                    return image_data, None, mime_type # Görsel bulursak hemen dön
                except:
                    pass
        
        # METİN KONTROLÜ
        if hasattr(part, 'text') and part.text:
            text_data = part.text

    # Eğer döngü bitti ve görsel yoksa, metni döndür (varsa)
    return None, text_data, "text/plain"


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
        try:
            with st.spinner(f"{selected_model} çalışıyor..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(selected_model)
                
                # İsteği Gönder
                response = model.generate_content(
                    user_prompt,
                    safety_settings=no_filter_settings
                )
                
                # --- YENİ GÜVENLİ İŞLEME ---
                image_res, text_res, mime = safe_extract_response(response)

                # 1. GÖRSEL VARSA
                if image_res:
                    img_obj, raw_bytes = image_res
                    st.success("✨ Görsel Oluşturuldu!")
                    st.image(img_obj, caption="Nano Banana Output", use_column_width=True)
                    
                    ext = mime.split('/')[-1] if mime else "png"
                    st.download_button(
                        "💾 Görseli Kaydet",
                        data=raw_bytes,
                        file_name=f"nano_banana.{ext}",
                        mime=mime
                    )
                
                # 2. METİN VARSA
                elif text_res:
                    st.success("📄 Metin Oluşturuldu")
                    st.write(text_res)
                    st.download_button(
                        "💾 Metni İndir",
                        data=text_res,
                        file_name="output.txt",
                        mime="text/plain"
                    )

                # 3. HİÇBİRİ YOKSA
                else:
                    st.info("İşlem bitti ancak görüntülenecek veri bulunamadı.")
                    st.markdown("**Teknik Detaylar:**")
                    st.json({
                        "finish_reason": response.candidates[0].finish_reason if response.candidates else "Unknown",
                        "parts_found": False
                    })

        except Exception as e:
            st.error("Bir hata oluştu:")
            st.code(str(e))
