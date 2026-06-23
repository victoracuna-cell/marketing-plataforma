import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re
import json as _json

st.set_page_config(
    page_title="Social Trends · by TUU",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📊</text></svg>",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── DESIGN TOKENS & CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300;0,14..32,400;0,14..32,500;0,14..32,600;0,14..32,700;1,14..32,400&display=swap');

:root {
  --blue:      #3457FF;
  --blue-light:#EEF3FF;
  --blue-dark: #2440CC;
  --sidebar:   #111827;
  --sidebar2:  #1F2937;
  --bg:        #F5F6FA;
  --card:      #FFFFFF;
  --border:    #E5E7EB;
  --text1:     #111827;
  --text2:     #6B7280;
  --text3:     #9CA3AF;
  --green:     #22C55E;
  --red:       #EF4444;
  --amber:     #F59E0B;
}

/* ── RESET ── */
html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif !important; }
.stApp { background: var(--bg) !important; }
.block-container { padding: 2rem 2.5rem !important; max-width: 1280px !important; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] > div {
  background: var(--sidebar) !important;
  border-right: none !important;
}
section[data-testid="stSidebar"] * { color: #9CA3AF !important; }
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.06) !important; margin: 8px 0 !important; }

/* Sidebar radio */
div[role="radiogroup"] { gap: 2px !important; display: flex; flex-direction: column; }
div[role="radiogroup"] label {
  border-radius: 8px !important;
  padding: 8px 12px !important;
  transition: background 0.15s !important;
  cursor: pointer;
}
div[role="radiogroup"] label:hover { background: rgba(255,255,255,0.06) !important; }
div[role="radiogroup"] [aria-checked="true"] { background: rgba(52,87,255,0.18) !important; }
div[role="radiogroup"] [aria-checked="true"] p { color: #ffffff !important; font-weight: 600 !important; }
.stRadio [data-testid="stMarkdownContainer"] p {
  font-size: 0.875rem !important; font-weight: 500 !important;
  color: #9CA3AF !important; letter-spacing: 0.005em;
}
div[role="radiogroup"] label:hover p { color: #E5E7EB !important; }

/* Sidebar labels */
section[data-testid="stSidebar"] label {
  color: #4B5563 !important; font-size: 0.7rem !important;
  font-weight: 600 !important; letter-spacing: 0.08em;
}

/* ── INPUTS ── */
.stTextInput input, .stSelectbox [data-baseweb="select"] > div {
  background: var(--sidebar2) !important; border: 1px solid #374151 !important;
  border-radius: 8px !important; color: #E5E7EB !important; font-size: 0.85rem !important;
}
.stTextInput input::placeholder { color: #4B5563 !important; }
.stTextInput input:focus { border-color: var(--blue) !important; }

/* Main area inputs */
.main .stTextInput input {
  background: #fff !important; border: 1.5px solid var(--border) !important; color: var(--text1) !important;
}
.main .stTextInput input:focus { border-color: var(--blue) !important; box-shadow: 0 0 0 3px rgba(52,87,255,0.1) !important; }
.main .stSelectbox [data-baseweb="select"] > div {
  background: #fff !important; border: 1.5px solid var(--border) !important; color: var(--text1) !important;
  border-radius: 8px !important;
}

/* ── MULTISELECT TAGS ── */
[data-baseweb="tag"] { background: var(--blue-light) !important; border: 1px solid #C7D2FE !important; border-radius: 6px !important; }
[data-baseweb="tag"] span { color: var(--blue) !important; font-weight: 600 !important; font-size: 0.75rem !important; }
[data-baseweb="tag"] button svg { fill: var(--blue) !important; }
.main [data-baseweb="select"] > div { background: #fff !important; border: 1.5px solid var(--border) !important; border-radius: 8px !important; }

/* ── SLIDER ── */
.stSlider [data-baseweb="slider"] div[role="slider"] { background: var(--blue) !important; }
[data-testid="stSliderThumb"] { background: var(--blue) !important; }

/* ── BUTTONS ── */
.stButton > button {
  background: var(--blue) !important; color: #fff !important; border: none !important;
  border-radius: 8px !important; font-weight: 600 !important; font-size: 0.875rem !important;
  padding: 10px 20px !important; box-shadow: 0 1px 2px rgba(52,87,255,0.3) !important;
  transition: all 0.15s !important; letter-spacing: 0.005em !important;
}
.stButton > button:hover { background: var(--blue-dark) !important; transform: translateY(-1px) !important; box-shadow: 0 4px 12px rgba(52,87,255,0.35) !important; }
.stButton > button:disabled { background: #374151 !important; color: #6B7280 !important; box-shadow: none !important; transform: none !important; }

.stDownloadButton > button {
  background: #fff !important; color: var(--blue) !important;
  border: 1.5px solid var(--blue) !important; border-radius: 8px !important;
  font-weight: 600 !important; font-size: 0.8rem !important;
  box-shadow: none !important; width: auto !important; padding: 6px 16px !important;
}
.stDownloadButton > button:hover { background: var(--blue-light) !important; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--card) !important; border-bottom: 2px solid var(--border) !important;
  border-radius: 12px 12px 0 0 !important; padding: 0 4px !important; gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important; border: none !important; border-radius: 0 !important;
  color: var(--text2) !important; font-weight: 500 !important; font-size: 0.875rem !important;
  padding: 12px 20px !important;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--blue) !important; }
.stTabs [aria-selected="true"] { color: var(--blue) !important; font-weight: 600 !important; border-bottom: 2px solid var(--blue) !important; }
.stTabs [data-baseweb="tab-panel"] { padding: 20px 0 0 0 !important; }

/* ── DATAFRAME ── */
.stDataFrame { border-radius: 10px !important; border: 1px solid var(--border) !important; overflow: hidden !important; }
.stDataFrame thead tr th { background: #F9FAFB !important; color: var(--text1) !important; font-weight: 600 !important; font-size: 0.78rem !important; text-transform: uppercase; letter-spacing: 0.05em; }
.stDataFrame tbody tr:hover { background: #F9FAFB !important; }

/* ── ALERTS ── */
.stAlert { border-radius: 10px !important; }
.stSuccess { background: #F0FDF4 !important; border-left: 3px solid var(--green) !important; }
.stWarning { background: #FFFBEB !important; border-left: 3px solid var(--amber) !important; }
.stError   { background: #FEF2F2 !important; border-left: 3px solid var(--red) !important; }
.stInfo    { background: var(--blue-light) !important; border-left: 3px solid var(--blue) !important; }

/* ── EXPANDER ── */
.streamlit-expanderHeader { background: var(--card) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; }

/* ── SPINNER ── */
.stSpinner > div { border-top-color: var(--blue) !important; }

/* ── CUSTOM COMPONENTS ── */
.kpi-card {
  background: var(--card); border-radius: 16px; padding: 20px 24px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05), 0 0 0 1px rgba(0,0,0,0.04);
  height: 100%;
}
.kpi-card.primary { background: var(--blue); }
.kpi-card.primary .kpi-label, .kpi-card.primary .kpi-value { color: #fff !important; }
.kpi-label { font-size: 0.72rem; font-weight: 600; color: var(--text2); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; }
.kpi-value { font-size: 2rem; font-weight: 700; color: var(--text1); line-height: 1; }
.kpi-sub   { font-size: 0.78rem; color: var(--text3); margin-top: 4px; }
.kpi-up    { font-size: 0.78rem; color: var(--green); font-weight: 600; margin-top: 6px; }
.kpi-down  { font-size: 0.78rem; color: var(--red);   font-weight: 600; margin-top: 6px; }

.section-card {
  background: var(--card); border-radius: 16px; padding: 24px 28px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05), 0 0 0 1px rgba(0,0,0,0.04);
  margin-bottom: 20px;
}

.filter-bar {
  background: var(--card); border-radius: 12px; padding: 16px 20px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.04); margin-bottom: 20px;
  border: 1px solid var(--border);
}

.page-title { font-size: 1.6rem; font-weight: 700; color: var(--text1); }
.page-title span { color: var(--blue); }
.page-sub   { font-size: 0.82rem; color: var(--text2); margin-top: 3px; }

.trend-card {
  background: var(--card); border-radius: 12px; padding: 16px 20px;
  border: 1px solid var(--border); margin-bottom: 8px;
  transition: box-shadow 0.15s, border-color 0.15s;
}
.trend-card:hover { box-shadow: 0 4px 16px rgba(52,87,255,0.1); border-color: #C7D2FE; }
.trend-rank { font-size: 0.75rem; font-weight: 700; color: var(--text3); text-transform: uppercase; letter-spacing: 0.05em; }
.trend-author { font-size: 0.95rem; font-weight: 600; color: var(--text1); }
.trend-desc   { font-size: 0.8rem; color: var(--text2); margin-top: 2px; line-height: 1.5; }
.trend-stat   { font-size: 0.82rem; font-weight: 600; color: var(--text1); }
.trend-stat-label { font-size: 0.7rem; color: var(--text3); font-weight: 400; }

.badge {
  display: inline-block; padding: 2px 8px; border-radius: 20px;
  font-size: 0.7rem; font-weight: 600; margin-right: 4px; margin-top: 3px;
}
.badge-blue   { background: var(--blue-light); color: var(--blue); }
.badge-green  { background: #F0FDF4; color: #16A34A; }
.badge-amber  { background: #FFFBEB; color: #B45309; }
.badge-gray   { background: #F3F4F6; color: #4B5563; }

.rank-circle {
  display: inline-flex; align-items: center; justify-content: center;
  width: 30px; height: 30px; border-radius: 50%;
  background: var(--blue-light); color: var(--blue);
  font-weight: 700; font-size: 0.8rem;
}

.empty-state {
  text-align: center; padding: 64px 24px;
  background: var(--card); border-radius: 16px;
  border: 1px dashed var(--border);
}
.empty-state-icon { font-size: 2.5rem; margin-bottom: 12px; color: #D1D5DB; }
.empty-state-title { font-size: 1rem; font-weight: 600; color: var(--text2); margin-bottom: 4px; }
.empty-state-sub   { font-size: 0.82rem; color: var(--text3); }

.insight-pill {
  background: var(--blue-light); border: 1px solid #C7D2FE;
  border-radius: 10px; padding: 12px 16px; margin-bottom: 10px;
}
.insight-pill-title { font-size: 0.72rem; font-weight: 700; color: var(--text2); text-transform: uppercase; letter-spacing: 0.06em; }
.insight-pill-value { font-size: 1.4rem; font-weight: 700; color: var(--blue); margin-top: 2px; }
.insight-pill-desc  { font-size: 0.75rem; color: var(--text2); margin-top: 2px; }

.status-dot-green { display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--green);margin-right:6px; }
.status-dot-red   { display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--red);margin-right:6px; }
.status-dot-gray  { display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--text3);margin-right:6px; }

hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
PAISES = {
    "Chile":      {"hashtag": "chile",     "codigo": "CL", "flag": "🇨🇱"},
    "Argentina":  {"hashtag": "argentina", "codigo": "AR", "flag": "🇦🇷"},
    "México":     {"hashtag": "mexico",    "codigo": "MX", "flag": "🇲🇽"},
    "Colombia":   {"hashtag": "colombia",  "codigo": "CO", "flag": "🇨🇴"},
    "Perú":       {"hashtag": "peru",      "codigo": "PE", "flag": "🇵🇪"},
    "Venezuela":  {"hashtag": "venezuela", "codigo": "VE", "flag": "🇻🇪"},
    "Uruguay":    {"hashtag": "uruguay",   "codigo": "UY", "flag": "🇺🇾"},
}
PAISES_DISPLAY = {f"{v['flag']} {k}": k for k, v in PAISES.items()}

CATEGORIAS = {
    "Negocios":            ["negocios", "business", "emprendimiento"],
    "Emprendimiento":      ["emprendimiento", "startup", "emprender"],
    "Marketing Digital":   ["marketingdigital", "marketing", "ventas"],
    "Finanzas":            ["finanzaspersonales", "inversion", "dinero"],
    "Tecnología":          ["tecnologia", "tech", "ia"],
    "Productividad":       ["productividad", "freelance", "trabajoremoto"],
    "Desarrollo Personal": ["desarrollopersonal", "motivacion", "exito"],
    "Vida Corporativa":    ["corporativo", "liderazgo", "carrera"],
}

PL = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font_color="#6B7280", title_font_color="#111827",
    font_family="Inter", title_font_size=14,
    margin=dict(l=0, r=0, t=36, b=0),
)

def fmt(n):
    if not n: return "0"
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(n)

def build_queries_tt(pais_key, cats):
    hp = PAISES[pais_key]["hashtag"]
    q = []
    for cat in cats:
        for kw in CATEGORIAS[cat]:
            q.append(f"#{kw}{hp}"); q.append(f"#{kw}")
    q.append(f"trending {hp}")
    return list(dict.fromkeys(q))[:10]

def build_hashtags_ig(pais_key, cats):
    hp = PAISES[pais_key]["hashtag"]
    t = []
    for cat in cats:
        for kw in CATEGORIAS[cat]:
            t.append(f"{kw}{hp}"); t.append(kw)
    return list(dict.fromkeys(t))[:8]

def kpi(val, label, sub=None, primary=False):
    cls = "kpi-card primary" if primary else "kpi-card"
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return f'<div class="{cls}"><div class="kpi-label">{label}</div><div class="kpi-value">{val}</div>{sub_html}</div>'

def section(title, desc=None):
    d = f'<div class="page-sub">{desc}</div>' if desc else ""
    return f'<div style="margin-bottom:20px"><div class="page-title">{title}</div>{d}</div>'

def empty(icon, title, sub):
    return f'<div class="empty-state"><div class="empty-state-icon">{icon}</div><div class="empty-state-title">{title}</div><div class="empty-state-sub">{sub}</div></div>'

# ─── SESSION DEFAULTS ─────────────────────────────────────────────────────────
for k in ["tt_df","tt_err","ig_df","ig_err","au_df","au_err","au_src",
          "cx_data","cx_err","cx_keyword","cx_growth","cx_debug",
          "apify_token","trends_token","default_pais","default_cats"]:
    if k not in st.session_state:
        st.session_state[k] = None

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:24px 16px 20px">
        <div style="font-size:1.1rem;font-weight:700;color:#F9FAFB;letter-spacing:-0.02em">Social Trends</div>
        <div style="font-size:0.72rem;color:#4B5563;margin-top:3px;font-weight:500">Powered by TUU + Trends MCP</div>
    </div>
    <div style="border-top:1px solid rgba(255,255,255,0.06);margin:0 16px 16px"></div>
    <div style="font-size:0.65rem;font-weight:700;color:#374151;letter-spacing:0.1em;text-transform:uppercase;padding:0 16px 8px">DASHBOARD</div>
    """, unsafe_allow_html=True)

    nav = st.radio("nav", [
        "Dashboard",
        "TikTok Trends",
        "Instagram Trends",
        "Audio Trends",
        "Tendencias Cruzadas",
        "Ajustes",
    ], label_visibility="collapsed")

    st.markdown("""
    <div style="border-top:1px solid rgba(255,255,255,0.06);margin:16px 16px 12px"></div>
    <div style="font-size:0.65rem;font-weight:700;color:#374151;letter-spacing:0.1em;text-transform:uppercase;padding:0 16px 8px">PRÓXIMAMENTE</div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="padding:0 16px">
        <div style="color:#374151;font-size:0.82rem;font-weight:500;padding:8px 12px;border-radius:8px;">Comparador de Marcas</div>
        <div style="color:#374151;font-size:0.82rem;font-weight:500;padding:8px 12px;border-radius:8px;">Reportes</div>
        <div style="color:#374151;font-size:0.82rem;font-weight:500;padding:8px 12px;border-radius:8px;">Historial</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="border-top:1px solid rgba(255,255,255,0.06);margin:16px 16px 16px"></div>
    <div style="padding:0 16px 16px">
        <div style="font-size:0.72rem;color:#4B5563;font-weight:500;">v1.0 · Social Trends Platform</div>
    </div>
    """, unsafe_allow_html=True)

# ─── READ TOKENS FROM SETTINGS ────────────────────────────────────────────────
apify_token  = st.session_state.apify_token or ""
trends_token = st.session_state.trends_token or ""
default_pais = st.session_state.default_pais or "Chile"
default_cats = st.session_state.default_cats or ["Negocios", "Emprendimiento"]

# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if nav == "Dashboard":
    st.markdown(section("Dashboard", "Resumen de actividad y estado de la plataforma"), unsafe_allow_html=True)

    has_tt = st.session_state.tt_df is not None and not st.session_state.tt_df.empty
    has_ig = st.session_state.ig_df is not None and not st.session_state.ig_df.empty
    has_au = st.session_state.au_df is not None and not st.session_state.au_df.empty

    tt_df = st.session_state.tt_df if has_tt else pd.DataFrame()
    ig_df = st.session_state.ig_df if has_ig else pd.DataFrame()
    au_df = st.session_state.au_df if has_au else pd.DataFrame()

    tt_count = len(tt_df) if has_tt else 0
    ig_count = len(ig_df) if has_ig else 0
    au_count = len(au_df) if has_au else 0
    ht_count = int(tt_df["hashtags"].str.count("#").sum()) if has_tt and "hashtags" in tt_df.columns else 0

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(kpi(tt_count, "TikTok Videos", "Última búsqueda", primary=True), unsafe_allow_html=True)
    with c2: st.markdown(kpi(ig_count, "Instagram Posts", "Última búsqueda"), unsafe_allow_html=True)
    with c3: st.markdown(kpi(au_count, "Audios Únicos", "Última búsqueda"), unsafe_allow_html=True)
    with c4: st.markdown(kpi(ht_count, "Hashtags Detectados", "Desde TikTok"), unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns([2, 1])

    with col_a:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("**Actividad reciente**")
        if has_tt or has_ig or has_au:
            activity = []
            if has_tt:
                activity.append({"Módulo":"TikTok Trends","Resultados":tt_count,"Estado":"Completado","Tipo":"Videos"})
            if has_ig:
                activity.append({"Módulo":"Instagram Trends","Resultados":ig_count,"Estado":"Completado","Tipo":"Posts"})
            if has_au:
                activity.append({"Módulo":"Audio Trends","Resultados":au_count,"Estado":"Completado","Tipo":"Audios"})
            st.dataframe(pd.DataFrame(activity), use_container_width=True, hide_index=True)
        else:
            st.markdown('<div style="color:#9CA3AF;font-size:0.85rem;padding:20px 0">No hay búsquedas recientes. Ve a un módulo y ejecuta una búsqueda.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("**Estado de APIs**")
        apify_ok  = bool(apify_token)
        trends_ok = bool(trends_token)
        dot_a = "status-dot-green" if apify_ok else "status-dot-red"
        dot_t = "status-dot-green" if trends_ok else "status-dot-gray"
        st.markdown(f"""
        <div style="margin-top:8px">
            <div style="padding:10px 0;border-bottom:1px solid #F3F4F6;font-size:0.85rem">
                <span class="{dot_a}"></span><strong>Apify</strong>
                <span style="float:right;color:{'#22C55E' if apify_ok else '#EF4444'};font-size:0.78rem;font-weight:600">
                    {'Configurado' if apify_ok else 'Sin token'}
                </span>
            </div>
            <div style="padding:10px 0;border-bottom:1px solid #F3F4F6;font-size:0.85rem">
                <span class="{dot_t}"></span><strong>TrendsMCP</strong>
                <span style="float:right;color:{'#22C55E' if trends_ok else '#9CA3AF'};font-size:0.78rem;font-weight:600">
                    {'Configurado' if trends_ok else 'Sin token'}
                </span>
            </div>
        </div>
        <div style="margin-top:12px;font-size:0.78rem;color:#9CA3AF">
            Configura los tokens en <strong>Ajustes → APIs</strong>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if has_tt and "plays" in tt_df.columns:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("**Top TikTok · Reproducciones**")
        fig = px.bar(tt_df.head(10), x="plays", y="nickname", orientation="h",
                     color="plays", color_continuous_scale=["#EEF3FF","#3457FF"],
                     labels={"plays":"Reproducciones","nickname":""})
        fig.update_layout(**PL, coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
        fig.update_xaxes(gridcolor="#F3F4F6"); fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TIKTOK TRENDS
# ══════════════════════════════════════════════════════════════════════════════
elif nav == "TikTok Trends":
    st.markdown(section("TikTok <span>Trends</span>", "Analiza videos virales por país y categoría · Powered by Apify"), unsafe_allow_html=True)

    if not apify_token:
        st.warning("Configura tu Apify API Token en **Ajustes → APIs** antes de continuar.")
    else:
        for k in ["tt_df","tt_err"]:
            if k not in st.session_state: st.session_state[k] = None

        # ── FILTER BAR ──
        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
        fc1,fc2,fc3,fc4 = st.columns([2,3,2,1])
        with fc1:
            pais_disp = st.selectbox("País", list(PAISES_DISPLAY.keys()), index=0, key="tt_pais")
            pais_key  = PAISES_DISPLAY[pais_disp]
        with fc2:
            cats = st.multiselect("Categorías", list(CATEGORIAS.keys()), default=default_cats, key="tt_cats")
        with fc3:
            n_items = st.slider("Cantidad de videos", 10, 100, 30, step=10, key="tt_n")
        with fc4:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            run_btn = st.button("Buscar", key="tt_run", disabled=not cats)
        st.markdown('</div>', unsafe_allow_html=True)

        if run_btn and cats:
            queries  = build_queries_tt(pais_key, cats)
            actor_id = "clockworks~free-tiktok-scraper"
            url      = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"
            payload  = {"searchQueries":queries,"maxItems":n_items,"resultsPerPage":n_items,
                        "shouldDownloadVideos":False,"shouldDownloadCovers":False}
            with st.spinner("Analizando TikTok..."):
                try:
                    resp = requests.post(url, json=payload, params={"token":apify_token,"timeout":120}, timeout=180)
                    resp.raise_for_status()
                    rows = []
                    for item in resp.json():
                        a = item.get("authorMeta",{}) or {}
                        m = item.get("musicMeta",{}) or {}
                        rows.append({
                            "nickname":    "@"+a.get("nickName",""),
                            "autor":       a.get("name",""),
                            "likes":       item.get("diggCount",0) or 0,
                            "comentarios": item.get("commentCount",0) or 0,
                            "shares":      item.get("shareCount",0) or 0,
                            "plays":       item.get("playCount",0) or 0,
                            "musica":      m.get("musicName",""),
                            "hashtags":    ", ".join([f"#{h}" for h in (item.get("hashtags") or [])[:5]]),
                            "url":         item.get("webVideoUrl",""),
                            "descripcion": (item.get("text","") or "")[:120],
                            "fecha":       datetime.fromtimestamp(item.get("createTime",0)).strftime("%Y-%m-%d") if item.get("createTime") else "",
                        })
                    df = pd.DataFrame(rows)
                    if not df.empty:
                        df = df.sort_values("plays", ascending=False).reset_index(drop=True)
                        df.index += 1
                    st.session_state.tt_df  = df
                    st.session_state.tt_err = None
                except Exception as e:
                    st.session_state.tt_err = str(e)
                    st.session_state.tt_df  = None

        if st.session_state.tt_err:
            st.error(f"Error: {st.session_state.tt_err}")

        df = st.session_state.tt_df
        if df is not None and not df.empty:
            # KPIs
            c1,c2,c3,c4 = st.columns(4)
            eng = ((df["likes"]+df["comentarios"]+df["shares"])/df["plays"].replace(0,1)*100).mean()
            with c1: st.markdown(kpi(len(df), "Videos analizados"), unsafe_allow_html=True)
            with c2: st.markdown(kpi(fmt(df["plays"].sum()), "Reproducciones totales"), unsafe_allow_html=True)
            with c3: st.markdown(kpi(fmt(df["likes"].sum()), "Likes acumulados"), unsafe_allow_html=True)
            with c4: st.markdown(kpi(f"{eng:.1f}%", "Engagement promedio"), unsafe_allow_html=True)

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

            tab1, tab2, tab3 = st.tabs(["Top Videos", "Analytics", "Tabla de datos"])

            with tab1:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown('<div style="font-weight:600;color:#111827;margin-bottom:16px">Top 10 videos por reproducciones</div>', unsafe_allow_html=True)
                for i, row in df.head(10).iterrows():
                    tags = " ".join([f'<span class="badge badge-blue">{t.strip()}</span>' for t in row["hashtags"].split(",") if t.strip()])
                    st.markdown(f"""
                    <div class="trend-card">
                        <div style="display:flex;align-items:flex-start;gap:16px">
                            <div><span class="rank-circle">{i}</span></div>
                            <div style="flex:1;min-width:0">
                                <div class="trend-author">{row["nickname"]} <span style="color:#9CA3AF;font-weight:400;font-size:0.82rem">{row["autor"]}</span></div>
                                <div class="trend-desc">{row["descripcion"] or "—"}</div>
                                <div style="margin-top:6px">{tags}</div>
                                {f'<a href="{row["url"]}" target="_blank" style="font-size:0.72rem;color:#3457FF;text-decoration:none;display:inline-block;margin-top:6px">Ver en TikTok →</a>' if row["url"] else ""}
                            </div>
                            <div style="text-align:right;min-width:120px">
                                <div class="trend-stat">{fmt(row["plays"])}</div>
                                <div class="trend-stat-label">reproducciones</div>
                                <div style="margin-top:6px;display:flex;gap:12px;justify-content:flex-end">
                                    <span style="font-size:0.78rem;color:#6B7280">{fmt(row["likes"])} likes</span>
                                    <span style="font-size:0.78rem;color:#6B7280">{fmt(row["comentarios"])} com.</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with tab2:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown('<div class="section-card">', unsafe_allow_html=True)
                    fig = px.bar(df.head(15), x="plays", y="nickname", orientation="h",
                                 color="plays", color_continuous_scale=["#EEF3FF","#3457FF"],
                                 labels={"plays":"Reproducciones","nickname":""})
                    fig.update_layout(**PL, coloraxis_showscale=False, yaxis=dict(autorange="reversed"), title="Top 15 · Reproducciones")
                    fig.update_xaxes(gridcolor="#F3F4F6"); fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_b:
                    st.markdown('<div class="section-card">', unsafe_allow_html=True)
                    mc = df["musica"].value_counts().head(6).reset_index(); mc.columns=["musica","count"]
                    fig2 = px.pie(mc, values="count", names="musica", hole=0.55,
                                  color_discrete_sequence=["#3457FF","#7B96FF","#A5B8FF","#C7D2FE","#EEF3FF","#111827"],
                                  title="Músicas más usadas")
                    fig2.update_layout(**PL); fig2.update_traces(textinfo="none")
                    st.plotly_chart(fig2, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                fig3 = px.scatter(df, x="plays", y="likes", size="comentarios", color="shares",
                                  hover_name="nickname", color_continuous_scale=["#EEF3FF","#3457FF"],
                                  labels={"plays":"Reproducciones","likes":"Likes","shares":"Shares"},
                                  title="Reproducciones vs Likes · tamaño = comentarios")
                fig3.update_layout(**PL, coloraxis_showscale=False)
                fig3.update_xaxes(gridcolor="#F3F4F6"); fig3.update_yaxes(gridcolor="#F3F4F6")
                st.plotly_chart(fig3, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with tab3:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                show = ["nickname","autor","plays","likes","comentarios","shares","musica","hashtags","fecha","url"]
                st.dataframe(df[[c for c in show if c in df.columns]], use_container_width=True, height=420, hide_index=False)
                st.download_button("Descargar CSV", df.to_csv(index=False).encode(), f"tiktok_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
                st.markdown('</div>', unsafe_allow_html=True)

        elif run_btn:
            pass
        else:
            st.markdown(empty("↑", "Configura los filtros y presiona Buscar", "Los resultados aparecerán aquí"), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  INSTAGRAM TRENDS
# ══════════════════════════════════════════════════════════════════════════════
elif nav == "Instagram Trends":
    st.markdown(section("Instagram <span>Trends</span>", "Posts y Reels virales por hashtag · Powered by Apify"), unsafe_allow_html=True)

    if not apify_token:
        st.warning("Configura tu Apify API Token en **Ajustes → APIs** antes de continuar.")
    else:
        for k in ["ig_df","ig_err"]:
            if k not in st.session_state: st.session_state[k] = None

        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
        fc1,fc2,fc3,fc4 = st.columns([2,3,2,1])
        with fc1:
            pais_disp = st.selectbox("País", list(PAISES_DISPLAY.keys()), index=0, key="ig_pais")
            pais_key  = PAISES_DISPLAY[pais_disp]
        with fc2:
            cats = st.multiselect("Categorías", list(CATEGORIAS.keys()), default=default_cats, key="ig_cats")
        with fc3:
            tipos = st.multiselect("Tipo", ["Reel","Imagen","Carousel"], default=["Reel","Imagen","Carousel"], key="ig_tipos")
            n_items = st.slider("Cantidad", 10, 100, 30, step=10, key="ig_n")
        with fc4:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            run_ig = st.button("Buscar", key="ig_run", disabled=not cats)
        st.markdown('</div>', unsafe_allow_html=True)

        if run_ig and cats:
            hashtags = build_hashtags_ig(pais_key, cats)
            actor_id = "apify~instagram-hashtag-scraper"
            url      = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"
            payload  = {"hashtags":hashtags,"resultsLimit":n_items,"proxy":{"useApifyProxy":True}}
            with st.spinner("Analizando Instagram..."):
                try:
                    resp = requests.post(url, json=payload, params={"token":apify_token,"timeout":120}, timeout=180)
                    resp.raise_for_status()
                    rows = []
                    for item in resp.json():
                        owner   = item.get("ownerUsername","") or (item.get("owner",{}) or {}).get("username","")
                        tr      = item.get("type","") or ""
                        if "reel" in tr.lower() or item.get("isVideo",False): tipo = "Reel"
                        elif item.get("mediaCount",1)>1 or "sidecar" in tr.lower(): tipo = "Carousel"
                        else: tipo = "Imagen"
                        caption = str(item.get("caption","") or "")[:140]
                        rows.append({
                            "autor":"@"+owner,"tipo":tipo,
                            "likes":item.get("likesCount",0) or 0,
                            "comentarios":item.get("commentsCount",0) or 0,
                            "views":item.get("videoViewCount",0) or 0,
                            "caption":caption,
                            "hashtags":", ".join([f"#{t}" for t in re.findall(r"#(\w+)",caption)[:6]]),
                            "hashtag_src":"#"+(item.get("hashtag","") or ""),
                            "url":item.get("url","") or item.get("shortCode",""),
                            "fecha":(item.get("timestamp","") or "")[:10],
                        })
                    df = pd.DataFrame(rows)
                    if not df.empty:
                        df["engagement"] = df["likes"]+df["comentarios"]
                        df = df.sort_values("engagement",ascending=False).reset_index(drop=True)
                        df.index += 1
                    st.session_state.ig_df  = df
                    st.session_state.ig_err = None
                except Exception as e:
                    st.session_state.ig_err = str(e); st.session_state.ig_df = None

        if st.session_state.ig_err:
            st.error(f"Error: {st.session_state.ig_err}")

        df = st.session_state.ig_df
        if df is not None and not df.empty:
            df_f = df[df["tipo"].isin(tipos)].copy() if tipos else df.copy()

            TIPO_COLOR = {"Reel":"#3457FF","Imagen":"#111827","Carousel":"#7B96FF"}
            TIPO_BADGE = {"Reel":"badge-blue","Imagen":"badge-gray","Carousel":"badge-blue"}

            c1,c2,c3,c4 = st.columns(4)
            with c1: st.markdown(kpi(len(df_f), "Posts analizados"), unsafe_allow_html=True)
            with c2: st.markdown(kpi(fmt(df_f["likes"].sum()), "Likes acumulados"), unsafe_allow_html=True)
            with c3: st.markdown(kpi(fmt(df_f["engagement"].sum()), "Engagement total"), unsafe_allow_html=True)
            with c4: st.markdown(kpi(fmt(df_f["views"].sum()), "Vistas Reels"), unsafe_allow_html=True)

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

            tab1,tab2,tab3,tab4 = st.tabs(["Top Posts","Analytics","Insights","Tabla"])

            with tab1:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                for i,row in df_f.head(10).iterrows():
                    tb  = TIPO_BADGE.get(row["tipo"],"badge-gray")
                    tc  = TIPO_COLOR.get(row["tipo"],"#6B7280")
                    tags = " ".join([f'<span class="badge badge-blue">{t.strip()}</span>' for t in row["hashtags"].split(",") if t.strip()])
                    vw = f'<span style="font-size:0.78rem;color:#6B7280">{fmt(row["views"])} views</span>' if row["views"]>0 else ""
                    lnk = row["url"] if row["url"].startswith("http") else f"https://www.instagram.com/p/{row['url']}"
                    st.markdown(f"""
                    <div class="trend-card">
                        <div style="display:flex;align-items:flex-start;gap:16px">
                            <div><span class="rank-circle">{i}</span></div>
                            <div style="flex:1">
                                <div class="trend-author">{row["autor"]} <span class="badge {tb}">{row["tipo"]}</span></div>
                                <div class="trend-desc">{row["caption"] or "—"}</div>
                                <div style="margin-top:6px">{tags}</div>
                                <a href="{lnk}" target="_blank" style="font-size:0.72rem;color:#3457FF;text-decoration:none;margin-top:6px;display:inline-block">Ver en Instagram →</a>
                            </div>
                            <div style="text-align:right;min-width:130px">
                                <div class="trend-stat">{fmt(row["engagement"])}</div>
                                <div class="trend-stat-label">engagement</div>
                                <div style="margin-top:4px;font-size:0.78rem;color:#6B7280">{fmt(row["likes"])} likes · {fmt(row["comentarios"])} com.</div>
                                <div style="margin-top:2px">{vw}</div>
                                <div style="font-size:0.72rem;color:#9CA3AF;margin-top:4px">{row["fecha"]}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with tab2:
                col_a,col_b = st.columns(2)
                with col_a:
                    st.markdown('<div class="section-card">', unsafe_allow_html=True)
                    fig = px.bar(df_f.head(15),x="engagement",y="autor",orientation="h",
                                 color="engagement",color_continuous_scale=["#EEF3FF","#3457FF"],
                                 labels={"engagement":"Engagement","autor":""},title="Top 15 · Engagement")
                    fig.update_layout(**PL,coloraxis_showscale=False,yaxis=dict(autorange="reversed"))
                    fig.update_xaxes(gridcolor="#F3F4F6"); fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig,use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_b:
                    st.markdown('<div class="section-card">', unsafe_allow_html=True)
                    tc = df_f["tipo"].value_counts().reset_index(); tc.columns=["tipo","count"]
                    fig2 = px.pie(tc,values="count",names="tipo",hole=0.55,
                                  color_discrete_map={"Reel":"#3457FF","Imagen":"#111827","Carousel":"#7B96FF"},
                                  title="Distribución por tipo")
                    fig2.update_layout(**PL); fig2.update_traces(textinfo="none")
                    st.plotly_chart(fig2,use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            with tab3:
                col_a,col_b = st.columns(2)
                best_g = df_f.groupby("tipo")["engagement"].mean()
                top_a  = df_f.groupby("autor")["engagement"].sum()
                reels  = df_f[df_f["tipo"]=="Reel"]["engagement"].mean() if "Reel" in df_f["tipo"].values else 0
                otros  = df_f[df_f["tipo"]!="Reel"]["engagement"].mean() if len(df_f[df_f["tipo"]!="Reel"])>0 else 0
                ratio  = df_f["likes"].sum()/max(df_f["comentarios"].sum(),1)
                with col_a:
                    if not best_g.empty:
                        bt,bv = best_g.idxmax(),best_g.max()
                        st.markdown(f'<div class="insight-pill"><div class="insight-pill-title">Mejor formato</div><div class="insight-pill-value">{bt}</div><div class="insight-pill-desc">Promedio {fmt(int(bv))} interacciones</div></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="insight-pill"><div class="insight-pill-title">Ratio Likes / Comentarios</div><div class="insight-pill-value">{ratio:.0f}:1</div><div class="insight-pill-desc">Por cada comentario hay {ratio:.0f} likes</div></div>', unsafe_allow_html=True)
                with col_b:
                    if not top_a.empty:
                        ta,tv = top_a.idxmax(),top_a.max()
                        st.markdown(f'<div class="insight-pill"><div class="insight-pill-title">Cuenta con más engagement</div><div class="insight-pill-value">{ta}</div><div class="insight-pill-desc">{fmt(int(tv))} engagement acumulado</div></div>', unsafe_allow_html=True)
                    if reels and otros:
                        diff = ((reels-otros)/max(otros,1))*100
                        st.markdown(f'<div class="insight-pill"><div class="insight-pill-title">Reels vs otros formatos</div><div class="insight-pill-value">{diff:+.0f}%</div><div class="insight-pill-desc">Diferencia de engagement promedio</div></div>', unsafe_allow_html=True)

            with tab4:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                show = ["autor","tipo","likes","comentarios","views","engagement","hashtag_src","fecha","url"]
                st.dataframe(df_f[[c for c in show if c in df_f.columns]], use_container_width=True, height=420, hide_index=False)
                st.download_button("Descargar CSV", df_f.to_csv(index=False).encode(), f"instagram_{datetime.now().strftime('%Y%m%d')}.csv","text/csv")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(empty("↑", "Configura los filtros y presiona Buscar", "Los resultados aparecerán aquí"), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  AUDIO TRENDS
# ══════════════════════════════════════════════════════════════════════════════
elif nav == "Audio Trends":
    st.markdown(section("Audio <span>Trends</span>", "Sonidos virales en TikTok por país · Powered by Apify"), unsafe_allow_html=True)

    if not apify_token:
        st.warning("Configura tu Apify API Token en **Ajustes → APIs** antes de continuar.")
    else:
        for k in ["au_df","au_err","au_src"]:
            if k not in st.session_state: st.session_state[k] = None

        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
        fc1,fc2,fc3,fc4 = st.columns([2,2,2,1])
        with fc1:
            pais_disp = st.selectbox("País", list(PAISES_DISPLAY.keys()), index=0, key="au_pais")
            pais_key  = PAISES_DISPLAY[pais_disp]
        with fc2:
            periodo   = st.selectbox("Período", ["7 días","30 días","120 días"], key="au_periodo")
            pval      = {"7 días":7,"30 días":30,"120 días":120}[periodo]
        with fc3:
            n_audio   = st.slider("Sonidos", 10, 50, 20, step=10, key="au_n")
        with fc4:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            run_au = st.button("Buscar", key="au_run")
        st.markdown('</div>', unsafe_allow_html=True)

        pais_info    = PAISES[pais_key]
        country_code = pais_info["codigo"]

        if run_au:
            with st.spinner("Buscando audios trending..."):
                df_au = None; source_label = ""
                try:
                    resp = requests.post(
                        f"https://api.apify.com/v2/acts/alien_force~tiktok-trending-sounds-tracker/run-sync-get-dataset-items",
                        json={"country_code":country_code,"limit":n_audio},
                        params={"token":apify_token,"timeout":90}, timeout=120)
                    resp.raise_for_status()
                    raw = resp.json()
                    if raw and any(r.get("title") or r.get("rank") for r in raw):
                        rows = []
                        for item in raw:
                            rows.append({"rank":item.get("rank") or len(rows)+1,
                                         "titulo":item.get("title") or item.get("name","—"),
                                         "artista":item.get("author") or item.get("authorName","—"),
                                         "duracion":item.get("duration",0) or 0,
                                         "usos":item.get("useCount") or item.get("videoCount") or 0,
                                         "trend_7d":item.get("trend7") or 0,
                                         "url_sound":item.get("playUrl") or item.get("link") or "",
                                         "likes_total":0,"plays_total":0})
                        df_au = pd.DataFrame(rows)
                        source_label = "TikTok Creative Center (ranking oficial)"
                except Exception: pass
                if df_au is None or df_au.empty:
                    try:
                        hp = pais_info["hashtag"]
                        resp2 = requests.post(
                            f"https://api.apify.com/v2/acts/clockworks~free-tiktok-scraper/run-sync-get-dataset-items",
                            json={"searchQueries":[f"#{hp}",f"trending {hp}",f"#fyp{hp}",f"#foryou{hp}"],
                                  "maxItems":300,"resultsPerPage":300,"shouldDownloadVideos":False,"shouldDownloadCovers":False},
                            params={"token":apify_token,"timeout":120}, timeout=180)
                        resp2.raise_for_status()
                        raw2 = resp2.json(); md = {}
                        for item in raw2:
                            m = item.get("musicMeta") or {}
                            mid = m.get("musicId") or m.get("musicName","")
                            if not mid: continue
                            if mid not in md:
                                md[mid]={"titulo":m.get("musicName","") or "Sonido original",
                                         "artista":m.get("musicAuthor","") or "—",
                                         "duracion":m.get("musicDuration",0) or 0,
                                         "url_sound":m.get("musicPlay","") or "",
                                         "usos":0,"likes_total":0,"plays_total":0}
                            md[mid]["usos"]+=1
                            md[mid]["likes_total"]+=item.get("diggCount",0) or 0
                            md[mid]["plays_total"]+=item.get("playCount",0) or 0
                        rows2 = [{"rank":r+1,"titulo":d["titulo"],"artista":d["artista"],
                                  "duracion":d["duracion"],"usos":d["usos"],
                                  "likes_total":d["likes_total"],"plays_total":d["plays_total"],
                                  "url_sound":d["url_sound"],"trend_7d":0}
                                 for r,(mid,d) in enumerate(sorted(md.items(),key=lambda x:x[1]["usos"],reverse=True))]
                        df_au = pd.DataFrame(rows2[:n_audio])
                        source_label = f"Agregado de {len(raw2)} videos trending"
                    except Exception as e2:
                        st.session_state.au_err = str(e2); df_au = None
                st.session_state.au_df = df_au
                st.session_state.au_src = source_label
                if df_au is not None: st.session_state.au_err = None

        if st.session_state.au_err:
            st.error(f"Error: {st.session_state.au_err}")

        df_au = st.session_state.au_df
        if df_au is not None and not df_au.empty:
            if st.session_state.au_src:
                st.markdown(f'<div style="font-size:0.75rem;color:#9CA3AF;margin-bottom:12px">Fuente: {st.session_state.au_src}</div>', unsafe_allow_html=True)

            c1,c2,c3,c4 = st.columns(4)
            with c1: st.markdown(kpi(len(df_au), "Audios únicos"), unsafe_allow_html=True)
            with c2: st.markdown(kpi(fmt(df_au["usos"].max() if "usos" in df_au.columns else 0), "Max. videos / audio"), unsafe_allow_html=True)
            with c3: st.markdown(kpi(fmt(df_au.get("likes_total",pd.Series([0])).max()), "Likes audio top"), unsafe_allow_html=True)
            with c4: st.markdown(kpi(f'{df_au["duracion"].mean():.0f}s', "Duración promedio"), unsafe_allow_html=True)

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

            tab1,tab2,tab3 = st.tabs(["Ranking","Analytics","Tabla"])

            with tab1:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                for _,row in df_au.iterrows():
                    td = ""
                    if row.get("trend_7d"):
                        s = "▲" if row["trend_7d"]>0 else "▼"
                        c = "#22C55E" if row["trend_7d"]>0 else "#EF4444"
                        td = f'<span style="color:{c};font-size:0.75rem;font-weight:600">{s} {abs(row["trend_7d"]):.0f}% 7d</span>'
                    st.markdown(f"""
                    <div class="trend-card">
                        <div style="display:flex;align-items:center;gap:16px">
                            <span class="rank-circle">{int(row["rank"])}</span>
                            <div style="flex:1">
                                <div class="trend-author">{row["titulo"]}</div>
                                <div style="font-size:0.8rem;color:#6B7280;margin-top:2px">
                                    {row["artista"]} · {row["duracion"]}s {td}
                                </div>
                            </div>
                            <div style="text-align:right">
                                <div class="trend-stat">{fmt(row["usos"])}</div>
                                <div class="trend-stat-label">videos</div>
                                {f'<a href="{row["url_sound"]}" target="_blank" style="font-size:0.72rem;color:#3457FF;text-decoration:none">Escuchar →</a>' if row.get("url_sound") else ""}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with tab2:
                col_a,col_b = st.columns(2)
                with col_a:
                    st.markdown('<div class="section-card">', unsafe_allow_html=True)
                    fig = px.bar(df_au.head(15),x="usos",y="titulo",orientation="h",
                                 color="usos",color_continuous_scale=["#EEF3FF","#3457FF"],
                                 labels={"usos":"Videos","titulo":""},title="Top sonidos · Videos")
                    fig.update_layout(**PL,coloraxis_showscale=False,yaxis=dict(autorange="reversed"))
                    fig.update_xaxes(gridcolor="#F3F4F6")
                    st.plotly_chart(fig,use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_b:
                    st.markdown('<div class="section-card">', unsafe_allow_html=True)
                    fig2 = px.histogram(df_au,x="duracion",nbins=10,
                                        color_discrete_sequence=["#3457FF"],
                                        labels={"duracion":"Duración (s)"},title="Duración de audios")
                    fig2.update_layout(**PL)
                    fig2.update_xaxes(gridcolor="#F3F4F6"); fig2.update_yaxes(gridcolor="#F3F4F6")
                    st.plotly_chart(fig2,use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            with tab3:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                show = ["rank","titulo","artista","usos","likes_total","plays_total","duracion","url_sound"]
                st.dataframe(df_au[[c for c in show if c in df_au.columns]], use_container_width=True, height=420, hide_index=True)
                st.download_button("Descargar CSV", df_au.to_csv(index=False).encode(), f"audio_{country_code}_{datetime.now().strftime('%Y%m%d')}.csv","text/csv")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(empty("♪", "Configura los filtros y presiona Buscar", "Los audios trending aparecerán aquí"), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TENDENCIAS CRUZADAS
# ══════════════════════════════════════════════════════════════════════════════
elif nav == "Tendencias Cruzadas":
    st.markdown(section("Tendencias <span>Cruzadas</span>", "Compara un keyword en Google, TikTok, YouTube y Reddit · Powered by TrendsMCP"), unsafe_allow_html=True)

    if not trends_token:
        st.warning("Configura tu TrendsMCP API Key en **Ajustes → APIs** antes de continuar.")
        st.info("Obtén tu key gratis en **trendsmcp.ai** — 100 requests/mes sin tarjeta.")
    else:
        for k in ["cx_data","cx_err","cx_keyword","cx_growth","cx_debug"]:
            if k not in st.session_state: st.session_state[k] = None

        FUENTES = {"Google Search":"google search","TikTok":"tiktok","YouTube":"youtube","Reddit":"reddit","Amazon":"amazon"}

        st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
        fc1,fc2,fc3,fc4 = st.columns([3,2,2,1])
        with fc1: keyword = st.text_input("Keyword a analizar", placeholder="emprendimiento, startup chile...", key="cx_kw")
        with fc2: fuentes_sel = st.multiselect("Plataformas", list(FUENTES.keys()), default=["Google Search","TikTok","YouTube","Reddit"])
        with fc3: periodo_cx = st.select_slider("Período", ["1M","3M","6M","12M","2Y","5Y"], value="12M")
        with fc4:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            run_cx = st.button("Analizar", key="cx_run", disabled=not keyword or not fuentes_sel)
        st.markdown('</div>', unsafe_allow_html=True)

        def fetch_series(kw, source, period):
            try:
                r = requests.post("https://api.trendsmcp.ai/api",
                    headers={"Authorization":f"Bearer {trends_token}","Content-Type":"application/json"},
                    json={"keyword":kw,"source":source}, timeout=20)
                if r.status_code == 200:
                    d = r.json(); body = d.get("body") or d
                    if isinstance(body, str): body = _json.loads(body)
                    return body if isinstance(body, list) else (body.get("data") or body.get("results") or body.get("series") or [])
            except Exception: pass
            return []

        def fetch_growth(kw, source):
            try:
                r = requests.post("https://api.trendsmcp.ai/api",
                    headers={"Authorization":f"Bearer {trends_token}","Content-Type":"application/json"},
                    json={"keyword":kw,"source":source,"type":"growth","percent_growth":["1M","3M","12M"]}, timeout=15)
                if r.status_code == 200:
                    d = r.json(); body = d.get("body") or d
                    if isinstance(body, str): body = _json.loads(body)
                    return body if isinstance(body, dict) else {}
            except Exception: pass
            return {}

        def parse_series(series):
            dates,values = [],[]
            for pt in series:
                if isinstance(pt,dict):
                    d = pt.get("date") or pt.get("week") or pt.get("timestamp","")
                    v = pt.get("value") or pt.get("interest") or pt.get("score") or 0
                elif isinstance(pt,(list,tuple)) and len(pt)>=2: d,v = pt[0],pt[1]
                else: continue
                dates.append(d); values.append(float(v) if v else 0)
            return dates,values

        if run_cx and keyword and fuentes_sel:
            with st.spinner(f"Comparando '{keyword}' en {len(fuentes_sel)} plataformas..."):
                all_s,all_g,errors,dbg = {},{},{},{}
                for lbl in fuentes_sel:
                    src = FUENTES[lbl]
                    s = fetch_series(keyword,src,periodo_cx)
                    if s: all_s[lbl]=s
                    else: errors.append(lbl)
                    g = fetch_growth(keyword,src)
                    if g: all_g[lbl]=g
                    dbg[lbl]={"series_len":len(s),"growth_keys":list(g.keys())}
                st.session_state.cx_data=all_s; st.session_state.cx_growth=all_g
                st.session_state.cx_keyword=keyword; st.session_state.cx_err=errors if errors else None
                st.session_state.cx_debug=dbg

        if st.session_state.cx_err:
            st.warning(f"Sin datos para: {', '.join(st.session_state.cx_err)}")
            if st.session_state.get("cx_debug"):
                with st.expander("Debug — respuesta API"):
                    st.json(st.session_state.cx_debug)

        cx_data=st.session_state.cx_data; cx_growth=st.session_state.cx_growth; kw=st.session_state.cx_keyword
        COLORS = ["#3457FF","#111827","#7B96FF","#A5B8FF","#C7D2FE","#6B7280"]

        if cx_data and kw:
            st.markdown(f'<div style="font-size:0.9rem;font-weight:600;color:#6B7280;margin-bottom:16px">Resultados para: <strong style="color:#111827">{kw}</strong></div>', unsafe_allow_html=True)

            tab1,tab2,tab3 = st.tabs(["Series de tiempo","Crecimiento","Datos"])

            with tab1:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                fig = go.Figure()
                avgs = {}
                for idx,(lbl,series) in enumerate(cx_data.items()):
                    dates,values = parse_series(series)
                    if dates:
                        fig.add_trace(go.Scatter(x=dates,y=values,name=lbl,
                            line=dict(color=COLORS[idx%len(COLORS)],width=2),mode="lines"))
                        avgs[lbl]=sum(values)/max(len(values),1)
                fig.update_layout(**PL, title=f"Interés normalizado (0–100) · {kw}",
                    legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#6B7280")),
                    yaxis=dict(range=[0,100],gridcolor="#F3F4F6"),
                    xaxis=dict(gridcolor="#F3F4F6"), hovermode="x unified")
                st.plotly_chart(fig,use_container_width=True)
                if avgs:
                    top = max(avgs,key=avgs.get)
                    st.markdown(f'<div class="insight-pill"><div class="insight-pill-title">Plataforma con mayor tracción</div><div class="insight-pill-value">{top}</div><div class="insight-pill-desc">Interés promedio {avgs[top]:.0f}/100</div></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with tab2:
                if cx_growth:
                    rows_g = []
                    for lbl,gdata in cx_growth.items():
                        for r in (gdata.get("results") or gdata.get("data") or []):
                            if isinstance(r,dict):
                                rows_g.append({"Plataforma":lbl,"Período":r.get("period","—"),"Crecimiento":r.get("growth") or r.get("value") or 0})
                    if rows_g:
                        st.markdown('<div class="section-card">', unsafe_allow_html=True)
                        df_g = pd.DataFrame(rows_g)
                        try:
                            pivot = df_g.pivot(index="Plataforma",columns="Período",values="Crecimiento")
                            fig2 = px.imshow(pivot,color_continuous_scale=["#EF4444","#F9FAFB","#3457FF"],
                                             aspect="auto",text_auto=".1f",title=f"Heatmap de crecimiento · {kw}")
                            fig2.update_layout(**PL)
                            st.plotly_chart(fig2,use_container_width=True)
                        except Exception: pass
                        periodos = df_g["Período"].unique().tolist()
                        if periodos:
                            p = st.selectbox("Ver período",periodos,key="cx_p")
                            df_p = df_g[df_g["Período"]==p].copy()
                            df_p["color"] = df_p["Crecimiento"].apply(lambda x:"Subiendo" if x>0 else "Bajando")
                            fig3 = px.bar(df_p,x="Plataforma",y="Crecimiento",color="color",
                                color_discrete_map={"Subiendo":"#3457FF","Bajando":"#EF4444"},
                                title=f"Crecimiento {p} por plataforma",labels={"Crecimiento":"% cambio"})
                            fig3.update_layout(**PL,showlegend=False)
                            st.plotly_chart(fig3,use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else: st.info("Sin datos de crecimiento.")
                else: st.info("Sin datos de crecimiento. Prueba otro keyword.")

            with tab3:
                for lbl,series in cx_data.items():
                    with st.expander(f"{lbl} · {len(series)} puntos"):
                        dates,values = parse_series(series)
                        if dates:
                            df_r = pd.DataFrame({"fecha":dates,"valor":values})
                            st.dataframe(df_r,use_container_width=True,height=220,hide_index=True)
                            st.download_button(f"CSV {lbl}",df_r.to_csv(index=False).encode(),
                                f"cx_{kw}_{lbl.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.csv","text/csv",key=f"dl_{lbl}")
        else:
            st.markdown(empty("~", "Ingresa un keyword y presiona Analizar", "Compara el interés entre Google, TikTok, YouTube y Reddit"), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  AJUSTES
# ══════════════════════════════════════════════════════════════════════════════
elif nav == "Ajustes":
    st.markdown(section("Ajustes", "Configura tokens, preferencias y conexiones de la plataforma"), unsafe_allow_html=True)

    tab_gen, tab_api = st.tabs(["General", "APIs"])

    with tab_gen:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("**Preferencias generales**")
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        col1,col2 = st.columns(2)
        with col1:
            pais_opts = list(PAISES.keys())
            idx = pais_opts.index(default_pais) if default_pais in pais_opts else 0
            new_pais = st.selectbox("País por defecto", pais_opts, index=idx)
        with col2:
            new_cats = st.multiselect("Categorías por defecto", list(CATEGORIAS.keys()), default=default_cats)

        if st.button("Guardar preferencias", key="save_gen"):
            st.session_state.default_pais = new_pais
            st.session_state.default_cats = new_cats
            default_pais = new_pais; default_cats = new_cats
            st.success("Preferencias guardadas")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_api:
        col1,col2 = st.columns(2)

        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("**Apify**")
            st.markdown('<div style="font-size:0.8rem;color:#6B7280;margin-bottom:12px">Usado para TikTok Trends, Instagram Trends y Audio Trends</div>', unsafe_allow_html=True)
            new_apify = st.text_input("API Token", value=apify_token or "", type="password",
                                      placeholder="apify_api_xxxxxxxxxxxx", key="inp_apify")
            apify_status = "Configurado" if new_apify else "Sin token"
            dot = "status-dot-green" if new_apify else "status-dot-red"
            st.markdown(f'<div style="font-size:0.8rem;margin-top:8px"><span class="{dot}"></span>{apify_status}</div>', unsafe_allow_html=True)
            if st.button("Guardar token Apify", key="save_apify"):
                st.session_state.apify_token = new_apify
                apify_token = new_apify
                st.success("Token guardado")
            st.markdown('<div style="font-size:0.75rem;color:#9CA3AF;margin-top:8px">Obtén tu token en <strong>apify.com → Settings → Integrations</strong></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("**TrendsMCP**")
            st.markdown('<div style="font-size:0.8rem;color:#6B7280;margin-bottom:12px">Usado para Tendencias Cruzadas (Google, TikTok, YouTube, Reddit)</div>', unsafe_allow_html=True)
            new_trends = st.text_input("API Key", value=trends_token or "", type="password",
                                       placeholder="tmcp_xxxxxxxxxxxx", key="inp_trends")
            trends_status = "Configurado" if new_trends else "Sin token"
            dot2 = "status-dot-green" if new_trends else "status-dot-gray"
            st.markdown(f'<div style="font-size:0.8rem;margin-top:8px"><span class="{dot2}"></span>{trends_status}</div>', unsafe_allow_html=True)
            if st.button("Guardar token TrendsMCP", key="save_trends"):
                st.session_state.trends_token = new_trends
                trends_token = new_trends
                st.success("Token guardado")
            st.markdown('<div style="font-size:0.75rem;color:#9CA3AF;margin-top:8px">Obtén tu key gratis en <strong>trendsmcp.ai</strong> — 100 req/mes sin tarjeta</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("**Próximas integraciones**")
        st.markdown("""
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-top:12px">
            <div style="border:1.5px dashed #E5E7EB;border-radius:10px;padding:16px;text-align:center">
                <div style="font-weight:600;color:#9CA3AF;font-size:0.85rem">OpenAI</div>
                <div style="font-size:0.75rem;color:#D1D5DB;margin-top:4px">Análisis semántico</div>
            </div>
            <div style="border:1.5px dashed #E5E7EB;border-radius:10px;padding:16px;text-align:center">
                <div style="font-weight:600;color:#9CA3AF;font-size:0.85rem">Slack</div>
                <div style="font-size:0.75rem;color:#D1D5DB;margin-top:4px">Alertas de trends</div>
            </div>
            <div style="border:1.5px dashed #E5E7EB;border-radius:10px;padding:16px;text-align:center">
                <div style="font-weight:600;color:#9CA3AF;font-size:0.85rem">Google Sheets</div>
                <div style="font-size:0.75rem;color:#D1D5DB;margin-top:4px">Exportar reportes</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
