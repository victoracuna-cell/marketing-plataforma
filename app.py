import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
import re

st.set_page_config(
    page_title="Social Trends Platform",
    page_icon="🚀",
    layout="wide",
)

# ─── ESTILOS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Inter:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; color: #f0f0f5; }
    .stApp { background: linear-gradient(135deg, #0a0a0f 0%, #12121f 100%); }
    section[data-testid="stSidebar"] { background: #0d0d1a; border-right: 1px solid rgba(255,255,255,0.06); }
    .metric-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 12px;
    }
    .metric-value-tiktok {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem; font-weight: 700; color: #fe2c55;
    }
    .metric-value-ig {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem; font-weight: 700;
        background: linear-gradient(90deg, #f09433, #dc2743, #bc1888);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .metric-label { font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px; }
    .tag {
        display: inline-block;
        background: rgba(254,44,85,0.15); color: #fe2c55;
        border-radius: 6px; padding: 2px 8px;
        font-size: 0.72rem; font-weight: 600; margin-right: 4px;
    }
    .tag-ig {
        display: inline-block;
        background: rgba(220,39,67,0.12); color: #e6683c;
        border-radius: 6px; padding: 2px 8px;
        font-size: 0.72rem; font-weight: 600; margin-right: 4px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid rgba(255,255,255,0.07); }
    .stTabs [data-baseweb="tab"] { color: #666; font-family: 'Space Grotesk', sans-serif; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #fe2c55 !important; }
    hr { border-color: rgba(255,255,255,0.06); }
    .insight-box {
        background: rgba(220,39,67,0.06); border: 1px solid rgba(220,39,67,0.15);
        border-radius: 12px; padding: 16px 20px; margin-bottom: 12px;
    }
    .insight-value { font-size: 1.4rem; font-weight: 700; color: #e6683c; margin-top: 4px; }
    .insight-desc { font-size: 0.75rem; color: #555; margin-top: 2px; }
    .metric-value-audio {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem; font-weight: 700;
        background: linear-gradient(90deg, #6c63ff, #a855f7, #ec4899);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .rank-badge {
        display: inline-flex; align-items: center; justify-content: center;
        width: 36px; height: 36px; border-radius: 50%;
        background: rgba(108,99,255,0.15); border: 1px solid rgba(108,99,255,0.3);
        font-family: 'Space Grotesk', sans-serif; font-weight: 700;
        color: #a855f7; font-size: 0.9rem;
    }
    .promoted-badge {
        display: inline-block; background: rgba(236,72,153,0.15);
        color: #ec4899; border-radius: 6px; padding: 2px 8px;
        font-size: 0.7rem; font-weight: 700; margin-left: 6px;
    }
    .audio-card {
        background: rgba(108,99,255,0.04); border: 1px solid rgba(108,99,255,0.1);
        border-radius: 14px; padding: 16px 20px; margin-bottom: 10px;
        transition: border-color 0.2s;
    }
    .audio-card:hover { border-color: rgba(168,85,247,0.4); }
</style>
""", unsafe_allow_html=True)

# ─── DATOS ─────────────────────────────────────────────────────────────────────
PAISES = {
    "🇨🇱 Chile":     {"hashtag": "chile",     "codigo": "CL"},
    "🇦🇷 Argentina": {"hashtag": "argentina", "codigo": "AR"},
    "🇲🇽 México":    {"hashtag": "mexico",    "codigo": "MX"},
    "🇨🇴 Colombia":  {"hashtag": "colombia",  "codigo": "CO"},
    "🇵🇪 Perú":      {"hashtag": "peru",      "codigo": "PE"},
    "🇻🇪 Venezuela": {"hashtag": "venezuela", "codigo": "VE"},
    "🇺🇾 Uruguay":   {"hashtag": "uruguay",   "codigo": "UY"},
}

CATEGORIAS = {
    "💼 Negocios":            ["negocios", "business", "emprendimiento"],
    "🚀 Emprendimiento":      ["emprendimiento", "startup", "emprender"],
    "📈 Marketing Digital":   ["marketingdigital", "marketing", "ventas"],
    "💰 Finanzas":            ["finanzaspersonales", "inversion", "dinero"],
    "🤖 Tecnología":          ["tecnologia", "tech", "ia"],
    "📊 Productividad":       ["productividad", "freelance", "trabajoremoto"],
    "🧠 Desarrollo Personal": ["desarrollopersonal", "motivacion", "exito"],
    "🏢 Vida Corporativa":    ["corporativo", "liderazgo", "carrera"],
}

def fmt_number(n):
    if not n: return "0"
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(n)

def build_queries_tiktok(pais_key, cats_sel):
    hp = PAISES[pais_key]["hashtag"]
    queries = []
    for cat in cats_sel:
        for kw in CATEGORIAS[cat]:
            queries.append(f"#{kw}{hp}")
            queries.append(f"#{kw}")
    queries.append(f"trending {hp}")
    seen = list(dict.fromkeys(queries))
    return seen[:10]

def build_hashtags_ig(pais_key, cats_sel):
    hp = PAISES[pais_key]["hashtag"]
    tags = []
    for cat in cats_sel:
        for kw in CATEGORIAS[cat]:
            tags.append(f"{kw}{hp}")
            tags.append(kw)
    seen = list(dict.fromkeys(tags))
    return seen[:8]

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🚀 Social Trends")
    st.markdown("---")

    modulo = st.radio(
        "Módulo",
        ["🎵 TikTok Trends", "📸 Instagram Trends", "🔊 Audio Trends"],
        index=0,
    )

    st.markdown("---")

    api_token = st.text_input(
        "Apify API Token",
        type="password",
        placeholder="apify_api_xxxxxxxxxxxx",
    )

    st.markdown(f"#### 🌎 País")
    pais_sel = st.selectbox("País", list(PAISES.keys()), index=0, label_visibility="collapsed")

    if modulo != "🔊 Audio Trends":
        st.markdown("#### 📂 Categorías")
        cats_sel = st.multiselect(
            "Categorías", list(CATEGORIAS.keys()),
            default=["💼 Negocios", "🚀 Emprendimiento"],
            label_visibility="collapsed",
        )
    else:
        cats_sel = []

    if modulo == "🔊 Audio Trends":
        st.markdown("#### ⏱ Período")
        periodo = st.selectbox(
            "Período",
            {"7 días": 7, "30 días": 30, "120 días": 120}.keys(),
            index=0,
            label_visibility="collapsed",
        )
        periodo_val = {"7 días": 7, "30 días": 30, "120 días": 120}[periodo]
        max_items_audio = st.slider("Sonidos a analizar", 10, 50, 20, step=10)
    else:
        periodo_val = 7
        max_items_audio = 20

    max_items = st.slider("Posts a analizar", 10, 100, 30, step=10) if modulo != "🔊 Audio Trends" else 30
    fetch_btn = st.button("🔍 Buscar Trends", disabled=not api_token or (modulo != "🔊 Audio Trends" and not cats_sel))

    st.markdown("---")
    st.markdown("<span style='color:#333; font-size:0.72rem;'>Powered by Apify</span>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  MÓDULO 1 — TIKTOK
# ══════════════════════════════════════════════════════
if modulo == "🎵 TikTok Trends":

    st.markdown("""
    <div style="padding:28px 0 16px; border-bottom:1px solid rgba(255,255,255,0.07); margin-bottom:28px;">
        <div style="font-family:'Space Grotesk',sans-serif; font-size:2.2rem; font-weight:700; color:#f0f0f5;">
            TikTok <span style="color:#fe2c55">Trends</span>
        </div>
        <div style="color:#555; font-size:0.9rem; margin-top:6px;">Datos en tiempo real · Módulo 1</div>
    </div>
    """, unsafe_allow_html=True)

    # init state
    for k in ["tt_df","tt_err","tt_pais","tt_cats"]:
        if k not in st.session_state: st.session_state[k] = None

    if fetch_btn and api_token and cats_sel:
        queries = build_queries_tiktok(pais_sel, cats_sel)
        actor_id = "clockworks~free-tiktok-scraper"
        url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"
        payload = {"searchQueries": queries, "maxItems": max_items,
                   "resultsPerPage": max_items, "shouldDownloadVideos": False,
                   "shouldDownloadCovers": False}
        with st.spinner("⏳ Extrayendo trends de TikTok..."):
            try:
                resp = requests.post(url, json=payload,
                                     params={"token": api_token, "timeout": 120}, timeout=180)
                resp.raise_for_status()
                raw = resp.json()
                rows = []
                for item in raw:
                    author = item.get("authorMeta", {}) or {}
                    music  = item.get("musicMeta", {}) or {}
                    rows.append({
                        "nickname":    "@" + author.get("nickName", ""),
                        "autor":       author.get("name", ""),
                        "likes":       item.get("diggCount", 0) or 0,
                        "comentarios": item.get("commentCount", 0) or 0,
                        "shares":      item.get("shareCount", 0) or 0,
                        "plays":       item.get("playCount", 0) or 0,
                        "musica":      music.get("musicName", ""),
                        "hashtags":    ", ".join([f"#{h}" for h in (item.get("hashtags") or [])[:5]]),
                        "url":         item.get("webVideoUrl", ""),
                        "descripcion": (item.get("text", "") or "")[:120],
                        "fecha":       datetime.fromtimestamp(item.get("createTime",0)).strftime("%Y-%m-%d")
                                       if item.get("createTime") else "",
                    })
                df = pd.DataFrame(rows)
                if not df.empty:
                    df = df.sort_values("plays", ascending=False).reset_index(drop=True)
                    df.index += 1
                st.session_state.tt_df   = df
                st.session_state.tt_err  = None
                st.session_state.tt_pais = pais_sel
                st.session_state.tt_cats = cats_sel
            except requests.exceptions.HTTPError:
                st.session_state.tt_err = f"Error HTTP {resp.status_code}. Verifica tu token."
                st.session_state.tt_df  = None
            except Exception as e:
                st.session_state.tt_err = str(e)
                st.session_state.tt_df  = None

    if st.session_state.tt_err:
        st.error(f"❌ {st.session_state.tt_err}")

    df = st.session_state.tt_df
    if df is not None and not df.empty:
        c1,c2,c3,c4 = st.columns(4)
        for col,(val,lbl) in zip([c1,c2,c3,c4],[
            (len(df),"Videos"),
            (fmt_number(df['plays'].sum()),"Reproducciones"),
            (fmt_number(df['likes'].sum()),"Likes"),
            (f"{((df['likes']+df['comentarios']+df['shares'])/df['plays'].replace(0,1)*100).mean():.1f}%","Engagement"),
        ]):
            with col:
                st.markdown(f'<div class="metric-card"><div class="metric-value-tiktok">{val}</div><div class="metric-label">{lbl}</div></div>', unsafe_allow_html=True)

        tab1,tab2,tab3 = st.tabs(["🏆 Top Trends","📊 Gráficos","📋 Tabla"])

        with tab1:
            for i,row in df.head(10).iterrows():
                ca,cb,cc = st.columns([1,6,3])
                with ca:
                    st.markdown(f"<div style='font-family:Space Grotesk;font-size:1.4rem;font-weight:700;color:rgba(254,44,85,0.6)'>#{i}</div>", unsafe_allow_html=True)
                with cb:
                    tags_html = " ".join([f'<span class="tag">{t.strip()}</span>' for t in row["hashtags"].split(",") if t.strip()])
                    st.markdown(f"<div style='font-weight:600;color:#f0f0f5'>{row['nickname']}</div><div style='font-size:0.8rem;color:#666'>{row['descripcion']}</div><div style='margin-top:4px'>{tags_html}</div>", unsafe_allow_html=True)
                with cc:
                    st.markdown(f"<div style='text-align:right'><div style='color:#f0f0f5;font-weight:600'>▶ {fmt_number(row['plays'])}</div><div style='color:#fe2c55;font-size:0.85rem'>♥ {fmt_number(row['likes'])}</div><div style='color:#666;font-size:0.78rem'>💬 {fmt_number(row['comentarios'])}</div></div>", unsafe_allow_html=True)
                if row["url"]:
                    st.markdown(f"<a href='{row['url']}' target='_blank' style='color:#444;font-size:0.72rem;'>Ver en TikTok ↗</a>", unsafe_allow_html=True)
                st.markdown("<hr>", unsafe_allow_html=True)

        with tab2:
            PL = dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#aaa",title_font_color="#f0f0f5",margin=dict(l=0,r=10,t=40,b=0))
            ca,cb = st.columns(2)
            with ca:
                fig = px.bar(df.head(15),x="plays",y="nickname",orientation="h",title="Top 15 · Reproducciones",color="plays",color_continuous_scale=["#1a1a2e","#fe2c55"],labels={"plays":"Plays","nickname":""})
                fig.update_layout(**PL,coloraxis_showscale=False,yaxis=dict(autorange="reversed"))
                fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)")
                st.plotly_chart(fig,use_container_width=True)
            with cb:
                mc = df["musica"].value_counts().head(6).reset_index(); mc.columns=["musica","count"]
                fig2 = px.pie(mc,values="count",names="musica",title="🎵 Músicas más usadas",hole=0.45,color_discrete_sequence=px.colors.sequential.RdBu)
                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",font_color="#aaa",title_font_color="#f0f0f5")
                st.plotly_chart(fig2,use_container_width=True)

        with tab3:
            show = ["nickname","autor","likes","comentarios","shares","plays","musica","hashtags","fecha","url"]
            st.dataframe(df[[c for c in show if c in df.columns]], use_container_width=True, height=450)
            st.download_button("⬇ CSV", df.to_csv(index=False).encode(), f"tiktok_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
    else:
        st.markdown("<div style='text-align:center;padding:80px 20px;color:#444;'><div style='font-size:3rem'>🎵</div><div style='color:#555;margin-top:12px;font-family:Space Grotesk'>Ingresa tu token y pulsa <strong style=\"color:#fe2c55\">Buscar Trends</strong></div></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  MÓDULO 2 — INSTAGRAM
# ══════════════════════════════════════════════════════
elif modulo == "📸 Instagram Trends":

    st.markdown("""
    <div style="padding:28px 0 16px; border-bottom:1px solid rgba(255,255,255,0.07); margin-bottom:28px;">
        <div style="font-family:'Space Grotesk',sans-serif; font-size:2.2rem; font-weight:700; color:#f0f0f5;">
            Instagram <span style="background:linear-gradient(90deg,#f09433,#dc2743,#bc1888);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Trends</span>
        </div>
        <div style="color:#555; font-size:0.9rem; margin-top:6px;">Datos en tiempo real · Módulo 2</div>
    </div>
    """, unsafe_allow_html=True)

    for k in ["ig_df","ig_err","ig_pais","ig_cats","ig_tags"]:
        if k not in st.session_state: st.session_state[k] = None

    if fetch_btn and api_token and cats_sel:
        hashtags = build_hashtags_ig(pais_sel, cats_sel)
        st.session_state.ig_tags = hashtags
        actor_id = "apify~instagram-hashtag-scraper"
        url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"
        payload = {"hashtags": hashtags, "resultsLimit": max_items, "proxy": {"useApifyProxy": True}}
        with st.spinner("⏳ Extrayendo trends de Instagram..."):
            try:
                resp = requests.post(url, json=payload,
                                     params={"token": api_token, "timeout": 120}, timeout=180)
                resp.raise_for_status()
                raw = resp.json()
                rows = []
                for item in raw:
                    owner = item.get("ownerUsername","") or (item.get("owner",{}) or {}).get("username","")
                    tipo_raw = item.get("type","") or ""
                    if "reel" in tipo_raw.lower() or item.get("isVideo",False): tipo = "Reel"
                    elif item.get("mediaCount",1)>1 or "sidecar" in tipo_raw.lower(): tipo = "Carousel"
                    else: tipo = "Imagen"
                    caption = str(item.get("caption","") or "")[:140]
                    tags_found = re.findall(r"#(\w+)", caption)[:6]
                    rows.append({
                        "autor":       "@"+owner,
                        "tipo":        tipo,
                        "likes":       item.get("likesCount",0) or 0,
                        "comentarios": item.get("commentsCount",0) or 0,
                        "views":       item.get("videoViewCount",0) or 0,
                        "caption":     caption,
                        "hashtags":    ", ".join([f"#{t}" for t in tags_found]),
                        "hashtag_src": "#"+(item.get("hashtag","") or ""),
                        "url":         item.get("url","") or item.get("shortCode",""),
                        "fecha":       (item.get("timestamp","") or "")[:10],
                    })
                df = pd.DataFrame(rows)
                if not df.empty:
                    df["engagement"] = df["likes"]+df["comentarios"]
                    df = df.sort_values("engagement",ascending=False).reset_index(drop=True)
                    df.index += 1
                st.session_state.ig_df   = df
                st.session_state.ig_err  = None
                st.session_state.ig_pais = pais_sel
                st.session_state.ig_cats = cats_sel
            except requests.exceptions.HTTPError:
                st.session_state.ig_err = f"Error HTTP {resp.status_code}. Verifica tu token."
                st.session_state.ig_df  = None
            except Exception as e:
                st.session_state.ig_err = str(e)
                st.session_state.ig_df  = None

    if st.session_state.ig_err:
        st.error(f"❌ {st.session_state.ig_err}")

    df = st.session_state.ig_df
    if df is not None and not df.empty:
        c1,c2,c3,c4 = st.columns(4)
        for col,(val,lbl) in zip([c1,c2,c3,c4],[
            (len(df),"Posts"),
            (fmt_number(df['likes'].sum()),"Likes"),
            (fmt_number(df['engagement'].sum()),"Engagement"),
            (fmt_number(df['views'].sum()),"Vistas Reels"),
        ]):
            with col:
                st.markdown(f'<div class="metric-card"><div class="metric-value-ig">{val}</div><div class="metric-label">{lbl}</div></div>', unsafe_allow_html=True)

        tab1,tab2,tab3,tab4 = st.tabs(["🏆 Top Posts","📊 Gráficos","💡 Insights","📋 Tabla"])

        with tab1:
            for i,row in df.head(10).iterrows():
                ca,cb,cc = st.columns([1,6,3])
                with ca:
                    st.markdown(f"<div style='font-family:Space Grotesk;font-size:1.4rem;font-weight:700;color:rgba(220,39,67,0.6)'>#{i}</div>", unsafe_allow_html=True)
                with cb:
                    tipo_color = {"Reel":"#bc1888","Imagen":"#f09433","Carousel":"#dc2743"}.get(row["tipo"],"#666")
                    tags_html = " ".join([f'<span class="tag-ig">{t.strip()}</span>' for t in row["hashtags"].split(",") if t.strip()])
                    st.markdown(f"<div style='font-weight:600;color:#f0f0f5'>{row['autor']} <span style='color:{tipo_color};font-size:0.78rem;font-weight:700'>{row['tipo']}</span></div><div style='font-size:0.8rem;color:#666'>{row['caption']}</div><div style='margin-top:4px'>{tags_html}</div>", unsafe_allow_html=True)
                with cc:
                    views_html = f"<div style='color:#bc1888;font-size:0.78rem'>▶ {fmt_number(row['views'])}</div>" if row["views"]>0 else ""
                    st.markdown(f"<div style='text-align:right'><div style='color:#f0f0f5;font-weight:600'>♥ {fmt_number(row['likes'])}</div><div style='color:#e6683c;font-size:0.85rem'>💬 {fmt_number(row['comentarios'])}</div>{views_html}</div>", unsafe_allow_html=True)
                if row["url"]:
                    link = row["url"] if row["url"].startswith("http") else f"https://www.instagram.com/p/{row['url']}"
                    st.markdown(f"<a href='{link}' target='_blank' style='color:#444;font-size:0.72rem;'>Ver en Instagram ↗</a>", unsafe_allow_html=True)
                st.markdown("<hr>", unsafe_allow_html=True)

        with tab2:
            PL = dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#aaa",title_font_color="#f0f0f5",margin=dict(l=0,r=10,t=40,b=0))
            ca,cb = st.columns(2)
            with ca:
                fig = px.bar(df.head(15),x="engagement",y="autor",orientation="h",title="Top 15 · Engagement",color="engagement",color_continuous_scale=["#1a0a1f","#bc1888"],labels={"engagement":"Engagement","autor":""})
                fig.update_layout(**PL,coloraxis_showscale=False,yaxis=dict(autorange="reversed"))
                fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)")
                st.plotly_chart(fig,use_container_width=True)
            with cb:
                tc = df["tipo"].value_counts().reset_index(); tc.columns=["tipo","count"]
                fig2 = px.pie(tc,values="count",names="tipo",title="Distribución por tipo",hole=0.5,color_discrete_map={"Reel":"#bc1888","Imagen":"#f09433","Carousel":"#dc2743"})
                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",font_color="#aaa",title_font_color="#f0f0f5")
                st.plotly_chart(fig2,use_container_width=True)

        with tab3:
            ca,cb = st.columns(2)
            with ca:
                best = df.groupby("tipo")["engagement"].mean()
                if not best.empty:
                    bt,bv = best.idxmax(), best.max()
                    st.markdown(f'<div class="insight-box"><div style="font-weight:700;color:#f0f0f5">🏆 Mejor formato</div><div class="insight-value">{bt}</div><div class="insight-desc">Promedio {fmt_number(int(bv))} interacciones</div></div>', unsafe_allow_html=True)
                ratio = df["likes"].sum() / max(df["comentarios"].sum(),1)
                st.markdown(f'<div class="insight-box"><div style="font-weight:700;color:#f0f0f5">💬 Ratio Likes/Comentarios</div><div class="insight-value">{ratio:.0f}:1</div><div class="insight-desc">Por cada comentario hay {ratio:.0f} likes</div></div>', unsafe_allow_html=True)
            with cb:
                top_a = df.groupby("autor")["engagement"].sum()
                if not top_a.empty:
                    ta,tv = top_a.idxmax(), top_a.max()
                    st.markdown(f'<div class="insight-box"><div style="font-weight:700;color:#f0f0f5">⭐ Cuenta top</div><div class="insight-value">{ta}</div><div class="insight-desc">{fmt_number(int(tv))} engagement acumulado</div></div>', unsafe_allow_html=True)
                reels = df[df["tipo"]=="Reel"]["engagement"].mean() if "Reel" in df["tipo"].values else 0
                otros = df[df["tipo"]!="Reel"]["engagement"].mean() if len(df[df["tipo"]!="Reel"])>0 else 0
                if reels and otros:
                    diff = ((reels-otros)/max(otros,1))*100
                    st.markdown(f'<div class="insight-box"><div style="font-weight:700;color:#f0f0f5">🎬 Reels vs otros</div><div class="insight-value">{diff:+.0f}%</div><div class="insight-desc">Diferencia de engagement</div></div>', unsafe_allow_html=True)

        with tab4:
            show = ["autor","tipo","likes","comentarios","views","engagement","hashtag_src","fecha","url"]
            st.dataframe(df[[c for c in show if c in df.columns]], use_container_width=True, height=450)
            st.download_button("⬇ CSV", df.to_csv(index=False).encode(), f"instagram_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
    else:
        st.markdown("<div style='text-align:center;padding:80px 20px;color:#444;'><div style='font-size:3rem'>📸</div><div style='color:#555;margin-top:12px;font-family:Space Grotesk'>Ingresa tu token y pulsa <strong style=\"color:#dc2743\">Buscar Trends</strong></div></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  MÓDULO 3 — AUDIO TRENDS
# ══════════════════════════════════════════════════════
elif modulo == "🔊 Audio Trends":

    pais_info = PAISES[pais_sel]
    country_code = pais_info["codigo"]

    st.markdown(f"""
    <div style="padding:28px 0 16px; border-bottom:1px solid rgba(255,255,255,0.07); margin-bottom:28px;">
        <div style="font-family:'Space Grotesk',sans-serif; font-size:2.2rem; font-weight:700; color:#f0f0f5;">
            🔊 Audio <span style="background:linear-gradient(90deg,#6c63ff,#a855f7,#ec4899);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Trends</span>
        </div>
        <div style="color:#555; font-size:0.9rem; margin-top:6px;">Sonidos virales en TikTok · {pais_sel} · Módulo 3</div>
    </div>
    """, unsafe_allow_html=True)

    for k in ["au_df","au_err"]:
        if k not in st.session_state: st.session_state[k] = None

    if fetch_btn and api_token:
        # Estrategia: extraer videos trending del país y agregar audios por frecuencia de uso
        actor_id = "clockworks~free-tiktok-scraper"
        url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"
        hp = pais_info["hashtag"]
        payload = {
            "searchQueries": [f"#{hp}", f"trending {hp}", f"#fyp{hp}", "#chile"],
            "maxItems": max(max_items_audio * 3, 60),
            "resultsPerPage": max(max_items_audio * 3, 60),
            "shouldDownloadVideos": False,
            "shouldDownloadCovers": False,
        }
        with st.spinner(f"⏳ Extrayendo audios trending en {pais_sel}..."):
            try:
                resp = requests.post(url, json=payload,
                                     params={"token": api_token, "timeout": 120}, timeout=180)
                resp.raise_for_status()
                raw = resp.json()

                # Agregar audios por frecuencia
                music_data = {}
                for item in raw:
                    music = item.get("musicMeta") or {}
                    mid   = music.get("musicId") or music.get("musicName", "")
                    if not mid: continue
                    name  = music.get("musicName","") or music.get("musicOriginal","Sonido original")
                    author= music.get("musicAuthor","") or "—"
                    dur   = music.get("musicDuration", 0) or 0
                    play  = music.get("musicPlay","") or ""
                    if mid not in music_data:
                        music_data[mid] = {
                            "titulo":   name,
                            "artista":  author,
                            "duracion": dur,
                            "url_sound": play,
                            "usos":     0,
                            "likes_total": 0,
                            "plays_total": 0,
                        }
                    music_data[mid]["usos"]        += 1
                    music_data[mid]["likes_total"] += item.get("diggCount", 0) or 0
                    music_data[mid]["plays_total"] += item.get("playCount", 0) or 0

                rows = []
                for rank, (mid, d) in enumerate(
                    sorted(music_data.items(), key=lambda x: x[1]["usos"], reverse=True), 1
                ):
                    rows.append({
                        "rank":        rank,
                        "titulo":      d["titulo"] or "Sonido original",
                        "artista":     d["artista"],
                        "duracion":    d["duracion"],
                        "usos":        d["usos"],
                        "likes_total": d["likes_total"],
                        "plays_total": d["plays_total"],
                        "url_sound":   d["url_sound"],
                        "promocionado": False,
                        "trend_7d":    0,
                        "trend_30d":   0,
                    })

                df_au = pd.DataFrame(rows[:max_items_audio]) if rows else pd.DataFrame()
                st.session_state.au_df  = df_au
                st.session_state.au_err = None
            except requests.exceptions.HTTPError:
                st.session_state.au_err = f"Error HTTP {resp.status_code}. Verifica tu token."
                st.session_state.au_df  = None
            except Exception as e:
                st.session_state.au_err = str(e)
                st.session_state.au_df  = None

    if st.session_state.au_err:
        st.error(f"❌ {st.session_state.au_err}")

    df_au = st.session_state.au_df

    if df_au is not None and not df_au.empty:

        # KPIs
        c1,c2,c3,c4 = st.columns(4)
        top_usos    = df_au["usos"].max() if "usos" in df_au.columns else 0
        avg_dur     = df_au["duracion"].mean() if "duracion" in df_au.columns else 0
        top_likes   = df_au["likes_total"].max() if "likes_total" in df_au.columns else 0
        top_plays   = df_au["plays_total"].max() if "plays_total" in df_au.columns else 0
        for col,(val,lbl) in zip([c1,c2,c3,c4],[
            (len(df_au),              "Audios únicos"),
            (fmt_number(top_usos),    "Máx. videos con este audio"),
            (fmt_number(top_likes),   "Likes del audio top"),
            (f"{avg_dur:.0f}s",       "Duración promedio"),
        ]):
            with col:
                st.markdown(f'<div class="metric-card"><div class="metric-value-audio">{val}</div><div class="metric-label">{lbl}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["🏆 Ranking", "📊 Visualizaciones", "📋 Tabla"])

        # ── TAB 1: RANKING ──
        with tab1:
            st.markdown(f"#### Top sonidos trending en {pais_sel} · últimos {periodo_val} días")
            for _, row in df_au.iterrows():
                promo_html = '<span class="promoted-badge">📢 Promocionado</span>' if row.get("promocionado") else ""
                trend_html = ""
                if row.get("trend_7d"):
                    signo = "▲" if row["trend_7d"] > 0 else "▼"
                    color = "#4ade80" if row["trend_7d"] > 0 else "#f87171"
                    trend_html = f'<span style="color:{color};font-size:0.78rem">{signo} {abs(row["trend_7d"]):.0f}% 7d</span>'

                ca, cb, cc = st.columns([1, 7, 2])
                with ca:
                    st.markdown(f'<div class="rank-badge">#{int(row["rank"])}</div>', unsafe_allow_html=True)
                with cb:
                    st.markdown(f"""
                    <div style="padding-top:4px">
                        <div style="font-family:Space Grotesk;font-weight:700;color:#f0f0f5;font-size:1rem">
                            {row['titulo']} {promo_html}
                        </div>
                        <div style="color:#888;font-size:0.82rem;margin-top:2px">
                            🎤 {row['artista']} &nbsp;·&nbsp; ⏱ {row['duracion']}s &nbsp;·&nbsp; {trend_html}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with cc:
                    usos_fmt = fmt_number(row["usos"]) if row["usos"] else "—"
                    st.markdown(f"""
                    <div style="text-align:right;padding-top:4px">
                        <div style="font-family:Space Grotesk;font-weight:700;color:#a855f7;font-size:1.1rem">{usos_fmt}</div>
                        <div style="color:#555;font-size:0.72rem">videos usando este audio</div>
                    </div>
                    """, unsafe_allow_html=True)

                if row.get("url_sound"):
                    st.markdown(f"<a href='{row['url_sound']}' target='_blank' style='color:#444;font-size:0.72rem;'>Escuchar ↗</a>", unsafe_allow_html=True)
                st.markdown("<hr>", unsafe_allow_html=True)

        # ── TAB 2: CHARTS ──
        with tab2:
            PL = dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                      font_color="#aaa",title_font_color="#f0f0f5",margin=dict(l=0,r=10,t=40,b=0))

            # Usos por sonido
            fig1 = px.bar(
                df_au.head(15), x="usos", y="titulo", orientation="h",
                title="🎵 Top sonidos por cantidad de videos",
                color="usos", color_continuous_scale=["#1a1030","#a855f7"],
                labels={"usos":"Videos","titulo":""},
            )
            fig1.update_layout(**PL, coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
            fig1.update_xaxes(gridcolor="rgba(255,255,255,0.05)")
            st.plotly_chart(fig1, use_container_width=True)

            ca, cb = st.columns(2)
            with ca:
                # Duración distribución
                fig2 = px.histogram(
                    df_au, x="duracion", nbins=10,
                    title="⏱ Distribución de duración (seg)",
                    color_discrete_sequence=["#6c63ff"],
                    labels={"duracion":"Duración (s)"},
                )
                fig2.update_layout(**PL)
                fig2.update_xaxes(gridcolor="rgba(255,255,255,0.05)")
                fig2.update_yaxes(gridcolor="rgba(255,255,255,0.05)")
                st.plotly_chart(fig2, use_container_width=True)

            with cb:
                fig3 = px.scatter(
                    df_au, x="usos", y="likes_total",
                    hover_name="titulo", size="usos",
                    title="🎯 Usos vs Likes totales",
                    color_discrete_sequence=["#a855f7"],
                    labels={"usos":"Videos usando el audio","likes_total":"Likes acumulados"},
                )
                fig3.update_layout(**PL)
                fig3.update_xaxes(gridcolor="rgba(255,255,255,0.05)")
                fig3.update_yaxes(gridcolor="rgba(255,255,255,0.05)")
                st.plotly_chart(fig3, use_container_width=True)

        # ── TAB 3: TABLA ──
        with tab3:
            show = ["rank","titulo","artista","usos","likes_total","plays_total","duracion","url_sound"]
            st.dataframe(
                df_au[[c for c in show if c in df_au.columns]].rename(columns={
                    "rank":"Rank","titulo":"Título","artista":"Artista",
                    "usos":"Videos con este audio","likes_total":"Likes acumulados",
                    "plays_total":"Plays acumulados","duracion":"Duración (s)",
                    "url_sound":"URL Audio",
                }),
                use_container_width=True, height=450,
            )
            st.download_button(
                "⬇ CSV", df_au.to_csv(index=False).encode(),
                f"audio_trends_{country_code}_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv"
            )

    else:
        st.markdown(f"""
        <div style="text-align:center;padding:80px 20px;color:#444;">
            <div style="font-size:3rem">🔊</div>
            <div style="color:#555;margin-top:12px;font-family:Space Grotesk;font-size:1.1rem">
                Ingresa tu token y pulsa <strong style="color:#a855f7">Buscar Trends</strong>
            </div>
            <div style="color:#333;font-size:0.82rem;margin-top:8px">
                Extrae los audios más virales en TikTok {pais_sel} via TikTok Creative Center
            </div>
        </div>
        """, unsafe_allow_html=True)
