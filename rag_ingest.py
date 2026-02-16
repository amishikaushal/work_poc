import os
import shutil
import time
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings  # ✅ Updated import

# Get current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Explicit input files
INPUT_FILES = [
    os.path.join(BASE_DIR, "output", "transcript.txt"),
    os.path.join(BASE_DIR, "output", "doctor_summary.txt"),
    os.path.join(BASE_DIR, "output", "patient_summary.txt"),
]

documents = []

for file_path in INPUT_FILES:
    if not os.path.exists(file_path):
        print(f"⚠ File not found: {file_path}")
        continue

    if file_path.endswith(".txt"):
        loader = TextLoader(file_path, encoding="utf-8")
        documents.extend(loader.load())

    elif file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
        documents.extend(loader.load())

print("Total documents loaded:", len(documents))

if len(documents) == 0:
    print("❌ No valid input files found.")
    exit()

# Split documents
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150
)

docs = splitter.split_documents(documents)

# Embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Safe delete old RAG index
index_path = os.path.join(BASE_DIR, "rag_index")

if os.path.exists(index_path):
    print("🗑 Attempting to delete old RAG index...")

    for i in range(3):  # retry 3 times
        try:
            shutil.rmtree(index_path)
            print("✅ Old RAG index deleted.")
            break
        except PermissionError:
            print("⚠ Index in use. Retrying...")
            time.sleep(2)
    else:
        print("❌ Could not delete rag_index. Close Streamlit or any running app and try again.")
        exit()

# Create FAISS index
vectorstore = FAISS.from_documents(docs, embeddings)

# Save fresh index
vectorstore.save_local("rag_index")

print("✅ RAG index created successfully from transcript + summaries!")

