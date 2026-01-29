# import streamlit as st
# import os
# import sys

# # Add the current directory to sys.path so we can import from 'scripts'
# sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# # Import your backend functions
# from scripts.main import process_pdf, process_audio

# # --- UI Configuration ---
# st.set_page_config(page_title="Medical AI Scribe", page_icon="⚕️", layout="wide")

# st.title("⚕️ Medical Consultation AI Assistant")
# st.markdown("Extract insights from medical reports or consultation recordings instantly.")

# # --- Sidebar: Settings ---
# with st.sidebar:
#     st.header("Settings")
#     # Mapping UI names to backend language codes
#     lang_map = {
#         "Hindi": "hi",
#         "Marathi": "mr",
#         "Gujarati": "gu",
#         "English": "en",
#         "Spanish": "es"
#     }
#     selected_lang = st.selectbox("Preferred Output Language", list(lang_map.keys()))
#     target_lang_code = lang_map[selected_lang]
#     st.info(f"Summary will be generated in: **{selected_lang}**")

# # --- Layout: Input Columns ---
# col1, col2 = st.columns(2)

# with col1:
#     st.subheader("📄 Medical Documents")
#     uploaded_pdf = st.file_uploader("Upload Patient Report (PDF)", type=["pdf"])

# with col2:
#     st.subheader("🎤 Consultation Audio")
#     uploaded_audio = st.file_uploader("Upload Recording (WAV/MP3/M4A)", type=["wav", "mp3", "m4a"])

# # --- Processing Logic ---
# st.divider()

# if st.button("✨ Generate AI Analysis", use_container_width=True):
#     if not uploaded_pdf and not uploaded_audio:
#         st.warning("Please upload a file to proceed.")
#     else:
#         with st.status("AI is processing... Please wait.", expanded=True) as status:
#             try:
#                 # 1. Handle PDF Processing
#                 if uploaded_pdf:
#                     st.write("Processing PDF with OCR...")
#                     temp_path = "temp_input.pdf"
#                     with open(temp_path, "wb") as f:
#                         f.write(uploaded_pdf.getbuffer())
                    
#                     # Call backend
#                     patient_res, doctor_res = process_pdf(temp_path, target_lang_code)

#                 # 2. Handle Audio Processing
#                 elif uploaded_audio:
#                     st.write("Processing Audio (Diarization & Transcription)...")
#                     # Save with correct extension
#                     ext = os.path.splitext(uploaded_audio.name)[1]
#                     temp_path = f"temp_audio{ext}"
#                     with open(temp_path, "wb") as f:
#                         f.write(uploaded_audio.getbuffer())
                    
#                     # Call backend
#                     patient_res, doctor_res = process_audio(temp_path, target_lang_code)

#                 status.update(label="Analysis Complete!", state="complete", expanded=False)

#                 # --- Display Results ---
#                 st.success("Summaries generated successfully!")
#                 tab1, tab2 = st.tabs(["👤 Patient Action Plan", "🩺 Clinical Doctor Summary"])
                
#                 with tab1:
#                     st.markdown(f"### {selected_lang} Patient Summary")
#                     st.info(patient_res)
#                     st.download_button("Download Patient Plan", patient_res, file_name="patient_plan.txt")

#                 with tab2:
#                     st.markdown(f"### {selected_lang} Medical Summary")
#                     st.code(doctor_res, language="markdown")
#                     st.download_button("Download Doctor Summary", doctor_res, file_name="doctor_summary.txt")

#                 # Cleanup temp files
#                 if os.path.exists(temp_path):
#                     os.remove(temp_path)

#             except Exception as e:
#                 st.error(f"Error during processing: {e}")




import streamlit as st
import os
import sys

# Connect to your backend
from scripts.main import process_pdf, process_audio
from scripts.audio.mic_recorder import record_audio

# --- Page Configuration ---
st.set_page_config(
    page_title="Medical AI Scribe", 
    page_icon="⚕️", 
    layout="wide"
)

# --- Custom Styling ---
st.markdown("""
    <style>
    /* Force the main header to be massive and override Streamlit defaults */
    .main-header { 
        font-size: 3.5rem !important;
        color: #007bff !important; 
        font-weight: 900 !important; 
        text-align: center !important; 
        margin-top: -50px !important;
        margin-bottom: 0px !important; 
        line-height: 1.2 !important;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.1) !important;
        display: block !important;
    }
    
    .sub-header { 
        text-align: center !important; 
        color: #6c757d !important; 
        font-size: 1.8rem !important; 
        margin-bottom: 3rem !important; 
        font-weight: 400 !important;
    }
    
    .stButton>button { border-radius: 8px; font-weight: 600; height: 3em; }
    
    .input-card { 
        padding: 20px; 
        border: 1px solid #e6e9ef;
        border-radius: 10px; 
        background-color: #ffffff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Use a div container to ensure the class is applied correctly
    st.markdown('<div class="main-header">⚕️ Healthcare AI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Automated Medical Scribe & Report Analyzer</div>', unsafe_allow_html=True)

    # --- Initialize Session State (The "Memory") ---
    if "final_audio_path" not in st.session_state:
        st.session_state.final_audio_path = None
    if "patient_res" not in st.session_state:
        st.session_state.patient_res = None
    if "doctor_res" not in st.session_state:
        st.session_state.doctor_res = None

    # --- Sidebar: Global Settings ---
    with st.sidebar:
        st.header("⚙️ Settings")
        lang_map = {
            "English": "en",
            "French": "fr", 
            "Spanish": "es",
        }
        selected_lang = st.selectbox("Preferred Output Language", list(lang_map.keys()))
        target_lang_code = lang_map[selected_lang]
        st.divider()
        
        if st.sidebar.button("🗑️ Clear Current Session"):
            st.session_state.final_audio_path = None
            st.session_state.patient_res = None
            st.session_state.doctor_res = None
            st.rerun()

    # --- Main Input Section ---
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.subheader("📄 Document Input")
        uploaded_pdf = st.file_uploader("Upload Medical Report (PDF)", type=["pdf"])
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.subheader("🎤 Consultation Audio")
        audio_choice = st.radio("Select Source:", ["Upload File", "Record Live"], horizontal=True)
        
        if audio_choice == "Upload File":
            uploaded_audio = st.file_uploader("Upload WAV/MP3/M4A", type=["wav", "mp3", "m4a"])
            if uploaded_audio:
                st.session_state.final_audio_path = f"temp_{uploaded_audio.name}"
                with open(st.session_state.final_audio_path, "wb") as f:
                    f.write(uploaded_audio.getbuffer())
                st.audio(st.session_state.final_audio_path)
        
        else:
            duration = st.slider("Record Duration (sec)", 5, 120, 30)
            if st.button("🎙️ Start Recording"):
                with st.status("Recording... Please speak clearly."):
                    st.session_state.final_audio_path = record_audio(output_file="live_consultation.wav", duration=duration)
                
            if st.session_state.final_audio_path and os.path.exists(st.session_state.final_audio_path):
                st.success("✅ Recording captured and ready!")
                st.audio(st.session_state.final_audio_path)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Processing Action ---
    st.divider()
    
    # Generate Button
    if st.button("✨ Generate AI Analysis", use_container_width=True, type="primary"):
        if not uploaded_pdf and not st.session_state.final_audio_path:
            st.warning("⚠️ Please provide a PDF or Audio input first.")
        else:
            with st.status("🛠️ Analyzing Medical Content...", expanded=True) as status:
                try:
                    if uploaded_pdf:
                        temp_pdf = "process_input.pdf"
                        with open(temp_pdf, "wb") as f: 
                            f.write(uploaded_pdf.getbuffer())
                        # Store results in Session State
                        st.session_state.patient_res, st.session_state.doctor_res = process_pdf(temp_pdf, target_lang_code)
                    else:
                        # Store results in Session State
                        st.session_state.patient_res, st.session_state.doctor_res = process_audio(st.session_state.final_audio_path, target_lang_code)

                    status.update(label="✅ Success!", state="complete", expanded=False)
                
                except Exception as e:
                    st.error(f"Error: {e}")

    # --- RESULTS DISPLAY AREA ---
    if st.session_state.patient_res and st.session_state.doctor_res:
        st.markdown("### 📊 Analysis Results")
        tab1, tab2 = st.tabs(["👤 Patient Action Plan", "🩺 Doctor Summary"])
        
        with tab1:
            st.markdown(f"#### {selected_lang} Patient Instructions")
            # Patient Plan already has blue padding from st.info
            st.info(st.session_state.patient_res)
            st.download_button(
                label="📩 Download Patient Plan", 
                data=st.session_state.patient_res, 
                file_name=f"patient_plan_{target_lang_code}.txt",
                key="btn_pat_dl"
            )
            
        with tab2:
            st.markdown(f"#### {selected_lang} Clinical Summary")
            # Custom styled div for Doctor Summary to match the padding look
            st.markdown(f"""
                        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #007bff; color: #1f2937;"> 
                            {st.session_state.doctor_res}
                        </div>
                        """, unsafe_allow_html=True)
            st.write("") # Small spacer
            st.download_button(
                label="📂 Download Clinical Data", 
                data=st.session_state.doctor_res, 
                file_name=f"doctor_summary_{target_lang_code}.txt",
                key="btn_doc_dl"
            )

if __name__ == "__main__":
    main()