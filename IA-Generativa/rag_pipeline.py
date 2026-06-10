"""
rag_pipeline.py
===============
Núcleo do assistente RAG (Retrieval-Augmented Generation).

Responsável por:
  1. Ler documentos (PDF, TXT, DOCX)
  2. Dividir o texto em pedaços (chunks)
  3. Gerar embeddings (OpenAI)
  4. Armazenar e buscar no vector store (FAISS)
  5. Gerar respostas com o modelo generativo (GPT)
  6. Transcrever áudio em texto (Whisper)
  7. Converter texto em áudio (TTS)

Global Solution 2026 - FIAP - Inteligência Artificial Generativa
"""

import os
import tempfile
from typing import Dict, List

from openai import OpenAI
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


# ──────────────────────────────────────────────────────────────
# Prompt que orienta o modelo a responder SÓ com base nos documentos
# ──────────────────────────────────────────────────────────────
RAG_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""Você é um assistente especializado na nova economia espacial
(clima, satélites, agricultura inteligente, monitoramento ambiental,
desastres naturais e exploração espacial).

Responda à pergunta usando APENAS as informações dos trechos abaixo.
Se a resposta não estiver nos trechos, diga claramente que não encontrou
essa informação nos documentos. Responda em português, de forma clara e objetiva.

TRECHOS DOS DOCUMENTOS:
{context}

PERGUNTA: {question}

RESPOSTA:""",
)


class RAGPipeline:
    """Encapsula todo o fluxo RAG + recursos de áudio (Whisper e TTS)."""

    def __init__(self, api_key: str):
        # Cliente direto da OpenAI (usado para Whisper e TTS)
        self.client = OpenAI(api_key=api_key)

        # Modelo que transforma texto em vetores numéricos (embeddings)
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=api_key,
        )

        # Modelo generativo que escreve as respostas
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            openai_api_key=api_key,
        )

        # Divisor de texto em pedaços menores
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=["\n\n", "\n", ".", " ", ""],
        )

        self.vectorstore: FAISS | None = None
        self.qa_chain = None

    # ──────────────────────────────────────────────────────────
    # 1. LEITURA DE DOCUMENTOS
    # ──────────────────────────────────────────────────────────
    def _load_single(self, file) -> List:
        """Salva o arquivo enviado em disco temporário e o carrega."""
        ext = file.name.rsplit(".", 1)[-1].lower()

        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
            tmp.write(file.getvalue())
            tmp_path = tmp.name

        try:
            if ext == "pdf":
                loader = PyPDFLoader(tmp_path)
            elif ext == "txt":
                loader = TextLoader(tmp_path, encoding="utf-8")
            elif ext == "docx":
                loader = Docx2txtLoader(tmp_path)
            else:
                raise ValueError(f"Formato não suportado: .{ext}")

            docs = loader.load()
            # Marca a origem de cada trecho (para mostrar a fonte depois)
            for d in docs:
                d.metadata["source"] = file.name
        finally:
            os.unlink(tmp_path)

        return docs

    def load_documents(self, uploaded_files) -> int:
        """
        Lê todos os arquivos, divide em chunks, gera embeddings e
        indexa no FAISS. Retorna a quantidade de chunks indexados.
        """
        all_docs = []
        for file in uploaded_files:
            all_docs.extend(self._load_single(file))

        if not all_docs:
            raise ValueError("Nenhum documento válido foi carregado.")

        chunks = self.splitter.split_documents(all_docs)

        # Cria o vector store com os embeddings dos chunks
        self.vectorstore = FAISS.from_documents(chunks, self.embeddings)

        # Monta a cadeia de pergunta-e-resposta
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4},
            ),
            chain_type_kwargs={"prompt": RAG_PROMPT},
            return_source_documents=True,
        )

        return len(chunks)

    # ──────────────────────────────────────────────────────────
    # 2. CONSULTA (RETRIEVAL + GERAÇÃO)
    # ──────────────────────────────────────────────────────────
    def query(self, question: str) -> Dict:
        """Busca trechos relevantes e gera a resposta."""
        if self.qa_chain is None:
            raise RuntimeError("Carregue documentos antes de perguntar.")

        result = self.qa_chain.invoke({"query": question})

        sources, seen = [], set()
        for doc in result.get("source_documents", []):
            key = doc.page_content[:120]
            if key in seen:
                continue
            seen.add(key)
            src = doc.metadata.get("source", "Documento")
            page = doc.metadata.get("page", "")
            trecho = doc.page_content[:220].strip()
            label = f"**{src}{f' - p.{page}' if page != '' else ''}**\n\n{trecho}..."
            sources.append(label)

        return {"answer": result["result"], "sources": sources}

    # ──────────────────────────────────────────────────────────
    # 3. ÁUDIO -> TEXTO (WHISPER)
    # ──────────────────────────────────────────────────────────
    def transcribe_audio(self, audio_bytes: bytes) -> str:
        """Recebe bytes de áudio e devolve o texto transcrito."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="pt",
                )
        finally:
            os.unlink(tmp_path)

        return transcript.text

    # ──────────────────────────────────────────────────────────
    # 4. TEXTO -> ÁUDIO (TTS)
    # ──────────────────────────────────────────────────────────
    def text_to_speech(self, text: str) -> bytes:
        """Recebe texto e devolve os bytes do áudio (mp3) com a fala."""
        response = self.client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text[:4000],  # limite de segurança
        )
        return response.content
