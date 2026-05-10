# 🏥 Medical AI Scribe — Complete Codebase Explained

This is a **Proof-of-Concept (POC)** Medical AI Scribe application. It takes either a **PDF medical report** or a **recorded/uploaded audio consultation** and automatically generates two summaries (one for the Patient, one for the Doctor), then lets you chat with the data using a RAG-powered chatbot.

---

## 📁 Project Structure Overview

```
work_poc/
├── app.py                        ← Main Streamlit UI (entry point)
├── rag_ingest.py                 ← Standalone script to rebuild the RAG index
├── generate_french_report.py     ← Test data generator (French PDF)
├── generate_spanish_report.py    ← Test data generator (Spanish PDF)
├── requirements.txt              ← Core Python dependencies
├── requirements_audio.txt        ← Audio-specific dependencies
├── .env                          ← Secret API keys (never commit this)
├── .gitignore                    ← Files Git should ignore
├── input/                        ← Sample input PDFs and audio files
├── output/                       ← All generated text outputs (transcripts, summaries)
└── scripts/
    ├── __init__.py               ← Makes 'scripts' a Python package
    ├── main.py                   ← Orchestrates PDF and Audio pipelines
    ├── final_summarize.py        ← Calls Sarvam AI to generate summaries
    ├── preprocess.py             ← Cleans raw OCR text from PDFs
    ├── translate_utils.py        ← Language detection + Google Translate
    └── audio/
        ├── __init__.py           ← Makes 'audio' a Python sub-package
        ├── audio_preprocess.py   ← Converts any audio to 16kHz mono WAV
        ├── diarization.py        ← Splits audio by speaker (who spoke when)
        ├── transcription.py      ← Converts speech to English text
        ├── role_inference.py     ← Labels speakers as Doctor or Patient
        └── mic_recorder.py       ← Records audio from microphone
```

---

## 🔑 `.env` — Environment Variables

```
OPENAI_API_KEY=sk-proj-...
SARVAM_API_KEY=sk_lj92wr1i_...
```

**What it is:** A plain text file that stores secret API keys.

**Why we use it:** Hard-coding API keys directly in Python files is a major security risk. This file is loaded by the `python-dotenv` library at runtime. It is listed in `.gitignore` so it is never accidentally pushed to GitHub.

- `OPENAI_API_KEY` — Used by LangChain for any OpenAI-based operations.
- `SARVAM_API_KEY` — Used to call the Sarvam AI API for medical summarisation.

---

## 📦 `requirements.txt` — Core Dependencies

| Package | Why it's used |
|---|---|
| `pdf2image` | Converts each PDF page into a PIL image so Tesseract can read it |
| `pytesseract` | Python wrapper for Tesseract OCR engine — reads text from images |
| `Pillow` | Image processing library required by pdf2image |
| `langdetect` | Detects language of text (English, French, Spanish, etc.) |
| `deep-translator` | An alternative translator (present but Google Translate API used directly) |
| `requests` | Makes HTTP calls to Google Translate and Sarvam AI |
| `langchain` | Framework for building LLM-powered chains and agents |
| `langchain-community` | Community integrations: FAISS vectorstore, ChatOllama |
| `langchain-text-splitters` | Splits long documents into smaller chunks for embedding |
| `langchain-huggingface` | HuggingFace embedding model integration for LangChain |
| `sentence-transformers` | Provides the `all-MiniLM-L6-v2` embedding model |
| `faiss-cpu` | Facebook AI Similarity Search — stores and searches text embeddings |
| `streamlit` | Builds the entire web UI with pure Python |
| `python-dotenv` | Loads `.env` file variables into `os.getenv()` |

## 📦 `requirements_audio.txt` — Audio Dependencies

| Package | Why it's used |
|---|---|
| `torch` / `torchaudio` | Deep learning framework required by NeMo and Whisper |
| `nemo_toolkit[asr]` | NVIDIA NeMo — provides the Sortformer diarization model |
| `openai-whisper` | OpenAI's speech-to-text model (fallback if faster-whisper missing) |
| `pydub` | Slices audio segments by timestamp (millisecond precision) |
| `soundfile` | Reads and writes WAV files |
| `librosa` | Audio analysis utilities |
| `noisereduce` | Reduces background noise from recordings |
| `sounddevice` | Records audio directly from the system microphone |
| `faster-whisper` | Optimized version of Whisper (runs on CPU with int8 quantization) |

---

## 🚀 `app.py` — Main Application (Entry Point)

This is the **heart of the application**. Running `streamlit run app.py` launches the entire UI.

### Lines 1–19: Imports and Startup Checks
```python
import logging
import streamlit as st
import whisper
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s")
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    st.error("🚨 OPENAI_API_KEY not found.")
    st.stop()
```
- `logging.basicConfig(...)` — Sets up a single consistent log format for the **entire** application. Every module uses `getLogger(__name__)` which inherits this config.
- `load_dotenv()` — Reads `.env` file and injects keys into the process environment.
- The API key check with `st.stop()` — Prevents the app from running at all if the key is missing. Fails fast.

### Lines 62–71: Cached Resource Loaders
```python
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("small")

@st.cache_resource
def load_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
```
**Why `@st.cache_resource`?** Streamlit re-runs the entire Python script on every user interaction. Without caching, it would reload the Whisper model (hundreds of MB) and the embedding model **on every button click**. `@st.cache_resource` loads them **once per server session** and reuses the object — drastically reducing latency.

### Lines 75–89: `build_rag_chain()` — Builds the Chatbot
```python
def build_rag_chain(patient_text, doctor_text):
    docs = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
              .split_documents([Document(page_content=patient_text),
                                Document(page_content=doctor_text)])
    vectorstore = FAISS.from_documents(docs, load_embeddings())
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    return ConversationalRetrievalChain.from_llm(
        llm=ChatOllama(model="llama3", temperature=0),
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        memory=memory,
    )
```
**Step by step:**
1. **Text splitting** — The two summaries are broken into overlapping chunks of 800 characters (overlap=150 ensures no sentence is cut off at a boundary).
2. **FAISS vectorstore** — Each chunk is converted to a numerical vector (embedding) and stored in a FAISS index for ultra-fast similarity search.
3. **ConversationBufferMemory** — Keeps the full chat history so follow-up questions have context.
4. **ConversationalRetrievalChain** — When a user asks a question: (a) find the 3 most relevant chunks from FAISS, (b) pass them + the question to the LLaMA3 model running locally via Ollama.
5. **`temperature=0`** — Makes LLaMA3 deterministic (no random creativity) — important for accurate medical information.

### Lines 93–103: `_init_session()`
```python
def _init_session():
    defaults = {"final_audio_path": None, "patient_res": None, 
                "doctor_res": None, "qa_chain": None, "chat_messages": []}
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
```
Streamlit is stateless — each interaction re-runs the script. `st.session_state` is a dictionary that **persists across re-runs**. This function initialises all required keys only if they don't already exist (so it won't reset them on every click).

### Lines 107–263: `main()` — The UI

#### Sidebar
```python
lang_map = {"English": "en", "French": "fr", "Spanish": "es"}
selected_lang = st.selectbox("Output Language", list(lang_map.keys()))
```
The user can choose what language the final summaries are output in.

#### Input Section (Two Columns)
- **Column 1 (PDF):** `st.file_uploader` for a PDF. When uploaded, it's written to disk as `process_input.pdf` and passed to `process_pdf()`.
- **Column 2 (Audio):** Radio button selects between "Upload File" or "Record Live":
  - **Upload:** Saves to a temp file, stores path in session state.
  - **Record Live:** Calls `record_audio()` with a user-chosen duration.

#### Generate AI Analysis Button
```python
if st.button("✨ Generate AI Analysis", type="primary"):
```
This is the main action button. It:
1. Calls either `process_pdf()` or `process_audio()` from `scripts/main.py`
2. Gets back `(patient_summary, doctor_summary)` strings
3. Calls `build_rag_chain()` to make the chatbot ready

#### Results Display
Two tabs: **Patient Summary** and **Doctor Summary**, each with a download button.

#### Chatbot Section (Lines 210–263)
Two ways to ask questions:
- **Voice:** Records audio → transcribes with Whisper → sends to RAG chain.
- **Text:** Standard `st.chat_input()` → sends to RAG chain.
Both display the conversation history in a chat bubble format.

---

## 🧠 `scripts/main.py` — Pipeline Orchestrator

This module **coordinates** the full processing pipeline. It never does OCR or AI calls itself — it delegates to specialist modules.

### `_generate_summaries()` — Parallel Summary Generation
```python
with ThreadPoolExecutor(max_workers=2) as pool:
    fut_patient = pool.submit(run_summarization, text, "Patient")
    fut_doctor  = pool.submit(run_summarization, text, "Doctor")
    patient_en  = fut_patient.result()
    doctor_en   = fut_doctor.result()
```
**Why ThreadPoolExecutor?** Both the Patient and Doctor summaries are **independent API calls** to Sarvam AI. Running them sequentially would take 2× as long. `ThreadPoolExecutor` runs both API calls **at the same time** (in parallel threads), halving the wait time.

Then, if a non-English output was selected, it runs **two translation calls in parallel** using the same pattern.

Finally, both summaries are written to `output/patient_summary.txt` and `output/doctor_summary.txt`.

### `process_pdf()` — PDF Pipeline
```
PDF file → convert pages to images → OCR each image → detect language 
→ translate to English (if needed) → clean text → generate summaries
```
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pages = convert_from_path(input_pdf)
full_text = "".join(pytesseract.image_to_string(page, lang="eng+fra+spa") + "\n" for page in pages)
```
- `convert_from_path` — Converts each page of the PDF into a PIL image.
- `pytesseract.image_to_string(page, lang="eng+fra+spa")` — Runs OCR on the image, recognising English, French, and Spanish characters simultaneously.
- After all pages, it detects the language → if not English, translates → cleans → summarises.

### `process_audio()` — Audio Pipeline
```
Audio file → convert to WAV → diarise (who spoke when) 
→ transcribe each segment → infer roles (Doctor/Patient) 
→ save labelled transcript → generate summaries
```

---

## ✨ `scripts/final_summarize.py` — Sarvam AI Summarisation

### Persistent HTTP Session
```python
_session = requests.Session()
_session.headers.update({"Authorization": f"Bearer {_API_KEY}", "Content-Type": "application/json"})
```
**Why `requests.Session()`?** A normal `requests.post()` opens a new TCP connection for every call. A `Session` object **reuses the same TCP/TLS connection** across multiple calls, saving ~200-500ms per request (no repeated TLS handshake). Since Patient and Doctor summaries are called in parallel, this matters.

### `run_summarization(text, perspective)`
```python
payload = {
    "model": "sarvam-m",
    "messages": [
        {"role": "system", "content": f"You are a professional medical scribe. Provide ONLY a clean, concise {perspective} perspective summary..."},
        {"role": "user",   "content": f"Summarize the following medical consultation for a {perspective}:\n{text}"},
    ],
    "temperature": 0.3,
    "max_tokens": 500,
}
```
- **`temperature: 0.3`** — Low randomness. The AI gives focused, factual medical summaries rather than creative responses.
- **`max_tokens: 500`** — Keeps summaries concise, prevents runaway responses.
- **`perspective`** — The same text is summarised twice with different instructions: once "for a Patient" (simple language, what they need to know) and once "for a Doctor" (clinical terminology, diagnoses, prescriptions).

### `_clean_response()`
```python
text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
text = re.sub(r"<.*?>", "", text)
```
Some AI models include internal reasoning tags like `<think>...</think>` in their raw output. This function strips all XML-like tags so only the clean summary text is returned.

---

## 🧹 `scripts/preprocess.py` — OCR Text Cleaner

This runs **after OCR** to clean up noise and errors before sending text to the AI.

### Step 1: Noise Removal
```python
noise_patterns = [r"Regd\. Office:.*", r"Corporate Identity.*", r"Tel:? \+[\d\s-]+", ...]
```
Removes boilerplate text that appears on medical letterheads — office addresses, phone/fax numbers, legal identifiers. These add no clinical value and waste AI tokens.

### Step 2: OCR Correction
```python
corrections = {"Simdmas": "Symptoms", "fibere": "fever", "antibotics": "antibiotics", ...}
```
OCR frequently mis-reads medical terms. `"Simdmas"` is a common OCR error for `"Symptoms"`. These manual corrections fix known mis-reads so the AI receives accurate clinical text.

### Step 3: Semantic Highlighting
```python
headers = ["Diagnosis", "Symptoms", "Prescription", "Treatment", "Next Appointment", ...]
re.sub(rf"^\s*({header})\b", r"[\1]", cleaned_soup, flags=re.IGNORECASE | re.MULTILINE)
```
Section headers like `Diagnosis:` are wrapped in brackets → `[Diagnosis]`. This signals structure to the AI, helping it understand where one section ends and another begins. The `^` anchor ensures only line-starting headers are bracketed (not the word "symptoms" appearing mid-sentence).

### Step 4: Final Cleanup
- Special characters (`|`, `®`, `©`, `»`) → bullet point `•`
- Stray letter `e` at line start (common OCR artifact) → `•`
- Double brackets `[[` → `[` (prevents re-running corruption)
- Multiple blank lines → single newline

---

## 🌐 `scripts/translate_utils.py` — Translation & Language Detection

### `detect_language(text)`
```python
from langdetect import detect
return detect(text[:500])
```
Detects what language the text is in. Only the first 500 characters are checked — enough to detect language without processing the entire document. Returns ISO 639-1 codes: `"en"`, `"fr"`, `"es"`, etc.

### `translate_text(text, source_lang, target_lang)`
```python
_TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"
_MAX_CHUNK_CHARS = 4_500
chunks = [text[i : i + _MAX_CHUNK_CHARS] for i in range(0, len(text), _MAX_CHUNK_CHARS)]
```
**Why chunking?** Google Translate's unofficial endpoint has a character limit per request. Long medical reports are split into 4,500-character chunks, each translated separately, then joined back together. This uses the **unofficial** Google Translate endpoint (no API key needed, free).

### `save_audio_output(segments, role_map, input_file)`
```python
for seg in segments:
    role = role_map.get(seg["speaker"], seg["speaker"])
    f.write(f"{role}: {seg['text']}\n")
```
Writes the diarised + transcribed + role-labelled transcript to `output/transcript.txt` in a readable format like:
```
Doctor: How long have you had this fever?
Patient: About three days now.
```

---

## 🎙️ `scripts/audio/audio_preprocess.py` — Format Converter

```python
subprocess.run(["ffmpeg", "-y", "-i", input_file, "-ac", "1", "-ar", "16000", wav_file], check=True)
```
Uses **FFmpeg** to convert any audio format (MP3, M4A, MP4, etc.) to 16kHz mono WAV. Why?
- `-ac 1` → mono (1 channel) — NeMo diarization and Whisper require mono audio
- `-ar 16000` → 16,000 Hz sample rate — this is the standard for speech recognition models
- `-y` → automatically overwrite if output file already exists
- If the file is already `.wav`, it skips conversion entirely (performance optimisation)

---

## 👥 `scripts/audio/diarization.py` — Who Spoke When

```python
from nemo.collections.asr.models import SortformerEncLabelModel
_diar_model = SortformerEncLabelModel.from_pretrained("nvidia/diar_streaming_sortformer_4spk-v2.1")
```
Uses NVIDIA's **Sortformer** model — a state-of-the-art speaker diarization model that can distinguish up to 4 speakers. "Diarization" means answering: *"who spoke when?"*

**Module-level cache:** `_diar_model = None` at the top, loaded once on first call via `_get_model()`. Prevents re-downloading the model on each call.

**Streaming parameters tuned:**
```python
model.sortformer_modules.chunk_len = 340              # process 340 frames at a time
model.sortformer_modules.chunk_right_context = 40     # look 40 frames ahead
model.sortformer_modules.fifo_len = 40                # frame buffer size
model.sortformer_modules.spkcache_update_period = 300 # refresh speaker profile every 300 frames
```
These settings balance **accuracy vs. latency** for the streaming mode.

**Output:** A list of dicts like `[{"start": 0.5, "end": 3.2, "speaker": "speaker_0"}, ...]`

---

## 📝 `scripts/audio/transcription.py` — Speech to Text

### Dual Backend Strategy
```python
try:
    from faster_whisper import WhisperModel as _FasterWhisperModel
    _USE_FASTER = True
except ImportError:
    import whisper as _openai_whisper
    _USE_FASTER = False
```
**Why two backends?** `faster-whisper` is significantly faster than the original `openai-whisper` (uses CTranslate2 with int8 quantization). If it's installed, use it; if not, silently fall back to the standard version. This makes the code robust across different environments.

### `transcribe_segments(wav_file, diarized_segments)`
For each diarized segment (a time window of one speaker):
```python
chunk = audio[int(seg["start"] * 1000) : int(seg["end"] * 1000)]  # slice by milliseconds
samples = np.array(chunk.get_array_of_samples())
audio_np = samples.astype(np.float32) / float(2 ** (8 * chunk.sample_width - 1))  # normalise to [-1, 1]
```
- **pydub** slices the audio by timestamp (in milliseconds).
- The raw samples are normalised to the `[-1.0, 1.0]` float range that Whisper expects.
- **`task="translate"`** — Whisper translates directly to **English** regardless of what language was spoken. This is a key feature — no separate translation step needed for audio.

### `transcribe_file(wav_file)` 
A simpler function that transcribes an entire file at once (used in the chatbot voice question feature).

---

## 🕵️ `scripts/audio/role_inference.py` — Doctor vs Patient Detection

```python
_DOCTOR_KEYWORDS = ["since when", "how long", "do you have", "any history",
                    "diagnosis", "treatment", "prescribe", "recommend", "you should"]
```
After transcription, we know *who* spoke but not *which role* they play. This module uses **keyword scoring** — doctors statistically use clinical question phrases, while patients describe their symptoms.

```python
scores = {spk: _doctor_score(txt) for spk, txt in speaker_text.items()}
doctor_speaker = max(scores, key=scores.get)
role_map = {spk: "Doctor" if spk == doctor_speaker else "Patient" for spk in scores}
```
The speaker with the highest count of doctor-like keywords is labelled "Doctor". Everyone else is "Patient". Simple and effective for a two-speaker consultation.

---

## 🎤 `scripts/audio/mic_recorder.py` — Microphone Recording

### Fixed-Duration Recording: `record_audio()`
```python
audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
sd.wait()   # blocks until recording is complete
sf.write(output_file, audio, sample_rate)
```
- `sounddevice.rec()` — Captures `duration × 16000` samples from the default microphone.
- `sd.wait()` — Blocks the thread until recording is finished.
- `soundfile.write()` — Saves raw numpy array as a proper WAV file.

### Non-Blocking Recording: `start_recording()` / `stop_recording()`
Uses a background **InputStream** with a callback. Audio frames are collected into `_frames` list as they come in. When `stop_recording()` is called, all frames are concatenated and saved. This allows a "Start/Stop" button pattern in the UI without blocking the interface.

---

## 📊 `rag_ingest.py` — Standalone RAG Index Builder

This is a **utility script** run manually from the command line, not by the main app.

```python
INPUT_FILES = ["output/transcript.txt", "output/doctor_summary.txt", "output/patient_summary.txt"]
```
It loads these three text files, splits them into chunks, embeds them using `all-MiniLM-L6-v2`, and saves a **FAISS vector index** to a folder called `rag_index/`.

**Safe deletion with retry:**
```python
for i in range(3):  # retry 3 times
    try:
        shutil.rmtree(index_path)
        break
    except PermissionError:
        time.sleep(2)  # wait if file is locked
```
On Windows, FAISS index files can be locked by the running Streamlit app. The retry loop waits 2 seconds between attempts.

> Note: The main `app.py` builds the RAG index **in-memory** (no files), so this script is used when you want to persist the index to disk for reuse.

---

## 🧪 `generate_french_report.py` & `generate_spanish_report.py` — Test Data Generators

These scripts create **sample PDF medical reports** in French and Spanish for testing the multilingual pipeline.

```python
from fpdf import FPDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", 'B', 16)
pdf.cell(200, 10, txt="RESUME DE SORTIE MEDICALE", ln=True, align='C')
```
`fpdf` generates PDFs programmatically. They include:
- Patient demographics (name, ID, age, gender, doctor)
- Diagnosis
- Prescribed treatment
- Administrative footer (intentional noise, to test the noise-removal in `preprocess.py`)

**Why these exist:** To test the full OCR → language detection → translation → summarisation pipeline without needing real patient data.

---

## 🔄 How Everything Connects — End-to-End Flow

```
USER uploads PDF
        │
        ▼
   process_pdf()  [scripts/main.py]
        │
        ├─→ pdf2image converts pages to PIL images
        ├─→ pytesseract OCR reads text (English + French + Spanish)
        ├─→ detect_language() [translate_utils.py]
        ├─→ translate_text() if not English [translate_utils.py]
        ├─→ clean_medical_report() [preprocess.py]
        └─→ _generate_summaries() [main.py]
                  │
                  ├─→ run_summarization(text, "Patient") ──┐  [final_summarize.py]
                  ├─→ run_summarization(text, "Doctor")  ──┘  (run in PARALLEL)
                  └─→ translate both if needed (PARALLEL)
                            │
                            ▼
                  Returns (patient_summary, doctor_summary)
                            │
                            ▼
                     build_rag_chain() [app.py]
                            │
                            ├─→ Split summaries into chunks
                            ├─→ Embed with all-MiniLM-L6-v2
                            ├─→ Store in FAISS vectorstore
                            └─→ Chain with LLaMA3 via Ollama
                                        │
                                        ▼
                               User asks a question
                                        │
                               FAISS finds top 3 relevant chunks
                                        │
                               LLaMA3 generates answer
```

```
USER uploads AUDIO
        │
        ▼
   process_audio()  [scripts/main.py]
        │
        ├─→ convert_to_wav() [audio_preprocess.py] — FFmpeg → 16kHz mono WAV
        ├─→ diarize_audio() [diarization.py] — NVIDIA Sortformer → segments with speaker IDs
        ├─→ transcribe_segments() [transcription.py] — Whisper → English text per segment
        ├─→ infer_roles() [role_inference.py] — keyword scoring → Doctor/Patient labels
        ├─→ save_audio_output() [translate_utils.py] — writes transcript.txt
        └─→ _generate_summaries() → same as PDF path above
```
