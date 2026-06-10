# 🚀 SpaceIntel RPA

**Pipeline de Automação Inteligente — Economia Espacial**

---

## 📋 O que é?

SpaceIntel RPA é um pipeline de automação ponta a ponta que:

1. **Coleta** lançamentos espaciais em tempo real via Launch Library 2 API
2. **Coleta** cotações de insumos aeroespaciais via Yahoo Finance (yfinance)
3. **Limpa e normaliza** os dados com Pandas
4. **Analisa** com GPT-4o (OpenAI API) — fallback heurístico automático se API indisponível
5. **Gera artefatos** — Excel estilizado (.xlsx) + relatório Markdown (.md)

---

## 🏗️ Arquitetura

```
spaceintel_rpa/
│
├── main.py                          # Orquestrador principal (asyncio)
│
├── config/
│   └── settings.py                  # Constantes, URLs, parâmetros
│
├── scraper/
│   ├── launches_scraper.py          # Launch Library 2 REST API
│   └── market_scraper.py            # Yahoo Finance (yfinance)
│
├── processor/
│   ├── cleaner.py                   # Normalização Pandas
│   └── ai_analyzer.py              # GPT-4o + fallback heurístico
│
├── output/
│   ├── report_generator.py          # Excel + Markdown
│   └── logger.py                    # Logger Rich colorido
│
└── output/                          # Artefatos gerados
    ├── spaceintel_report.xlsx
    └── spaceintel_analysis.md
```

---

## ⚙️ Fluxo do Pipeline

```
ETAPA 1 — Coleta (paralela)
├── Launch Library 2 API  →  20 lançamentos JSON
└── Yahoo Finance (yfinance)  →  4 cotações

ETAPA 2 — Limpeza
└── Pandas  →  DataFrames normalizados

ETAPA 3 — Análise IA
├── GPT-4o (OpenAI API)  →  insights estruturados JSON
└── fallback heurístico  →  se OPENAI_API_KEY indisponível

ETAPA 4 — Outputs
├── openpyxl  →  spaceintel_report.xlsx
└── Markdown  →  spaceintel_analysis.md
```

---

## 🧩 Tópicos cobertos

| Tópico | Implementação | Arquivo |
|:---|:---|:---|
| **Web Scraping / API REST** | Coleta via Launch Library 2 com retry e cache | `scraper/launches_scraper.py` |
| **Extração de dados de mercado** | yfinance — Yahoo Finance API | `scraper/market_scraper.py` |
| **Orquestração de fluxos** | asyncio + gather para coleta paralela | `main.py` |
| **Limpeza e normalização** | Pandas — DataFrames estruturados | `processor/cleaner.py` |
| **Recursos de IA / LLM** | GPT-4o (OpenAI API) + fallback heurístico | `processor/ai_analyzer.py` |
| **Geração de artefatos** | Excel (.xlsx) estilizado + Markdown (.md) | `output/report_generator.py` |

---

## 🚀 Instalação e Execução

### 1. Clone e entre no projeto
```bash
cd spaceintel_rpa
```

### 2. Crie o ambiente virtual
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure a API key
Edite o arquivo `.env`:
```env
OPENAI_API_KEY=sk-proj-sua-chave-aqui
```

> ⚠️ Sem a chave, o pipeline usa análise heurística automática e entrega todos os artefatos normalmente.

### 5. Execute
```bash
python main.py
```

---

## 📦 Dependências principais

```
requests>=2.32.3        # HTTP scraping com retry
yfinance>=0.2.40        # Yahoo Finance API
pandas>=2.2.2           # Manipulação de dados
openpyxl>=3.1.2         # Excel estilizado
openai>=1.30.0          # GPT-4o (análise IA)
rich>=13.7.1            # Terminal colorido
python-dotenv>=1.0.1    # Variáveis de ambiente
```

---

## 📊 Outputs gerados

| Arquivo | Descrição |
|:---|:---|
| `output/spaceintel_report.xlsx` | 5 abas: Dashboard, Lançamentos, Mercado, Análise IA, Gráfico |
| `output/spaceintel_analysis.md` | Relatório narrativo completo com tabelas e insights da IA |
| `logs/` | Logs detalhados de cada execução |

---

*SpaceIntel RPA*

---

## 🖥️ Dashboard Streamlit

O projeto inclui um frontend de visualização que lê os outputs gerados pelo pipeline.

### Executar

```bash
# 1. Execute o pipeline primeiro para gerar os dados
python main.py

# 2. Suba o dashboard
streamlit run dashboard.py
```

Acesse em `http://localhost:8501`

### Páginas do dashboard

| Página | Conteúdo |
|:---|:---|
| 📊 Dashboard | Métricas gerais, resumo executivo e gráfico de mercado |
| 🛸 Lançamentos | Tabela filtrável com todas as missões coletadas |
| 📈 Mercado | Cards de cotação, gráfico e análise da IA |
| 🧠 Análise IA | Insights completos do GPT-4o (riscos, oportunidades, recomendações) |
| 📋 Logs | Visualizador dos logs de cada execução |
