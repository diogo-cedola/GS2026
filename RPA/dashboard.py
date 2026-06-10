"""
SpaceIntel RPA — Dashboard Streamlit
Frontend de visualização dos dados coletados e analisados pelo pipeline.

Execução:
    streamlit run dashboard.py
"""

import json
from pathlib import Path
from datetime import datetime

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SpaceIntel RPA",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR   = Path(__file__).resolve().parent
CACHE_DIR  = BASE_DIR / "cache"
OUTPUT_DIR = BASE_DIR / "output"

C_DARK  = "#0D1B2A"
C_MID   = "#1B3A5C"
C_CYAN  = "#00C2FF"
C_NEG   = "#C0392B"
C_POS   = "#1A7A4A"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  [data-testid="stAppViewContainer"] {{ background: {C_DARK}; }}
  [data-testid="stSidebar"] {{ background: {C_MID} !important; }}
  [data-testid="stSidebar"] * {{ color: #E0EAF4 !important; }}
  .main .block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1200px; }}
  h1, h2, h3, h4 {{ color: white !important; }}
  p, li, span, label {{ color: #C5D5E8 !important; }}
  [data-testid="metric-container"] {{
      background: {C_MID}; border: 1px solid #1E3F6A; border-radius: 12px; padding: 1rem 1.25rem;
  }}
  [data-testid="stMetricValue"]  {{ color: white !important; font-size: 1.8rem !important; }}
  [data-testid="stMetricLabel"]  {{ color: #A0B8D0 !important; }}
  [data-testid="stMetricDelta"]  {{ font-size: 0.85rem !important; }}
  div[data-testid="stExpander"]  {{ background: {C_MID}; border: 1px solid #1E3F6A; border-radius: 8px; }}
  .status-badge {{ display:inline-block; padding:3px 10px; border-radius:20px; font-size:12px; font-weight:600; }}
  .tag-green {{ background:#1A4A2E; color:#4ADE80; }}
  .tag-red   {{ background:#4A1A1A; color:#F87171; }}
  .tag-amber {{ background:#4A3A1A; color:#FCD34D; }}
  .tag-blue  {{ background:#1A2E4A; color:#60A5FA; }}
  .section-divider {{ border:none; border-top:1px solid #1E3F6A; margin:1.5rem 0; }}
  .insight-box {{
      background:{C_MID}; border-left:4px solid {C_CYAN};
      border-radius:0 8px 8px 0; padding:1rem 1.25rem; margin:0.5rem 0;
  }}
  .insight-box p {{ color:#E0EAF4 !important; margin:0; line-height:1.6; }}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_cache() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    launches_df, market_df, meta = pd.DataFrame(), pd.DataFrame(), {}
    lpath, mpath = CACHE_DIR / "launches.json", CACHE_DIR / "market.json"
    if lpath.exists():
        raw = json.loads(lpath.read_text(encoding="utf-8"))
        meta["launches_ts"] = raw.get("timestamp", "")
        launches_df = pd.DataFrame(raw.get("data", []))
    if mpath.exists():
        raw = json.loads(mpath.read_text(encoding="utf-8"))
        meta["market_ts"] = raw.get("timestamp", "")
        market_df = pd.DataFrame(raw.get("data", []))
    return launches_df, market_df, meta


@st.cache_data(ttl=60)
def load_ai_insights() -> dict:
    xlsx = OUTPUT_DIR / "spaceintel_report.xlsx"
    if not xlsx.exists():
        return {}
    try:
        df = pd.read_excel(xlsx, sheet_name="🧠 Análise IA", header=2)
        return {
            str(row.iloc[0]).strip().lower().replace(" ", "_"): str(row.iloc[1]).strip()
            for _, row in df.iterrows()
        }
    except Exception:
        return {}


def fmt_ts(ts: str) -> str:
    try:
        return datetime.fromisoformat(ts).strftime("%d/%m/%Y %H:%M")
    except Exception:
        return ts or "—"


def build_market_chart(market_df: pd.DataFrame) -> plt.Figure:
    ativos  = market_df["ativo"].tolist()
    valores = [float(v) for v in market_df["variacao_pct"]]
    precos  = [float(v) for v in market_df["preco_atual"]]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5),
                                    gridspec_kw={"width_ratios": [2, 1]})
    fig.patch.set_facecolor(C_DARK)

    ax1.set_facecolor(C_DARK)
    colors = [C_NEG if v < 0 else C_POS for v in valores]
    bars = ax1.bar(ativos, valores, color=colors, width=0.5, zorder=3, edgecolor="none")
    for bar, val in zip(bars, valores):
        ypos = val - 0.18 if val < 0 else val + 0.1
        ax1.text(bar.get_x() + bar.get_width() / 2, ypos, f"{val:+.2f}%",
                 ha="center", va="top" if val < 0 else "bottom",
                 color="white", fontsize=10.5, fontweight="bold")
    ax1.axhline(0, color=C_CYAN, linewidth=1.2, zorder=2)
    ax1.yaxis.grid(True, color="#1B3A5C", linewidth=0.8, linestyle="--", zorder=1)
    ax1.set_axisbelow(True)
    ax1.set_title("Variação % por Ativo", color="white", fontsize=12, fontweight="bold", pad=12)
    ax1.set_ylabel("Variação (%)", color=C_CYAN, fontsize=10)
    ax1.tick_params(colors="white", labelsize=10)
    plt.setp(ax1.get_xticklabels(), color="white")
    plt.setp(ax1.get_yticklabels(), color="#A0B4C8")
    for spine in ax1.spines.values():
        spine.set_edgecolor("#1B3A5C")

    ax2.set_facecolor(C_DARK)
    ax2.axis("off")
    ax2.set_title("Cotações Atuais (USD)", color="white", fontsize=12, fontweight="bold", pad=12)
    rows = [[a, f"${p:,.2f}", f"{v:+.2f}%"] for a, p, v in zip(ativos, precos, valores)]
    tbl = ax2.table(cellText=rows, colLabels=["Ativo", "Preço", "Var%"],
                    cellLoc="center", loc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 1.6)
    for (row, col), cell in tbl.get_celld().items():
        if row == 0:
            cell.set_facecolor("#1B3A5C")
            cell.set_text_props(color=C_CYAN, fontweight="bold")
        else:
            cell.set_facecolor("#0F2338" if row % 2 == 0 else "#162840")
            txt_color = "white"
            if col == 2:
                txt_color = "#F87171" if rows[row-1][2].startswith("-") else "#4ADE80"
            cell.set_text_props(color=txt_color)
        cell.set_edgecolor("#1E3F6A")

    plt.tight_layout(pad=1.5)
    return fig


def sentiment_badge(s):
    m = {"Otimista":("tag-green","🟢"), "Neutro":("tag-amber","🟡"), "Pessimista":("tag-red","🔴")}
    css, icon = m.get(s, ("tag-blue","⚪"))
    return f'<span class="status-badge {css}">{icon} {s}</span>'

def activity_badge(a):
    m = {"Alto":("tag-green","🔥"), "Médio":("tag-amber","📡"), "Baixo":("tag-red","🌑")}
    css, icon = m.get(a, ("tag-blue","📡"))
    return f'<span class="status-badge {css}">{icon} {a}</span>'

def launch_status_badge(s):
    s = str(s)
    if "Go"   in s: return f'<span class="status-badge tag-green">✓ {s}</span>'
    if "Hold" in s: return f'<span class="status-badge tag-amber">⏸ {s}</span>'
    return f'<span class="status-badge tag-blue">{s}</span>'


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚀 SpaceIntel RPA")
    st.markdown("*Pipeline de Automação Inteligente*")
    st.markdown("---")
    page = st.radio(
        "Navegação",
        ["📊 Dashboard", "🛸 Lançamentos", "📈 Mercado", "🧠 Análise IA", "📋 Logs"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    if st.button("🔄 Atualizar dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    st.markdown("<small style='color:#6A8AAA'>Execute `python main.py` para coletar novos dados.</small>",
                unsafe_allow_html=True)


# ── Carrega dados ─────────────────────────────────────────────────────────────
launches_df, market_df, meta = load_cache()
insights = load_ai_insights()
has_launches = not launches_df.empty
has_market   = not market_df.empty


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown("# 📊 Dashboard Executivo")
    st.markdown(f"<small>Última atualização: {fmt_ts(meta.get('launches_ts',''))}</small>",
                unsafe_allow_html=True)
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    atv  = insights.get("atividade_espacial", insights.get("índice_de_atividade_espacial", "—"))
    sent = insights.get("sentimento_de_mercado", insights.get("sentimento_mercado", "—"))
    c1.metric("🛸 Lançamentos", len(launches_df) if has_launches else "—", "coletados")
    c2.metric("📦 Ativos",      len(market_df)   if has_market   else "—", "monitorados")
    c3.metric("📡 Atividade",   atv)
    c4.metric("📊 Sentimento",  sent)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    resumo = insights.get("resumo_executivo", "")
    if resumo and resumo != "nan":
        st.markdown("### 🧠 Resumo Executivo")
        st.markdown(f'<div class="insight-box"><p>{resumo}</p></div>', unsafe_allow_html=True)
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    if has_market:
        st.markdown("### 📈 Variação de Insumos Aeroespaciais")
        fig = build_market_chart(market_df)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    if has_launches:
        st.markdown("### 🛸 Próximos Lançamentos")
        top5 = launches_df.head(5)[["data","missao","veiculo","local","status"]].copy()
        top5.columns = ["Data","Missão","Veículo","Local","Status"]
        st.dataframe(top5, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# LANÇAMENTOS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🛸 Lançamentos":
    st.markdown("# 🛸 Missões Espaciais")

    if not has_launches:
        st.warning("Nenhum dado encontrado. Execute `python main.py` primeiro.")
    else:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            agencias = ["Todas"] + sorted(launches_df["agencia"].dropna().unique().tolist())
            ag_sel = st.selectbox("Filtrar por agência", agencias)
        with col_f2:
            status_list = ["Todos"] + sorted(launches_df["status"].dropna().unique().tolist())
            st_sel = st.selectbox("Filtrar por status", status_list)

        df_filt = launches_df.copy()
        if ag_sel != "Todas":
            df_filt = df_filt[df_filt["agencia"] == ag_sel]
        if st_sel != "Todos":
            df_filt = df_filt[df_filt["status"] == st_sel]

        st.markdown(f"**{len(df_filt)} missões** encontradas")
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        for i, (_, row) in enumerate(df_filt.iterrows()):
            with st.expander(f"🚀 {row['missao']}", expanded=(i == 0)):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.markdown(f"**Veículo:** {row['veiculo']}")
                    st.markdown(f"**Local:** {row['local']}")
                    st.markdown(f"**Data:** {row['data']}")
                    st.markdown(f"**Agência:** {row.get('agencia','—')}")
                    desc = str(row.get("descricao",""))
                    if desc and desc != "nan":
                        st.markdown(f"**Descrição:** {desc[:300]}{'...' if len(desc)>300 else ''}")
                with c2:
                    st.markdown(launch_status_badge(row.get("status","—")), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MERCADO
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Mercado":
    st.markdown("# 📈 Insumos Aeroespaciais")

    if not has_market:
        st.warning("Nenhum dado encontrado. Execute `python main.py` primeiro.")
    else:
        st.markdown(f"<small>Cotações de: {fmt_ts(meta.get('market_ts',''))}</small>",
                    unsafe_allow_html=True)
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        cols = st.columns(len(market_df))
        for col, (_, row) in zip(cols, market_df.iterrows()):
            v = float(row["variacao_pct"])
            col.metric(row["ativo"], f"${float(row['preco_atual']):,.2f}",
                       f"{v:+.2f}%", delta_color="normal" if v >= 0 else "inverse")

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        fig = build_market_chart(market_df)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown("### Dados Completos")
        cols_show = [c for c in ["ativo","ticker","preco_atual","abertura","maxima","minima",
                                  "variacao_pct","volume","data"] if c in market_df.columns]
        st.dataframe(
            market_df[cols_show].rename(columns={
                "ativo":"Ativo","ticker":"Ticker","preco_atual":"Preço Atual",
                "abertura":"Abertura","maxima":"Máxima","minima":"Mínima",
                "variacao_pct":"Var %","volume":"Volume","data":"Data",
            }),
            use_container_width=True, hide_index=True,
        )

        analise = insights.get("análise_de_mercado", insights.get("analise_mercado",""))
        if analise and analise != "nan":
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            st.markdown("### 🧠 Análise de Mercado")
            st.markdown(f'<div class="insight-box"><p>{analise}</p></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ANÁLISE IA
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧠 Análise IA":
    st.markdown("# 🧠 Análise Inteligente")
    fonte = insights.get("fonte_analise", insights.get("fonte_de_ia", "—"))
    st.markdown(f"<small>Gerado por: **{fonte}**</small>", unsafe_allow_html=True)
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    if not insights:
        st.warning("Nenhuma análise encontrada. Execute `python main.py` primeiro.")
    else:
        atv  = insights.get("atividade_espacial", insights.get("índice_de_atividade_espacial","—"))
        sent = insights.get("sentimento_de_mercado", insights.get("sentimento_mercado","—"))
        col1, col2 = st.columns(2)
        col1.markdown(f"**Atividade Espacial:** {activity_badge(atv)}", unsafe_allow_html=True)
        col2.markdown(f"**Sentimento de Mercado:** {sentiment_badge(sent)}", unsafe_allow_html=True)
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

        def render_insight(label, keys, icon=""):
            for k in keys:
                val = insights.get(k, "")
                if val and val != "nan":
                    st.markdown(f"### {icon} {label}")
                    if "," in val and len(val) > 60:
                        for item in [i.strip() for i in val.split(",") if i.strip()]:
                            st.markdown(f"- {item}")
                    else:
                        st.markdown(f'<div class="insight-box"><p>{val}</p></div>',
                                    unsafe_allow_html=True)
                    return

        render_insight("Resumo Executivo",     ["resumo_executivo"], "📋")
        render_insight("Eventos Críticos",     ["eventos_críticos","eventos_criticos"], "🔸")
        render_insight("Riscos Identificados", ["riscos_identificados"], "⚠️")
        render_insight("Oportunidades",        ["oportunidades"], "💡")
        render_insight("Recomendações",        ["recomendações","recomendacoes"], "✅")
        render_insight("Análise de Mercado",   ["análise_de_mercado","analise_mercado"], "📊")


# ══════════════════════════════════════════════════════════════════════════════
# LOGS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Logs":
    st.markdown("# 📋 Logs de Execução")

    logs_dir  = BASE_DIR / "logs"
    log_files = sorted(logs_dir.glob("*.log"), reverse=True) if logs_dir.exists() else []

    if not log_files:
        st.warning("Nenhum log encontrado.")
    else:
        sel      = st.selectbox("Selecionar execução", [f.name for f in log_files])
        content  = (logs_dir / sel).read_text(encoding="utf-8", errors="replace")
        lines    = content.splitlines()
        c1, c2, c3 = st.columns(3)
        c1.metric("INFO",    sum(1 for l in lines if "INFO"    in l))
        c2.metric("WARNING", sum(1 for l in lines if "WARNING" in l))
        c3.metric("ERROR",   sum(1 for l in lines if "ERROR"   in l))
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.code(content, language="bash")


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown(
    "<center><small style='color:#3A5A7A'>SpaceIntel RPA — Pipeline de Automação Inteligente</small></center>",
    unsafe_allow_html=True,
)
