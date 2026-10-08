"""
Simple Streamlit client for the Financial Advisory Bot.
Talks to the backend exclusively through the REST API — no RAG logic here.
Run with: streamlit run frontend/streamlit_app.py
"""
import uuid

import requests
import streamlit as st
API_BASE_URL = "http://localhost:8000"
st.set_page_config(page_title="Financial Advisory Bot", page_icon="💰", layout="centered")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("💰 Financial Advisory Bot")
st.caption("RAG-powered assistant for financial news, banking, and general investment education.")

with st.sidebar:
    st.subheader("Session")
    st.text(f"ID: {st.session_state.session_id[:8]}...")
    if st.button("🆕 New Conversation"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.subheader("Knowledge Base")
    if st.button("📥 Ingest latest financial news"):
        with st.spinner("Fetching and storing financial news..."):
            try:
                r = requests.post(f"{API_BASE_URL}/api/v1/ingest", json={}, timeout=30)
                r.raise_for_status()
                st.success(f"Ingested: {r.json()}")
            except requests.RequestException as e:
                st.error(f"Ingestion failed: {e}")

    if st.button("🧩 Index documents into vector store"):
        with st.spinner("Chunking + embedding documents..."):
            try:
                r = requests.post(f"{API_BASE_URL}/api/v1/index", json={}, timeout=60)
                r.raise_for_status()
                st.success(f"Indexed: {r.json()}")
            except requests.RequestException as e:
                st.error(f"Indexing failed: {e}")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("📚 Sources"):
                for s in msg["sources"]:
                    st.markdown(f"- **{s.get('source', 'Unknown')}** — {s.get('title', '')}  \n{s.get('url', '')}")

question = st.chat_input("Ask a financial question...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("_Thinking..._")
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/chat",
                json={"session_id": st.session_state.session_id, "question": question},
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            answer = data["answer"]
            sources = data.get("sources", [])

            placeholder.markdown(answer)
            if sources:
                with st.expander("📚 Sources"):
                    for s in sources:
                        st.markdown(f"- **{s.get('source', 'Unknown')}** — {s.get('title', '')}  \n{s.get('url', '')}")

            st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
        except requests.RequestException as e:
            error_msg = f"⚠️ Could not reach the assistant backend: {e}"
            placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
