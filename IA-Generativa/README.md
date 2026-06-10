# 🚀 Space Intelligence Assistant
# https://github.com/felipesayegg/space-rag-assistant/tree/main
Assistente inteligente com arquitetura **RAG** (Retrieval-Augmented Generation) para
responder perguntas sobre documentos da **nova economia espacial** — clima, satélites,
agricultura inteligente, monitoramento ambiental, desastres naturais e exploração espacial.

Diferencial: além do chat por texto, o assistente entende **perguntas por voz**
(Whisper) e **responde falando** (Text-to-Speech).

**Global Solution 2026 — FIAP — Inteligência Artificial Generativa**

---

## 🧠 Como funciona (fluxo RAG)

```
1. Documento (PDF/TXT/DOCX)
        ↓
2. Divisão em pedaços menores (chunks)
        ↓
3. Cada chunk vira um vetor numérico (embeddings — OpenAI)
        ↓
4. Vetores armazenados no FAISS (vector store local)
        ↓
5. Pergunta do usuário (texto OU voz transcrita por Whisper)
        ↓
6. A pergunta vira vetor e busca os 4 trechos mais parecidos no FAISS
        ↓
7. Trechos + pergunta vão para o modelo generativo (GPT-4o-mini)
        ↓
8. Resposta em texto + leitura em voz (TTS)
```

---

## 🛠️ Tecnologias

| Componente | Tecnologia |
|---|---|
| Framework RAG | LangChain |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vector Store | FAISS (local) |
| Modelo generativo | OpenAI `gpt-4o-mini` |
| Áudio → texto | OpenAI `whisper-1` |
| Texto → áudio | OpenAI `tts-1` |
| Interface | Streamlit |
| Leitura de documentos | pypdf, docx2txt |

---

## ▶️ Como rodar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Rodar o app
```bash
streamlit run app.py
```
O app abre em `http://localhost:8501`

### 3. Usar
1. Cole sua **OpenAI API Key** na barra lateral
2. Faça upload de documentos (PDF/TXT/DOCX)
3. Clique em **Processar Documentos**
4. Use a aba **Texto** para digitar ou a aba **Voz** para falar

---

## 📂 Estrutura do projeto

```
space-rag-assistant/
├── app.py              # Interface (Streamlit) — texto e voz
├── rag_pipeline.py     # Núcleo RAG + Whisper + TTS
├── requirements.txt    # Dependências
├── README.md           # Este arquivo
└── documents/          # Documentos de exemplo (opcional)
```

---

## 📑 Documentos sugeridos

- NASA Technical Reports — https://ntrs.nasa.gov
- IPCC Climate Reports — https://www.ipcc.ch/reports
- INPE Monitoramento — https://www.gov.br/inpe
- ESA Earth Observation — https://www.esa.int

---

## ⚠️ Limitações

- Depende de chave da OpenAI (custo por uso, baixo para demonstração)
- Vector store em memória — não persiste ao fechar o app
- Qualidade da resposta depende da qualidade dos documentos carregados
- Limite de 4 trechos por consulta (configurável)

## 🔮 Melhorias futuras

- Persistir o vector store em disco
- Adicionar reranking dos trechos recuperados
- Suporte a embeddings multilíngues gratuitos
- Avaliação automática da qualidade RAG (RAGAS)
