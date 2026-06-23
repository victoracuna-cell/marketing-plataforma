import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ─── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Instagram Trends Dashboard",
    page_icon="📸",
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
    .metric-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label { font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px; }

    .post-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 12px;
        transition: border-color 0.2s;
    }
    .post-card:hover { border-color: rgba(220, 39, 67, 0.4); }

    .post-rank {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: rgba(220,39,67,0.6);
    }
    .post-author { font-weight: 700; color: #f0f0f5; font-size: 1rem; }
    .post-caption { font-size: 0.82rem; color: #777; margin-top: 4px; line-height: 1.5; }

    .tag {
        display: inline-block;
        background: rgba(220,39,67,0.12);
        color: #e6683c;
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-right: 4px;
        margin-top: 4px;
    }

    .type-badge {
        display: inline-block;
        border-radius: 6px;
        padding: 2px 10px;
        font-size: 0.7rem;
        font-weight: 700;
        margin-right: 6px;
    }
    .type-reel { background: rgba(188,24,136,0.2); color: #bc1888; }
    .type-image { background: rgba(240,148,51,0.2); color: #f09433; }
    .type-carousel { background: rgba(220,39,67,0.2); color: #dc2743; }

    .filter-badge {
        display: inline-block;
        background: rgba(220,39,67,0.1);
        border: 1px solid rgba(220,39,67,0.3);
        color: #e6683c;
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 12px;
    }

    .hero-header { padding: 32px 0 20px; border-bottom: 1px solid rgba(255,255,255,0.07); margin-bottom: 32px; }
    .hero-title { font-family: 'Space Grotesk', sans-serif; font-size: 2.4rem; font-weight: 700; color: #f0f0f5; }
    .ig-gradient {
        background: linear-gradient(90deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle { color: #666; font-size: 0.95rem; margin-top: 8px; }

    section[data-testid="stSidebar"] { background: #0d0d1a; border-right: 1px solid rgba(255,255,255,0.06); }

    .stButton > button {
        background: linear-gradient(90deg, #dc2743, #bc1888);
        color: white; border: none;
        border-radius: 10px; font-family: 'Space Grotesk', sans-serif;
        font-weight: 600; padding: 10px 24px; width: 100%;
    }
    .stButton > button:hover { opacity: 0.88; border: none; }

    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid rgba(255,255,255,0.07); }
    .stTabs [data-baseweb="tab"] { color: #666; font-family: 'Space Grotesk', sans-serif; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #dc2743 !important; }
    hr { border-color: rgba(255,255,255,0.06); }

    .insight-box {
        background: rgba(220,39,67,0.06);
        border: 1px solid rgba(220,39,67,0.15);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .insight-title { font-family: 'Space Grotesk', sans-serif; font-weight: 700; color: #f0f0f5; font-size: 0.9rem; }
    .insight-value { font-size: 1.4rem; font-weight: 700; color: #e6683c; margin-top: 4px; }
    .insight-desc { font-size: 0.75rem; color: #555; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ─── DATOS ─────────────────────────────────────────────────────────────────────
PAISES = {
    "🇨🇱 Chile":      {"hashtag": "chile",     "ciudad": "Santiago"},
    "🇦🇷 Argentina":  {"hashtag": "argentina", "ciudad": "Buenos Aires"},
    "🇲🇽 México":     {"hashtag": "mexico",    "ciudad": "Ciudad de México"},
    "🇨🇴 Colombia":   {"hashtag": "colombia",  "ciudad": "Bogotá"},
    "🇵🇪 Perú":       {"hashtag": "peru",      "ciudad": "Lima"},
    "🇻🇪 Venezuela":  {"hashtag": "venezuela", "ciudad": "Caracas"},
    "🇺🇾 Uruguay":    {"hashtag": "uruguay",   "ciudad": "Montevideo"},
}

CATEGORIAS = {
    "💼 Negocios":            ["negocios", "business", "emprendimiento"],
    "🚀 Emprendimiento":      ["emprendimiento", "startup", "emprender"],
    "📈 Marketing Digital":   ["marketingdigital", "marketing", "contenido"],
    "💰 Finanzas":            ["finanzaspersonales", "inversion", "dinero"],
    "🤖 Tecnología":          ["tecnologia", "tech", "ia"],
    "📊 Productividad":       ["productividad", "freelance", "trabajoremoto"],
    "🧠 Desarrollo Personal": ["desarrollopersonal", "motivacion", "exito"],
    "🏢 Vida Corporativa":    ["corporativo", "liderazgo", "carrera"],
}

# ─── FUNCIONES ─────────────────────────────────────────────────────────────────

def build_hashtags(pais_key: str, categorias_sel: list) -> list:
    pais = PAISES[pais_key]
    hp = pais["hashtag"]
    tags = []
    for cat in categorias_sel:
        for kw in CATEGORIAS[cat]:
            tags.append(f"{kw}{hp}")   # e.g. negocioschile
            tags.append(kw)             # e.g. negocios
    tags.append(f"emprendedor{hp}")
    tags.append(f"startups{hp}")
    # dedup, máx 8
    seen = []
    for t in tags:
        if t not in seen:
            seen.append(t)
        if len(seen) >= 8:
            break
    return seen


def fetch_instagram_trends(api_token: str, hashtags: list, max_items: int = 30):
    """
    Usa apify/instagram-hashtag-scraper
    Actor ID: apify~instagram-hashtag-scraper
    """
    actor_id = "apify~instagram-hashtag-scraper"
    url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"
    params = {"token": api_token, "timeout": 120}
    payload = {
        "hashtags": hashtags,
        "resultsLimit": max_items,
        "proxy": {"useApifyProxy": True},
    }
    with st.spinner("⏳ Extrayendo trends de Instagram..."):
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


def parse_instagram_data(raw: list) -> pd.DataFrame:
    rows = []
    for item in raw:
        owner = item.get("ownerUsername", "") or item.get("owner", {}).get("username", "")
        tipo_raw = item.get("type", "") or ""
        if "reel" in tipo_raw.lower() or item.get("isVideo", False):
            tipo = "Reel"
        elif item.get("mediaCount", 1) > 1 or "sidecar" in tipo_raw.lower():
            tipo = "Carousel"
        else:
            tipo = "Imagen"

        caption_raw = item.get("caption", "") or item.get("text", "") or ""
        caption = str(caption_raw)[:140] if caption_raw else ""

        # hashtags del caption
        import re
        tags_found = re.findall(r"#(\w+)", caption)[:6]
        hashtags_str = ", ".join([f"#{t}" for t in tags_found])

        rows.append({
            "autor":        "@" + owner,
            "tipo":         tipo,
            "likes":        item.get("likesCount", 0) or 0,
            "comentarios":  item.get("commentsCount", 0) or 0,
            "views":        item.get("videoViewCount", 0) or item.get("videoPlayCount", 0) or 0,
            "caption":      caption,
            "hashtags":     hashtags_str,
            "hashtag_src":  "#" + (item.get("hashtag", "") or ""),
            "url":          item.get("url", "") or item.get("shortCode", ""),
            "fecha":        item.get("timestamp", "")[:10] if item.get("timestamp") else "",
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df["engagement"] = df["likes"] + df["comentarios"]
        df = df.sort_values("engagement", ascending=False).reset_index(drop=True)
        df.index += 1
    return df


def fmt_number(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(n)

def tipo_badge(t):
    if t == "Reel":     return '<span class="type-badge type-reel">🎬 Reel</span>'
    if t == "Carousel": return '<span class="type-badge type-carousel">🖼️ Carousel</span>'
    return '<span class="type-badge type-image">📸 Imagen</span>'


# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📸 Instagram Trends")
    st.markdown("---")

    api_token = st.text_input(
        "Apify API Token",
        type="password",
        placeholder="apify_api_xxxxxxxxxxxx",
    )

    st.markdown("#### 🌎 País")
    pais_sel = st.selectbox(
        "País",
        options=list(PAISES.keys()),
        index=0,
        label_visibility="collapsed",
    )

    st.markdown("#### 📂 Categorías")
    cats_sel = st.multiselect(
        "Categorías",
        options=list(CATEGORIAS.keys()),
        default=["💼 Negocios", "🚀 Emprendimiento"],
        label_visibility="collapsed",
    )

    st.markdown("#### 🔽 Tipo de contenido")
    tipos_sel = st.multiselect(
        "Tipos",
        options=["Reel", "Imagen", "Carousel"],
        default=["Reel", "Imagen", "Carousel"],
        label_visibility="collapsed",
    )

    max_items = st.slider("Posts a analizar", 10, 100, 30, step=10)

    st.markdown("---")
    fetch_btn = st.button("🔍 Buscar Trends", disabled=not api_token or not cats_sel)

    st.markdown("---")
    st.markdown(
        "<span style='color:#333; font-size:0.72rem;'>Powered by Apify · apify/instagram-hashtag-scraper</span>",
        unsafe_allow_html=True,
    )

# ─── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <div class="hero-title">Instagram <span class="ig-gradient">Trends</span> Dashboard</div>
    <div class="hero-subtitle">Datos en tiempo real extraídos via Apify · Módulo 2</div>
</div>
""", unsafe_allow_html=True)

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
for key in ["df", "error", "last_pais", "last_cats", "last_hashtags"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ─── FETCH ─────────────────────────────────────────────────────────────────────
if fetch_btn and api_token and cats_sel:
    hashtags = build_hashtags(pais_sel, cats_sel)
    st.session_state.last_hashtags = hashtags
    raw, err = fetch_instagram_trends(api_token, hashtags, max_items)
    if err:
        st.session_state.error = err
        st.session_state.df = None
    else:
        st.session_state.df = parse_instagram_data(raw)
        st.session_state.error = None
        st.session_state.last_pais = pais_sel
        st.session_state.last_cats = cats_sel

if st.session_state.error:
    st.error(f"❌ {st.session_state.error}")

# ─── DASHBOARD ─────────────────────────────────────────────────────────────────
df_raw = st.session_state.df

if df_raw is not None and not df_raw.empty:

    # Filtrar por tipo
    df = df_raw[df_raw["tipo"].isin(tipos_sel)].copy() if tipos_sel else df_raw.copy()

    # Badges activos
    badges = f'<span class="filter-badge">{st.session_state.last_pais}</span>'
    for c in (st.session_state.last_cats or []):
        badges += f'<span class="filter-badge">{c}</span>'
    st.markdown(f"<div style='margin-bottom:8px'>{badges}</div>", unsafe_allow_html=True)

    # Hashtags usados
    if st.session_state.last_hashtags:
        ht_html = " ".join([f'<span class="tag">#{h}</span>' for h in st.session_state.last_hashtags])
        st.markdown(f"<div style='margin-bottom:20px'>{ht_html}</div>", unsafe_allow_html=True)

    # KPIs
    total_eng  = df["engagement"].sum()
    total_like = df["likes"].sum()
    total_views = df["views"].sum()
    top_tipo = df["tipo"].value_counts().idxmax() if not df.empty else "—"

    c1, c2, c3, c4 = st.columns(4)
    kpis = [
        (len(df),                  "Posts analizados"),
        (fmt_number(total_like),   "Likes acumulados"),
        (fmt_number(total_eng),    "Engagement total"),
        (fmt_number(total_views),  "Vistas (Reels)"),
    ]
    for col, (val, label) in zip([c1, c2, c3, c4], kpis):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Top Posts", "📊 Visualizaciones", "💡 Insights", "📋 Tabla"])

    # ── TAB 1: TOP POSTS ──
    with tab1:
        st.markdown("#### Top 10 posts con más engagement")
        for i, row in df.head(10).iterrows():
            col_rank, col_info, col_stats = st.columns([1, 6, 3])
            with col_rank:
                st.markdown(f"<div class='post-rank'>#{i}</div>", unsafe_allow_html=True)
            with col_info:
                caption_text = row["caption"] if row["caption"] else "Sin caption"
                tags_html = " ".join([f'<span class="tag">{t.strip()}</span>' for t in row["hashtags"].split(",") if t.strip()])
                src_badge = f'<span class="tag">{row["hashtag_src"]}</span>' if row["hashtag_src"] != "#" else ""
                st.markdown(f"""
                <div>
                    <div class="post-author">{row['autor']} {tipo_badge(row['tipo'])} {src_badge}</div>
                    <div class="post-caption">{caption_text}</div>
                    <div style="margin-top:6px">{tags_html}</div>
                </div>""", unsafe_allow_html=True)
            with col_stats:
                views_html = f'<div style="color:#bc1888; font-size:0.78rem">▶ {fmt_number(row["views"])}</div>' if row["views"] > 0 else ""
                url_display = row['url'] if row['url'].startswith('http') else f"https://www.instagram.com/p/{row['url']}"
                st.markdown(f"""
                <div style="text-align:right; padding-top:4px">
                    <div style="color:#f0f0f5; font-weight:600">♥ {fmt_number(row['likes'])}</div>
                    <div style="color:#e6683c; font-size:0.85rem">💬 {fmt_number(row['comentarios'])}</div>
                    {views_html}
                    <div style="color:#555; font-size:0.75rem; margin-top:4px">{row['fecha']}</div>
                </div>""", unsafe_allow_html=True)
            if row["url"]:
                url_link = row['url'] if row['url'].startswith('http') else f"https://www.instagram.com/p/{row['url']}"
                st.markdown(f"<a href='{url_link}' target='_blank' style='color:#444; font-size:0.72rem;'>Ver en Instagram ↗</a>", unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

    # ── TAB 2: VISUALIZACIONES ──
    with tab2:
        PLOT = dict(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#aaa",
            title_font_color="#f0f0f5",
            margin=dict(l=0, r=10, t=40, b=0),
        )

        col_a, col_b = st.columns(2)

        with col_a:
            fig1 = px.bar(
                df.head(15), x="engagement", y="autor", orientation="h",
                title="Top 15 · Mayor Engagement",
                color="engagement",
                color_continuous_scale=["#1a0a1f", "#bc1888"],
                labels={"engagement": "Engagement", "autor": ""},
            )
            fig1.update_layout(**PLOT, coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
            fig1.update_xaxes(gridcolor="rgba(255,255,255,0.05)")
            fig1.update_yaxes(gridcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig1, use_container_width=True)

        with col_b:
            tipo_counts = df["tipo"].value_counts().reset_index()
            tipo_counts.columns = ["tipo", "count"]
            fig2 = px.pie(
                tipo_counts, values="count", names="tipo",
                title="📊 Distribución por tipo de contenido",
                color_discrete_map={
                    "Reel":     "#bc1888",
                    "Imagen":   "#f09433",
                    "Carousel": "#dc2743",
                },
                hole=0.5,
            )
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#aaa", title_font_color="#f0f0f5")
            st.plotly_chart(fig2, use_container_width=True)

        # Likes vs Comentarios scatter
        fig3 = px.scatter(
            df, x="likes", y="comentarios",
            color="tipo", size="engagement",
            hover_name="autor",
            title="Likes vs Comentarios por tipo de contenido",
            color_discrete_map={"Reel": "#bc1888", "Imagen": "#f09433", "Carousel": "#dc2743"},
            labels={"likes": "Likes", "comentarios": "Comentarios"},
        )
        fig3.update_layout(**PLOT)
        fig3.update_xaxes(gridcolor="rgba(255,255,255,0.05)")
        fig3.update_yaxes(gridcolor="rgba(255,255,255,0.05)")
        st.plotly_chart(fig3, use_container_width=True)

        # Hashtag source breakdown
        if "hashtag_src" in df.columns:
            ht_counts = df["hashtag_src"].value_counts().reset_index()
            ht_counts.columns = ["hashtag", "posts"]
            fig4 = px.bar(
                ht_counts.head(10), x="hashtag", y="posts",
                title="Posts por hashtag buscado",
                color="posts",
                color_continuous_scale=["#1a0a1f", "#e6683c"],
            )
            fig4.update_layout(**PLOT, coloraxis_showscale=False)
            fig4.update_xaxes(gridcolor="rgba(0,0,0,0)")
            fig4.update_yaxes(gridcolor="rgba(255,255,255,0.05)")
            st.plotly_chart(fig4, use_container_width=True)

    # ── TAB 3: INSIGHTS ──
    with tab3:
        st.markdown("#### 💡 Insights del contenido")

        col_i1, col_i2 = st.columns(2)

        with col_i1:
            # Mejor tipo de contenido
            best_tipo = df.groupby("tipo")["engagement"].mean().idxmax() if not df.empty else "—"
            best_tipo_val = df.groupby("tipo")["engagement"].mean().max() if not df.empty else 0
            st.markdown(f"""
            <div class="insight-box">
                <div class="insight-title">🏆 Tipo de contenido con más engagement</div>
                <div class="insight-value">{best_tipo}</div>
                <div class="insight-desc">Promedio de {fmt_number(int(best_tipo_val))} interacciones por post</div>
            </div>""", unsafe_allow_html=True)

            # Ratio likes/comentarios
            ratio = (df["likes"].sum() / max(df["comentarios"].sum(), 1))
            st.markdown(f"""
            <div class="insight-box">
                <div class="insight-title">💬 Ratio Likes / Comentarios</div>
                <div class="insight-value">{ratio:.0f}:1</div>
                <div class="insight-desc">Por cada comentario hay {ratio:.0f} likes en promedio</div>
            </div>""", unsafe_allow_html=True)

        with col_i2:
            # Top autor
            top_autor = df.groupby("autor")["engagement"].sum().idxmax() if not df.empty else "—"
            top_autor_eng = df.groupby("autor")["engagement"].sum().max() if not df.empty else 0
            st.markdown(f"""
            <div class="insight-box">
                <div class="insight-title">⭐ Cuenta con más engagement total</div>
                <div class="insight-value">{top_autor}</div>
                <div class="insight-desc">{fmt_number(int(top_autor_eng))} interacciones acumuladas</div>
            </div>""", unsafe_allow_html=True)

            # Reels vs resto
            reels_df = df[df["tipo"] == "Reel"]
            otros_df  = df[df["tipo"] != "Reel"]
            if not reels_df.empty and not otros_df.empty:
                reels_avg = reels_df["engagement"].mean()
                otros_avg = otros_df["engagement"].mean()
                diff_pct  = ((reels_avg - otros_avg) / max(otros_avg, 1)) * 100
                signo     = "+" if diff_pct > 0 else ""
                st.markdown(f"""
                <div class="insight-box">
                    <div class="insight-title">🎬 Reels vs otros formatos</div>
                    <div class="insight-value">{signo}{diff_pct:.0f}%</div>
                    <div class="insight-desc">Diferencia de engagement de Reels vs Imágenes/Carousel</div>
                </div>""", unsafe_allow_html=True)

        # Mejor horario (si hay fechas)
        if df["fecha"].notna().any() and (df["fecha"] != "").any():
            df["fecha_dt"] = pd.to_datetime(df["fecha"], errors="coerce")
            by_date = df.dropna(subset=["fecha_dt"]).groupby("fecha_dt")["engagement"].mean().reset_index()
            if not by_date.empty:
                fig5 = px.line(
                    by_date, x="fecha_dt", y="engagement",
                    title="📅 Engagement promedio por fecha de publicación",
                    labels={"fecha_dt": "Fecha", "engagement": "Engagement promedio"},
                    color_discrete_sequence=["#e6683c"],
                )
                fig5.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#aaa",
                    title_font_color="#f0f0f5",
                )
                fig5.update_xaxes(gridcolor="rgba(255,255,255,0.05)")
                fig5.update_yaxes(gridcolor="rgba(255,255,255,0.05)")
                st.plotly_chart(fig5, use_container_width=True)

    # ── TAB 4: TABLA ──
    with tab4:
        cols_show = ["autor", "tipo", "likes", "comentarios", "views", "engagement", "hashtag_src", "hashtags", "fecha", "url"]
        st.dataframe(
            df[[c for c in cols_show if c in df.columns]].rename(columns={
                "autor": "Usuario", "tipo": "Tipo", "likes": "Likes",
                "comentarios": "Comentarios", "views": "Vistas",
                "engagement": "Engagement", "hashtag_src": "Hashtag búsqueda",
                "hashtags": "Hashtags del post", "fecha": "Fecha", "url": "URL",
            }),
            use_container_width=True, height=500,
        )
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Descargar CSV",
            data=csv,
            file_name=f"instagram_trends_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )

else:
    st.markdown("""
    <div style="text-align:center; padding: 80px 20px;">
        <div style="font-size: 3.5rem; margin-bottom: 16px;">📸</div>
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.3rem; color: #555; margin-bottom: 8px;">
            Selecciona país, categorías y pulsa <strong style="color:#dc2743">Buscar Trends</strong>
        </div>
        <div style="font-size: 0.85rem; color: #333;">
            Los datos se extraen en tiempo real desde Instagram via Apify
        </div>
    </div>
    """, unsafe_allow_html=True)
