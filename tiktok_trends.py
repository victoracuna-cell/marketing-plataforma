import streamlit as st
import requests
import pandas as pd
import plotly.express as px
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
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; color: #f0f0f5; }
    .stApp { background: linear-gradient(135deg, #0a0a0f 0%, #12121f 100%); }
    .metric-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 12px;
    }
    .metric-value { font-family: 'Space Grotesk', sans-serif; font-size: 2rem; font-weight: 700; color: #fe2c55; }
    .metric-label { font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px; }
    .trend-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 10px;
    }
    .trend-rank { font-family: 'Space Grotesk', sans-serif; font-size: 1.4rem; font-weight: 700; color: rgba(254,44,85,0.6); }
    .trend-title { font-weight: 600; color: #f0f0f5; font-size: 1rem; }
    .trend-meta { font-size: 0.78rem; color: #666; margin-top: 4px; }
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
    .filter-badge {
        display: inline-block;
        background: rgba(254,44,85,0.1);
        border: 1px solid rgba(254,44,85,0.3);
        color: #fe2c55;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 12px;
    }
    .hero-header { padding: 32px 0 20px; border-bottom: 1px solid rgba(255,255,255,0.07); margin-bottom: 32px; }
    .hero-title { font-family: 'Space Grotesk', sans-serif; font-size: 2.4rem; font-weight: 700; color: #f0f0f5; }
    .hero-subtitle { color: #666; font-size: 0.95rem; margin-top: 8px; }
    .tiktok-dot { color: #fe2c55; }
    section[data-testid="stSidebar"] { background: #0d0d1a; border-right: 1px solid rgba(255,255,255,0.06); }
    .stButton > button {
        background: #fe2c55; color: white; border: none;
        border-radius: 10px; font-family: 'Space Grotesk', sans-serif;
        font-weight: 600; padding: 10px 24px; width: 100%;
    }
    .stButton > button:hover { background: #e0253f; border: none; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid rgba(255,255,255,0.07); }
    .stTabs [data-baseweb="tab"] { color: #666; font-family: 'Space Grotesk', sans-serif; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #fe2c55 !important; }
    hr { border-color: rgba(255,255,255,0.06); }
</style>
""", unsafe_allow_html=True)

# ─── CONFIGURACIÓN DE PAÍSES Y CATEGORÍAS ──────────────────────────────────────

PAISES = {
    "🇨🇱 Chile":      {"codigo": "CL", "hashtag": "chile",     "idioma": "es"},
    "🇦🇷 Argentina":  {"codigo": "AR", "hashtag": "argentina", "idioma": "es"},
    "🇲🇽 México":     {"codigo": "MX", "hashtag": "mexico",    "idioma": "es"},
    "🇨🇴 Colombia":   {"codigo": "CO", "hashtag": "colombia",  "idioma": "es"},
    "🇵🇪 Perú":       {"codigo": "PE", "hashtag": "peru",      "idioma": "es"},
    "🇻🇪 Venezuela":  {"codigo": "VE", "hashtag": "venezuela", "idioma": "es"},
    "🇺🇾 Uruguay":    {"codigo": "UY", "hashtag": "uruguay",   "idioma": "es"},
}

CATEGORIAS = {
    "💼 Negocios":         ["negocios", "business", "emprendimiento"],
    "🚀 Emprendimiento":   ["emprendimiento", "startup", "emprender"],
    "📈 Marketing":        ["marketing", "marketingdigital", "ventas"],
    "💰 Finanzas":         ["finanzas", "finanzaspersonales", "inversion"],
    "🤖 Tecnología":       ["tecnologia", "tech", "inteligenciaartificial"],
    "📊 Productividad":    ["productividad", "trabajoremoto", "freelance"],
    "🧠 Desarrollo personal": ["desarrollopersonal", "motivacion", "exito"],
    "🏢 Vida corporativa": ["trabajocorporativo", "oficina", "carrera"],
}

# ─── FUNCIONES ─────────────────────────────────────────────────────────────────

def build_queries(pais_key: str, categorias_sel: list) -> list:
    pais = PAISES[pais_key]
    hashtag_pais = pais["hashtag"]
    queries = []
    for cat in categorias_sel:
        for kw in CATEGORIAS[cat]:
            queries.append(f"#{kw}{hashtag_pais}")
            queries.append(f"#{kw}")
    queries.append(f"#{hashtag_pais}negocios")
    queries.append(f"trending {hashtag_pais}")
    return list(dict.fromkeys(queries))[:10]  # máx 10 queries únicas


def fetch_tiktok_trends(api_token: str, queries: list, max_items: int = 30):
    actor_id = "clockworks~free-tiktok-scraper"
    url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"
    params = {"token": api_token, "timeout": 120}
    payload = {
        "searchQueries": queries,
        "maxItems": max_items,
        "resultsPerPage": max_items,
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
        "shouldDownloadSubtitles": False,
        "shouldDownloadSlideshowImages": False,
    }
    with st.spinner("⏳ Extrayendo trends de TikTok..."):
        try:
            resp = requests.post(url, json=payload, params=params, timeout=180)
            resp.raise_for_status()
            return resp.json(), None
        except requests.exceptions.Timeout:
            return None, "Timeout: Apify tardó demasiado. Intenta con menos items."
        except requests.exceptions.HTTPError:
            if resp.status_code == 401:
                return None, "Token de Apify inválido."
            return None, f"Error HTTP {resp.status_code}"
        except Exception as e:
            return None, f"Error: {e}"


def parse_tiktok_data(raw: list) -> pd.DataFrame:
    rows = []
    for item in raw:
        author = item.get("authorMeta", {}) or {}
        music  = item.get("musicMeta", {}) or {}
        rows.append({
            "descripcion":   (item.get("text", "") or "")[:120],
            "autor":         author.get("name", ""),
            "nickname":      "@" + author.get("nickName", ""),
            "likes":         item.get("diggCount", 0) or 0,
            "comentarios":   item.get("commentCount", 0) or 0,
            "shares":        item.get("shareCount", 0) or 0,
            "plays":         item.get("playCount", 0) or 0,
            "musica":        music.get("musicName", ""),
            "hashtags":      ", ".join([f"#{h}" for h in (item.get("hashtags") or [])[:5]]),
            "url":           item.get("webVideoUrl", ""),
            "fecha":         datetime.fromtimestamp(item.get("createTime", 0)).strftime("%Y-%m-%d")
                             if item.get("createTime") else "",
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("plays", ascending=False).reset_index(drop=True)
        df.index += 1
    return df


def fmt_number(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(n)


# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎵 TikTok Trends")
    st.markdown("---")

    api_token = st.text_input(
        "Apify API Token",
        type="password",
        placeholder="apify_api_xxxxxxxxxxxx",
    )

    st.markdown("#### 🌎 País")
    pais_sel = st.selectbox(
        "Selecciona un país",
        options=list(PAISES.keys()),
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("#### 📂 Categorías")
    cats_sel = st.multiselect(
        "Selecciona una o más categorías",
        options=list(CATEGORIAS.keys()),
        default=["💼 Negocios", "🚀 Emprendimiento"],
        label_visibility="collapsed",
    )

    max_items = st.slider("Videos a analizar", 10, 100, 30, step=10)

    st.markdown("---")
    fetch_btn = st.button(
        "🔍 Buscar Trends",
        disabled=not api_token or not cats_sel
    )

    st.markdown("---")
    st.markdown(
        "<span style='color:#333; font-size:0.72rem;'>Powered by Apify · clockworks/free-tiktok-scraper</span>",
        unsafe_allow_html=True,
    )

# ─── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-header">
    <div class="hero-title">TikTok <span class="tiktok-dot">Trends</span> Dashboard</div>
    <div class="hero-subtitle">Datos en tiempo real extraídos via Apify · Módulo 1</div>
</div>
""", unsafe_allow_html=True)

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
if "df" not in st.session_state:    st.session_state.df = None
if "error" not in st.session_state: st.session_state.error = None
if "last_pais" not in st.session_state: st.session_state.last_pais = ""
if "last_cats" not in st.session_state: st.session_state.last_cats = []

# ─── FETCH ─────────────────────────────────────────────────────────────────────
if fetch_btn and api_token and cats_sel:
    queries = build_queries(pais_sel, cats_sel)
    raw, err = fetch_tiktok_trends(api_token, queries, max_items)
    if err:
        st.session_state.error = err
        st.session_state.df = None
    else:
        st.session_state.df = parse_tiktok_data(raw)
        st.session_state.error = None
        st.session_state.last_pais = pais_sel
        st.session_state.last_cats = cats_sel

if st.session_state.error:
    st.error(f"❌ {st.session_state.error}")

# ─── DASHBOARD ─────────────────────────────────────────────────────────────────
df = st.session_state.df

if df is not None and not df.empty:

    # Filtros activos
    badges = f'<span class="filter-badge">{st.session_state.last_pais}</span>'
    for c in st.session_state.last_cats:
        badges += f'<span class="filter-badge">{c}</span>'
    st.markdown(f"<div style='margin-bottom:20px'>{badges}</div>", unsafe_allow_html=True)

    # KPIs
    total_plays  = df["plays"].sum()
    total_likes  = df["likes"].sum()
    avg_eng = ((df["likes"] + df["comentarios"] + df["shares"]) / df["plays"].replace(0, 1) * 100).mean()

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label in [
        (c1, len(df),        "Videos analizados"),
        (c2, fmt_number(total_plays), "Reproducciones totales"),
        (c3, fmt_number(total_likes), "Likes acumulados"),
        (c4, f"{avg_eng:.1f}%",       "Engagement promedio"),
    ]:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🏆 Top Trends", "📊 Visualizaciones", "📋 Tabla completa"])

    # ── TAB 1 ──
    with tab1:
        st.markdown("#### Top 10 videos más virales")
        for i, row in df.head(10).iterrows():
            col_rank, col_info, col_stats = st.columns([1, 6, 3])
            with col_rank:
                st.markdown(f"<div class='trend-rank'>#{i}</div>", unsafe_allow_html=True)
            with col_info:
                desc = row["descripcion"] or "Sin descripción"
                tags_html = " ".join([f'<span class="tag">{t.strip()}</span>' for t in row["hashtags"].split(",") if t.strip()])
                st.markdown(f"""
                <div>
                    <div class="trend-title">{row['nickname']} · {row['autor']}</div>
                    <div class="trend-meta">{desc}</div>
                    <div style="margin-top:6px">{tags_html}</div>
                </div>""", unsafe_allow_html=True)
            with col_stats:
                st.markdown(f"""
                <div style="text-align:right; padding-top:4px">
                    <div style="color:#f0f0f5; font-weight:600">▶ {fmt_number(row['plays'])}</div>
                    <div style="color:#fe2c55; font-size:0.85rem">♥ {fmt_number(row['likes'])}</div>
                    <div style="color:#666; font-size:0.78rem">💬 {fmt_number(row['comentarios'])} · ↗ {fmt_number(row['shares'])}</div>
                </div>""", unsafe_allow_html=True)
            if row["url"]:
                st.markdown(f"<a href='{row['url']}' target='_blank' style='color:#444; font-size:0.72rem;'>Ver en TikTok ↗</a>", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

    # ── TAB 2 ──
    with tab2:
        col_a, col_b = st.columns(2)

        PLOT_LAYOUT = dict(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#aaa",
            title_font_color="#f0f0f5",
            margin=dict(l=0, r=10, t=40, b=0),
        )

        with col_a:
            fig1 = px.bar(
                df.head(15), x="plays", y="nickname", orientation="h",
                title="Top 15 · Reproducciones",
                color="plays", color_continuous_scale=["#1a1a2e", "#fe2c55"],
                labels={"plays": "Plays", "nickname": ""},
            )
            fig1.update_layout(**PLOT_LAYOUT, coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
            fig1.update_xaxes(gridcolor="rgba(255,255,255,0.05)")
            fig1.update_yaxes(gridcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig1, use_container_width=True)

        with col_b:
            fig2 = px.scatter(
                df, x="plays", y="likes", size="comentarios", color="shares",
                hover_name="nickname",
                title="Plays vs Likes (tamaño = comentarios)",
                color_continuous_scale=["#12122a", "#fe2c55"],
                labels={"plays": "Reproducciones", "likes": "Likes"},
            )
            fig2.update_layout(**PLOT_LAYOUT, coloraxis_showscale=False)
            fig2.update_xaxes(gridcolor="rgba(255,255,255,0.05)")
            fig2.update_yaxes(gridcolor="rgba(255,255,255,0.05)")
            st.plotly_chart(fig2, use_container_width=True)

        music_counts = df["musica"].value_counts().head(8).reset_index()
        music_counts.columns = ["musica", "count"]
        fig3 = px.pie(
            music_counts, values="count", names="musica",
            title="🎵 Músicas más usadas en trends",
            color_discrete_sequence=px.colors.sequential.RdBu, hole=0.45,
        )
        fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#aaa", title_font_color="#f0f0f5")
        st.plotly_chart(fig3, use_container_width=True)

    # ── TAB 3 ──
    with tab3:
        cols_show = ["nickname", "autor", "likes", "comentarios", "shares", "plays", "musica", "hashtags", "fecha", "url"]
        st.dataframe(
            df[[c for c in cols_show if c in df.columns]].rename(columns={
                "nickname": "Usuario", "autor": "Nombre", "likes": "Likes",
                "comentarios": "Comentarios", "shares": "Shares",
                "plays": "Reproducciones", "musica": "Música",
                "hashtags": "Hashtags", "fecha": "Fecha", "url": "URL",
            }),
            use_container_width=True, height=480,
        )
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Descargar CSV", data=csv,
            file_name=f"tiktok_trends_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )

else:
    st.markdown("""
    <div style="text-align:center; padding: 80px 20px; color: #444;">
        <div style="font-size: 3rem; margin-bottom: 16px;">🎵</div>
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.3rem; color: #555; margin-bottom: 8px;">
            Selecciona país, categorías y pulsa <strong style="color:#fe2c55">Buscar Trends</strong>
        </div>
        <div style="font-size: 0.85rem; color: #333;">Los datos se extraen en tiempo real desde TikTok via Apify</div>
    </div>
    """, unsafe_allow_html=True)
