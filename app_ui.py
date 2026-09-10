import streamlit as st
import requests

# FastAPI Backend Endpoints
API_URL = "http://127.0.0.1:8000/query"
UPLOAD_URL = "http://127.0.0.1:8000/upload"

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
                else:
                    error_detail = response.json().get("detail", "Unknown error")
                    st.sidebar.error(f"❌ Ingestion failed: {error_detail}")
            except requests.exceptions.ConnectionError:
                st.sidebar.error("Could not connect to FastAPI backend.")
            except Exception as e:
                st.sidebar.error(f"An error occurred: {e}")

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

    # Call FastAPI backend
    with st.chat_message("assistant"):
        with st.spinner("Executing hybrid retrieval, reranking, and synthesis..."):
            try:
                response = requests.post(API_URL, json={"query": prompt}, timeout=60)
                
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
                st.error("Could not connect to the FastAPI backend. Make sure `uvicorn app:app --reload` is running!")
            except Exception as e:
                st.error(f"An error occurred: {e}")

# --- Sidebar File Inventory ---
st.sidebar.divider()
st.sidebar.subheader("📚 Active Documents")
try:
    res = requests.get("http://127.0.0.1:8000/files")
    if res.status_code == 200:
        active_files = res.json().get("files", [])
        for f in active_files:
            st.sidebar.text(f"• {f}")
except:
    st.sidebar.text("Could not fetch file list.")