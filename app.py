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
</style>
""", unsafe_allow_html=True)

# ─── DATOS ─────────────────────────────────────────────────────────────────────
PAISES = {
    "🇨🇱 Chile":     {"hashtag": "chile"},
    "🇦🇷 Argentina": {"hashtag": "argentina"},
    "🇲🇽 México":    {"hashtag": "mexico"},
    "🇨🇴 Colombia":  {"hashtag": "colombia"},
    "🇵🇪 Perú":      {"hashtag": "peru"},
    "🇻🇪 Venezuela": {"hashtag": "venezuela"},
    "🇺🇾 Uruguay":   {"hashtag": "uruguay"},
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
        ["🎵 TikTok Trends", "📸 Instagram Trends"],
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

    st.markdown("#### 📂 Categorías")
    cats_sel = st.multiselect(
        "Categorías", list(CATEGORIAS.keys()),
        default=["💼 Negocios", "🚀 Emprendimiento"],
        label_visibility="collapsed",
    )

    max_items = st.slider("Posts a analizar", 10, 100, 30, step=10)
    fetch_btn = st.button("🔍 Buscar Trends", disabled=not api_token or not cats_sel)

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
else:

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
