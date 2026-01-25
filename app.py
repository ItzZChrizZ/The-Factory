import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import io
import json
from PIL import Image

# --- 1. SETUP & PAGE CONFIG ---
st.set_page_config(page_title="FactoryIR", layout="wide")

# --- CSS: ONE PAGE & ALIGNMENT MASTER FIX ---
st.markdown("""
    <style>
    /* Sidebar Gizle */
    [data-testid="stSidebar"] { display: none; }
    
    /* Üst ve Alt Boşlukları Azalt (Compact Mode) */
    .block-container { 
        padding-top: 1rem; 
        padding-bottom: 1rem; 
    }
    
    /* Input Alanı (Terminal Hissi) */
    .stTextArea textarea { 
        font-family: 'JetBrains Mono', monospace; 
        background-color: #161b22; 
        color: #e6edf3;
    }
    
    /* Buton Stilleri */
    .stButton button { 
        height: 3em; 
        font-weight: bold; 
        border-radius: 8px;
    }
    
    /* GÖRSEL BOYUT FIXLEME (Hizalama Kilidi) */
    /* Input alanı 480px olacak, görseli de max 480px'e sabitliyoruz. */
    /* Böylece sol ve sağ sütun eşit boyda biter, butonlar hizalanır. */
    div[data-testid="stImage"] img {
        max-height: 480px;  
        width: auto;
        object-fit: contain;
        margin: 0 auto;
        display: block;
    }
    
    h1 { margin-bottom: 0.2rem; font-size: 2rem; }
    h3 { margin-top: 0.5rem; margin-bottom: 0.5rem; font-size: 1.2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API CONFIG ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Error: GOOGLE_API_KEY not found in secrets.")
    st.stop()

# --- 3. 🧠 THE LOGIC BRIDGE (100% FAITHFUL) ---
def apply_logic_bridge(raw_json_prompt):
    try:
        data = json.loads(raw_json_prompt)
        recipe = data.get("cinematography_recipe", {})
        lp = recipe.get("phase_4_lighting_physics", {})
        
        for key in ["key_light", "fill_light", "back_light", "setup"]:
            if key in lp:
                lp[key] = lp[key].lower().replace("softbox", "diffused volumetric light source") \
                                         .replace("bounce board", "indirect fill reflection") \
                                         .replace("light stand", "invisible point source") \
                                         .replace("setup", "lighting physics")

        framing_rules = """
        - SHOT TYPE: Extreme Wide Shot (EWS).
        - COMPOSITION: The subject must occupy roughly 60-70% of the vertical frame height.
        - HEADROOM & FOOTROOM: Leave clear empty grey space above the head and below the shoes.
        - NO CROPPING: Full body visible, centered against the seamless cyc wall.
        """

        phase1 = recipe.get("phase_1_subject_retention", {})
        location = phase1.get("environment_override", {}).get("location", "").lower()
        notes = lp.get("director_notes", "").lower()
        original_pose_details = ", ".join(phase1.get("four_by_four_analysis", {}).get("pose", []))

        pose_rules = ""
        if "studio" in location and "leaning" in original_pose_details.lower():
            if not any(word in notes for word in ["chair", "car", "table", "wall", "prop", "object", "block"]):
                pose_rules = f"""
                - POSE CORRECTION (PHYSICS): The subject cannot 'lean' against air.
                - NEW DIRECTION: Convert the 'leaning' pose into a strong, self-supporting HIGH-FASHION STANDING stance. Do not be robotic.
                - CRITICAL RETENTION: You MUST maintain these specific stylistic details from the original request while standing: "Hands tucked in pockets", "Slightly tilted head", "stoic gaze".
                - NO FURNITURE: No blocks, no props. Just the subject standing confidently.
                """

        refined_prompt = f"""
        ACT AS: Professional Fashion Director of Photography (Kacper Kasprzyk style).
        
        {json.dumps(data)}
        
        STRICT EXECUTION DIRECTIVES:
        {framing_rules}
        {pose_rules}
        - RENDER RULE: 100% Invisible studio equipment. Only render the light effect.
        - ATMOSPHERE: High-end, minimalist, moody editorial feel.
        """
        return refined_prompt
    except Exception:
        return raw_json_prompt

# --- 4. SAFETY & EXTRACTION ---
no_filter_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

def safe_extract_response(response):
    try:
        if not hasattr(response, 'candidates') or not response.candidates:
            return None, "No candidates returned", None
        parts = response.parts if hasattr(response, 'parts') else response.candidates[0].content.parts
        for part in parts:
            if hasattr(part, 'inline_data') and part.inline_data.mime_type.startswith('image/'):
                img_bytes = part.inline_data.data
                img = Image.open(io.BytesIO(img_bytes))
                return (img, img_bytes), None, part.inline_data.mime_type
            if hasattr(part, 'text') and part.text:
                return None, part.text, "text/plain"
        return None, None, None
    except Exception as e: 
        return None, str(e), None

# --- 5. UI LAYOUT & EXECUTION ---
st.title("FactoryIR")

@st.cache_data
def get_available_models():
    try:
        return [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except:
        return ["models/gemini-1.5-pro-latest"]

available_models = get_available_models()

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.write("### Input")
    # FIX: 480px ideal yükseklik. Scroll gerektirmez, One Page hissini korur.
    user_prompt = st.text_area("CineLab JSON Input:", height=480, placeholder="Paste JSON code here...", label_visibility="collapsed")
    
    # Yer kazanmak için Settings başlığını kaldırdık, direkt seçim kutusu
    c1, c2 = st.columns([2, 1])
    with c1:
        if available_models:
            selected_model = st.selectbox("Model", available_models, index=0, label_visibility="collapsed")
        else:
            selected_model = st.text_input("Model", "gemini-1.5-pro", label_visibility="collapsed")
    
    with c2:
        # Generate Butonu (Sol altta)
        generate_btn = st.button("🚀 GENERATE", type="primary", use_container_width=True)

with col_right:
    st.write("### Output Stream")
    
    if generate_btn and user_prompt:
        final_prompt = apply_logic_bridge(user_prompt)
        model = genai.GenerativeModel(selected_model)
        
        # 1. GRID SİSTEMİ: Görsel sayısı kadar sütun açıyoruz (Yan yana dizilim)
        grid_cols = st.columns(image_count)
        
        for i in range(image_count):
            # Her bir sütunun içine giriyoruz
            with grid_cols[i]:
                # 2. KART GÖRÜNÜMÜ: İçeriği çerçeveli kutuya alıyoruz
                with st.container(border=True):
                    
                    # 3. SADAKAT MANTIĞI (Logic Bridge)
                    # İlk görsel (i==0) -> Temp 0.2 (%100 Sadık)
                    # Diğerleri (i>0)   -> Temp 0.9 (%90 Sadık + %10 Yaratıcılık)
                    current_temp = 0.2 if i == 0 else 0.9
                    
                    # Başlık (Badge)
                    if i == 0:
                        st.caption("💎 Master (Strict)")
                    else:
                        st.caption(f"🎨 Variant {i}")
                    
                    with st.spinner("Rendering..."):
                        try:
                            # Sıcaklık ayarını burada gönderiyoruz
                            config = GenerationConfig(temperature=current_temp)
                            
                            response = model.generate_content(
                                final_prompt, 
                                safety_settings=no_filter_settings,
                                generation_config=config
                            )
                            img_res, text_res, mime = safe_extract_response(response)

                            if img_res:
                                img_obj, img_bytes = img_res
                                
                                # Görseli kartın genişliğine oturt (Responsive)
                                st.image(img_obj, use_container_width=True)
                                
                                # İndirme Butonu
                                st.download_button(
                                    label="💾 SAVE", 
                                    data=img_bytes, 
                                    file_name=f"render_v{i+1}.png", 
                                    mime=mime, 
                                    use_container_width=True
                                )
                            elif text_res:
                                st.error("Text Error")
                                st.code(text_res, language="text")
                            else:
                                st.error("Blocked")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            
    elif not generate_btn:
        st.info("Ready. Set count and click RUN.")
