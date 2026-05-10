import os
import logging
import streamlit as st
import whisper
from dotenv import load_dotenv

# ── Logging — configured once here; all submodules use getLogger(__name__) ─────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)

# ── Environment ───────────────────────────────────────────────────────────────
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    st.error("🚨 OPENAI_API_KEY not found. Add it to your .env file.")
    st.stop()

# ── Backend imports ────────────────────────────────────────────────────────────
from scripts.main import process_pdf, process_audio
from scripts.audio.mic_recorder import record_audio

# ── RAG imports ────────────────────────────────────────────────────────────────
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Medical AI Scribe", page_icon="⚕️", layout="wide")

st.markdown("""
<style>
    .main-header {
        font-size: 2.6rem;
        font-weight: 800;
        color: #1a73e8;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        text-align: center;
        color: #5f6368;
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        height: 2.8em;
    }
</style>
""", unsafe_allow_html=True)


# ── Cached resource loaders (loaded once per server session) ───────────────────
@st.cache_resource
def load_whisper_model():
    """Load Whisper 'small' model once for the entire app lifetime."""
    return whisper.load_model("small")


@st.cache_resource
def load_embeddings():
    """Load HuggingFace sentence embeddings once for the entire app lifetime."""
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


# ── RAG chain builder ──────────────────────────────────────────────────────────
def build_rag_chain(patient_text: str, doctor_text: str):
    """Build a ConversationalRetrievalChain from the two generated summaries."""
    docs = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=150
    ).split_documents([
        Document(page_content=patient_text),
        Document(page_content=doctor_text),
    ])
    vectorstore = FAISS.from_documents(docs, load_embeddings())
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    return ConversationalRetrievalChain.from_llm(
        llm=ChatOllama(model="llama3", temperature=0),
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        memory=memory,
    )


# ── Session state init ─────────────────────────────────────────────────────────
def _init_session():
    defaults = {
        "final_audio_path": None,
        "patient_res": None,
        "doctor_res": None,
        "qa_chain": None,
        "chat_messages": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    st.markdown('<div class="main-header">⚕️ Healthcare AI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Automated Medical Scribe & Intelligent Chatbot</div>', unsafe_allow_html=True)

    _init_session()

    # ── Sidebar ────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ Settings")
        lang_map = {"English": "en", "French": "fr", "Spanish": "es"}
        selected_lang = st.selectbox("Output Language", list(lang_map.keys()))
        target_lang = lang_map[selected_lang]
        st.divider()
        if st.button("🗑️ Clear Session"):
            st.session_state.clear()
            st.rerun()

    # ── Input section ──────────────────────────────────────────────────────────
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.subheader("📄 Document Input")
        uploaded_pdf = st.file_uploader("Upload Medical Report (PDF)", type=["pdf"])

    with col2:
        st.subheader("🎤 Consultation Audio")
        audio_choice = st.radio("Source", ["Upload File", "Record Live"], horizontal=True)

        if audio_choice == "Upload File":
            uploaded_audio = st.file_uploader("Upload WAV / MP3 / M4A", type=["wav", "mp3", "m4a"])
            if uploaded_audio:
                temp_path = f"temp_{uploaded_audio.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_audio.getbuffer())
                st.session_state.final_audio_path = temp_path
                st.audio(temp_path)
        else:
            duration = st.slider("Record Duration (sec)", 5, 120, 30)
            if st.button("🎙️ Start Recording"):
                with st.spinner(f"Recording for {duration}s…"):
                    st.session_state.final_audio_path = record_audio(
                        output_file="live_consultation.wav", duration=duration
                    )
            if st.session_state.final_audio_path and os.path.exists(st.session_state.final_audio_path):
                st.success("✅ Recording ready")
                st.audio(st.session_state.final_audio_path)

    st.divider()

    # ── Generate analysis ──────────────────────────────────────────────────────
    if st.button("✨ Generate AI Analysis", use_container_width=True, type="primary"):
        has_input = uploaded_pdf or st.session_state.final_audio_path
        if not has_input:
            st.warning("Please provide a PDF report or an audio recording first.")
        else:
            with st.status("Processing…", expanded=True):
                try:
                    st.session_state.qa_chain = None
                    st.session_state.chat_messages = []

                    if uploaded_pdf:
                        pdf_path = "process_input.pdf"
                        with open(pdf_path, "wb") as f:
                            f.write(uploaded_pdf.getbuffer())
                        st.session_state.patient_res, st.session_state.doctor_res = process_pdf(
                            pdf_path, target_lang
                        )
                    else:
                        st.session_state.patient_res, st.session_state.doctor_res = process_audio(
                            st.session_state.final_audio_path, target_lang
                        )

                    st.write("Building knowledge base…")
                    st.session_state.qa_chain = build_rag_chain(
                        st.session_state.patient_res,
                        st.session_state.doctor_res,
                    )
                    st.success("✅ Analysis complete. Chatbot is ready!")
                except Exception as e:
                    st.error(f"Processing error: {e}")

    # ── Results ────────────────────────────────────────────────────────────────
    if st.session_state.patient_res and st.session_state.doctor_res:
        st.markdown("### 📊 Analysis Results")
        tab1, tab2 = st.tabs(["👤 Patient Summary", "🩺 Doctor Summary"])

        with tab1:
            st.info(st.session_state.patient_res)
            st.download_button(
                "📩 Download Patient Summary",
                st.session_state.patient_res,
                file_name=f"patient_summary_{target_lang}.txt",
            )

        with tab2:
            st.info(st.session_state.doctor_res)
            st.download_button(
                "📂 Download Doctor Summary",
                st.session_state.doctor_res,
                file_name=f"doctor_summary_{target_lang}.txt",
            )

    # ── Chatbot ────────────────────────────────────────────────────────────────
    st.divider()
    st.header("🏥 Medical Knowledge Chatbot")

    if st.session_state.qa_chain is None:
        st.info("Generate AI Analysis first to activate the chatbot.")
        return

    # Render chat history
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Voice question
    st.markdown("#### 🎙️ Ask via Voice")
    voice_duration = st.slider("Duration (sec)", 3, 30, 5, key="chat_voice_duration")

    if st.button("🎤 Record Question", key="chat_record_btn"):
        with st.spinner(f"Recording for {voice_duration}s…"):
            voice_file = record_audio(output_file="voice_question.wav", duration=voice_duration)

        with st.spinner("Transcribing…"):
            result = load_whisper_model().transcribe(
                voice_file,
                language="en",
                task="transcribe",
                temperature=0.0,
                beam_size=5,
                fp16=False,
            )
        voice_prompt = result["text"].strip()

        with st.chat_message("user"):
            st.markdown(voice_prompt)
        st.session_state.chat_messages.append({"role": "user", "content": voice_prompt})

        with st.chat_message("assistant"):
            with st.spinner("Analyzing…"):
                answer = st.session_state.qa_chain.invoke({"question": voice_prompt})["answer"]
            st.markdown(answer)
        st.session_state.chat_messages.append({"role": "assistant", "content": answer})

    # Text question
    if prompt := st.chat_input("Ask a question about this case…"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Analyzing…"):
                answer = st.session_state.qa_chain.invoke(
                    {"question": f"Answer this medical question directly and concisely:\n\n{prompt}"}
                )["answer"]
            st.markdown(answer)
        st.session_state.chat_messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()