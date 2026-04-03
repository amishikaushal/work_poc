import streamlit as st
import os
from dotenv import load_dotenv

# ==============================
# Load Environment Variables
# ==============================
load_dotenv()


# Safe rerun helper: call Streamlit's experimental rerun when available,
# otherwise raise the internal RerunException or fall back to stopping.
def _safe_rerun():
    try:
        st.experimental_rerun()
        return
    except Exception:
        pass

    # Try importing and raising the internal rerun exception used by Streamlit
    try:
        from streamlit.runtime.scriptrunner.script_runner import RerunException
        raise RerunException()
    except Exception:
        try:
            # older/newer internal path
            from streamlit.runtime.scriptrunner import RerunException as RE
            raise RE()
        except Exception:
            # As a last resort, stop execution; interaction will trigger a rerun
            try:
                st.session_state["_needs_rerun_fallback"] = True
            except Exception:
                pass
            st.stop()

if not os.getenv("OPENAI_API_KEY"):
    st.error("🚨 OPENAI_API_KEY not found. Please add it to your .env file.")
    st.stop()

# Backend
from scripts.main import process_pdf, process_audio
from scripts.audio.mic_recorder import record_audio, start_recording, stop_recording
from scripts.audio.transcription import transcribe_file

# RAG Imports
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ==============================
# Page Config
# ==============================
st.set_page_config(
    page_title="Medical AI Scribe",
    page_icon="⚕️",
    layout="wide"
)

# ==============================
# Custom Styling (From Code 2)
# ==============================
st.markdown("""
    <style>
    .main-header { 
        font-size: 3.5rem !important;
        color: #007bff !important; 
        font-weight: 900 !important; 
        text-align: center !important; 
        margin-top: -50px !important;
        margin-bottom: 0px !important; 
        line-height: 1.2 !important;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.1) !important;
    }
    .sub-header { 
        text-align: center !important; 
        color: #6c757d !important; 
        font-size: 1.8rem !important; 
        margin-bottom: 3rem !important; 
    }
    .stButton>button { 
        border-radius: 8px !important; 
        font-weight: 600; 
        height: 3em; 
        padding: 0.6rem 1rem;
    }
    /* compact mic buttons only */
    .mic-button-wrap .stButton>button {
        border-radius: 12px; 
        height: 2.6em;
        width: 2.6em;
        padding: 0.15rem 0.25rem;
        font-size: 1.1rem;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    /* Recording indicator */
    .recording-dot {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: #d9534f;
        border-radius: 50%;
        margin-right: 8px;
        vertical-align: middle;
        animation: blink 1s steps(2, start) infinite;
    }
    @keyframes blink { to { visibility: hidden; } }
    .recording-label { color: #d9534f; font-weight: 700; vertical-align: middle; }
    .input-card { 
        padding: 20px; 
        border: 1px solid #e6e9ef;
        border-radius: 10px; 
        background-color: #ffffff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)


# ==============================
# Build Dynamic RAG
# ==============================
def build_rag_from_summaries(patient_text, doctor_text):

    documents = [
        Document(page_content=patient_text),
        Document(page_content=doctor_text)
    ]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    docs = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.from_documents(docs, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    llm = ChatOllama(
        model="llama3",
        temperature=0
    )

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory
    )

    return qa_chain


# ==============================
# MAIN APP
# ==============================
def main():

    st.markdown('<div class="main-header">⚕️ Healthcare AI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Automated Medical Scribe & Intelligent Medical Chatbot</div>', unsafe_allow_html=True)

    # Session Defaults
    defaults = {
        "final_audio_path": None,
        "patient_res": None,
        "doctor_res": None,
        "qa_chain": None,
        "chat_messages": [],
        "pending_transcription": False,
        "pending_transcribed_text": None,
        "chat_recording": False,
        "chat_recording_path": None,
        "pending_chat_input": "",
        "submitted_query": None
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # ==============================
    # Sidebar
    # ==============================
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

        if st.button("🗑️ Clear Full Session"):
            st.session_state.clear()
            st.rerun()

    # ==============================
    # Input Section
    # ==============================
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
                temp_audio = f"temp_{uploaded_audio.name}"
                with open(temp_audio, "wb") as f:
                    f.write(uploaded_audio.getbuffer())
                st.session_state.final_audio_path = temp_audio
                st.audio(temp_audio)

        else:
            duration = st.slider("Record Duration (sec)", 5, 120, 30)
            if st.button("🎙️ Start Recording"):
                with st.status("Recording..."):
                    st.session_state.final_audio_path = record_audio(
                        output_file="live_consultation.wav",
                        duration=duration
                    )

            if st.session_state.final_audio_path and os.path.exists(st.session_state.final_audio_path):
                st.success("Recording ready!")
                st.audio(st.session_state.final_audio_path)

        st.markdown('</div>', unsafe_allow_html=True)

    # ==============================
    # Generate AI Analysis
    # ==============================
    st.divider()

    if st.button("✨ Generate AI Analysis", use_container_width=True, type="primary"):

        if not uploaded_pdf and not st.session_state.final_audio_path:
            st.warning("Please provide PDF or Audio.")
        else:
            with st.status("Processing...", expanded=True):
                try:
                    st.session_state.qa_chain = None
                    st.session_state.chat_messages = []

                    if uploaded_pdf:
                        temp_pdf = "process_input.pdf"
                        with open(temp_pdf, "wb") as f:
                            f.write(uploaded_pdf.getbuffer())

                        st.session_state.patient_res, st.session_state.doctor_res = process_pdf(
                            temp_pdf,
                            target_lang_code
                        )

                    else:
                        st.session_state.patient_res, st.session_state.doctor_res = process_audio(
                            st.session_state.final_audio_path,
                            target_lang_code
                        )

                    # Build RAG
                    st.session_state.qa_chain = build_rag_from_summaries(
                        st.session_state.patient_res,
                        st.session_state.doctor_res
                    )

                    st.success("Analysis Complete & Chatbot Ready!")

                except Exception as e:
                    st.error(f"Processing Error: {e}")

    # ==============================
    # Results Display
    # ==============================
    if st.session_state.patient_res and st.session_state.doctor_res:

        st.markdown("### 📊 Analysis Results")

        tab1, tab2 = st.tabs(["👤 Patient Action Plan", "🩺 Doctor Summary"])

        with tab1:
            st.info(st.session_state.patient_res)
            st.download_button(
                "📩 Download Patient Plan",
                st.session_state.patient_res,
                file_name=f"patient_plan_{target_lang_code}.txt"
            )

        with tab2:
            st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #007bff;">
                    {st.session_state.doctor_res}
                </div>
            """, unsafe_allow_html=True)

            st.download_button(
                "📂 Download Doctor Summary",
                st.session_state.doctor_res,
                file_name=f"doctor_summary_{target_lang_code}.txt"
            )

    # ==============================
    # RAG CHATBOT
    # ==============================
    st.divider()
    st.header("🏥 Medical Knowledge Chatbot")

    if st.session_state.qa_chain is None:
        st.info("Generate AI Analysis first to activate chatbot.")
        return

    qa_chain = st.session_state.qa_chain

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input + mic toggle
    # Handle pending chat input from transcription (before rendering chat_input widget)

    col_prompt, col_mic = st.columns([9, 1])

    with col_prompt:
        # Use form so text_input only submits on Enter or button click
        with st.form(key="chat_form", clear_on_submit=True):
            initial_input = st.session_state.get("pending_chat_input", "")
            prompt_input = st.text_input(
                "Ask a question about this case...",
                value=initial_input,
                label_visibility="collapsed"
            )

            # Submit button styled as arrow (Streamlit will add it to the right of the input)
            submitted = st.form_submit_button("↑", use_container_width=False)
            if submitted and prompt_input:
                # Store submitted query and clear any pending transcription (only after submit)
                st.session_state.submitted_query = prompt_input
                if st.session_state.get("pending_chat_input"):
                    st.session_state.pending_chat_input = ""

    # Get the submitted query if it exists (outside the form so it doesn't clear)
    prompt = st.session_state.get("submitted_query", None)
    if prompt:
        st.session_state.submitted_query = None  # Clear after retrieving

    with col_mic:
        st.markdown('<div class="mic-button-wrap">', unsafe_allow_html=True)
        if st.session_state.chat_recording:
            # show small blinking recording indicator
            st.markdown('<div><span class="recording-dot"></span><span class="recording-label">Recording...</span></div>', unsafe_allow_html=True)
            if st.button("⏹️", key="mic_stop"):
                saved_path = stop_recording()
                st.session_state.chat_recording = False
                if saved_path:
                    st.session_state.final_audio_path = saved_path
                    st.success("Recording saved.")
                    # Transcribe and place into session for prefill on next rerun
                    try:
                        transcribed = transcribe_file(saved_path)
                        # Store transcription to prefill chat input on next rerun
                        st.session_state.pending_chat_input = transcribed
                        st.success("Transcription ready in input. Press the arrow to send.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Transcription error: {e}")
        else:
            if st.button("🎤", key="mic_start"):
                out = start_recording("chat_input.wav")
                if out:
                    st.session_state.chat_recording = True
                    st.session_state.chat_recording_path = out
                    st.info("Recording... press stop to finish.")
                    # Immediately rerun so the recording indicator appears right away
                    _safe_rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    if prompt:

        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.chat_messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                result = qa_chain({"question": prompt})
                response = result["answer"]
                st.markdown(response)

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": response
        })

    # No automatic posting: transcriptions are placed into the chat input (`pending_chat_input`) and
    # the user must press the arrow button to send the query for processing.


if __name__ == "__main__":
    main()