from __future__ import annotations

import io
import re
import unicodedata
from datetime import timedelta
from urllib.parse import parse_qs, urlparse

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import streamlit as st

DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1tpQmqkinlA4AscPI8kIkmm5DGD9Jw_wHb-5sy5itSGg/edit?gid=1149526076#gid=1149526076"
CACHE_TTL_SECONDS = 300

COLORS = {
    "primary": "#0C6E74",
    "secondary": "#1D3557",
    "accent": "#E76F51",
    "gold": "#F4A261",
    "mint": "#2A9D8F",
    "ink": "#0B132B",
    "muted": "#5C677D",
    "bg_light": "#F3F6F9",
}


st.set_page_config(
    page_title="Dashboard de Produtos Faturados",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');

            :root {
                --primary: #0C6E74;
                --secondary: #1D3557;
                --accent: #E76F51;
                --gold: #F4A261;
                --ink: #0B132B;
                --muted: #5C677D;
                --card: rgba(255, 255, 255, 0.82);
            }

            .stApp {
                background:
                    radial-gradient(circle at 8% 12%, rgba(231, 111, 81, 0.16) 0%, rgba(231, 111, 81, 0) 40%),
                    radial-gradient(circle at 86% 6%, rgba(12, 110, 116, 0.16) 0%, rgba(12, 110, 116, 0) 38%),
                    linear-gradient(180deg, #f9fcff 0%, #edf3f8 100%);
                color: var(--ink);
                font-family: 'Space Grotesk', sans-serif;
            }

            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0B132B 0%, #15213f 100%);
                border-right: 1px solid rgba(255, 255, 255, 0.08);
            }

            [data-testid="stSidebar"] * {
                color: #e9f1ff !important;
                font-family: 'Space Grotesk', sans-serif;
            }

            h1, h2, h3 {
                font-family: 'Fraunces', serif !important;
                color: #11203f;
                letter-spacing: 0.2px;
            }

            .hero {
                background: linear-gradient(120deg, rgba(12,110,116,0.95), rgba(29,53,87,0.95));
                border: 1px solid rgba(255, 255, 255, 0.18);
                border-radius: 22px;
                padding: 1.3rem 1.5rem;
                margin-bottom: 1.2rem;
                box-shadow: 0 12px 30px rgba(16, 24, 40, 0.18);
            }

            .hero h2 {
                margin: 0;
                color: #ffffff;
                font-size: 1.9rem;
            }

            .hero p {
                margin: 0.35rem 0 0 0;
                color: rgba(255, 255, 255, 0.9);
                font-size: 1rem;
            }

            .kpi-card {
                border-radius: 18px;
                padding: 1rem 1.05rem;
                background: var(--card);
                border: 1px solid rgba(17, 32, 63, 0.08);
                box-shadow: 0 6px 18px rgba(17, 32, 63, 0.08);
                backdrop-filter: blur(2px);
                min-height: 130px;
            }

            .kpi-label {
                font-size: 0.82rem;
                font-weight: 700;
                color: var(--muted);
                text-transform: uppercase;
                letter-spacing: 0.7px;
                margin-bottom: 0.45rem;
            }

            .kpi-value {
                font-family: 'Fraunces', serif;
                font-weight: 700;
                color: var(--ink);
                font-size: 1.78rem;
                line-height: 1.08;
            }

            .kpi-sub {
                color: #42506b;
                font-size: 0.83rem;
                margin-top: 0.35rem;
            }

            .kpi-delta-up {
                margin-top: 0.45rem;
                color: #1c8c63;
                font-size: 0.8rem;
                font-weight: 600;
            }

            .kpi-delta-down {
                margin-top: 0.45rem;
                color: #c44536;
                font-size: 0.8rem;
                font-weight: 600;
            }

            .insight-box {
                background: rgba(255, 255, 255, 0.82);
                border: 1px solid rgba(17, 32, 63, 0.08);
                border-left: 6px solid #E76F51;
                border-radius: 16px;
                padding: 1rem 1.1rem;
                margin-top: 0.6rem;
                box-shadow: 0 4px 14px rgba(17, 32, 63, 0.06);
            }

            .insight-box p {
                margin: 0.2rem 0;
                color: #1f2d4a;
                font-size: 0.93rem;
            }

            .story-row {
                background: rgba(255, 255, 255, 0.82);
                border: 1px solid rgba(17, 32, 63, 0.08);
                border-radius: 16px;
                padding: 0.9rem 1rem;
                box-shadow: 0 4px 14px rgba(17, 32, 63, 0.06);
                margin-top: 0.6rem;
                margin-bottom: 0.8rem;
            }

            .story-row p {
                margin: 0.22rem 0;
                color: #1f2d4a;
                font-size: 0.92rem;
            }

            .alert-card {
                border-radius: 14px;
                padding: 0.75rem 0.9rem;
                margin-bottom: 0.55rem;
                border: 1px solid rgba(17, 32, 63, 0.1);
                background: rgba(255,255,255,0.85);
            }

            .alert-title {
                font-weight: 700;
                font-size: 0.88rem;
                margin-bottom: 0.2rem;
            }

            .alert-text {
                font-size: 0.84rem;
                color: #2b395a;
                margin: 0.08rem 0;
            }

            .risk-high {
                border-left: 6px solid #d62828;
            }

            .risk-mid {
                border-left: 6px solid #f4a261;
            }

            .risk-low {
                border-left: 6px solid #2a9d8f;
            }

            .foot-note {
                margin-top: 1rem;
                font-size: 0.8rem;
                color: #556078;
            }

            @media (max-width: 900px) {
                .hero h2 {
                    font-size: 1.45rem;
                }
                .kpi-value {
                    font-size: 1.42rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = ascii_text.lower().strip()
    ascii_text = re.sub(r"[^a-z0-9]+", "_", ascii_text)
    ascii_text = re.sub(r"_+", "_", ascii_text).strip("_")
    return ascii_text


def to_brl(value: float) -> str:
    if pd.isna(value):
        return "R$ 0,00"
    formatted = f"{value:,.2f}"
    return f"R$ {formatted}".replace(",", "X").replace(".", ",").replace("X", ".")


def to_int(value: float) -> str:
    if pd.isna(value):
        return "0"
    return f"{int(round(value)):,}".replace(",", ".")


def to_pct(value: float) -> str:
    if pd.isna(value):
        return "0,0%"
    return f"{value * 100:.1f}%".replace(".", ",")


def build_export_url(sheet_url: str) -> str:
    parsed = urlparse(sheet_url)
    if "export?format=csv" in sheet_url:
        return sheet_url

    match = re.search(r"/d/([a-zA-Z0-9-_]+)", sheet_url)
    if not match:
        raise ValueError("Link inválido: não foi possível identificar o ID da planilha.")

    sheet_id = match.group(1)
    query_params = parse_qs(parsed.query)
    gid_from_query = query_params.get("gid", [None])[0]

    gid = gid_from_query
    if gid is None and parsed.fragment:
        fragment_match = re.search(r"gid=([0-9]+)", parsed.fragment)
        gid = fragment_match.group(1) if fragment_match else None

    if gid is None:
        gid = "0"

    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"


def parse_br_number(series: pd.Series) -> pd.Series:
    cleaned = (
        series.fillna("")
        .astype(str)
        .str.replace("\u00a0", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace("R$", "", regex=False)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.replace(r"[^0-9.\-]", "", regex=True)
    )
    return pd.to_numeric(cleaned, errors="coerce")


def parse_best_date(series: pd.Series) -> pd.Series:
    first = pd.to_datetime(series, errors="coerce", dayfirst=False)
    second = pd.to_datetime(series, errors="coerce", dayfirst=True)
    if first.notna().sum() >= second.notna().sum():
        return first
    return second


def canonical_column_names(columns: list[str]) -> dict[str, str]:
    renamed: dict[str, str] = {}
    for original in columns:
        key = normalize_text(original)

        if "data" in key and "emiss" in key:
            renamed[original] = "data_emissao"
        elif "nota" == key or key.startswith("nota"):
            renamed[original] = "nota"
        elif "pedido" in key:
            renamed[original] = "pedido"
        elif "cfop" in key:
            renamed[original] = "cfop"
        elif "destinat" in key:
            renamed[original] = "destinatario"
        elif "municip" in key:
            renamed[original] = "municipio"
        elif "frete" in key:
            renamed[original] = "frete"
        elif "vendedor" in key:
            renamed[original] = "vendedor"
        elif "quant" in key:
            renamed[original] = "quantidade"
        elif "valor" in key and "unit" in key:
            renamed[original] = "valor_unit"
        elif "valor" in key and "total" in key:
            renamed[original] = "valor_total"
        elif key == "st":
            renamed[original] = "st"
        elif "cod" in key and "prod" in key:
            renamed[original] = "cod_prod"
        elif "venc" in key and "fatura" in key:
            renamed[original] = "venc_fatura"
        elif "descricao" in key and "produto" in key:
            renamed[original] = "descricao_produto"
        elif "situ" in key:
            renamed[original] = "situacao"
        else:
            renamed[original] = key
    return renamed


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def load_data(sheet_url: str) -> pd.DataFrame:
    export_url = build_export_url(sheet_url)
    response = requests.get(export_url, timeout=45)
    response.raise_for_status()

    csv_text = response.content.decode("utf-8-sig", errors="ignore")
    df = pd.read_csv(io.StringIO(csv_text), dtype=str)
    df = df.rename(columns=canonical_column_names(list(df.columns)))

    required_cols = [
        "data_emissao",
        "pedido",
        "destinatario",
        "municipio",
        "frete",
        "vendedor",
        "quantidade",
        "valor_unit",
        "valor_total",
        "cod_prod",
        "descricao_produto",
        "situacao",
        "nota",
        "cfop",
    ]

    for col in required_cols:
        if col not in df.columns:
            df[col] = np.nan

    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = (
                df[col]
                .astype(str)
                .str.replace("\u00a0", " ", regex=False)
                .str.strip()
                .replace({"": np.nan, "nan": np.nan, "None": np.nan})
            )

    df["data_emissao"] = parse_best_date(df["data_emissao"])
    df["quantidade"] = parse_br_number(df["quantidade"]).fillna(0)
    df["valor_unit"] = parse_br_number(df["valor_unit"]).fillna(0)
    df["valor_total"] = parse_br_number(df["valor_total"]).fillna(0)

    df = df[df["data_emissao"].notna()].copy()
    df["pedido"] = df["pedido"].astype(str)

    df["ano"] = df["data_emissao"].dt.year
    df["mes"] = df["data_emissao"].dt.month
    df["ano_mes"] = df["data_emissao"].dt.to_period("M").dt.to_timestamp()
    df["dia_semana"] = df["data_emissao"].dt.day_name()

    cidade_estado = df["municipio"].fillna("-").str.rsplit("-", n=1, expand=True)
    if cidade_estado.shape[1] == 2:
        df["cidade"] = cidade_estado[0].str.strip()
        df["estado"] = cidade_estado[1].str.strip().str.upper()
    else:
        df["cidade"] = df["municipio"].fillna("-")
        df["estado"] = "NA"

    df["ticket_item"] = np.where(df["quantidade"] > 0, df["valor_total"] / df["quantidade"], 0)

    return df


def kpi_card(title: str, value: str, subtext: str, delta: float | None = None) -> str:
    delta_html = ""
    if delta is not None and np.isfinite(delta):
        delta_class = "kpi-delta-up" if delta >= 0 else "kpi-delta-down"
        arrow = "▲" if delta >= 0 else "▼"
        delta_html = f'<div class="{delta_class}">{arrow} {to_pct(abs(delta))} vs período anterior</div>'

    return f"""
        <div class="kpi-card">
            <div class="kpi-label">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{subtext}</div>
            {delta_html}
        </div>
    """


def compare_previous_period(df_all: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp, metric_col: str) -> float | None:
    if metric_col not in df_all.columns:
        return None

    days = (end_date - start_date).days + 1
    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - timedelta(days=max(days - 1, 1))

    current_mask = (df_all["data_emissao"] >= start_date) & (df_all["data_emissao"] <= end_date)
    prev_mask = (df_all["data_emissao"] >= prev_start) & (df_all["data_emissao"] <= prev_end)

    current_value = df_all.loc[current_mask, metric_col].sum()
    prev_value = df_all.loc[prev_mask, metric_col].sum()

    if prev_value <= 0:
        return None

    return (current_value - prev_value) / prev_value


def monthly_view(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("ano_mes", as_index=False)
        .agg(
            faturamento=("valor_total", "sum"),
            quantidade=("quantidade", "sum"),
            pedidos=("pedido", "nunique"),
        )
        .sort_values("ano_mes")
    )


def build_alerts(
    df: pd.DataFrame,
    cliente_limit: float,
    vendedor_limit: float,
) -> list[dict[str, str]]:
    if df.empty:
        return []

    alerts: list[dict[str, str]] = []
    receita_total = df["valor_total"].sum()

    if receita_total <= 0:
        return []

    cliente_agg = (
        df.groupby("destinatario", as_index=False)["valor_total"]
        .sum()
        .sort_values("valor_total", ascending=False)
    )
    if not cliente_agg.empty:
        share_cliente = cliente_agg.iloc[0]["valor_total"] / receita_total
        if share_cliente >= cliente_limit:
            alerts.append(
                {
                    "severity": "high",
                    "title": "Risco de concentração em cliente",
                    "detail": f"{cliente_agg.iloc[0]['destinatario']} representa {to_pct(share_cliente)} da receita.",
                    "action": "Ação sugerida: acelerar expansão em 2 a 3 contas de médio porte para reduzir dependência.",
                }
            )

    vendedor_agg = (
        df.groupby("vendedor", as_index=False)["valor_total"]
        .sum()
        .sort_values("valor_total", ascending=False)
    )
    if not vendedor_agg.empty:
        share_vendedor = vendedor_agg.iloc[0]["valor_total"] / receita_total
        if share_vendedor >= vendedor_limit:
            alerts.append(
                {
                    "severity": "mid",
                    "title": "Dependência comercial por vendedor",
                    "detail": f"Vendedor {vendedor_agg.iloc[0]['vendedor']} responde por {to_pct(share_vendedor)} do faturamento.",
                    "action": "Ação sugerida: redistribuir carteira e criar plano de cobertura comercial.",
                }
            )

    mensal = monthly_view(df)
    if len(mensal) >= 4:
        ult = mensal.iloc[-1]["faturamento"]
        media_3 = mensal.iloc[-4:-1]["faturamento"].mean()
        if media_3 > 0:
            delta = (ult - media_3) / media_3
            if delta <= -0.2:
                alerts.append(
                    {
                        "severity": "high",
                        "title": "Queda relevante no mês mais recente",
                        "detail": f"O último mês ficou {to_pct(abs(delta))} abaixo da média dos 3 meses anteriores.",
                        "action": "Ação sugerida: revisar rupturas, preço e mix de produtos de maior giro.",
                    }
                )

    ticket_item = np.where(df["quantidade"] > 0, df["valor_total"] / df["quantidade"], np.nan)
    if np.nanmean(ticket_item) > 0 and np.nanstd(ticket_item) / np.nanmean(ticket_item) > 1.2:
        alerts.append(
            {
                "severity": "mid",
                "title": "Alta dispersão de preço médio por item",
                "detail": "Existe grande variação de preço unitário entre vendas no recorte atual.",
                "action": "Ação sugerida: revisar política de preço e descontos por canal/cliente.",
            }
        )

    if not alerts:
        alerts.append(
            {
                "severity": "low",
                "title": "Operação estável no recorte",
                "detail": "Sem alertas críticos detectados com as regras atuais.",
                "action": "Ação sugerida: manter monitoramento semanal dos principais drivers.",
            }
        )

    return alerts[:4]


def build_forecast(mensal: pd.DataFrame, periods: int = 4) -> pd.DataFrame:
    if len(mensal) < 4:
        return pd.DataFrame()

    x = np.arange(len(mensal), dtype=float)
    y = mensal["faturamento"].to_numpy(dtype=float)

    slope, intercept = np.polyfit(x, y, 1)
    trend = slope * x + intercept
    residuals = y - trend
    sigma = float(np.std(residuals, ddof=1)) if len(residuals) > 1 else 0.0

    future_x = np.arange(len(mensal), len(mensal) + periods, dtype=float)
    future_y = slope * future_x + intercept
    future_dates = [mensal["ano_mes"].max() + pd.offsets.MonthBegin(i + 1) for i in range(periods)]

    z_score = 1.28
    lower = np.maximum(0, future_y - z_score * sigma)
    upper = np.maximum(0, future_y + z_score * sigma)

    forecast = pd.DataFrame(
        {
            "ano_mes": future_dates,
            "faturamento_previsto": np.maximum(0, future_y),
            "faixa_inferior": lower,
            "faixa_superior": upper,
        }
    )
    return forecast


def render_alerts(alerts: list[dict[str, str]]) -> None:
    level_map = {"high": "risk-high", "mid": "risk-mid", "low": "risk-low"}
    for item in alerts:
        level_class = level_map.get(item["severity"], "risk-low")
        st.markdown(
            (
                f'<div class="alert-card {level_class}">'
                f'<div class="alert-title">{item["title"]}</div>'
                f'<div class="alert-text">{item["detail"]}</div>'
                f'<div class="alert-text">{item["action"]}</div>'
                "</div>"
            ),
            unsafe_allow_html=True,
        )


def generate_insights(df: pd.DataFrame) -> list[str]:
    insights: list[str] = []

    if df.empty:
        return ["Sem dados após os filtros aplicados."]

    receita_total = df["valor_total"].sum()

    cliente_agg = df.groupby("destinatario", as_index=False)["valor_total"].sum().sort_values("valor_total", ascending=False)
    if not cliente_agg.empty and receita_total > 0:
        top_cliente = cliente_agg.iloc[0]
        share_cliente = top_cliente["valor_total"] / receita_total
        insights.append(
            f"Cliente líder: {top_cliente['destinatario']} concentra {to_pct(share_cliente)} do faturamento filtrado."
        )

    produto_agg = df.groupby("descricao_produto", as_index=False)["valor_total"].sum().sort_values("valor_total", ascending=False)
    if not produto_agg.empty and receita_total > 0:
        top_prod = produto_agg.iloc[0]
        share_prod = top_prod["valor_total"] / receita_total
        insights.append(
            f"Produto de maior impacto: {top_prod['descricao_produto']} representa {to_pct(share_prod)} da receita atual."
        )

    vendedor_agg = df.groupby("vendedor", as_index=False)["valor_total"].sum().sort_values("valor_total", ascending=False)
    if len(vendedor_agg) > 0 and receita_total > 0:
        share_vendedor = vendedor_agg.iloc[0]["valor_total"] / receita_total
        insights.append(
            f"Concentração comercial: vendedor {vendedor_agg.iloc[0]['vendedor']} responde por {to_pct(share_vendedor)} do faturamento."
        )

    mensal = df.groupby("ano_mes", as_index=False)["valor_total"].sum().sort_values("ano_mes")
    if len(mensal) >= 2 and mensal.iloc[-2]["valor_total"] > 0:
        last = mensal.iloc[-1]["valor_total"]
        previous = mensal.iloc[-2]["valor_total"]
        change = (last - previous) / previous
        direction = "crescimento" if change >= 0 else "queda"
        insights.append(f"Tendência recente: {direction} de {to_pct(abs(change))} no último mês fechado.")

    ticket_medio = np.where(df["quantidade"].sum() > 0, df["valor_total"].sum() / df["quantidade"].sum(), 0)
    insights.append(f"Preço médio ponderado no recorte: {to_brl(float(ticket_medio))} por unidade faturada.")

    return insights[:5]


def chart_layout(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        plot_bgcolor="rgba(255,255,255,0)",
        paper_bgcolor="rgba(255,255,255,0)",
        margin=dict(l=10, r=10, t=40, b=20),
        legend_title_text="",
        font=dict(family="Space Grotesk, sans-serif", color=COLORS["ink"]),
    )
    return fig


def render_presentation_mode(
    df_f: pd.DataFrame,
    mensal: pd.DataFrame,
    alerts: list[dict[str, str]],
    forecast_df: pd.DataFrame,
    meta_mensal: float,
    receita_total: float,
    quantidade_total: float,
    pedidos_unicos: int,
    ticket_medio_pedido: float,
    top_cliente_name: str,
    top_cliente_share: float,
    top_prod_name: str,
    mensal_last: float,
    media_3m: float,
    gap_meta: float,
) -> None:
    st.markdown("### Modo Apresentação")
    st.caption("Fluxo guiado para reunião executiva: avance pelas etapas e apresente com foco em decisão.")

    etapa = st.radio(
        "Etapa da apresentação",
        ["Panorama", "Riscos", "Oportunidades", "Plano"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if etapa == "Panorama":
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Faturamento", to_brl(receita_total))
        k2.metric("Volume", to_int(quantidade_total))
        k3.metric("Pedidos", to_int(pedidos_unicos))
        k4.metric("Ticket", to_brl(ticket_medio_pedido))

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=mensal["ano_mes"],
                y=mensal["faturamento"],
                mode="lines+markers",
                name="Faturamento",
                line=dict(color=COLORS["primary"], width=4),
            )
        )
        fig.add_trace(
            go.Bar(
                x=mensal["ano_mes"],
                y=mensal["quantidade"],
                name="Volume",
                marker_color="rgba(244,162,97,0.38)",
            )
        )
        fig.update_layout(title="Panorama Mensal de Receita e Volume")
        st.plotly_chart(chart_layout(fig), use_container_width=True)

        st.markdown(
            (
                f"**Mensagem-chave:** no recorte atual, o último mês fechou em {to_brl(mensal_last)} "
                f"(média de 3 meses: {to_brl(media_3m)})."
            )
        )

    elif etapa == "Riscos":
        render_alerts(alerts)

        top_clientes = (
            df_f.groupby("destinatario", as_index=False)["valor_total"]
            .sum()
            .sort_values("valor_total", ascending=False)
            .head(8)
        )
        fig_risk = px.bar(
            top_clientes.sort_values("valor_total"),
            x="valor_total",
            y="destinatario",
            orientation="h",
            title="Concentração de Receita - Top 8 Clientes",
            color="valor_total",
            color_continuous_scale=["#FCE4D8", "#F4A261", "#E76F51"],
            labels={"valor_total": "Receita (R$)", "destinatario": "Cliente"},
        )
        st.plotly_chart(chart_layout(fig_risk), use_container_width=True)

    elif etapa == "Oportunidades":
        c1, c2 = st.columns(2)

        produto_perf = (
            df_f.groupby("descricao_produto", as_index=False)["valor_total"]
            .sum()
            .sort_values("valor_total", ascending=False)
            .head(12)
        )
        estado_perf = (
            df_f.groupby("estado", as_index=False)["valor_total"]
            .sum()
            .sort_values("valor_total", ascending=False)
        )

        with c1:
            fig_prod = px.bar(
                produto_perf.sort_values("valor_total"),
                x="valor_total",
                y="descricao_produto",
                orientation="h",
                title="Top Produtos para Escalar Receita",
                color="valor_total",
                color_continuous_scale=["#D7EFEA", "#2A9D8F", "#1D3557"],
                labels={"valor_total": "Receita (R$)", "descricao_produto": "Produto"},
            )
            st.plotly_chart(chart_layout(fig_prod), use_container_width=True)

        with c2:
            fig_geo = px.bar(
                estado_perf,
                x="estado",
                y="valor_total",
                title="Estados com Maior Potencial de Crescimento",
                color="valor_total",
                color_continuous_scale=["#D6EAF8", "#0C6E74", "#1D3557"],
                labels={"valor_total": "Receita (R$)", "estado": "Estado"},
            )
            st.plotly_chart(chart_layout(fig_geo), use_container_width=True)

        st.markdown(
            f"**Mensagem-chave:** maior alavanca atual está em {top_prod_name}, e o cliente líder é {top_cliente_name} ({to_pct(top_cliente_share)} da receita)."
        )

    else:
        left, right = st.columns([1, 2])

        with left:
            fig_gauge = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=float(mensal_last),
                    number={"prefix": "R$ "},
                    title={"text": "Meta Mensal"},
                    gauge={
                        "axis": {"range": [0, max(meta_mensal * 1.5, mensal_last * 1.2 + 1)]},
                        "bar": {"color": COLORS["primary"]},
                        "steps": [
                            {"range": [0, meta_mensal * 0.85], "color": "#ffd6cc"},
                            {"range": [meta_mensal * 0.85, meta_mensal], "color": "#ffe9bf"},
                            {"range": [meta_mensal, max(meta_mensal * 1.5, mensal_last * 1.2 + 1)], "color": "#d8f3dc"},
                        ],
                        "threshold": {
                            "line": {"color": COLORS["accent"], "width": 4},
                            "thickness": 0.75,
                            "value": meta_mensal,
                        },
                    },
                )
            )
            fig_gauge.update_layout(height=320)
            st.plotly_chart(chart_layout(fig_gauge), use_container_width=True)

        with right:
            if forecast_df.empty:
                st.info("Sem meses suficientes para previsão no recorte atual.")
            else:
                fig_forecast = go.Figure()
                fig_forecast.add_trace(
                    go.Scatter(
                        x=mensal["ano_mes"],
                        y=mensal["faturamento"],
                        mode="lines+markers",
                        name="Histórico",
                        line=dict(color=COLORS["secondary"], width=3),
                    )
                )
                fig_forecast.add_trace(
                    go.Scatter(
                        x=forecast_df["ano_mes"],
                        y=forecast_df["faturamento_previsto"],
                        mode="lines+markers",
                        name="Previsão",
                        line=dict(color=COLORS["primary"], width=3, dash="dot"),
                    )
                )
                fig_forecast.update_layout(title="Previsão de Receita - 4 Meses")
                st.plotly_chart(chart_layout(fig_forecast), use_container_width=True)

        st.markdown("**Plano de ação recomendado:**")
        st.markdown("1. Defender as contas estratégicas e reduzir concentração com novas contas de médio porte.")
        st.markdown("2. Priorizar os produtos líderes com maior margem e maior giro.")
        st.markdown(
            f"3. {'Ativar plano comercial para recuperar' if gap_meta < 0 else 'Sustentar ritmo e elevar rentabilidade com mix premium'} {to_brl(abs(gap_meta))} {'abaixo' if gap_meta < 0 else 'acima'} da meta."
        )


def main() -> None:
    inject_styles()

    st.markdown(
        """
        <div class="hero">
            <h2>Radar Executivo de Produtos Faturados</h2>
            <p>Visão comercial e operacional em tempo real, conectada ao Google Sheets.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.title("Configuração")
        sheet_url = st.text_input("Link da planilha Google Sheets", value=DEFAULT_SHEET_URL)
        refresh_click = st.button("Atualizar dados agora", use_container_width=True)
        modo_apresentacao = st.toggle("Modo Apresentação", value=False)
        st.caption("Atualização automática em cache a cada 5 minutos.")

    if refresh_click:
        st.cache_data.clear()

    try:
        df = load_data(sheet_url)
    except Exception as exc:
        st.error(f"Não foi possível carregar a planilha. Erro: {exc}")
        st.stop()

    if df.empty:
        st.warning("A planilha não retornou dados válidos no recorte atual.")
        st.stop()

    data_min = df["data_emissao"].min().date()
    data_max = df["data_emissao"].max().date()

    with st.sidebar:
        st.markdown("---")
        st.subheader("Filtros")

        periodo = st.date_input(
            "Período",
            value=(data_min, data_max),
            min_value=data_min,
            max_value=data_max,
        )
        if not isinstance(periodo, tuple) or len(periodo) != 2:
            st.error("Selecione data inicial e final.")
            st.stop()

        clientes = sorted(df["destinatario"].dropna().unique().tolist())
        vendedores = sorted(df["vendedor"].dropna().unique().tolist())
        estados = sorted(df["estado"].dropna().unique().tolist())
        cidades = sorted(df["cidade"].dropna().unique().tolist())
        produtos = sorted(df["descricao_produto"].dropna().unique().tolist())
        fretes = sorted(df["frete"].dropna().unique().tolist())

        cliente_sel = st.multiselect("Cliente", options=clientes)
        vendedor_sel = st.multiselect("Vendedor", options=vendedores)
        estado_sel = st.multiselect("Estado", options=estados)
        cidade_sel = st.multiselect("Cidade", options=cidades)
        produto_sel = st.multiselect("Produto", options=produtos)
        frete_sel = st.multiselect("Frete", options=fretes)

        st.markdown("---")
        st.subheader("Metas e Alertas")
        meta_mensal = st.number_input(
            "Meta de faturamento mensal (R$)",
            min_value=0.0,
            value=300000.0,
            step=10000.0,
        )
        limite_cliente = st.slider("Alerta concentração por cliente", min_value=20, max_value=90, value=45, step=1) / 100
        limite_vendedor = st.slider("Alerta concentração por vendedor", min_value=20, max_value=95, value=70, step=1) / 100

    start_date = pd.Timestamp(periodo[0])
    end_date = pd.Timestamp(periodo[1])

    mask = (df["data_emissao"] >= start_date) & (df["data_emissao"] <= end_date)
    if cliente_sel:
        mask &= df["destinatario"].isin(cliente_sel)
    if vendedor_sel:
        mask &= df["vendedor"].isin(vendedor_sel)
    if estado_sel:
        mask &= df["estado"].isin(estado_sel)
    if cidade_sel:
        mask &= df["cidade"].isin(cidade_sel)
    if produto_sel:
        mask &= df["descricao_produto"].isin(produto_sel)
    if frete_sel:
        mask &= df["frete"].isin(frete_sel)

    df_f = df.loc[mask].copy()

    if df_f.empty:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")
        st.stop()

    receita_total = df_f["valor_total"].sum()
    quantidade_total = df_f["quantidade"].sum()
    pedidos_unicos = df_f["pedido"].nunique()
    clientes_ativos = df_f["destinatario"].nunique()
    produtos_ativos = df_f["descricao_produto"].nunique()
    ticket_medio_pedido = receita_total / pedidos_unicos if pedidos_unicos > 0 else 0
    preco_medio_ponderado = receita_total / quantidade_total if quantidade_total > 0 else 0

    delta_receita = compare_previous_period(df, start_date, end_date, "valor_total")
    delta_volume = compare_previous_period(df, start_date, end_date, "quantidade")
    mensal = monthly_view(df_f)

    forecast_df = build_forecast(mensal, periods=4)
    alerts = build_alerts(df_f, cliente_limit=limite_cliente, vendedor_limit=limite_vendedor)

    top_cliente_row = (
        df_f.groupby("destinatario", as_index=False)["valor_total"]
        .sum()
        .sort_values("valor_total", ascending=False)
        .head(1)
    )
    top_prod_row = (
        df_f.groupby("descricao_produto", as_index=False)["valor_total"]
        .sum()
        .sort_values("valor_total", ascending=False)
        .head(1)
    )
    top_cliente_name = top_cliente_row.iloc[0]["destinatario"] if not top_cliente_row.empty else "-"
    top_cliente_share = (top_cliente_row.iloc[0]["valor_total"] / receita_total) if (not top_cliente_row.empty and receita_total > 0) else 0
    top_prod_name = top_prod_row.iloc[0]["descricao_produto"] if not top_prod_row.empty else "-"

    mensal_last = mensal.iloc[-1]["faturamento"] if not mensal.empty else 0
    media_3m = mensal.tail(3)["faturamento"].mean() if not mensal.empty else 0
    gap_meta = mensal_last - meta_mensal

    if modo_apresentacao:
        render_presentation_mode(
            df_f=df_f,
            mensal=mensal,
            alerts=alerts,
            forecast_df=forecast_df,
            meta_mensal=meta_mensal,
            receita_total=receita_total,
            quantidade_total=quantidade_total,
            pedidos_unicos=pedidos_unicos,
            ticket_medio_pedido=ticket_medio_pedido,
            top_cliente_name=top_cliente_name,
            top_cliente_share=top_cliente_share,
            top_prod_name=top_prod_name,
            mensal_last=mensal_last,
            media_3m=media_3m,
            gap_meta=gap_meta,
        )

        missing_nota = df["nota"].isna().mean() * 100
        missing_cfop = df["cfop"].isna().mean() * 100
        st.markdown(
            f'<div class="foot-note">Qualidade de dados: Nota com {missing_nota:.1f}% de ausência e CFOP com {missing_cfop:.1f}% de ausência.</div>',
            unsafe_allow_html=True,
        )
        return

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(kpi_card("Faturamento", to_brl(receita_total), "Receita no período", delta_receita), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Volume", to_int(quantidade_total), "Unidades faturadas", delta_volume), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("Pedidos", to_int(pedidos_unicos), "Pedidos únicos"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("Ticket por Pedido", to_brl(ticket_medio_pedido), "Média por pedido"), unsafe_allow_html=True)
    with c5:
        st.markdown(kpi_card("Preço Médio", to_brl(preco_medio_ponderado), "Valor por unidade"), unsafe_allow_html=True)
    with c6:
        st.markdown(kpi_card("Clientes Ativos", to_int(clientes_ativos), f"{to_int(produtos_ativos)} produtos ativos"), unsafe_allow_html=True)

    insights = generate_insights(df_f)
    st.markdown('<div class="insight-box">' + "".join([f"<p>• {i}</p>" for i in insights]) + "</div>", unsafe_allow_html=True)

    st.subheader("Narrativa Executiva em 60 Segundos")
    st.markdown(
        (
            '<div class="story-row">'
            f"<p><strong>Onde estamos:</strong> faturamento recente de {to_brl(mensal_last)} versus média móvel trimestral de {to_brl(media_3m)}.</p>"
            f"<p><strong>O que move o resultado:</strong> principal cliente é {top_cliente_name} com {to_pct(top_cliente_share)} da receita; produto líder: {top_prod_name}.</p>"
            f"<p><strong>O que fazer agora:</strong> {'acelerar receita para fechar meta mensal' if gap_meta < 0 else 'sustentar ritmo e proteger margem'} ({to_brl(abs(gap_meta))} {'abaixo' if gap_meta < 0 else 'acima'} da meta).</p>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    st.subheader("Alertas Inteligentes")
    render_alerts(alerts)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Visão Executiva", "Comercial", "Produtos", "Geografia e Detalhes", "Previsão e Metas"]
    )

    with tab1:
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        fig_trend.add_trace(
            go.Bar(
                x=mensal["ano_mes"],
                y=mensal["quantidade"],
                name="Volume",
                marker_color="rgba(244,162,97,0.45)",
            ),
            secondary_y=False,
        )
        fig_trend.add_trace(
            go.Scatter(
                x=mensal["ano_mes"],
                y=mensal["faturamento"],
                name="Faturamento",
                mode="lines+markers",
                line=dict(color=COLORS["primary"], width=3),
                marker=dict(size=7, color=COLORS["secondary"]),
            ),
            secondary_y=True,
        )
        fig_trend.update_yaxes(title_text="Volume", secondary_y=False)
        fig_trend.update_yaxes(title_text="Faturamento (R$)", secondary_y=True)
        fig_trend.update_layout(title="Evolução Mensal de Receita e Volume")
        st.plotly_chart(chart_layout(fig_trend), use_container_width=True)

        top_clientes = (
            df_f.groupby("destinatario", as_index=False)["valor_total"]
            .sum()
            .sort_values("valor_total", ascending=False)
            .head(12)
        )
        top_clientes["acumulado"] = top_clientes["valor_total"].cumsum() / top_clientes["valor_total"].sum()

        fig_pareto_clientes = make_subplots(specs=[[{"secondary_y": True}]])
        fig_pareto_clientes.add_trace(
            go.Bar(
                x=top_clientes["destinatario"],
                y=top_clientes["valor_total"],
                name="Faturamento",
                marker_color=COLORS["secondary"],
            ),
            secondary_y=False,
        )
        fig_pareto_clientes.add_trace(
            go.Scatter(
                x=top_clientes["destinatario"],
                y=top_clientes["acumulado"] * 100,
                name="Acumulado %",
                mode="lines+markers",
                line=dict(color=COLORS["accent"], width=3),
            ),
            secondary_y=True,
        )
        fig_pareto_clientes.update_yaxes(title_text="Faturamento (R$)", secondary_y=False)
        fig_pareto_clientes.update_yaxes(title_text="Acumulado (%)", secondary_y=True, range=[0, 105])
        fig_pareto_clientes.update_layout(title="Pareto de Clientes (Top 12)")
        st.plotly_chart(chart_layout(fig_pareto_clientes), use_container_width=True)

    with tab2:
        col_a, col_b = st.columns(2)

        vendedor_perf = (
            df_f.groupby("vendedor", as_index=False)
            .agg(faturamento=("valor_total", "sum"), volume=("quantidade", "sum"), pedidos=("pedido", "nunique"))
            .sort_values("faturamento", ascending=False)
        )

        with col_a:
            fig_vendedores = px.pie(
                vendedor_perf,
                names="vendedor",
                values="faturamento",
                hole=0.45,
                color_discrete_sequence=[COLORS["primary"], COLORS["accent"], COLORS["gold"], COLORS["mint"]],
                title="Participação de Faturamento por Vendedor",
            )
            st.plotly_chart(chart_layout(fig_vendedores), use_container_width=True)

        with col_b:
            cliente_scatter = (
                df_f.groupby("destinatario", as_index=False)
                .agg(
                    faturamento=("valor_total", "sum"),
                    volume=("quantidade", "sum"),
                    ticket_medio=("ticket_item", "mean"),
                    pedidos=("pedido", "nunique"),
                )
                .sort_values("faturamento", ascending=False)
                .head(20)
            )
            fig_scatter = px.scatter(
                cliente_scatter,
                x="volume",
                y="faturamento",
                size="ticket_medio",
                color="pedidos",
                color_continuous_scale="Tealgrn",
                hover_name="destinatario",
                title="Clientes: Volume x Receita x Ticket",
                labels={"volume": "Volume", "faturamento": "Receita (R$)", "pedidos": "Pedidos"},
            )
            fig_scatter.update_traces(marker=dict(line=dict(width=1, color="white"), opacity=0.82))
            st.plotly_chart(chart_layout(fig_scatter), use_container_width=True)

        ticket_cliente = (
            df_f.groupby("destinatario", as_index=False)
            .agg(faturamento=("valor_total", "sum"), pedidos=("pedido", "nunique"))
            .query("pedidos > 0")
        )
        ticket_cliente["ticket"] = ticket_cliente["faturamento"] / ticket_cliente["pedidos"]
        ticket_cliente = ticket_cliente.sort_values("ticket", ascending=False).head(15)

        fig_ticket = px.bar(
            ticket_cliente,
            x="ticket",
            y="destinatario",
            orientation="h",
            title="Top 15 Clientes por Ticket Médio de Pedido",
            color="ticket",
            color_continuous_scale=["#CDECE7", "#2A9D8F", "#1D3557"],
            labels={"ticket": "Ticket Médio (R$)", "destinatario": "Cliente"},
        )
        fig_ticket.update_layout(yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(chart_layout(fig_ticket), use_container_width=True)

    with tab3:
        col_p1, col_p2 = st.columns(2)

        produto_perf = (
            df_f.groupby(["descricao_produto", "cod_prod"], as_index=False)
            .agg(faturamento=("valor_total", "sum"), volume=("quantidade", "sum"))
            .sort_values("faturamento", ascending=False)
        )

        top_prod = produto_perf.head(15).copy()
        top_prod["produto"] = top_prod["descricao_produto"].str.slice(0, 48)

        with col_p1:
            fig_prod = px.bar(
                top_prod.sort_values("faturamento"),
                x="faturamento",
                y="produto",
                orientation="h",
                title="Top 15 Produtos por Receita",
                color="faturamento",
                color_continuous_scale=["#FCE4D8", "#F4A261", "#E76F51"],
                labels={"faturamento": "Receita (R$)", "produto": "Produto"},
            )
            st.plotly_chart(chart_layout(fig_prod), use_container_width=True)

        with col_p2:
            fig_tree = px.treemap(
                top_prod,
                path=["produto"],
                values="faturamento",
                color="volume",
                color_continuous_scale=["#D7EFEA", "#2A9D8F", "#1D3557"],
                title="Mix de Receita dos Principais Produtos",
            )
            st.plotly_chart(chart_layout(fig_tree), use_container_width=True)

        pareto = produto_perf.copy()
        pareto["acumulado"] = pareto["faturamento"].cumsum() / pareto["faturamento"].sum()
        pareto_display = pareto.head(25)

        fig_pareto_prod = make_subplots(specs=[[{"secondary_y": True}]])
        fig_pareto_prod.add_trace(
            go.Bar(
                x=pareto_display["descricao_produto"].str.slice(0, 28),
                y=pareto_display["faturamento"],
                name="Receita",
                marker_color=COLORS["mint"],
            ),
            secondary_y=False,
        )
        fig_pareto_prod.add_trace(
            go.Scatter(
                x=pareto_display["descricao_produto"].str.slice(0, 28),
                y=pareto_display["acumulado"] * 100,
                name="Acumulado %",
                mode="lines+markers",
                line=dict(color=COLORS["accent"], width=3),
            ),
            secondary_y=True,
        )
        fig_pareto_prod.update_yaxes(title_text="Receita (R$)", secondary_y=False)
        fig_pareto_prod.update_yaxes(title_text="Acumulado (%)", secondary_y=True, range=[0, 105])
        fig_pareto_prod.update_layout(title="Curva ABC de Produtos (Top 25)")
        st.plotly_chart(chart_layout(fig_pareto_prod), use_container_width=True)

    with tab4:
        col_g1, col_g2 = st.columns(2)

        estado_perf = (
            df_f.groupby("estado", as_index=False)
            .agg(faturamento=("valor_total", "sum"), volume=("quantidade", "sum"), clientes=("destinatario", "nunique"))
            .sort_values("faturamento", ascending=False)
        )

        with col_g1:
            fig_estado = px.bar(
                estado_perf,
                x="estado",
                y="faturamento",
                color="clientes",
                title="Receita por Estado",
                color_continuous_scale=["#D6EAF8", "#0C6E74", "#1D3557"],
                labels={"faturamento": "Receita (R$)", "estado": "Estado", "clientes": "Clientes"},
            )
            st.plotly_chart(chart_layout(fig_estado), use_container_width=True)

        with col_g2:
            cidade_perf = (
                df_f.groupby("cidade", as_index=False)["valor_total"]
                .sum()
                .sort_values("valor_total", ascending=False)
                .head(15)
            )
            fig_cidade = px.bar(
                cidade_perf.sort_values("valor_total"),
                x="valor_total",
                y="cidade",
                orientation="h",
                title="Top 15 Cidades por Receita",
                color="valor_total",
                color_continuous_scale=["#EEF7FA", "#2A9D8F", "#1D3557"],
                labels={"valor_total": "Receita (R$)", "cidade": "Cidade"},
            )
            st.plotly_chart(chart_layout(fig_cidade), use_container_width=True)

        st.subheader("Detalhamento do Recorte")
        detalhamento = df_f[
            [
                "data_emissao",
                "pedido",
                "destinatario",
                "cidade",
                "estado",
                "vendedor",
                "descricao_produto",
                "quantidade",
                "valor_unit",
                "valor_total",
                "frete",
                "situacao",
            ]
        ].sort_values("data_emissao", ascending=False)

        st.dataframe(
            detalhamento,
            use_container_width=True,
            hide_index=True,
            height=390,
        )

        st.download_button(
            label="Baixar recorte filtrado (CSV)",
            data=detalhamento.to_csv(index=False).encode("utf-8-sig"),
            file_name="recorte_dashboard_produtos_faturados.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with tab5:
        c_meta1, c_meta2 = st.columns([1, 2])

        with c_meta1:
            fig_gauge = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=float(mensal_last),
                    number={"prefix": "R$ "},
                    title={"text": "Faturamento do mês recente"},
                    gauge={
                        "axis": {"range": [0, max(meta_mensal * 1.5, mensal_last * 1.2 + 1)]},
                        "bar": {"color": COLORS["primary"]},
                        "steps": [
                            {"range": [0, meta_mensal * 0.85], "color": "#ffd6cc"},
                            {"range": [meta_mensal * 0.85, meta_mensal], "color": "#ffe9bf"},
                            {"range": [meta_mensal, max(meta_mensal * 1.5, mensal_last * 1.2 + 1)], "color": "#d8f3dc"},
                        ],
                        "threshold": {
                            "line": {"color": COLORS["accent"], "width": 4},
                            "thickness": 0.75,
                            "value": meta_mensal,
                        },
                    },
                )
            )
            fig_gauge.update_layout(height=320)
            st.plotly_chart(chart_layout(fig_gauge), use_container_width=True)

            atingimento = (mensal_last / meta_mensal) if meta_mensal > 0 else 0
            st.metric("Atingimento da meta", to_pct(atingimento))

        with c_meta2:
            if forecast_df.empty:
                st.info("Previsão disponível quando houver pelo menos 4 meses no recorte filtrado.")
            else:
                historico = mensal[["ano_mes", "faturamento"]].copy()
                historico["tipo"] = "Histórico"

                previsto = forecast_df[["ano_mes", "faturamento_previsto"]].rename(columns={"faturamento_previsto": "faturamento"})
                previsto["tipo"] = "Previsto"

                fig_forecast = go.Figure()
                fig_forecast.add_trace(
                    go.Scatter(
                        x=historico["ano_mes"],
                        y=historico["faturamento"],
                        mode="lines+markers",
                        name="Histórico",
                        line=dict(color=COLORS["secondary"], width=3),
                    )
                )
                fig_forecast.add_trace(
                    go.Scatter(
                        x=forecast_df["ano_mes"],
                        y=forecast_df["faturamento_previsto"],
                        mode="lines+markers",
                        name="Previsão base",
                        line=dict(color=COLORS["primary"], width=3, dash="dot"),
                    )
                )
                fig_forecast.add_trace(
                    go.Scatter(
                        x=forecast_df["ano_mes"],
                        y=forecast_df["faixa_superior"],
                        mode="lines",
                        line=dict(width=0),
                        showlegend=False,
                        hoverinfo="skip",
                    )
                )
                fig_forecast.add_trace(
                    go.Scatter(
                        x=forecast_df["ano_mes"],
                        y=forecast_df["faixa_inferior"],
                        mode="lines",
                        line=dict(width=0),
                        fill="tonexty",
                        fillcolor="rgba(12,110,116,0.16)",
                        name="Faixa provável (80%)",
                    )
                )
                fig_forecast.update_layout(title="Projeção de Faturamento para Próximos 4 Meses")
                st.plotly_chart(chart_layout(fig_forecast), use_container_width=True)

                cenario = forecast_df[["ano_mes", "faturamento_previsto"]].copy()
                cenario["Conservador (-10%)"] = cenario["faturamento_previsto"] * 0.9
                cenario["Base"] = cenario["faturamento_previsto"]
                cenario["Otimista (+10%)"] = cenario["faturamento_previsto"] * 1.1
                cenario["ano_mes"] = cenario["ano_mes"].dt.strftime("%m/%Y")

                st.dataframe(
                    cenario.rename(columns={"ano_mes": "Mês"})[["Mês", "Conservador (-10%)", "Base", "Otimista (+10%)"]],
                    use_container_width=True,
                    hide_index=True,
                )

    missing_nota = df["nota"].isna().mean() * 100
    missing_cfop = df["cfop"].isna().mean() * 100
    st.markdown(
        f'<div class="foot-note">Qualidade de dados: Nota com {missing_nota:.1f}% de ausência e CFOP com {missing_cfop:.1f}% de ausência. Essas colunas foram mantidas fora das análises críticas.</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
