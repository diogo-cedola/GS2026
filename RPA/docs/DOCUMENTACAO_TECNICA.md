# 📄 Documentação Técnica — SpaceIntel RPA

**Documentação Técnica do Projeto**

---

## 1. Visão Geral

O **SpaceIntel RPA** é um pipeline de automação inteligente ponta a ponta desenvolvido para o ecossistema da **Nova Economia Espacial**. O sistema coleta dados de lançamentos espaciais e cotações de insumos aeroespaciais em tempo real, processa-os com IA generativa (GPT-4o) e gera relatórios automatizados em Excel e Markdown.

### Problema que resolve

A indústria espacial gera diariamente um volume massivo de dados não estruturados — missões, cotações de alumínio, titânio, petróleo e ETFs aeroespaciais — que exigem monitoramento contínuo e análise especializada. O SpaceIntel RPA automatiza esse ciclo completo: da coleta à entrega de inteligência acionável.

---

## 2. Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    SPACEINTEL RPA                        │
│                  Orquestrador: main.py                   │
└────────────┬──────────────────────┬─────────────────────┘
             │                      │
    ┌────────▼────────┐    ┌────────▼────────┐
    │  ETAPA 1        │    │  ETAPA 1        │
    │  launches_      │    │  market_        │  ← paralelo (asyncio)
    │  scraper.py     │    │  scraper.py     │
    │  Launch Lib 2   │    │  yfinance API   │
    └────────┬────────┘    └────────┬────────┘
             └──────────┬───────────┘
                ┌───────▼───────┐
                │   ETAPA 2     │
                │  cleaner.py   │
                │  Pandas       │
                └───────┬───────┘
                ┌───────▼───────┐
                │   ETAPA 3     │
                │ ai_analyzer   │
                │  GPT-4o API   │  → fallback heurístico
                └───────┬───────┘
                ┌───────▼───────┐
                │   ETAPA 4     │
                │report_genera- │
                │tor.py         │
                │ .xlsx  + .md  │
                └───────────────┘
```

### Módulos

| Módulo | Responsabilidade |
|:---|:---|
| `main.py` | Orquestrador async — coordena as 4 etapas |
| `config/settings.py` | Constantes globais: URLs, tickers, modelo IA, paths |
| `scraper/launches_scraper.py` | Coleta missões via Launch Library 2 REST API |
| `scraper/market_scraper.py` | Coleta cotações via Yahoo Finance (yfinance) |
| `processor/cleaner.py` | Normalização e limpeza com Pandas |
| `processor/ai_analyzer.py` | Análise GPT-4o + fallback heurístico |
| `output/report_generator.py` | Gera Excel estilizado (.xlsx) e Markdown (.md) |
| `output/logger.py` | Logger Rich com cores e arquivo em `logs/` |

---

## 3. Tópicos de Automação Cobertos

O projeto integra **seis tópicos** da disciplina:

### 3.1 Web Scraping / Coleta de Dados via API REST
**Arquivo:** `scraper/launches_scraper.py`

Coleta lançamentos espaciais da API pública **Launch Library 2** (`ll.thespacedevs.com`). Implementa retry automático com backoff exponencial (3 tentativas), cache local em JSON e tratamento completo de erros HTTP.

### 3.2 Extração de Dados de Mercado
**Arquivo:** `scraper/market_scraper.py`

Coleta cotações de 4 ativos estratégicos via **yfinance**:

| Ticker | Ativo | Relevância Espacial |
|:---|:---|:---|
| `ALI=F` | Alumínio | Estrutura de foguetes e satélites |
| `CL=F` | Petróleo | Combustível de propulsão |
| `REMX` | Titânio ETF | Metais raros para componentes |
| `ARKX` | ETF Aeroespacial | Exposição a SpaceX, Rocket Lab, etc. |

### 3.3 Orquestração de Fluxos Assíncrona
**Arquivo:** `main.py`

Usa `asyncio.gather()` para executar as duas coletas em paralelo, reduzindo o tempo total de ~15s para ~7s.

### 3.4 Processamento Inteligente de Dados
**Arquivo:** `processor/cleaner.py`

Normalização com Pandas: padronização de datas, remoção de nulos/duplicatas, cálculo de tendência por variação % e geração de payload compacto para o LLM.

### 3.5 Análise com IA Generativa (LLM)
**Arquivo:** `processor/ai_analyzer.py`

Envia dados normalizados ao **GPT-4o** com prompt estruturado que retorna JSON com resumo executivo, eventos críticos, análise de mercado, riscos, oportunidades e recomendações.

**Fallback heurístico automático:** se a API falhar, o sistema gera análise baseada em regras e entrega todos os artefatos normalmente.

### 3.6 Geração Automatizada de Artefatos
**Arquivo:** `output/report_generator.py`

Gera Excel com 5 abas estilizadas (incluindo gráfico matplotlib embutido) e relatório Markdown com tabelas e badges.

---

## 4. Fluxo de Dados Completo

```
Launch Library 2 API          Yahoo Finance (yfinance)
        │                               │
        ▼                               ▼
launches_raw (list[dict])     market_raw (list[dict])
        │                               │
        └──────────────┬────────────────┘
                       ▼
              cleaner.py (Pandas)
                       │
        ┌──────────────┴────────────────┐
        ▼                               ▼
launches_df (DataFrame)       market_df (DataFrame)
  cols: data, missao,           cols: ativo, preco_atual,
        veiculo, local                 variacao_pct, tendencia
        │                               │
        └──────────────┬────────────────┘
                       ▼
              summarize_for_ai() → dict JSON
                       ▼
              GPT-4o → insights dict
                       ▼
              ├── spaceintel_report.xlsx
              └── spaceintel_analysis.md
```

---

## 5. Configuração e Instalação

```bash
# 1. Ambiente virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/macOS

# 2. Dependências
pip install -r requirements.txt

# 3. Configurar .env
OPENAI_API_KEY=sk-proj-sua-chave-aqui

# 4. Executar
python main.py
```

---

## 6. Dependências

```
requests>=2.32.3      # Requisições HTTP com retry
yfinance>=0.2.40      # Yahoo Finance API
pandas>=2.2.2         # Manipulação de dados
openpyxl>=3.1.2       # Excel com formatação
matplotlib>=3.8.0     # Gráficos embutidos no Excel
openai>=1.30.0        # GPT-4o
rich>=13.7.1          # Terminal colorido
python-dotenv>=1.0.1  # Leitura do .env
beautifulsoup4>=4.12  # Parser HTML utilitário
```

---

## 7. Tratamento de Erros

| Falha | Comportamento |
|:---|:---|
| Launch Library 2 indisponível | Retry 3x com backoff — usa cache local se disponível |
| Yahoo Finance indisponível | Retry 3x — ativo marcado como `N/D` |
| `OPENAI_API_KEY` ausente | Fallback heurístico automático |
| OpenAI API com erro | Fallback heurístico automático |
| GPT-4o retorna JSON inválido | Regex extrai JSON parcial |
| Diretório `output/` inexistente | Criado automaticamente |

---

## 8. Estrutura de Diretórios

```
spaceintel_rpa/
├── main.py
├── requirements.txt
├── .env
├── config/settings.py
├── scraper/
│   ├── launches_scraper.py
│   ├── market_scraper.py
│   └── cache.py
├── processor/
│   ├── cleaner.py
│   └── ai_analyzer.py
├── output/
│   ├── report_generator.py
│   ├── logger.py
│   ├── spaceintel_report.xlsx   ← gerado na execução
│   └── spaceintel_analysis.md  ← gerado na execução
├── docs/
│   └── DOCUMENTACAO_TECNICA.md
└── logs/
```

---

## 9. Cobertura Técnica do Projeto

| Critério | Peso | Como é atendido |
|:---|:---:|:---|
| **Domínio Técnico e Integração de Conceitos** | 40% | 6 tópicos integrados: scraping, API REST, orquestração async, Pandas, GPT-4o, geração de artefatos |
| **Arquitetura de Fluxo e Engenharia de Software** | 25% | Pipeline modular em 4 etapas, tratamento de exceções em todos os módulos, fallback automático |
| **Inteligência de Dados e Recursos de IA** | 20% | GPT-4o com prompt estruturado JSON; análise heurística como fallback |
| **Entrega de Artefatos e Outputs Técnicos** | 15% | Excel com 5 abas + gráfico matplotlib; Markdown com tabelas e badges |

---

*SpaceIntel RPA — Documentação Técnica*
