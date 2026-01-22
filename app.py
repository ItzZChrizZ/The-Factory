import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import io
# Güvenlik ayarları için gerekli sınıf
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Cine Lab: Production Factory", layout="wide")

# --- AUTO-THEME & INDUSTRIAL UI CSS ---
st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    header {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    
    @media (prefers-color-scheme: dark) {{
        .stApp {{ background-color: #222121; color: #F9FEFF; }}
        .stTextArea textarea {{ background-color: #161b22; color: #F9FEFF; border: 1px solid #30363d; }}
        h1, h2, h3 {{ color: #CCD4D7; }}
        .stButton button {{ background-color: #CCD4D7; color: #222121; }}
    }}

    @media (prefers-color-scheme: light) {{
        .stApp {{ background-color: #F9FEFF; color: #222121; }}
        .stTextArea textarea {{ background-color: #FFFFFF; color: #222121; border: 1px solid #E0E0E0; }}
        h1, h2, h3 {{ color: #F7BE14; }}
        .stButton button {{ background-color: #F7BE14; color: #F9FEFF; }}
    }}

    .stButton button {{ 
        border-radius: 4px; font-weight: 700; width: 100%; border: none; height: 4em;
        text-transform: uppercase; letter-spacing: 2px; transition: 0.3s;
    }}
    .stButton button:hover {{ opacity: 0.9; transform: scale(0.99); }}
    </style>
    """, unsafe_allow_html=True)

# --- SECURE API CONNECTION ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # 2026 en güncel Imagen 3 model ismi
    model_id = "imagen-3.0-generate-001" 
except Exception as e:
    st.error("System Error: API Configuration failed.")

# --- PRODUCTION INTERFACE ---
st.title("Cine Lab: Production Factory")
st.markdown("---")

col_in, col_out = st.columns([1, 1.5], gap="large")

with col_in:
    st.subheader("JSON Recipe")
    json_input = st.text_area("Paste Cine Lab technical data:", height=450)
    generate_btn = st.button("RUN PRODUCTION")

with col_out:
    st.subheader("Factory Output")
    
    if generate_btn and json_input:
        try:
            recipe = json.loads(json_input)
            
            # ANTI-PLASTIC ENGINE
            anti_plastic = (
                "photorealistic, visible skin pores, natural skin texture, "
                "subtle imperfections, no airbrushing, high-frequency details, "
                "authentic lens grain, 8k raw sensor quality, unedited look."
            )
            
            master_prompt = (
                f"Professional Fine Art Photography, style: {recipe.get('style', 'high-end')}, "
                f"Shot on {recipe.get('camera', 'medium format')}, "
                f"Lens: {recipe.get('lens', 'prime')}, "
                f"Lighting: {recipe.get('lighting', 'cinematic')}, "
                f"Shadow depth: {recipe.get('shadow_density', 50)}%, "
                f"Quality focus: {anti_plastic}"
            )

            with st.spinner("Nano Banana is processing..."):
                # ÇÖZÜM: GenerativeModel kullanarak doğrudan görsel üretimi
                model = genai.GenerativeModel(model_id)
                # Görsel üretimi için generate_content yerine uygun parametreleri kullanıyoruz
                response = model.generate_content(
                    master_prompt,
                    # Sanatsal özgürlük için güvenlik ayarları
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    }
                )
                
                # API yanıtından görseli çekme (2026 güncel SDK yapısı)
                if response.candidates[0].content.parts:
                    # Bazı SDK sürümlerinde görsel 'parts' içinde blob olarak gelir
                    for part in response.candidates[0].content.parts:
                        if part.inline_data:
                            img_data = part.inline_data.data
                            image = Image.open(io.BytesIO(img_data))
                            st.image(image, use_container_width=True)
                            
                            # İndirme Butonu
                            buf = io.BytesIO()
                            image.save(buf, format="PNG")
                            st.download_button("DOWNLOAD RAW OUTPUT", data=buf.getvalue(), file_name="factory_output.png", mime="image/png")
                            break
                else:
                    st.warning("Production paused: Safety filters triggered or model response empty.")
                    
        except json.JSONDecodeError:
            st.error("Error: Invalid JSON.")
        except Exception as e:
            st.error(f"Factory Halted: {e}")
            st.info("Check if your API Key has 'Imagen 3' access enabled in Google AI Studio.")
    else:
        st.info("System Standby. Awaiting recipe.")
