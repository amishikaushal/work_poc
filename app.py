# import streamlit as st
# import os
# from dotenv import load_dotenv
# from streamlit_mic_recorder import mic_recorder
# import whisper


# # ==============================
# # Load Environment Variables
# # ==============================
# load_dotenv()

# if not os.getenv("OPENAI_API_KEY"):
#     st.error("🚨 OPENAI_API_KEY not found. Please add it to your .env file.")
#     st.stop()

# # Backend
# from scripts.main import process_pdf, process_audio
# from scripts.audio.mic_recorder import record_audio

# # RAG Imports
# from langchain_community.vectorstores import FAISS
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_community.chat_models import ChatOllama
# from langchain.chains import ConversationalRetrievalChain
# from langchain.memory import ConversationBufferMemory
# from langchain.schema import Document
# from langchain_text_splitters import RecursiveCharacterTextSplitter


# # ==============================
# # Page Config
# # ==============================
# st.set_page_config(
#     page_title="Medical AI Scribe",
#     page_icon="⚕️",
#     layout="wide"
# )

# # ==============================
# # Custom Styling (From Code 2)
# # ==============================
# st.markdown("""
#     <style>
#     .main-header { 
#         font-size: 3.5rem !important;
#         color: #007bff !important; 
#         font-weight: 900 !important; 
#         text-align: center !important; 
#         margin-top: -50px !important;
#         margin-bottom: 0px !important; 
#         line-height: 1.2 !important;
#         text-shadow: 3px 3px 6px rgba(0,0,0,0.1) !important;
#     }
#     .sub-header { 
#         text-align: center !important; 
#         color: #6c757d !important; 
#         font-size: 1.8rem !important; 
#         margin-bottom: 3rem !important; 
#     }
#     .stButton>button { 
#         border-radius: 8px; 
#         font-weight: 600; 
#         height: 3em; 
#     }
#     .input-card { 
#         padding: 20px; 
#         border: 1px solid #e6e9ef;
#         border-radius: 10px; 
#         background-color: #ffffff;
#         box-shadow: 0 4px 6px rgba(0,0,0,0.05);
#     }
#     </style>
#     """, unsafe_allow_html=True)


# # ==============================
# # Build Dynamic RAG
# # ==============================
# def build_rag_from_summaries(patient_text, doctor_text):

#     documents = [
#         Document(page_content=patient_text),
#         Document(page_content=doctor_text)
#     ]

#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=800,
#         chunk_overlap=150
#     )

#     docs = splitter.split_documents(documents)

#     embeddings = HuggingFaceEmbeddings(
#         model_name="sentence-transformers/all-MiniLM-L6-v2"
#     )

#     vectorstore = FAISS.from_documents(docs, embeddings)
#     retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

#     llm = ChatOllama(
#         model="llama3",
#         temperature=0
#     )

#     memory = ConversationBufferMemory(
#         memory_key="chat_history",
#         return_messages=True
#     )

#     qa_chain = ConversationalRetrievalChain.from_llm(
#         llm=llm,
#         retriever=retriever,
#         memory=memory
#     )

#     return qa_chain


# # ==============================
# # MAIN APP
# # ==============================
# def main():

#     st.markdown('<div class="main-header">⚕️ Healthcare AI Assistant</div>', unsafe_allow_html=True)
#     st.markdown('<div class="sub-header">Automated Medical Scribe & Intelligent Medical Chatbot</div>', unsafe_allow_html=True)

#     # Session Defaults
#     defaults = {
#         "final_audio_path": None,
#         "patient_res": None,
#         "doctor_res": None,
#         "qa_chain": None,
#         "chat_messages": []
#     }

#     for key, value in defaults.items():
#         if key not in st.session_state:
#             st.session_state[key] = value

#     # ==============================
#     # Sidebar
#     # ==============================
#     with st.sidebar:
#         st.header("⚙️ Settings")

#         lang_map = {
#             "English": "en",
#             "French": "fr",
#             "Spanish": "es",
#         }

#         selected_lang = st.selectbox("Preferred Output Language", list(lang_map.keys()))
#         target_lang_code = lang_map[selected_lang]

#         st.divider()

#         if st.button("🗑️ Clear Full Session"):
#             st.session_state.clear()
#             st.rerun()

#     # ==============================
#     # Input Section
#     # ==============================
#     col1, col2 = st.columns(2, gap="large")

#     with col1:
#         st.markdown('<div class="input-card">', unsafe_allow_html=True)
#         st.subheader("📄 Document Input")
#         uploaded_pdf = st.file_uploader("Upload Medical Report (PDF)", type=["pdf"])
#         st.markdown('</div>', unsafe_allow_html=True)

#     with col2:
#         st.markdown('<div class="input-card">', unsafe_allow_html=True)
#         st.subheader("🎤 Consultation Audio")

#         audio_choice = st.radio("Select Source:", ["Upload File", "Record Live"], horizontal=True)

#         if audio_choice == "Upload File":
#             uploaded_audio = st.file_uploader("Upload WAV/MP3/M4A", type=["wav", "mp3", "m4a"])
#             if uploaded_audio:
#                 temp_audio = f"temp_{uploaded_audio.name}"
#                 with open(temp_audio, "wb") as f:
#                     f.write(uploaded_audio.getbuffer())
#                 st.session_state.final_audio_path = temp_audio
#                 st.audio(temp_audio)

#         else:
#             duration = st.slider("Record Duration (sec)", 5, 120, 30)
#             if st.button("🎙️ Start Recording"):
#                 with st.status("Recording..."):
#                     st.session_state.final_audio_path = record_audio(
#                         output_file="live_consultation.wav",
#                         duration=duration
#                     )

#             if st.session_state.final_audio_path and os.path.exists(st.session_state.final_audio_path):
#                 st.success("Recording ready!")
#                 st.audio(st.session_state.final_audio_path)

#         st.markdown('</div>', unsafe_allow_html=True)

#     # ==============================
#     # Generate AI Analysis
#     # ==============================
#     st.divider()

#     if st.button("✨ Generate AI Analysis", use_container_width=True, type="primary"):

#         if not uploaded_pdf and not st.session_state.final_audio_path:
#             st.warning("Please provide PDF or Audio.")
#         else:
#             with st.status("Processing...", expanded=True):
#                 try:
#                     st.session_state.qa_chain = None
#                     st.session_state.chat_messages = []

#                     if uploaded_pdf:
#                         temp_pdf = "process_input.pdf"
#                         with open(temp_pdf, "wb") as f:
#                             f.write(uploaded_pdf.getbuffer())

#                         st.session_state.patient_res, st.session_state.doctor_res = process_pdf(
#                             temp_pdf,
#                             target_lang_code
#                         )

#                     else:
#                         st.session_state.patient_res, st.session_state.doctor_res = process_audio(
#                             st.session_state.final_audio_path,
#                             target_lang_code
#                         )

#                     # Build RAG
#                     st.session_state.qa_chain = build_rag_from_summaries(
#                         st.session_state.patient_res,
#                         st.session_state.doctor_res
#                     )

#                     st.success("Analysis Complete & Chatbot Ready!")

#                 except Exception as e:
#                     st.error(f"Processing Error: {e}")

#     # ==============================
#     # Results Display
#     # ==============================
#     if st.session_state.patient_res and st.session_state.doctor_res:

#         st.markdown("### 📊 Analysis Results")

#         tab1, tab2 = st.tabs(["👤 Patient Action Plan", "🩺 Doctor Summary"])

#         with tab1:
#             st.info(st.session_state.patient_res)
#             st.download_button(
#                 "📩 Download Patient Plan",
#                 st.session_state.patient_res,
#                 file_name=f"patient_plan_{target_lang_code}.txt"
#             )

#         with tab2:
#             st.markdown(f"""
#                 <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #007bff;">
#                     {st.session_state.doctor_res}
#                 </div>
#             """, unsafe_allow_html=True)

#             st.download_button(
#                 "📂 Download Doctor Summary",
#                 st.session_state.doctor_res,
#                 file_name=f"doctor_summary_{target_lang_code}.txt"
#             )

#     # ==============================
#     # RAG CHATBOT
#     # ==============================
#     st.divider()
#     st.header("🏥 Medical Knowledge Chatbot")

#     if st.session_state.qa_chain is None:
#         st.info("Generate AI Analysis first to activate chatbot.")
#         return

#     qa_chain = st.session_state.qa_chain

#     for message in st.session_state.chat_messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])

#        # ==============================
#     # 🎤 Voice Question (Working Version)
#     # ==============================
#     st.markdown("### 🎙️ Ask via Voice")

#     audio_data = mic_recorder(
#         start_prompt="🎤 Start Recording",
#         stop_prompt="⏹️ Stop & Send",
#         just_once=True,
#         use_container_width=True
#     )

#     if audio_data:

#         # Save recorded audio
#         import subprocess

#         # Save original browser audio (webm)
#         raw_file = "voice_question.webm"
#         with open(raw_file, "wb") as f:
#             f.write(audio_data["bytes"])

#         # Convert properly to real WAV
#         voice_file = "voice_question.wav"

#         subprocess.run([
#              "ffmpeg",
#             "-y",
#             "-i", raw_file,
#             "-ac", "1",
#             "-ar", "16000",
#             "-f", "wav",
#             voice_file
#         ], check=True)


#         with st.spinner("Transcribing..."):

#             model = whisper.load_model("base")   # lightweight & fast
#             result = model.transcribe(
#                     voice_file,
#                     language="en",      # 🔥 Force English
#                     task="transcribe",  # 🔥 Ensure no translation
#                     fp16=False          # 🔥 Important on CPU (Windows)
#                 )
#         voice_prompt = result["text"].strip()


#         # Show user message
#         with st.chat_message("user"):
#             st.markdown(voice_prompt)

#         st.session_state.chat_messages.append({
#             "role": "user",
#             "content": voice_prompt
#         })

#         # Get assistant response
#         with st.chat_message("assistant"):
#             with st.spinner("Analyzing..."):
#                 result = qa_chain({"question": f"Answer this medical question directly and concisely:\n\n{voice_prompt}"
# })

#                 response = result["answer"]
#                 st.markdown(response)

#         st.session_state.chat_messages.append({
#             "role": "assistant",
#             "content": response
#         })

#     if prompt := st.chat_input("Ask a question about this case..."):

#         with st.chat_message("user"):
#             st.markdown(prompt)

#         st.session_state.chat_messages.append({
#             "role": "user",
#             "content": prompt
#         })

#         with st.chat_message("assistant"):
#             with st.spinner("Analyzing..."):
#                 result = qa_chain({"question": f"Answer this medical question directly and concisely:\n\n{prompt}"
# })

#                 response = result["answer"]
#                 st.markdown(response)

#         st.session_state.chat_messages.append({
#             "role": "assistant",
#             "content": response
#         })


# if __name__ == "__main__":
#     main()
   



import streamlit as st
import os
from dotenv import load_dotenv
# from streamlit_mic_recorder import mic_recorder
import whisper


# ==============================
# Load Environment Variables
# ==============================
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    st.error("🚨 OPENAI_API_KEY not found. Please add it to your .env file.")
    st.stop()

# Backend
from scripts.main import process_pdf, process_audio
from scripts.audio.mic_recorder import record_audio

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
        border-radius: 8px; 
        font-weight: 600; 
        height: 3em; 
    }
    .input-card { 
        padding: 20px; 
        border: 1px solid #e6e9ef;
        border-radius: 10px; 
        background-color: #ffffff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* -------------------------------------- */
    /* Pill Design Chat Input Box             */
    /* -------------------------------------- */
    /* Target the container to make it a pill */
    [data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 25px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 100% !important;
        max-width: 704px !important; /* Matches Streamlit chat messages */
        background-color: #303134 !important;
        padding: 5px 25px !important;
        border-radius: 50px !important;
        border: none !important;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.4) !important;
        z-index: 1000 !important;
    }
    
    /* Force inner components to be transparent to fix the differently colored rectangle */
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] > div > div {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* Style the text area inside the pill */
    [data-testid="stChatInputTextArea"] {
        background-color: transparent !important;
        color: #e8eaed !important;
        font-size: 16px !important;
        padding-top: 15px !important;
        padding-right: 50px !important; /* make room for mic */
    }
    
    /* Streamlit's record button styled as the mic icon, absolute positioned inside the pill */
    div[data-testid="stElementContainer"]:has(#mic_btn_wrapper) + div[data-testid="stElementContainer"] {
        position: fixed !important;
        bottom: 37px !important; 
        left: calc(50% + 245px) !important; /* Positioned closely to the left side of the arrow */
        z-index: 1001 !important;
    }
    div[data-testid="stElementContainer"]:has(#mic_btn_wrapper) + div[data-testid="stElementContainer"] button {
        background-color: transparent !important;
        color: #9aa0a6 !important;
        border: none !important;
        padding: 0 !important;
        box-shadow: none !important;
        font-size: 22px !important;
    }
    div[data-testid="stElementContainer"]:has(#mic_btn_wrapper) + div[data-testid="stElementContainer"] button:hover {
        color: #ffffff !important;
        background-color: #4a4b50 !important;
        border-radius: 50% !important;
    }
    
    /* Style the submit icon to match the white circle with icon */
    [data-testid="stChatInputSubmitButton"] {
        background-color: #ffffff !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        margin-left: 15px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    [data-testid="stChatInputSubmitButton"] svg {
        fill: #000000 !important;
        color: #000000 !important;
        width: 20px !important;  
        height: 20px !important;
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
        "chat_messages": []
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

        tab1, tab2 = st.tabs(["👤 Patient Summary", "🩺 Doctor Summary"])

        with tab1:
            st.info(st.session_state.patient_res)
            st.download_button(
                "📩 Download Patient Summary",
                st.session_state.patient_res,
                file_name=f"patient_summary_{target_lang_code}.txt"
            )

        with tab2:
            st.info(st.session_state.doctor_res)

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

     
    # ==============================
    # 🎤 Voice Question (Integrated into Pill)
    # ==============================
    st.markdown('<div id="mic_btn_wrapper"></div>', unsafe_allow_html=True)

    if st.button("🎙️", key="chat_record_btn"):

        # Hardcoded duration for simplicity since slider is removed
        with st.spinner("Recording..."):
            voice_file = record_audio(
                output_file="voice_question.wav",
                duration=5
            )

        # Transcribe using improved Whisper settings
        with st.spinner("Transcribing..."):

            model = whisper.load_model("small")  # more accurate than base

            result = model.transcribe(
                voice_file,
                language="en",
                task="transcribe",
                temperature=0.0,
                beam_size=5,
                best_of=5,
                fp16=False
            )

        voice_prompt = result["text"].strip()

        # Display EXACT transcription
        with st.chat_message("user"):
            st.markdown(voice_prompt)

        st.session_state.chat_messages.append({
            "role": "user",
            "content": voice_prompt
        })

    # Send clean question to RAG
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                result = st.session_state.qa_chain.invoke({
                    "question": voice_prompt
                })
                response = result["answer"]
                st.markdown(response)

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": response
        })

    if prompt := st.chat_input("Ask anything"):

        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.chat_messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                result = st.session_state.qa_chain.invoke({"question": f"Answer this medical question directly and concisely:\n\n{prompt}"})
            response = result["answer"]
            st.markdown(response)

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": response
        })


if __name__ == "__main__":
    main()