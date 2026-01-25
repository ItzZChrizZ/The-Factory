import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import io
import json
from PIL import Image

# --- 1. SETUP & CONFIG ---
# Fetching API Key from Streamlit Secrets
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception:
    st.error("Error: GOOGLE_API_KEY not found in secrets.")
    st.stop()

st.set_page_config(page_title="FactoryIR", layout="wide")

# --- 2. SECURITY SETTINGS (100% FAITHFUL) ---
no_filter_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# --- 3. THE LOGIC BRIDGE (100% FAITHFUL) ---
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

# --- 4. HELPER FUNCTIONS ---
def safe_extract_response(response):
    try:
        parts = response.parts if hasattr(response, 'parts') else response.candidates[0].content.parts
        for part in parts:
            if hasattr(part, 'inline_data') and part.inline_data.mime_type.startswith('image/'):
                img_bytes = part.inline_data.data
                img = Image.open(io.BytesIO(img_bytes))
                return (img, img_bytes), None, part.inline_data.mime_type
            if hasattr(part, 'text') and part.text:
                return None, part.text, "text/plain"
        return None, None, None
    except: return None, None, None

# --- 5. UI LAYOUT ---
st.title("FactoryIR")
st.markdown("---")

# Sidebar for Model Selection
with st.sidebar:
    st.subheader("System Settings")
    if 'model_list' not in st.session_state or not st.session_state.model_list:
        try:
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            # Filtering for Image models specifically if needed, otherwise showing all
            st.session_state.model_list = [m.split('/')[-1] for m in models] 
        except:
            st.session_state.model_list = ["gemini-1.5-pro-latest"] # Fallback

    selected_model_display = st.selectbox("Active Model:", st.session_state.model_list)
    # Re-map to full name for API
    selected_model = f"models/{selected_model_display}"

# Main One-Page Split Layout
col_input, col_output = st.columns([1, 1], gap="medium")

with col_input:
    st.subheader("Input CineLab JSON")
    user_prompt = st.text_area("Paste code here:", height=500)
    generate_btn = st.button("GENERATE RENDER", type="primary", use_container_width=True)

with col_output:
    st.subheader("Output Terminal")
    if generate_btn:
        if not user_prompt:
            st.warning("Please input JSON data.")
        else:
            try:
                with st.spinner("Processing Logic Bridge & Rendering..."):
                    model = genai.GenerativeModel(selected_model)
                    final_prompt = apply_logic_bridge(user_prompt)
                    
                    response = model.generate_content(final_prompt, safety_settings=no_filter_settings)
                    image_res, text_res, mime = safe_extract_response(response)

                    if image_res:
                        img_obj, raw_bytes = image_res
                        
                        # Save button at the top of the result
                        st.download_button(
                            label="💾 DOWNLOAD RENDER",
                            data=raw_bytes,
                            file_name="factory_ir_output.png",
                            mime=mime,
                            use_container_width=True
                        )
                        
                        st.image(img_obj, use_container_width=True)
                    elif text_res:
                        st.info(text_res)
                    else:
                        st.error("No image generated by the model.")
            except Exception as e:
                st.error(f"Execution Error: {str(e)}")
    else:
        st.info("Awaiting input to generate render...")
