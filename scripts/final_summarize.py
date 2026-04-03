# # import os
# # import sys
# # import google.generativeai as genai

# # # --- PATH CONFIGURATION ---
# # # This ensures it finds the output folder inside D:\POCwork
# # script_dir = os.path.dirname(os.path.abspath(__file__))
# # project_root = os.path.abspath(os.path.join(script_dir, ".."))

# # INPUT_FILE = os.path.join(project_root, "output", "transcript.txt")
# # OUTPUT_FILE_DOC = os.path.join(project_root, "output", "doc.txt")
# # OUTPUT_FILE_PAT = os.path.join(project_root, "output", "patient.txt")

# # # Gemini Setup
# # API_KEY = "AIzaSyDYPeL_GmL8rfA-BZh4-7fnUZxBHO8yjYU" 
# # genai.configure(api_key=API_KEY)

# # def run_summarization():
# #     # 1. Check if input file exists
# #     if not os.path.exists(INPUT_FILE):
# #         print(f"Waiting for input file: {INPUT_FILE}...")
# #         return

# #     # 2. Read the input transcript
# #     with open(INPUT_FILE, "r", encoding="utf-8") as f:
# #         conversation_text = f.read()

# #     # 3. Prepare Prompt
# #     prompt = f"""
# #     Analyze the following medical input and generate two summaries.
# #     Format your response with markers [DOC_START], [DOC_END], [PAT_START], and [PAT_END].

# #     Input Content:
# #     {conversation_text}

# #     ### 1. CLINICAL DOCTOR SUMMARY (Professional Tone)
# #     [DOC_START]
# #     - Chief Complaint:
# #     - Diagnosis:
# #     - Treatment Plan:
# #     - Action Plan:
# #     [DOC_END]

# #     ### 2. PATIENT ACTION PLAN (Simple Language)
# #     [PAT_START]
# #     - Summary of Visit:
# #     - Medication Schedule:
# #     - Next Steps:
# #     [PAT_END]
# #     """

# #     # 4. Generate using Gemini
# #     print("Gemini is processing the data...")
    
# #     # UPDATED: Using 'gemini-1.5-flash-latest' to avoid 404 errors
# #     model = genai.GenerativeModel('gemini-1.5-flash')
    
# #     try:
# #         response = model.generate_content(prompt)
# #         full_output = response.text

# #         # 5. Parse and Save
# #         if "[DOC_START]" in full_output and "[PAT_START]" in full_output:
# #             doc_summary = full_output.split("[DOC_START]")[1].split("[DOC_END]")[0].strip()
# #             pat_summary = full_output.split("[PAT_START]")[1].split("[PAT_END]")[0].strip()

# #             # Save Doctor Summary
# #             with open(OUTPUT_FILE_DOC, "w", encoding="utf-8") as f:
# #                 f.write(f"### 1. CLINICAL DOCTOR SUMMARY\n{doc_summary}")

# #             # Save Patient Summary
# #             with open(OUTPUT_FILE_PAT, "w", encoding="utf-8") as f:
# #                 f.write(f"### 2. PATIENT ACTION PLAN\n{pat_summary}")

# #             print(f"Success! Summaries saved to {OUTPUT_FILE_DOC} and {OUTPUT_FILE_PAT}")
# #         else:
# #             print("Error: Gemini response was not in the expected format.")

# #     except Exception as e:
# #         print(f"Error during processing: {e}")

# # if __name__ == "__main__":
# #     # Ensure output directory exists in project root
# #     output_dir = os.path.join(project_root, "output")
# #     if not os.path.exists(output_dir):
# #         os.makedirs(output_dir)
        
# #     run_summarization()




# from langchain_groq import ChatGroq
# from langchain_core.messages import HumanMessage, SystemMessage

 
# llm = ChatGroq(
#     model="llama-3.1-8b-instant",
#     temperature=0,
#     max_tokens=None,
#     timeout=None,
#     max_retries=2,
#     api_key='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'
#     # other params...
# )




# messages = [
#     SystemMessage(
#         content="You are an expert assistant that summarizes text clearly and concisely."
#     ),
#     HumanMessage(
#         content="""
#         Artificial Intelligence has seen rapid growth in recent years.
#         It is now widely used in healthcare, finance, education,
#         and autonomous systems. However, ethical concerns such as
#         bias, transparency, and accountability remain important challenges.
#         """
#     )
# ]

# summary = llm.invoke(messages)
# print(summary.content)



# import os
# import google.generativeai as genai

# # --- 1. SETUP ---
# # Apni API Key yahan dalein
# API_KEY = "AIzaSyDYPeL_GmL8rfA-BZh4-7fnUZxBHO8yjYU" 
# genai.configure(api_key=API_KEY)

# # --- 2. PATHS (Folder Structure) ---
# # Hum 'output' folder ke andar 'transcript.txt' dhoondenge
# BASE_DIR = "output"
# INPUT_FILE = os.path.join(BASE_DIR, "transcript.txt") 
# OUTPUT_FILE_DOC = os.path.join(BASE_DIR, "doc.txt")
# OUTPUT_FILE_PAT = os.path.join(BASE_DIR, "patient.txt")

# # --- 3. AUTO-DETECT FUNCTION (No More 404 Errors) ---
# def get_available_model():
#     """Automatically finds a working model name for your account"""
#     print("🔍 Searching for available models...")
#     try:
#         for m in genai.list_models():
#             if 'generateContent' in m.supported_generation_methods:
#                 print(f"   Found active model: {m.name}")
#                 return m.name # Pehla working model return karega
#     except Exception as e:
#         print(f"   Could not list models: {e}")
    
#     return 'models/gemini-pro' # Fallback

# def run_summarization():
#     # 1. File Safety Check
#     if not os.path.exists(INPUT_FILE):
#         print(f"❌ Error: File nahi mili: {INPUT_FILE}")
#         print(f"   Make sure 'output' folder ke andar 'transcript.txt' hai.")
#         return

#     # 2. Read the input transcript
#     print(f"📖 Reading file: {INPUT_FILE}...")
#     with open(INPUT_FILE, "r", encoding="utf-8") as f:
#         conversation_text = f.read()

#     # 3. Model Selection
#     valid_model_name = get_available_model()
#     print(f"🚀 Using Model: {valid_model_name}")
#     model = genai.GenerativeModel(valid_model_name)

#     # 4. Detailed Prompt (Aapka Pasandeeda Format)
#     prompt = f"""
#     You are a highly skilled Medical Scribe. Your task is to analyze the provided medical conversation and generate two distinct, high-quality summaries.

#     ### INSTRUCTIONS:
#     1. **Clinical Doctor Summary**: Use professional, technical medical terminology. Focus on clinical findings, specific dosages, and professional next steps.
#     2. **Patient Action Plan**: Use simple, empathetic, and non-technical language (8th-grade reading level). Focus on clear instructions, what the patient needs to do at home, and simple explanations of medications.

#     ### FORMATTING RULES:
#     - Use bullet points with dashes (-) for each item.
#     - Strictly enclose the summaries within the markers [DOC_START], [DOC_END], [PAT_START], and [PAT_END].

#     ### EXAMPLE (FEW-SHOT):
#     Conversation: "Patient reports headaches. BP is 150/95. I'll add Amlodipine 5mg to your Atenolol 50mg."
#     [DOC_START]
#     - Chief Complaint: Frequent Headaches
#     - Diagnosis: Hypertension (high blood pressure)
#     - Treatment Plan: Continue Atenolol 50 mg once daily, add Amlodipine 5 mg once daily
#     - Action Plan: Monitor blood pressure, limit sodium intake.
#     [DOC_END]
#     [PAT_START]
#     - Summary of Visit: You have high blood pressure which is causing your headaches.
#     - Medication Schedule: Keep taking Atenolol 50mg once a day. Add the new pill, Amlodipine 5mg, once a day.
#     - Next Steps: Record your blood pressure daily. Use less salt in your food.
#     [PAT_END]

#     ### ACTUAL INPUT CONTENT:
#     {conversation_text}

#     ### OUTPUT:
#     Generate the summaries for the input provided above.
#     """
#     # 5. Generation & Saving
#     try:
#         print("⏳ AI is thinking...")
#         response = model.generate_content(prompt)
#         full_output = response.text

#         # Parsing Logic
#         try:
#             doc_summary = full_output.split("[DOC_START]")[1].split("[DOC_END]")[0].strip()
#             pat_summary = full_output.split("[PAT_START]")[1].split("[PAT_END]")[0].strip()
#         except:
#             print("⚠️ Markers missing. Saving raw output.")
#             doc_summary = full_output
#             pat_summary = "Check doc.txt"

#         # Save Doctor Summary
#         with open(OUTPUT_FILE_DOC, "w", encoding="utf-8") as f:
#             f.write(f"### 1. CLINICAL DOCTOR SUMMARY\n{doc_summary}")

#         # Save Patient Summary
#         with open(OUTPUT_FILE_PAT, "w", encoding="utf-8") as f:
#             f.write(f"### 2. PATIENT ACTION PLAN\n{pat_summary}")

#         print("\n✅ SUCCESS!")
#         print(f"   Doctor File:  {OUTPUT_FILE_DOC}")
#         print(f"   Patient File: {OUTPUT_FILE_PAT}")

#     except Exception as e:
#         print(f"\n❌ API Error: {e}")

# if __name__ == "__main__":
#     # Ensure output directory exists
#     if not os.path.exists("output"):
#         os.makedirs("output")
        
#     run_summarization()

import os
import requests
import re

# --- CONFIGURATION ---
API_KEY = "sk_lj92wr1i_R7P7HB77NAGA9T3O6yJRL96k"  # replace with your actual key
API_URL = "https://api.sarvam.ai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# --- CLEANING FUNCTION ---
def clean_response(text: str) -> str:
    """
    Removes <think>...</think> and any unwanted tags from model output
    """
    # Remove <think>...</think> blocks
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

    # Remove any remaining HTML/XML-like tags
    text = re.sub(r"<.*?>", "", text)

    return text.strip()


def run_summarization(text: str, perspective: str) -> str:
    """
    Summarize text into a specific perspective using Sarvam AI.
    perspective: "Patient" or "Doctor"
    """
    if not text.strip():
        return "Error: No input text provided for summarization."

    payload = {
        "model": "sarvam-m",
        "messages": [
            {
                "role": "system",
                "content": (
                    f"You are a professional medical scribe. "
                    f"Provide ONLY a clean and concise {perspective} perspective summary. "
                    f"Do NOT include thinking steps, reasoning, or any tags like <think>."
                )
            },
            {
                "role": "user",
                "content": f"Summarize the following medical consultation for a {perspective}:\n{text}"
            }
        ],
        "temperature": 0.3,
        "max_tokens": 500
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            data = response.json()
            raw_output = data["choices"][0]["message"]["content"]

            # ✅ CLEAN OUTPUT HERE
            cleaned_output = clean_response(raw_output)

            return cleaned_output

        else:
            return f"Error {response.status_code}: {response.text}"

    except Exception as e:
        return f"Request failed: {str(e)}"


if __name__ == "__main__":
    # 1. Locate current script directory
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # 2. Setup paths
    output_dir = os.path.abspath(os.path.join(base_dir, "..", "output"))
    INPUT_PATH = os.path.join(output_dir, "transcript.txt")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # 3. Read input
    if os.path.exists(INPUT_PATH):
        with open(INPUT_PATH, "r", encoding="utf-8") as f:
            input_text = f.read()

        print(f"✅ Loaded transcript from: {INPUT_PATH}")

        # 4. Generate summaries
        print("🧠 Generating Patient Perspective...")
        patient_summary = run_summarization(input_text, "Patient")

        print("🧠 Generating Doctor Perspective...")
        doctor_summary = run_summarization(input_text, "Doctor")

        # 5. Output files
        pat_out = os.path.join(output_dir, "patient_summary.txt")
        doc_out = os.path.join(output_dir, "doctor_summary.txt")

        with open(pat_out, "w", encoding="utf-8") as f:
            f.write(patient_summary)

        with open(doc_out, "w", encoding="utf-8") as f:
            f.write(doctor_summary)

        print("\n✅ SUCCESS!")
        print(f"📄 Patient Summary: {pat_out}")
        print(f"📄 Doctor Summary:  {doc_out}")

    else:
        print(f"❌ Error: transcript.txt not found at {INPUT_PATH}")