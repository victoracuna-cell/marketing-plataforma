import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ─── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TikTok Trends Dashboard",
    page_icon="🎵",
    layout="wide",
)

# ─── ESTILOS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Inter:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main { background-color: #0a0a0f; }

    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif;
        color: #f0f0f5;
    }

    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #12121f 100%);
    }

    /* Metric cards */
    .metric-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 12px;
    }

    .metric-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #fe2c55;
    }

    .metric-label {
        font-size: 0.8rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 4px;
    }

    /* Trend card */
    .trend-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 10px;
        transition: border-color 0.2s;
    }

    .trend-card:hover {
        border-color: rgba(254, 44, 85, 0.4);
    }

    .trend-rank {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: rgba(254,44,85,0.6);
        min-width: 40px;
    }

    .trend-title {
        font-weight: 600;
        color: #f0f0f5;
        font-size: 1rem;
    }

    .trend-meta {
        font-size: 0.78rem;
        color: #666;
        margin-top: 4px;
    }

    .tag {
        display: inline-block;
        background: rgba(254,44,85,0.15);
        color: #fe2c55;
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-right: 4px;
    }

    /* Header */
    .hero-header {
        padding: 32px 0 20px;
        border-bottom: 1px solid rgba(255,255,255,0.07);
        margin-bottom: 32px;
    }

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.4rem;
        font-weight: 700;
        color: #f0f0f5;
        line-height: 1.1;
    }

    .hero-subtitle {
        color: #666;
        font-size: 0.95rem;
        margin-top: 8px;
    }

    .tiktok-dot {
        color: #fe2c55;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #0d0d1a;
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    /* Buttons */
    .stButton > button {
        background: #fe2c55;
        color: white;
        border: none;
        border-radius: 10px;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        padding: 10px 24px;
        width: 100%;
    }

    .stButton > button:hover {
        background: #e0253f;
        border: none;
    }

    /* Input */
    .stTextInput input, .stSelectbox select {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
        color: #f0f0f5;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid rgba(255,255,255,0.07);
    }

    .stTabs [data-baseweb="tab"] {
        color: #666;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        color: #fe2c55 !important;
    }

    /* Divider */
    hr { border-color: rgba(255,255,255,0.06); }

    /* Dataframe */
    .stDataFrame { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ─── FUNCIONES APIFY ───────────────────────────────────────────────────────────
def fetch_tiktok_trends(api_token: str, country: str = "US", max_items: int = 30):
    """
    Llama al Actor de Apify para TikTok Trending Videos.
    Actor usado: clockworks/free-tiktok-scraper (público y gratuito)
    """
    actor_id = "clockworks~free-tiktok-scraper"
    url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"

    params = {"token": api_token, "timeout": 120}

    payload = {
        "searchQueries": ["trending"],
        "maxItems": max_items,
        "resultsPerPage": max_items,
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
        "shouldDownloadSubtitles": False,
        "shouldDownloadSlideshowImages": False,
    }

    with st.spinner("⏳ Conectando con Apify y extrayendo trends de TikTok..."):
        try:
            resp = requests.post(url, json=payload, params=params, timeout=180)
            resp.raise_for_status()
            return resp.json(), None
        except requests.exceptions.Timeout:
            return None, "Timeout: Apify tardó demasiado. Intenta con menos items."
        except requests.exceptions.HTTPError as e:
            if resp.status_code == 401:
                return None, "Token de Apify inválido. Verifica tu API token."
            return None, f"Error HTTP {resp.status_code}: {e}"
        except Exception as e:
            return None, f"Error inesperado: {e}"


def parse_tiktok_data(raw: list) -> pd.DataFrame:
    """Normaliza la respuesta cruda de Apify a un DataFrame limpio."""
    rows = []
    for item in raw:
        author = item.get("authorMeta", {}) or {}
        music = item.get("musicMeta", {}) or {}
        stats = item.get("diggCount", 0)

        rows.append({
            "id": item.get("id", ""),
            "descripcion": item.get("text", "")[:120],
            "autor": author.get("name", ""),
            "nickname": "@" + author.get("nickName", ""),
            "likes": item.get("diggCount", 0),
            "comentarios": item.get("commentCount", 0),
            "shares": item.get("shareCount", 0),
            "plays": item.get("playCount", 0),
            "musica": music.get("musicName", ""),
            "hashtags": ", ".join([f"#{h}" for h in (item.get("hashtags") or [])[:5]]),
            "url": item.get("webVideoUrl", ""),
            "fecha": datetime.fromtimestamp(item.get("createTime", 0)).strftime("%Y-%m-%d")
            if item.get("createTime") else "",
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("plays", ascending=False).reset_index(drop=True)
        df.index += 1
    return df


def fmt_number(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎵 TikTok Trends")
    st.markdown("---")

    api_token = st.text_input(
        "Apify API Token",
        type="password",
        placeholder="apify_api_xxxxxxxxxxxx",
        help="Encuéntralo en apify.com → Settings → Integrations"
    )

    max_items = st.slider("Cantidad de videos a analizar", 10, 100, 30, step=10)

    st.markdown("---")
    fetch_btn = st.button("🔍 Buscar Trends", disabled=not api_token)

    st.markdown("---")
    st.markdown(
        "<span style='color:#444; font-size:0.75rem;'>Powered by Apify · clockworks/free-tiktok-scraper</span>",
        unsafe_allow_html=True
    )


# ─── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <div class="hero-title">TikTok <span class="tiktok-dot">Trends</span> Dashboard</div>
    <div class="hero-subtitle">Datos en tiempo real extraídos via Apify · Módulo 1</div>
</div>
""", unsafe_allow_html=True)


# ─── ESTADO DE SESSION ─────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None
if "error" not in st.session_state:
    st.session_state.error = None


# ─── FETCH ─────────────────────────────────────────────────────────────────────
if fetch_btn and api_token:
    raw, err = fetch_tiktok_trends(api_token, max_items=max_items)
    if err:
        st.session_state.error = err
        st.session_state.df = None
    else:
        st.session_state.df = parse_tiktok_data(raw)
        st.session_state.error = None


# ─── ERROR ─────────────────────────────────────────────────────────────────────
if st.session_state.error:
    st.error(f"❌ {st.session_state.error}")


# ─── DASHBOARD ─────────────────────────────────────────────────────────────────
df = st.session_state.df

if df is not None and not df.empty:
    total_plays = df["plays"].sum()
    total_likes = df["likes"].sum()
    avg_engagement = ((df["likes"] + df["comentarios"] + df["shares"]) / df["plays"].replace(0, 1) * 100).mean()

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(df)}</div>
            <div class="metric-label">Videos analizados</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{fmt_number(total_plays)}</div>
            <div class="metric-label">Reproducciones totales</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{fmt_number(total_likes)}</div>
            <div class="metric-label">Likes acumulados</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_engagement:.1f}%</div>
            <div class="metric-label">Engagement promedio</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # TABS
    tab1, tab2, tab3 = st.tabs(["🏆 Top Trends", "📊 Visualizaciones", "📋 Tabla completa"])

    # ── TAB 1: Cards ──
    with tab1:
        st.markdown("#### Top 10 videos más virales")
        for i, row in df.head(10).iterrows():
            col_rank, col_info, col_stats = st.columns([1, 6, 3])
            with col_rank:
                st.markdown(f"<div class='trend-rank'>#{i}</div>", unsafe_allow_html=True)
            with col_info:
                desc = row["descripcion"] if row["descripcion"] else "Sin descripción"
                tags = row["hashtags"] if row["hashtags"] else ""
                st.markdown(f"""
                <div>
                    <div class="trend-title">{row['nickname']} · {row['autor']}</div>
                    <div class="trend-meta">{desc}</div>
                    <div style="margin-top:6px">{' '.join([f'<span class="tag">{t.strip()}</span>' for t in tags.split(',') if t.strip()])}</div>
                </div>""", unsafe_allow_html=True)
            with col_stats:
                st.markdown(f"""
                <div style="text-align:right; padding-top:4px">
                    <div style="color:#f0f0f5; font-weight:600">▶ {fmt_number(row['plays'])}</div>
                    <div style="color:#fe2c55; font-size:0.85rem">♥ {fmt_number(row['likes'])}</div>
                    <div style="color:#666; font-size:0.78rem">💬 {fmt_number(row['comentarios'])} · ↗ {fmt_number(row['shares'])}</div>
                </div>""", unsafe_allow_html=True)

            if row["url"]:
                st.markdown(f"<a href='{row['url']}' target='_blank' style='color:#444; font-size:0.72rem; text-decoration:none;'>Ver en TikTok ↗</a>", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

    # ── TAB 2: Charts ──
    with tab2:
        col_a, col_b = st.columns(2)

        with col_a:
            fig1 = px.bar(
                df.head(15),
                x="plays",
                y="nickname",
                orientation="h",
                title="Top 15 · Reproducciones",
                color="plays",
                color_continuous_scale=["#1a1a2e", "#fe2c55"],
                labels={"plays": "Plays", "nickname": ""},
            )
            fig1.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#aaa",
                title_font_color="#f0f0f5",
                coloraxis_showscale=False,
                yaxis=dict(autorange="reversed"),
                margin=dict(l=0, r=20, t=40, b=0),
            )
            fig1.update_xaxes(gridcolor="rgba(255,255,255,0.05)")
            fig1.update_yaxes(gridcolor="rgba(255,255,255,0)")
            st.plotly_chart(fig1, use_container_width=True)

        with col_b:
            fig2 = px.scatter(
                df,
                x="plays",
                y="likes",
                size="comentarios",
                color="shares",
                hover_name="nickname",
                hover_data={"descripcion": True},
                title="Plays vs Likes (tamaño = comentarios)",
                color_continuous_scale=["#12122a", "#fe2c55"],
                labels={"plays": "Reproducciones", "likes": "Likes", "shares": "Shares"},
            )
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#aaa",
                title_font_color="#f0f0f5",
                coloraxis_showscale=False,
                margin=dict(l=0, r=0, t=40, b=0),
            )
            fig2.update_xaxes(gridcolor="rgba(255,255,255,0.05)")
            fig2.update_yaxes(gridcolor="rgba(255,255,255,0.05)")
            st.plotly_chart(fig2, use_container_width=True)

        # Música más usada
        if "musica" in df.columns:
            music_counts = df["musica"].value_counts().head(8).reset_index()
            music_counts.columns = ["musica", "count"]
            fig3 = px.pie(
                music_counts,
                values="count",
                names="musica",
                title="🎵 Músicas más usadas en trends",
                color_discrete_sequence=px.colors.sequential.RdBu,
                hole=0.45,
            )
            fig3.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#aaa",
                title_font_color="#f0f0f5",
            )
            st.plotly_chart(fig3, use_container_width=True)

    # ── TAB 3: Tabla ──
    with tab3:
        cols_show = ["nickname", "autor", "likes", "comentarios", "shares", "plays", "musica", "hashtags", "fecha", "url"]
        cols_show = [c for c in cols_show if c in df.columns]
        st.dataframe(
            df[cols_show].rename(columns={
                "nickname": "Usuario",
                "autor": "Nombre",
                "likes": "Likes",
                "comentarios": "Comentarios",
                "shares": "Shares",
                "plays": "Reproducciones",
                "musica": "Música",
                "hashtags": "Hashtags",
                "fecha": "Fecha",
                "url": "URL",
            }),
            use_container_width=True,
            height=480,
        )

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Descargar CSV",
            data=csv,
            file_name=f"tiktok_trends_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )

else:
    # Empty state
    st.markdown("""
    <div style="text-align:center; padding: 80px 20px; color: #444;">
        <div style="font-size: 3rem; margin-bottom: 16px;">🎵</div>
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.3rem; color: #555; margin-bottom: 8px;">
            Ingresa tu token y pulsa <strong style="color:#fe2c55">Buscar Trends</strong>
        </div>
        <div style="font-size: 0.85rem; color: #333;">
            Los datos se extraen en tiempo real desde TikTok via Apify
        </div>
    </div>
    """, unsafe_allow_html=True)
