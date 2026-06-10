#!/usr/bin/env python3
"""
chatbot_app.py — Chatbot de Edifícios Verdes e Net Zero
Execução: python chatbot_app.py
Pré-requisitos: executar as Etapas 1-5 do notebook primeiro (modelo treinado em ./lora_model/)
"""

import os, sys, json, torch
from pathlib import Path

# ── Caminhos ──────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
MODEL_DIR   = BASE_DIR / "lora_model"
CHROMA_DIR  = BASE_DIR / "chroma_db"

if not MODEL_DIR.exists():
    print("❌ Modelo LoRA não encontrado em:", MODEL_DIR)
    print("   Execute as Etapas 1-5 do notebook primeiro.")
    sys.exit(1)

print("⏳ Carregando dependências...")
from unsloth import FastLanguageModel
import chromadb
from sentence_transformers import SentenceTransformer
import gradio as gr

# ── Carregar modelo fine-tunado ───────────────────────────────
print("⏳ Carregando modelo fine-tunado (Llama 3.2 3B QLoRA)...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=str(MODEL_DIR),
    max_seq_length=1024,
    dtype=None,
    load_in_4bit=True,
)
FastLanguageModel.for_inference(model)
print(f"✅ Modelo carregado! GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU (lento)'}")

# ── Carregar ChromaDB para RAG ─────────────────────────────────
USE_RAG = CHROMA_DIR.exists()
if USE_RAG:
    print("⏳ Carregando ChromaDB e embeddings...")
    chroma = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = chroma.get_collection("edificios_verdes")
    emb_model  = SentenceTransformer("intfloat/multilingual-e5-large")
    print(f"✅ ChromaDB: {collection.count()} vetores | RAG habilitado")
else:
    print("⚠️  ChromaDB não encontrado — RAG desabilitado. Execute a Etapa 4 do notebook.")
    collection = None
    emb_model  = None

# ── Configurações do sistema ──────────────────────────────────
SYSTEM_PROMPT = (
    "Você é um assistente especialista em edifícios verdes, sustentáveis e Net Zero. "
    "Tem profundo conhecimento em certificações LEED, AQUA-HQE, GBC Brasil EDGE, "
    "normas ABNT (NBR 15575, NBR 16783, NBR 15527), eficiência energética, "
    "energia solar fotovoltaica, reaproveitamento de águas cinzas e pluviais, "
    "BEMS (Building Energy Management Systems) e edificações Net Zero. "
    "Responda de forma técnica, precisa e em português brasileiro. "
    "Quando pertinente, cite normas, valores numéricos e referências técnicas específicas."
)

MAX_HISTORY   = 4     # número de trocas de histórico mantidas no contexto
MAX_NEW_TOKENS = 600  # limite de tokens na resposta


# ── Funções de geração ────────────────────────────────────────
def retrieve_context(query: str, n_results: int = 3) -> str:
    """Recupera chunks relevantes do ChromaDB via similaridade vetorial."""
    if not USE_RAG or not emb_model:
        return ""
    q_emb = emb_model.encode([f"query: {query}"], normalize_embeddings=True)[0]
    results = collection.query(query_embeddings=[q_emb.tolist()], n_results=n_results)
    if results["documents"][0]:
        docs   = results["documents"][0]
        metas  = results["metadatas"][0]
        ctx_parts = []
        for doc, meta in zip(docs, metas):
            src = meta.get("source", "corpus")
            ctx_parts.append(f"[Fonte: {src}]\n{doc}")
        return "\n\n---\n\n".join(ctx_parts)
    return ""


def gerar_resposta(message: str, history: list, usar_rag: bool) -> str:
    """Gera uma resposta do modelo com histórico e RAG opcional."""
    system_content = SYSTEM_PROMPT
    if usar_rag:
        ctx = retrieve_context(message)
        if ctx:
            system_content += f"\n\n[Contexto recuperado do corpus técnico]\n{ctx}\n[Fim do contexto]"

    messages = [{"role": "system", "content": system_content}]

    # Adicionar histórico (últimas MAX_HISTORY trocas)
    for user_msg, bot_msg in history[-MAX_HISTORY:]:
        messages.append({"role": "user",      "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})

    messages.append({"role": "user", "content": message})

    # Tokenizar e gerar
    inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to("cuda" if torch.cuda.is_available() else "cpu")

    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.eos_token_id,
        )

    new_tokens = outputs[0][inputs.shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


# ── Interface Gradio ──────────────────────────────────────────
CSS = """
.gradio-container { font-family: 'Segoe UI', sans-serif; }
.chatbot { font-size: 14px; }
"""

EXEMPLOS = [
    "Qual é o percentual mínimo de redução de água interior exigido pelo LEED v4.1?",
    "Como calcular a potência de pico de um sistema fotovoltaico para 1.000 m² de escritório?",
    "Quais são os parâmetros de qualidade exigidos pela NBR 16783 para reuso em vasos sanitários?",
    "O que é QLoRA e como é diferente do LoRA convencional?",
    "Quais são as 14 preocupações avaliadas pelo AQUA-HQE?",
    "O que é o BEMS e quais protocolos de comunicação ele utiliza?",
    "Como a NBR 15575 define os requisitos de transmitância térmica por zona bioclimática?",
    "Qual EUI alvo para um edifício de escritórios Net Zero Energy no Brasil?",
    "Quais etapas de tratamento são necessárias para reuso de águas cinzas em descargas de vasos?",
    "O que é o crédito EA2 do LEED e como se pontua?",
    "Como dimensionar uma cisterna de água pluvial pelo método Rippl?",
    "Quais são as diferenças entre LEED, AQUA-HQE e GBC Brasil EDGE?",
]

with gr.Blocks(title="🏗️ Edifícios Verdes", css=CSS, theme=gr.themes.Soft()) as demo:

    gr.Markdown("""
    # 🏗️ Assistente para Edifícios Verdes e Net Zero
    **Especialista em** LEED · AQUA-HQE · GBC Brasil EDGE · Energia Solar FV · Reuso de Água · NZEBs · BEMS · PROCEL
    """)

    with gr.Row():
        # Coluna principal — chat
        with gr.Column(scale=3):
            chatbot_ui = gr.Chatbot(
                label="Conversa",
                height=520,
                show_copy_button=True,
                bubble_full_width=False,
            )
            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Digite sua pergunta técnica sobre edifícios verdes...",
                    label="",
                    lines=2,
                    scale=5,
                )
                send_btn = gr.Button("Enviar ↗", variant="primary", scale=1, min_width=80)

            with gr.Row():
                clear_btn  = gr.Button("🗑️ Limpar conversa", variant="secondary")
                rag_toggle = gr.Checkbox(
                    value=True,
                    label="🔍 RAG ativo (recuperar contexto do corpus)",
                    interactive=USE_RAG,
                )

        # Coluna lateral — exemplos e info
        with gr.Column(scale=1):
            gr.Markdown("### 💡 Exemplos de perguntas")
            gr.Examples(
                examples=[[e] for e in EXEMPLOS],
                inputs=msg_input,
                label="",
            )
            gr.Markdown(f"""
            ---
            **Modelo**: Llama 3.2 3B (QLoRA)  
            **RAG**: {'✅ ChromaDB ativo' if USE_RAG else '❌ Desabilitado'}  
            **Corpus**: 10 documentos técnicos  
            **Pares Q&A**: 163  
            """)

    # ── Event handlers ────────────────────────────────────────
    def respond(message, chat_history, usar_rag):
        if not message.strip():
            return chat_history, ""
        response = gerar_resposta(message, chat_history, usar_rag)
        chat_history.append((message, response))
        return chat_history, ""

    def clear_chat():
        return [], ""

    send_btn.click(
        respond,
        inputs=[msg_input, chatbot_ui, rag_toggle],
        outputs=[chatbot_ui, msg_input],
    )
    msg_input.submit(
        respond,
        inputs=[msg_input, chatbot_ui, rag_toggle],
        outputs=[chatbot_ui, msg_input],
    )
    clear_btn.click(clear_chat, outputs=[chatbot_ui, msg_input])


# ── Executar ──────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Chatbot Edifícios Verdes")
    parser.add_argument("--share",  action="store_true", help="Criar link público Gradio")
    parser.add_argument("--port",   type=int, default=7860, help="Porta local (default: 7860)")
    parser.add_argument("--no-rag", action="store_true", help="Desabilitar RAG")
    args = parser.parse_args()

    if args.no_rag:
        USE_RAG = False
        print("⚠️  RAG desabilitado por argumento de linha de comando.")

    print(f"\n🚀 Iniciando chatbot na porta {args.port}...")
    if args.share:
        print("   Share link público será gerado (válido por 72h)...")

    demo.launch(
        server_port=args.port,
        share=args.share,
        inbrowser=True,
    )
