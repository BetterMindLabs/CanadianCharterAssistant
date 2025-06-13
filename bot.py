import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai

# === Load Gemini API Key from secrets ===
api_key = st.secrets["api_keys"]["google_api_key"]

# === Configure Gemini ===
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# === Function to extract text from a PDF ===
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text

# === Load the Canadian Charter PDF ===
pdf_path = "en3_canadian_charter_qc.pdf"
charter_text = extract_text_from_pdf(pdf_path)

# === Streamlit App UI ===
st.set_page_config(page_title="Canadian Charter RAG Assistant", page_icon="📜", layout="wide")
st.title("📜 Canadian Charter of Rights and Freedoms Assistant")
st.markdown("""
### Ask questions about the Canadian Charter of Rights and Freedoms

This tool provides answers based on the Canadian Charter. Type your question below and get a clear, accurate response grounded in the Charter's content.
""")

# === Chat Session Management ===
if "messages" not in st.session_state:
    st.session_state.messages = []

# === User Input ===
user_input = st.text_input("Your Question:", placeholder="Type your question here...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    # === Gemini Prompt Construction ===
    prompt = [
        "You are an intelligent assistant trained to provide accurate, clear, and Charter-grounded responses to queries about the Canadian Charter of Rights and Freedoms.",
        f"Canadian Charter content:\n{charter_text[:30000]}",  # Limit to avoid excessive context size
        f"User question:\n{user_input}"
    ]

    # === Generate Response ===
    with st.spinner("Generating response..."):
        response = model.generate_content(prompt).text

    st.text_area("Assistant Response:", response, height=200, key=f"response_{len(st.session_state.messages)}")
    st.session_state.messages.append({"role": "assistant", "content": response})

# === Chat History Display ===
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.write(f"**You:** {msg['content']}", key=f"user_{i}")
    else:
        st.write(f"**Assistant:** {msg['content']}", key=f"assistant_{i}")
