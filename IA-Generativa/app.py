"""
app.py
======
Interface do Space Intelligence Assistant.

Duas formas de usar:
  - Aba TEXTO: digita a pergunta e recebe a resposta escrita
  - Aba VOZ:   grava a pergunta por microfone, o sistema transcreve (Whisper),
               responde (RAG) e lê a resposta em voz alta (TTS)

Global Solution 2026 - FIAP - Inteligência Artificial Generativa
"""

import os
import streamlit as st
from dotenv import load_dotenv
from rag_pipeline import RAGPipeline

# Carrega a chave do arquivo .env (se existir) — assim não precisa digitar
load_dotenv()

# ──────────────────────────────────────────────────────────────
# Configuração da página
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Space Intelligence Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# CSS — tema escuro espacial
# ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(160deg, #0a0e27 0%, #131a3a 100%);
    }
    h1, h2, h3 { color: #e8eaf6 !important; }
    .main-header {
        font-size: 2.4rem; font-weight: 800;
        background: linear-gradient(90deg, #6c8cff, #b388ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .subtitle { color: #9fa8da; font-size: 1rem; margin-top: 0; }
    .source-box {
        background: rgba(108, 140, 255, 0.08);
        border-left: 3px solid #6c8cff;
        padding: 0.8rem 1rem; border-radius: 6px; margin: 0.4rem 0;
        font-size: 0.85rem; color: #c5cae9;
    }
    .stChatMessage { background: rgba(255,255,255,0.03); border-radius: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────
# Cabeçalho
# ──────────────────────────────────────────────────────────────
st.markdown('<p class="main-header">🚀 Space Intelligence Assistant</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Assistente com RAG para documentos da nova economia espacial — '
    'clima · satélites · agricultura · monitoramento ambiental · exploração espacial</p>',
    unsafe_allow_html=True,
)
st.divider()

# ──────────────────────────────────────────────────────────────
# Barra lateral — configuração e upload
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuração")
    # A chave é carregada internamente do arquivo .env (não aparece na tela)
    api_key = os.getenv("OPENAI_API_KEY", "")
    if api_key:
        st.success("🔑 Chave da OpenAI carregada")
    else:
        st.error("⚠️ Crie um arquivo .env com OPENAI_API_KEY=sua-chave")

    st.header("📄 Documentos")
    uploaded_files = st.file_uploader(
        "Carregar (PDF · TXT · DOCX)",
        accept_multiple_files=True,
        type=["pdf", "txt", "docx"],
    )

    if st.button("🔄 Processar Documentos", use_container_width=True,
                 disabled=not (uploaded_files and api_key)):
        with st.spinner("Gerando embeddings e indexando no FAISS..."):
            try:
                pipe = RAGPipeline(api_key=api_key)
                n = pipe.load_documents(uploaded_files)
                st.session_state["rag"] = pipe
                st.success(f"✅ {len(uploaded_files)} arquivo(s) → {n} chunks indexados")
            except Exception as e:
                st.error(f"Erro: {e}")

    st.divider()
    if "rag" in st.session_state:
        st.success("🟢 Base de conhecimento ativa")
        read_aloud = st.toggle("🔊 Ler respostas em voz (TTS)", value=True)
        if st.button("🗑️ Resetar", use_container_width=True):
            for k in ["rag", "messages"]:
                st.session_state.pop(k, None)
            st.rerun()
    else:
        st.info("🔴 Carregue documentos para começar")
        read_aloud = False

    st.divider()
    st.caption("Global Solution 2026 · FIAP")

# ──────────────────────────────────────────────────────────────
# Histórico de mensagens
# ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state["messages"] = []


def render_history():
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("audio"):
                st.audio(msg["audio"], format="audio/mp3")
            if msg.get("sources"):
                with st.expander("📚 Trechos recuperados dos documentos"):
                    for s in msg["sources"]:
                        st.markdown(f'<div class="source-box">{s}</div>',
                                    unsafe_allow_html=True)


def handle_question(question: str):
    """Processa uma pergunta (texto ou já transcrita) e gera a resposta."""
    st.session_state["messages"].append({"role": "user", "content": question})

    result = st.session_state["rag"].query(question)
    answer = result["answer"]

    audio = None
    if read_aloud:
        try:
            audio = st.session_state["rag"].text_to_speech(answer)
        except Exception as e:
            st.warning(f"Não foi possível gerar áudio: {e}")

    st.session_state["messages"].append({
        "role": "assistant",
        "content": answer,
        "sources": result["sources"],
        "audio": audio,
    })


# ──────────────────────────────────────────────────────────────
# Abas: Texto e Voz
# ──────────────────────────────────────────────────────────────
tab_texto, tab_voz = st.tabs(["💬 Texto", "🎙️ Voz"])

with tab_texto:
    render_history()
    if prompt := st.chat_input("Pergunte algo sobre os documentos..."):
        if "rag" not in st.session_state:
            st.warning("Carregue e processe documentos primeiro.")
        else:
            with st.spinner("Consultando documentos..."):
                handle_question(prompt)
            st.rerun()

with tab_voz:
    st.markdown("#### 🎙️ Grave sua pergunta")
    st.caption("Clique no microfone, fale a pergunta e pare a gravação.")

    audio_value = st.audio_input("Gravar pergunta")

    if audio_value is not None:
        if "rag" not in st.session_state:
            st.warning("Carregue e processe documentos primeiro.")
        else:
            if st.button("📨 Enviar pergunta de voz", use_container_width=True):
                with st.spinner("Transcrevendo o áudio (Whisper)..."):
                    question = st.session_state["rag"].transcribe_audio(audio_value.read())
                st.info(f"📝 Você perguntou: **{question}**")
                with st.spinner("Consultando documentos e gerando resposta..."):
                    handle_question(question)
                st.rerun()

    render_history()