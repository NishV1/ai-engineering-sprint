import os
import time
import requests
import streamlit as st

# FastAPI Backend Base URL (defaults to localhost for local dev, or http://backend:8000 in Docker)
API_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

API_URL = f"{API_BASE_URL}/query"
UPLOAD_URL = f"{API_BASE_URL}/upload"
FILES_URL = f"{API_BASE_URL}/files"

def wait_for_backend():
    """Blocks UI and displays a loading animation until FastAPI backend is fully initialized."""
    if "backend_ready" not in st.session_state:
        st.session_state.backend_ready = False

    if not st.session_state.backend_ready:
        with st.status("🚀 Booting Air-Gapped RAG Backend...", expanded=True) as status:
            st.write("📦 Loading SentenceTransformers & Cross-Encoder models into memory...")
            st.write("🔌 Connecting to PostgreSQL & indexing BM25 corpus...")
            
            while not st.session_state.backend_ready:
                try:
                    res = requests.get(f"{API_BASE_URL}/health", timeout=3)
                    if res.status_code == 200 and res.json().get("status") == "ready":
                        st.session_state.backend_ready = True
                        status.update(label="✅ Backend Ready! You can now ingest files or ask questions.", state="complete", expanded=False)
                        break
                except Exception:
                    pass
                time.sleep(2)

# Call at the top of the UI layout
wait_for_backend()

st.set_page_config(
    page_title="Air-Gapped Hybrid RAG Explorer",
    page_icon="🤖",
    layout="centered"
)

st.title("🛡️ Air-Gapped Hybrid RAG Assistant")
st.markdown("Ask questions about your ingested documentation. Powered by Hybrid Search (Vector + BM25), Cross-Encoder Reranking, and local Llama 3.2.")

# --- Sidebar for Dynamic Document Ingestion ---
st.sidebar.header("📁 Document Ingestion")
uploaded_file = st.sidebar.file_uploader("Upload a PDF Manual", type=["pdf"])

if uploaded_file is not None:
    if st.sidebar.button("Ingest Document"):
        with st.spinner("Processing, vectorizing, and indexing document..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                response = requests.post(UPLOAD_URL, files=files, timeout=300)
                
                if response.status_code == 200:
                    data = response.json()
                    st.sidebar.success(f"✅ Ingested {data['filename']} ({data['chunks_ingested']} chunks)!")
                    st.rerun()  # Forces immediate sidebar reload to display updated inventory
                else:
                    error_detail = response.json().get("detail", "Unknown error")
                    st.sidebar.error(f"❌ Ingestion failed: {error_detail}")
            except requests.exceptions.ConnectionError:
                st.sidebar.error("Could not connect to FastAPI backend.")
            except Exception as e:
                st.sidebar.error(f"An error occurred: {e}")

# --- Sidebar File Inventory & Document Scoping ---
st.sidebar.divider()
st.sidebar.subheader("📚 Active Documents")

active_files = []
try:
    # Uses dynamic FILES_URL instead of hardcoded 127.0.0.1
    res = requests.get(FILES_URL, timeout=5)
    if res.status_code == 200:
        active_files = res.json().get("files", [])
        if active_files:
            for f in active_files:
                st.sidebar.text(f"• {f}")
        else:
            st.sidebar.info("No active documents in database.")
    else:
        st.sidebar.text("Could not fetch file list.")
except Exception:
    st.sidebar.text("Could not fetch file list.")

# Target Document Selector
st.sidebar.divider()
selected_doc = st.sidebar.selectbox(
    "Query Target Document:",
    ["All Ingested Documents"] + active_files
)

target_file = None if selected_doc == "All Ingested Documents" else selected_doc

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            st.caption(f"**Sources Referenced:** {', '.join(message['sources'])}")

# Accept user input
if prompt := st.chat_input("Ask a question about your docs..."):
    # Add user message to state and display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call FastAPI backend with query and target document scope
    with st.chat_message("assistant"):
        with st.spinner("Executing hybrid retrieval, reranking, and synthesis..."):
            try:
                payload = {
                    "query": prompt,
                    "selected_file": target_file
                }
                response = requests.post(API_URL, json=payload, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer returned.")
                    sources = data.get("sources", [])
                    
                    st.markdown(answer)
                    if sources:
                        st.caption(f"**Sources Referenced:** {', '.join(sources)}")
                    
                    # Save assistant response to state
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                else:
                    error_detail = response.json().get("detail", "Unknown server error")
                    st.error(f"API Error ({response.status_code}): {error_detail}")
            
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the FastAPI backend. Verify backend container status.")
            except Exception as e:
                st.error(f"An error occurred: {e}")