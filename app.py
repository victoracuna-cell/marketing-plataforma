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
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=Rajdhani:wght@500;600;700&display=swap');

:root {
  --blue:     #3457FF;
  --blue-h:   #2440CC;
  --blue-l:   #EEF3FF;
  --sidebar:  #0F1629;
  --sidebar2: #1A2340;
  --bg:       #F4F6FB;
  --card:     #FFFFFF;
  --border:   #E8EBF2;
  --t1:       #0F1629;
  --t2:       #5A6380;
  --t3:       #9BA3BE;
  --green:    #22C55E;
  --red:      #EF4444;
  --amber:    #F59E0B;
}

/* ── RESET ── */
html,body,[class*="css"] { font-family:'DM Sans',-apple-system,sans-serif !important; }
.stApp { background:var(--bg) !important; }
.block-container { padding:2rem 2.5rem 3rem !important; max-width:1240px !important; }
* { box-sizing:border-box; }
p,div,span,label { font-family:'DM Sans',sans-serif !important; }
h1,h2,h3,h4 { font-family:'Rajdhani',sans-serif !important; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] { width:220px !important; min-width:220px !important; }
section[data-testid="stSidebar"] > div {
  background:var(--sidebar) !important;
  border-right:none !important;
  padding:0 !important;
}
section[data-testid="stSidebar"] * { color:#8A94B2 !important; font-size:0.875rem !important; }
section[data-testid="stSidebar"] hr { border-color:rgba(255,255,255,0.07) !important; margin:0 20px !important; }

/* Nav radio */
div[role="radiogroup"] {
  display:flex !important; flex-direction:column !important; gap:2px !important; padding:0 12px !important;
}
div[role="radiogroup"] label {
  border-radius:10px !important; padding:9px 14px !important;
  transition:background 0.15s !important; cursor:pointer !important;
  display:flex !important; align-items:center !important;
}
div[role="radiogroup"] label:hover { background:rgba(255,255,255,0.06) !important; }
div[role="radiogroup"] [aria-checked="true"] { background:rgba(52,87,255,0.2) !important; }
div[role="radiogroup"] [aria-checked="true"] p { color:#ffffff !important; font-weight:600 !important; }
div[role="radiogroup"] label p { color:#8A94B2 !important; font-size:0.875rem !important; font-weight:500 !important; margin:0 !important; }
div[role="radiogroup"] label:hover p { color:#C8D0E8 !important; }
/* hide the radio dot */
div[role="radiogroup"] label [data-testid="stMarkdownContainer"] { flex:1; }
div[role="radiogroup"] label > div:first-child { display:none !important; }

/* ── INPUTS (sidebar) ── */
section[data-testid="stSidebar"] .stTextInput input {
  background:#1A2340 !important; border:1px solid #2A3560 !important;
  border-radius:8px !important; color:#E2E8F5 !important; font-size:0.82rem !important;
}

/* ── MAIN INPUTS ── */
.main .stTextInput input, .main [data-baseweb="input"] input {
  background:#fff !important; border:1.5px solid var(--border) !important;
  border-radius:8px !important; color:var(--t1) !important; font-size:0.875rem !important;
}
.main .stTextInput input:focus { border-color:var(--blue) !important; box-shadow:0 0 0 3px rgba(52,87,255,0.08) !important; }
.main [data-baseweb="select"] > div {
  background:#fff !important; border:1.5px solid var(--border) !important;
  border-radius:8px !important; min-height:40px !important;
}

/* ── MULTISELECT TAGS ── */
[data-baseweb="tag"] { background:var(--blue-l) !important; border:1px solid #C0CFFF !important; border-radius:6px !important; }
[data-baseweb="tag"] span { color:var(--blue) !important; font-weight:600 !important; font-size:0.72rem !important; }
[data-baseweb="tag"] button svg { fill:var(--blue) !important; }

/* ── SLIDER ── */
[data-testid="stSlider"] [data-baseweb="slider"] { padding:0 !important; }

/* ── BUTTONS ── */
.stButton > button {
  background:var(--blue) !important; color:#fff !important; border:none !important;
  border-radius:8px !important; font-family:'DM Sans',sans-serif !important;
  font-weight:600 !important; font-size:0.875rem !important;
  padding:9px 20px !important; letter-spacing:0.01em !important;
  box-shadow:0 2px 8px rgba(52,87,255,0.25) !important;
  transition:all 0.15s !important; width:auto !important;
}
.stButton > button:hover { background:var(--blue-h) !important; transform:translateY(-1px) !important; box-shadow:0 4px 14px rgba(52,87,255,0.35) !important; }
.stButton > button:disabled { background:#C4C9D8 !important; box-shadow:none !important; transform:none !important; color:#fff !important; }
.stDownloadButton > button {
  background:#fff !important; color:var(--blue) !important;
  border:1.5px solid var(--blue) !important; border-radius:8px !important;
  font-weight:600 !important; font-size:0.82rem !important; box-shadow:none !important;
  padding:6px 16px !important; width:auto !important;
}
.stDownloadButton > button:hover { background:var(--blue-l) !important; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
  background:var(--card) !important; border-radius:12px 12px 0 0 !important;
  border-bottom:2px solid var(--border) !important; padding:0 !important; gap:0 !important;
}
.stTabs [data-baseweb="tab"] {
  background:transparent !important; border:none !important;
  color:var(--t2) !important; font-weight:500 !important; font-size:0.875rem !important;
  padding:12px 22px !important; border-radius:0 !important;
  font-family:'DM Sans',sans-serif !important;
}
.stTabs [data-baseweb="tab"]:hover { color:var(--blue) !important; }
.stTabs [aria-selected="true"] { color:var(--blue) !important; font-weight:600 !important; border-bottom:2px solid var(--blue) !important; }
.stTabs [data-baseweb="tab-panel"] { padding:0 !important; background:var(--card) !important; border-radius:0 0 12px 12px !important; }

/* ── DATAFRAME ── */
.stDataFrame { border-radius:10px !important; border:1px solid var(--border) !important; overflow:hidden !important; }
.stDataFrame thead tr th { background:#F8F9FD !important; color:var(--t1) !important; font-weight:600 !important; font-size:0.75rem !important; text-transform:uppercase; letter-spacing:0.05em; }

/* ── ALERTS ── */
.stAlert { border-radius:10px !important; font-size:0.875rem !important; }
.stWarning { background:#FFFBEB !important; border-left:3px solid var(--amber) !important; }
.stError   { background:#FEF2F2 !important; border-left:3px solid var(--red) !important; }
.stInfo    { background:var(--blue-l) !important; border-left:3px solid var(--blue) !important; }
.stSuccess { background:#F0FDF4 !important; border-left:3px solid var(--green) !important; }

/* ── EXPANDER ── */
.streamlit-expanderHeader { background:var(--card) !important; border:1px solid var(--border) !important; border-radius:8px !important; }

/* ── SPINNER ── */
.stSpinner > div { border-top-color:var(--blue) !important; }

/* ── HR ── */
hr { border-color:var(--border) !important; }

/* ════ CUSTOM COMPONENTS ════ */

/* KPI CARD */
.kpi { background:var(--card); border-radius:14px; padding:20px 22px; box-shadow:0 1px 3px rgba(0,0,0,0.05),0 0 0 1px rgba(0,0,0,0.03); }
.kpi.blue { background:var(--blue); }
.kpi-label { font-size:0.68rem; font-weight:700; color:var(--t3); text-transform:uppercase; letter-spacing:0.1em; margin-bottom:10px; }
.kpi.blue .kpi-label { color:rgba(255,255,255,0.6); }
.kpi-value { font-family:'Rajdhani',sans-serif !important; font-size:2.2rem; font-weight:700; color:var(--t1); line-height:1; }
.kpi.blue .kpi-value { color:#fff; }
.kpi-sub { font-size:0.75rem; color:var(--t3); margin-top:6px; }
.kpi.blue .kpi-sub { color:rgba(255,255,255,0.7); }

/* PAGE HEADER */
.ph { margin-bottom:24px; padding-bottom:20px; border-bottom:1px solid var(--border); }
.ph-title { font-family:'Rajdhani',sans-serif !important; font-size:1.9rem; font-weight:700; color:var(--t1); line-height:1; }
.ph-title b { color:var(--blue); font-weight:700; }
.ph-sub { font-size:0.82rem; color:var(--t2); margin-top:5px; }

/* FILTER CARD */
.fc { background:var(--card); border-radius:12px; padding:16px 20px; border:1px solid var(--border); margin-bottom:20px; box-shadow:0 1px 2px rgba(0,0,0,0.03); }
.fc-label { font-size:0.68rem; font-weight:700; color:var(--t3); text-transform:uppercase; letter-spacing:0.1em; margin-bottom:6px; display:block; }

/* RESULT CARD */
.rc { background:var(--card); border-radius:12px; padding:16px 20px; border:1px solid var(--border); margin-bottom:8px; transition:box-shadow 0.15s,border-color 0.15s; }
.rc:hover { box-shadow:0 4px 20px rgba(52,87,255,0.08); border-color:#C0CFFF; }
.rc-rank { display:inline-flex; align-items:center; justify-content:center; width:28px; height:28px; border-radius:8px; background:var(--blue-l); color:var(--blue); font-weight:700; font-size:0.78rem; flex-shrink:0; }
.rc-author { font-size:0.95rem; font-weight:600; color:var(--t1); }
.rc-desc { font-size:0.8rem; color:var(--t2); margin-top:2px; line-height:1.5; }
.rc-stat { font-family:'Rajdhani',sans-serif !important; font-size:1.35rem; font-weight:700; color:var(--t1); line-height:1; }
.rc-stat-lbl { font-size:0.68rem; color:var(--t3); font-weight:500; margin-top:2px; }

/* BADGE */
.bd { display:inline-block; padding:2px 8px; border-radius:20px; font-size:0.68rem; font-weight:600; margin-right:3px; margin-top:3px; }
.bd-blue  { background:var(--blue-l); color:var(--blue); }
.bd-gray  { background:#F1F3F9; color:var(--t2); }
.bd-green { background:#F0FDF4; color:#16A34A; }
.bd-amber { background:#FFFBEB; color:#B45309; }

/* SECTION CARD */
.sc { background:var(--card); border-radius:12px; padding:22px 24px; border:1px solid var(--border); margin-bottom:16px; box-shadow:0 1px 3px rgba(0,0,0,0.04); }
.sc-title { font-size:0.82rem; font-weight:700; color:var(--t1); margin-bottom:14px; text-transform:uppercase; letter-spacing:0.05em; }

/* INSIGHT PILL */
.ip { background:#F8F9FF; border:1px solid #DCE3FF; border-radius:10px; padding:14px 16px; margin-bottom:10px; }
.ip-label { font-size:0.68rem; font-weight:700; color:var(--t2); text-transform:uppercase; letter-spacing:0.08em; }
.ip-value { font-family:'Rajdhani',sans-serif !important; font-size:1.5rem; font-weight:700; color:var(--blue); margin-top:2px; }
.ip-desc  { font-size:0.75rem; color:var(--t2); margin-top:2px; }

/* STATUS */
.dot { display:inline-block; width:7px; height:7px; border-radius:50%; margin-right:6px; }
.dot-g { background:var(--green); }
.dot-r { background:var(--red); }
.dot-a { background:var(--t3); }

/* EMPTY STATE */
.es { text-align:center; padding:56px 24px; background:var(--card); border-radius:14px; border:1.5px dashed var(--border); }
.es-icon { font-size:2rem; color:#D1D5E8; margin-bottom:12px; }
.es-t { font-size:0.95rem; font-weight:600; color:var(--t2); margin-bottom:4px; }
.es-s { font-size:0.82rem; color:var(--t3); }

/* SIDEBAR NAV ICON */
.nav-icon { width:18px; height:18px; margin-right:10px; opacity:0.6; display:inline-block; vertical-align:middle; }
[aria-checked="true"] .nav-icon { opacity:1; }
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTS ───────────────────────────────────────────────────────────────
PAISES = {
    "Chile":     {"hashtag":"chile",    "codigo":"CL","flag":"🇨🇱"},
    "Argentina": {"hashtag":"argentina","codigo":"AR","flag":"🇦🇷"},
    "México":    {"hashtag":"mexico",   "codigo":"MX","flag":"🇲🇽"},
    "Colombia":  {"hashtag":"colombia", "codigo":"CO","flag":"🇨🇴"},
    "Perú":      {"hashtag":"peru",     "codigo":"PE","flag":"🇵🇪"},
    "Venezuela": {"hashtag":"venezuela","codigo":"VE","flag":"🇻🇪"},
    "Uruguay":   {"hashtag":"uruguay",  "codigo":"UY","flag":"🇺🇾"},
}
PAISES_OPTS = [f"{v['flag']} {k}" for k,v in PAISES.items()]
def pais_key(disp): return disp.split(" ",1)[1]

CATS = {
    "Negocios":           ["negocios","business","emprendimiento"],
    "Emprendimiento":     ["emprendimiento","startup","emprender"],
    "Marketing Digital":  ["marketingdigital","marketing","ventas"],
    "Finanzas":           ["finanzaspersonales","inversion","dinero"],
    "Tecnología":         ["tecnologia","tech","ia"],
    "Productividad":      ["productividad","freelance","trabajoremoto"],
    "Desarrollo Personal":["desarrollopersonal","motivacion","exito"],
    "Vida Corporativa":   ["corporativo","liderazgo","carrera"],
}

PL = dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
          font_color="#5A6380",title_font_color="#0F1629",font_family="DM Sans",
          title_font_size=13,margin=dict(l=0,r=0,t=32,b=0))

def fmt(n):
    if not n: return "0"
    if n>=1_000_000: return f"{n/1_000_000:.1f}M"
    if n>=1_000: return f"{n/1_000:.1f}K"
    return str(n)

def qq_tt(pk,cats):
    hp=PAISES[pk]["hashtag"]; q=[]
    for c in cats:
        for kw in CATS[c]: q.append(f"#{kw}{hp}"); q.append(f"#{kw}")
    q.append(f"trending {hp}")
    return list(dict.fromkeys(q))[:10]

def qq_ig(pk,cats):
    hp=PAISES[pk]["hashtag"]; t=[]
    for c in cats:
        for kw in CATS[c]: t.append(f"{kw}{hp}"); t.append(kw)
    return list(dict.fromkeys(t))[:8]

# ─── SESSION ─────────────────────────────────────────────────────────────────
for k in ["apify_token","trends_token","tt_df","tt_err","ig_df","ig_err",
          "au_df","au_err","au_src","cx_data","cx_err","cx_keyword","cx_growth","cx_debug"]:
    if k not in st.session_state: st.session_state[k]=None

AT = st.session_state.apify_token or ""
TT = st.session_state.trends_token or ""

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown("""
    <div style="padding:28px 20px 20px;border-bottom:1px solid rgba(255,255,255,0.07);margin-bottom:4px">
        <div style="font-family:'Rajdhani',sans-serif;font-size:1.25rem;font-weight:700;color:#F1F5FF;letter-spacing:-0.01em">Social Trends</div>
        <div style="font-size:0.68rem;color:#3D4A6B;margin-top:3px;font-weight:500;text-transform:uppercase;letter-spacing:0.05em">Powered by TUU + Trends MCP</div>
    </div>
    """, unsafe_allow_html=True)

    # Nav section label
    st.markdown('<div style="font-size:0.65rem;font-weight:700;color:#2A3560;letter-spacing:0.12em;text-transform:uppercase;padding:14px 20px 6px">DASHBOARD</div>', unsafe_allow_html=True)

    NAV_ICONS = {
        "Dashboard":           "⊞",
        "TikTok Trends":       "▶",
        "Instagram Trends":    "◈",
        "Audio Trends":        "♪",
        "Tendencias Cruzadas": "⊕",
        "Ajustes":             "⚙",
    }

    nav = st.radio("nav", list(NAV_ICONS.keys()), label_visibility="collapsed",
                   format_func=lambda x: f"{NAV_ICONS[x]}  {x}")

    # Coming soon
    st.markdown("""
    <div style="border-top:1px solid rgba(255,255,255,0.05);margin:16px 12px 12px">
        <div style="font-size:0.65rem;font-weight:700;color:#2A3560;letter-spacing:0.12em;text-transform:uppercase;padding:14px 8px 6px">PRÓXIMAMENTE</div>
        <div style="display:flex;flex-direction:column;gap:2px">
            <div style="padding:8px 12px;border-radius:8px;color:#2A3560;font-size:0.82rem;font-weight:500">⊟  Comparador de Marcas</div>
            <div style="padding:8px 12px;border-radius:8px;color:#2A3560;font-size:0.82rem;font-weight:500">⊡  Reportes</div>
            <div style="padding:8px 12px;border-radius:8px;color:#2A3560;font-size:0.82rem;font-weight:500">⊠  Historial</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div style="position:fixed;bottom:20px;left:0;width:220px;padding:0 20px">
        <div style="font-size:0.68rem;color:#2A3560;font-weight:500">v1.0 · Social Trends Platform</div>
    </div>
    """, unsafe_allow_html=True)

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def ph(title, accent, sub):
    return f'<div class="ph"><div class="ph-title">{title} <b>{accent}</b></div><div class="ph-sub">{sub}</div></div>'

def kpi_c(val, lbl, sub="", blue=False):
    cls = "kpi blue" if blue else "kpi"
    return f'<div class="{cls}"><div class="kpi-label">{lbl}</div><div class="kpi-value">{val}</div><div class="kpi-sub">{sub}</div></div>'

def empty(icon, title, sub):
    return f'<div class="es"><div class="es-icon">{icon}</div><div class="es-t">{title}</div><div class="es-s">{sub}</div></div>'

def no_token_msg():
    st.warning("Configura tu **Apify API Token** en **Ajustes → APIs** para continuar.")

# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if nav == "Dashboard":
    st.markdown(ph("Panel de", "Control", "Resumen de actividad y estado de la plataforma"), unsafe_allow_html=True)

    tt_df = st.session_state.tt_df
    ig_df = st.session_state.ig_df
    au_df = st.session_state.au_df

    tt_n = len(tt_df) if tt_df is not None and not tt_df.empty else 0
    ig_n = len(ig_df) if ig_df is not None and not ig_df.empty else 0
    au_n = len(au_df) if au_df is not None and not au_df.empty else 0
    ht_n = int(tt_df["hashtags"].str.count("#").sum()) if tt_df is not None and not tt_df.empty and "hashtags" in tt_df.columns else 0

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(kpi_c(tt_n,"TikTok Videos","Última búsqueda",blue=True), unsafe_allow_html=True)
    with c2: st.markdown(kpi_c(ig_n,"Instagram Posts","Última búsqueda"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_c(au_n,"Audios Únicos","Última búsqueda"), unsafe_allow_html=True)
    with c4: st.markdown(kpi_c(ht_n,"Hashtags","Desde TikTok"), unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    col_l, col_r = st.columns([3,2])

    with col_l:
        st.markdown('<div class="sc"><div class="sc-title">Actividad reciente</div>', unsafe_allow_html=True)
        if tt_n or ig_n or au_n:
            rows = []
            if tt_n: rows.append({"Módulo":"TikTok Trends","Resultados":tt_n,"Tipo":"Videos","Estado":"✓"})
            if ig_n: rows.append({"Módulo":"Instagram Trends","Resultados":ig_n,"Tipo":"Posts","Estado":"✓"})
            if au_n: rows.append({"Módulo":"Audio Trends","Resultados":au_n,"Tipo":"Audios","Estado":"✓"})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.markdown('<div style="color:#9BA3BE;font-size:0.85rem;padding:16px 0">No hay búsquedas recientes. Selecciona un módulo del sidebar para comenzar.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="sc"><div class="sc-title">Estado de conexiones</div>', unsafe_allow_html=True)
        a_ok = bool(AT); t_ok = bool(TT)
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;gap:10px">
            <div style="display:flex;align-items:center;justify-content:space-between;padding:12px 14px;background:#F8F9FD;border-radius:8px;border:1px solid var(--border)">
                <div><span class="dot {'dot-g' if a_ok else 'dot-r'}"></span><span style="font-weight:600;font-size:0.875rem;color:var(--t1)">Apify</span></div>
                <span style="font-size:0.75rem;font-weight:600;color:{'#22C55E' if a_ok else '#EF4444'}">{('Activo' if a_ok else 'Sin token')}</span>
            </div>
            <div style="display:flex;align-items:center;justify-content:space-between;padding:12px 14px;background:#F8F9FD;border-radius:8px;border:1px solid var(--border)">
                <div><span class="dot {'dot-g' if t_ok else 'dot-a'}"></span><span style="font-weight:600;font-size:0.875rem;color:var(--t1)">TrendsMCP</span></div>
                <span style="font-size:0.75rem;font-weight:600;color:{'#22C55E' if t_ok else '#9BA3BE'}">{('Activo' if t_ok else 'Sin token')}</span>
            </div>
        </div>
        <div style="margin-top:14px;font-size:0.78rem;color:var(--t3)">Gestiona los tokens en <strong style="color:var(--blue)">Ajustes → APIs</strong></div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Chart si hay data
    if tt_df is not None and not tt_df.empty and "plays" in tt_df.columns:
        st.markdown('<div class="sc"><div class="sc-title">Top TikTok · Reproducciones</div>', unsafe_allow_html=True)
        fig = px.bar(tt_df.head(10), x="plays", y="nickname", orientation="h",
                     color="plays", color_continuous_scale=["#EEF3FF","#3457FF"],
                     labels={"plays":"","nickname":""})
        fig.update_layout(**PL, coloraxis_showscale=False, yaxis=dict(autorange="reversed"), height=280)
        fig.update_xaxes(gridcolor="#F4F6FB", showline=False)
        fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TIKTOK TRENDS
# ══════════════════════════════════════════════════════════════════════════════
elif nav == "TikTok Trends":
    st.markdown(ph("TikTok","Trends","Analiza videos virales por país y categoría · Powered by Apify"), unsafe_allow_html=True)

    if not AT:
        no_token_msg()
    else:
        # ── FILTER BAR ──
        st.markdown('<div class="fc">', unsafe_allow_html=True)
        fc1,fc2,fc3,fc4 = st.columns([2,3,2,1])
        with fc1:
            st.markdown('<span class="fc-label">País</span>', unsafe_allow_html=True)
            pd_sel = st.selectbox("p",PAISES_OPTS,index=0,label_visibility="collapsed",key="tt_p")
            pk = pais_key(pd_sel)
        with fc2:
            st.markdown('<span class="fc-label">Categorías</span>', unsafe_allow_html=True)
            cats = st.multiselect("c",list(CATS.keys()),default=["Negocios","Emprendimiento"],label_visibility="collapsed",key="tt_c")
        with fc3:
            st.markdown('<span class="fc-label">Cantidad de videos</span>', unsafe_allow_html=True)
            n = st.slider("n",10,100,30,step=10,label_visibility="collapsed",key="tt_n")
        with fc4:
            st.markdown('<span class="fc-label">&nbsp;</span>', unsafe_allow_html=True)
            run = st.button("Buscar",key="tt_run",disabled=not cats)
        st.markdown('</div>', unsafe_allow_html=True)

        if run and cats:
            queries = qq_tt(pk,cats)
            url = f"https://api.apify.com/v2/acts/clockworks~free-tiktok-scraper/run-sync-get-dataset-items"
            payload = {"searchQueries":queries,"maxItems":n,"resultsPerPage":n,"shouldDownloadVideos":False,"shouldDownloadCovers":False}
            with st.spinner("Analizando TikTok..."):
                try:
                    r = requests.post(url,json=payload,params={"token":AT,"timeout":120},timeout=180)
                    r.raise_for_status()
                    rows=[]
                    for item in r.json():
                        a=item.get("authorMeta",{}) or {}; m=item.get("musicMeta",{}) or {}
                        rows.append({"nickname":"@"+a.get("nickName",""),"autor":a.get("name",""),
                            "likes":item.get("diggCount",0) or 0,"comentarios":item.get("commentCount",0) or 0,
                            "shares":item.get("shareCount",0) or 0,"plays":item.get("playCount",0) or 0,
                            "musica":m.get("musicName",""),
                            "hashtags":", ".join([f"#{h}" for h in (item.get("hashtags") or [])[:5]]),
                            "url":item.get("webVideoUrl",""),
                            "descripcion":(item.get("text","") or "")[:120],
                            "fecha":datetime.fromtimestamp(item.get("createTime",0)).strftime("%Y-%m-%d") if item.get("createTime") else ""})
                    df=pd.DataFrame(rows)
                    if not df.empty:
                        df=df.sort_values("plays",ascending=False).reset_index(drop=True); df.index+=1
                    st.session_state.tt_df=df; st.session_state.tt_err=None
                except Exception as e:
                    st.session_state.tt_err=str(e); st.session_state.tt_df=None

        if st.session_state.tt_err: st.error(f"Error: {st.session_state.tt_err}")

        df = st.session_state.tt_df
        if df is not None and not df.empty:
            eng = ((df["likes"]+df["comentarios"]+df["shares"])/df["plays"].replace(0,1)*100).mean()
            c1,c2,c3,c4 = st.columns(4)
            with c1: st.markdown(kpi_c(len(df),"Videos","Analizados",blue=True), unsafe_allow_html=True)
            with c2: st.markdown(kpi_c(fmt(df["plays"].sum()),"Reproducciones","Total"), unsafe_allow_html=True)
            with c3: st.markdown(kpi_c(fmt(df["likes"].sum()),"Likes","Acumulados"), unsafe_allow_html=True)
            with c4: st.markdown(kpi_c(f"{eng:.1f}%","Engagement","Promedio"), unsafe_allow_html=True)

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

            tab1,tab2,tab3 = st.tabs(["  Top Videos  ","  Analytics  ","  Tabla de datos  "])

            with tab1:
                st.markdown('<div style="padding:16px 0 0">', unsafe_allow_html=True)
                for i,row in df.head(10).iterrows():
                    tags=" ".join([f'<span class="bd bd-blue">{t.strip()}</span>' for t in row["hashtags"].split(",") if t.strip()])
                    lnk=f'<a href="{row["url"]}" target="_blank" style="font-size:0.75rem;color:var(--blue);text-decoration:none;margin-top:6px;display:inline-block">Ver en TikTok →</a>' if row["url"] else ""
                    st.markdown(f"""
                    <div class="rc">
                        <div style="display:flex;align-items:flex-start;gap:14px">
                            <span class="rc-rank">{i}</span>
                            <div style="flex:1;min-width:0">
                                <div class="rc-author">{row["nickname"]} <span style="color:var(--t2);font-weight:400;font-size:0.82rem">{row["autor"]}</span></div>
                                <div class="rc-desc">{row["descripcion"] or "—"}</div>
                                <div style="margin-top:6px">{tags}</div>
                                {lnk}
                            </div>
                            <div style="text-align:right;min-width:110px;flex-shrink:0">
                                <div class="rc-stat">{fmt(row["plays"])}</div>
                                <div class="rc-stat-lbl">reproducciones</div>
                                <div style="margin-top:8px;display:flex;flex-direction:column;gap:2px;align-items:flex-end">
                                    <span style="font-size:0.75rem;color:var(--t2)">{fmt(row["likes"])} likes</span>
                                    <span style="font-size:0.75rem;color:var(--t2)">{fmt(row["comentarios"])} comentarios</span>
                                    <span style="font-size:0.72rem;color:var(--t3)">{row["fecha"]}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with tab2:
                st.markdown('<div style="padding:16px 0 0">', unsafe_allow_html=True)
                ca,cb = st.columns(2)
                with ca:
                    st.markdown('<div class="sc"><div class="sc-title">Top 15 · Reproducciones</div>', unsafe_allow_html=True)
                    fig=px.bar(df.head(15),x="plays",y="nickname",orientation="h",
                               color="plays",color_continuous_scale=["#EEF3FF","#3457FF"],
                               labels={"plays":"","nickname":""})
                    fig.update_layout(**PL,coloraxis_showscale=False,yaxis=dict(autorange="reversed"),height=320)
                    fig.update_xaxes(gridcolor="#F4F6FB"); fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig,use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                with cb:
                    st.markdown('<div class="sc"><div class="sc-title">Músicas más usadas</div>', unsafe_allow_html=True)
                    mc=df["musica"].value_counts().head(6).reset_index(); mc.columns=["musica","count"]
                    fig2=px.pie(mc,values="count",names="musica",hole=0.58,
                                color_discrete_sequence=["#3457FF","#6A87FF","#99AAFF","#C0CFFF","#EEF3FF","#0F1629"])
                    fig2.update_layout(**PL,height=320); fig2.update_traces(textinfo="none")
                    st.plotly_chart(fig2,use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('<div class="sc"><div class="sc-title">Reproducciones vs Likes</div>', unsafe_allow_html=True)
                fig3=px.scatter(df,x="plays",y="likes",size="comentarios",color="shares",
                                hover_name="nickname",color_continuous_scale=["#EEF3FF","#3457FF"],
                                labels={"plays":"Reproducciones","likes":"Likes","shares":"Shares"})
                fig3.update_layout(**PL,coloraxis_showscale=False,height=300)
                fig3.update_xaxes(gridcolor="#F4F6FB"); fig3.update_yaxes(gridcolor="#F4F6FB")
                st.plotly_chart(fig3,use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with tab3:
                st.markdown('<div style="padding:16px 0 0">', unsafe_allow_html=True)
                show=["nickname","autor","plays","likes","comentarios","shares","musica","hashtags","fecha","url"]
                st.dataframe(df[[c for c in show if c in df.columns]],use_container_width=True,height=420,hide_index=False)
                st.download_button("Descargar CSV",df.to_csv(index=False).encode(),f"tiktok_{datetime.now().strftime('%Y%m%d')}.csv","text/csv")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(empty("▶","Configura los filtros y presiona Buscar","Los videos trending aparecerán aquí"), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  INSTAGRAM TRENDS
# ══════════════════════════════════════════════════════════════════════════════
elif nav == "Instagram Trends":
    st.markdown(ph("Instagram","Trends","Posts y Reels virales por hashtag · Powered by Apify"), unsafe_allow_html=True)

    if not AT:
        no_token_msg()
    else:
        st.markdown('<div class="fc">', unsafe_allow_html=True)
        fc1,fc2,fc3,fc4,fc5 = st.columns([2,3,2,2,1])
        with fc1:
            st.markdown('<span class="fc-label">País</span>', unsafe_allow_html=True)
            pd_sel=st.selectbox("p",PAISES_OPTS,index=0,label_visibility="collapsed",key="ig_p")
            pk=pais_key(pd_sel)
        with fc2:
            st.markdown('<span class="fc-label">Categorías</span>', unsafe_allow_html=True)
            cats=st.multiselect("c",list(CATS.keys()),default=["Negocios","Emprendimiento"],label_visibility="collapsed",key="ig_c")
        with fc3:
            st.markdown('<span class="fc-label">Tipo de contenido</span>', unsafe_allow_html=True)
            tipos=st.multiselect("t",["Reel","Imagen","Carousel"],default=["Reel","Imagen","Carousel"],label_visibility="collapsed",key="ig_t")
        with fc4:
            st.markdown('<span class="fc-label">Cantidad</span>', unsafe_allow_html=True)
            n=st.slider("n",10,100,30,step=10,label_visibility="collapsed",key="ig_n")
        with fc5:
            st.markdown('<span class="fc-label">&nbsp;</span>', unsafe_allow_html=True)
            run=st.button("Buscar",key="ig_run",disabled=not cats)
        st.markdown('</div>', unsafe_allow_html=True)

        if run and cats:
            hashtags=qq_ig(pk,cats)
            url=f"https://api.apify.com/v2/acts/apify~instagram-hashtag-scraper/run-sync-get-dataset-items"
            with st.spinner("Analizando Instagram..."):
                try:
                    r=requests.post(url,json={"hashtags":hashtags,"resultsLimit":n,"proxy":{"useApifyProxy":True}},
                                    params={"token":AT,"timeout":120},timeout=180)
                    r.raise_for_status(); rows=[]
                    for item in r.json():
                        owner=item.get("ownerUsername","") or (item.get("owner",{}) or {}).get("username","")
                        tr=item.get("type","") or ""
                        tipo="Reel" if ("reel" in tr.lower() or item.get("isVideo",False)) else ("Carousel" if (item.get("mediaCount",1)>1 or "sidecar" in tr.lower()) else "Imagen")
                        cap=str(item.get("caption","") or "")[:140]
                        rows.append({"autor":"@"+owner,"tipo":tipo,
                            "likes":item.get("likesCount",0) or 0,"comentarios":item.get("commentsCount",0) or 0,
                            "views":item.get("videoViewCount",0) or 0,"caption":cap,
                            "hashtags":", ".join([f"#{t}" for t in re.findall(r"#(\w+)",cap)[:6]]),
                            "hashtag_src":"#"+(item.get("hashtag","") or ""),
                            "url":item.get("url","") or item.get("shortCode",""),
                            "fecha":(item.get("timestamp","") or "")[:10]})
                    df=pd.DataFrame(rows)
                    if not df.empty:
                        df["engagement"]=df["likes"]+df["comentarios"]
                        df=df.sort_values("engagement",ascending=False).reset_index(drop=True); df.index+=1
                    st.session_state.ig_df=df; st.session_state.ig_err=None
                except Exception as e:
                    st.session_state.ig_err=str(e); st.session_state.ig_df=None

        if st.session_state.ig_err: st.error(f"Error: {st.session_state.ig_err}")

        df=st.session_state.ig_df
        if df is not None and not df.empty:
            df_f=df[df["tipo"].isin(tipos)].copy() if tipos else df.copy()
            TCOLOR={"Reel":"#3457FF","Imagen":"var(--t1)","Carousel":"#6A87FF"}

            c1,c2,c3,c4=st.columns(4)
            with c1: st.markdown(kpi_c(len(df_f),"Posts","Analizados",blue=True),unsafe_allow_html=True)
            with c2: st.markdown(kpi_c(fmt(df_f["likes"].sum()),"Likes","Acumulados"),unsafe_allow_html=True)
            with c3: st.markdown(kpi_c(fmt(df_f["engagement"].sum()),"Engagement","Total"),unsafe_allow_html=True)
            with c4: st.markdown(kpi_c(fmt(df_f["views"].sum()),"Vistas","Reels"),unsafe_allow_html=True)

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

            tab1,tab2,tab3,tab4=st.tabs(["  Top Posts  ","  Analytics  ","  Insights  ","  Tabla  "])

            with tab1:
                st.markdown('<div style="padding:16px 0 0">', unsafe_allow_html=True)
                for i,row in df_f.head(10).iterrows():
                    TBADGE={"Reel":"bd-blue","Imagen":"bd-gray","Carousel":"bd-blue"}
                    tb=TBADGE.get(row["tipo"],"bd-gray")
                    tags=" ".join([f'<span class="bd bd-blue">{t.strip()}</span>' for t in row["hashtags"].split(",") if t.strip()])
                    lnk=row["url"] if row["url"].startswith("http") else f"https://www.instagram.com/p/{row['url']}"
                    vw=f'<span style="font-size:0.75rem;color:var(--t2)">{fmt(row["views"])} views</span>' if row["views"]>0 else ""
                    st.markdown(f"""
                    <div class="rc">
                        <div style="display:flex;align-items:flex-start;gap:14px">
                            <span class="rc-rank">{i}</span>
                            <div style="flex:1;min-width:0">
                                <div class="rc-author">{row["autor"]} <span class="bd {tb}">{row["tipo"]}</span></div>
                                <div class="rc-desc">{row["caption"] or "—"}</div>
                                <div style="margin-top:6px">{tags}</div>
                                <a href="{lnk}" target="_blank" style="font-size:0.75rem;color:var(--blue);text-decoration:none;margin-top:6px;display:inline-block">Ver en Instagram →</a>
                            </div>
                            <div style="text-align:right;min-width:110px;flex-shrink:0">
                                <div class="rc-stat">{fmt(row["engagement"])}</div>
                                <div class="rc-stat-lbl">engagement</div>
                                <div style="margin-top:6px;display:flex;flex-direction:column;gap:2px;align-items:flex-end">
                                    <span style="font-size:0.75rem;color:var(--t2)">{fmt(row["likes"])} likes</span>
                                    <span style="font-size:0.75rem;color:var(--t2)">{fmt(row["comentarios"])} com.</span>
                                    {vw}
                                    <span style="font-size:0.72rem;color:var(--t3)">{row["fecha"]}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with tab2:
                st.markdown('<div style="padding:16px 0 0">', unsafe_allow_html=True)
                ca,cb=st.columns(2)
                with ca:
                    st.markdown('<div class="sc"><div class="sc-title">Top 15 · Engagement</div>',unsafe_allow_html=True)
                    fig=px.bar(df_f.head(15),x="engagement",y="autor",orientation="h",color="engagement",
                               color_continuous_scale=["#EEF3FF","#3457FF"],labels={"engagement":"","autor":""})
                    fig.update_layout(**PL,coloraxis_showscale=False,yaxis=dict(autorange="reversed"),height=320)
                    fig.update_xaxes(gridcolor="#F4F6FB"); fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig,use_container_width=True)
                    st.markdown('</div>',unsafe_allow_html=True)
                with cb:
                    st.markdown('<div class="sc"><div class="sc-title">Distribución por tipo</div>',unsafe_allow_html=True)
                    tc=df_f["tipo"].value_counts().reset_index(); tc.columns=["tipo","count"]
                    fig2=px.pie(tc,values="count",names="tipo",hole=0.58,
                                color_discrete_map={"Reel":"#3457FF","Imagen":"#0F1629","Carousel":"#6A87FF"})
                    fig2.update_layout(**PL,height=320); fig2.update_traces(textinfo="none")
                    st.plotly_chart(fig2,use_container_width=True)
                    st.markdown('</div>',unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with tab3:
                st.markdown('<div style="padding:16px 0 0">', unsafe_allow_html=True)
                ca,cb=st.columns(2)
                bg=df_f.groupby("tipo")["engagement"].mean(); ta=df_f.groupby("autor")["engagement"].sum()
                reels=df_f[df_f["tipo"]=="Reel"]["engagement"].mean() if "Reel" in df_f["tipo"].values else 0
                otros=df_f[df_f["tipo"]!="Reel"]["engagement"].mean() if len(df_f[df_f["tipo"]!="Reel"])>0 else 0
                ratio=df_f["likes"].sum()/max(df_f["comentarios"].sum(),1)
                with ca:
                    if not bg.empty:
                        bt,bv=bg.idxmax(),bg.max()
                        st.markdown(f'<div class="ip"><div class="ip-label">Mejor formato</div><div class="ip-value">{bt}</div><div class="ip-desc">Promedio {fmt(int(bv))} interacciones</div></div>',unsafe_allow_html=True)
                    st.markdown(f'<div class="ip"><div class="ip-label">Ratio Likes / Comentarios</div><div class="ip-value">{ratio:.0f}:1</div><div class="ip-desc">Por cada comentario hay {ratio:.0f} likes</div></div>',unsafe_allow_html=True)
                with cb:
                    if not ta.empty:
                        tav,tvv=ta.idxmax(),ta.max()
                        st.markdown(f'<div class="ip"><div class="ip-label">Cuenta con mayor engagement</div><div class="ip-value">{tav}</div><div class="ip-desc">{fmt(int(tvv))} eng. acumulado</div></div>',unsafe_allow_html=True)
                    if reels and otros:
                        diff=((reels-otros)/max(otros,1))*100
                        st.markdown(f'<div class="ip"><div class="ip-label">Reels vs otros formatos</div><div class="ip-value">{diff:+.0f}%</div><div class="ip-desc">Diferencia en engagement promedio</div></div>',unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with tab4:
                st.markdown('<div style="padding:16px 0 0">', unsafe_allow_html=True)
                show=["autor","tipo","likes","comentarios","views","engagement","hashtag_src","fecha","url"]
                st.dataframe(df_f[[c for c in show if c in df_f.columns]],use_container_width=True,height=420,hide_index=False)
                st.download_button("Descargar CSV",df_f.to_csv(index=False).encode(),f"instagram_{datetime.now().strftime('%Y%m%d')}.csv","text/csv")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(empty("◈","Configura los filtros y presiona Buscar","Los posts y reels aparecerán aquí"),unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  AUDIO TRENDS
# ══════════════════════════════════════════════════════════════════════════════
elif nav == "Audio Trends":
    st.markdown(ph("Audio","Trends","Sonidos virales en TikTok por país · Powered by Apify"), unsafe_allow_html=True)

    if not AT:
        no_token_msg()
    else:
        st.markdown('<div class="fc">', unsafe_allow_html=True)
        fc1,fc2,fc3,fc4=st.columns([2,2,2,1])
        with fc1:
            st.markdown('<span class="fc-label">País</span>', unsafe_allow_html=True)
            pd_sel=st.selectbox("p",PAISES_OPTS,index=0,label_visibility="collapsed",key="au_p")
            pk=pais_key(pd_sel); pi=PAISES[pk]; cc=pi["codigo"]
        with fc2:
            st.markdown('<span class="fc-label">Período</span>', unsafe_allow_html=True)
            periodo=st.selectbox("per",["7 días","30 días","120 días"],label_visibility="collapsed",key="au_per")
            pval={"7 días":7,"30 días":30,"120 días":120}[periodo]
        with fc3:
            st.markdown('<span class="fc-label">Cantidad de sonidos</span>', unsafe_allow_html=True)
            n_a=st.slider("na",10,50,20,step=10,label_visibility="collapsed",key="au_n")
        with fc4:
            st.markdown('<span class="fc-label">&nbsp;</span>', unsafe_allow_html=True)
            run_a=st.button("Buscar",key="au_run")
        st.markdown('</div>', unsafe_allow_html=True)

        if run_a:
            with st.spinner("Buscando audios trending..."):
                df_au=None; src_lbl=""
                try:
                    r=requests.post(f"https://api.apify.com/v2/acts/alien_force~tiktok-trending-sounds-tracker/run-sync-get-dataset-items",
                                    json={"country_code":cc,"limit":n_a},params={"token":AT,"timeout":90},timeout=120)
                    r.raise_for_status(); raw=r.json()
                    if raw and any(x.get("title") or x.get("rank") for x in raw):
                        rows=[{"rank":item.get("rank") or i+1,
                               "titulo":item.get("title") or item.get("name","—"),
                               "artista":item.get("author") or item.get("authorName","—"),
                               "duracion":item.get("duration",0) or 0,
                               "usos":item.get("useCount") or item.get("videoCount") or 0,
                               "trend_7d":item.get("trend7") or 0,
                               "url_sound":item.get("playUrl") or item.get("link") or "",
                               "likes_total":0,"plays_total":0} for i,item in enumerate(raw)]
                        df_au=pd.DataFrame(rows); src_lbl="TikTok Creative Center (ranking oficial)"
                except Exception: pass
                if df_au is None or df_au.empty:
                    try:
                        hp=pi["hashtag"]
                        r2=requests.post(f"https://api.apify.com/v2/acts/clockworks~free-tiktok-scraper/run-sync-get-dataset-items",
                                         json={"searchQueries":[f"#{hp}",f"trending {hp}",f"#fyp{hp}",f"#foryou{hp}"],
                                               "maxItems":300,"resultsPerPage":300,"shouldDownloadVideos":False,"shouldDownloadCovers":False},
                                         params={"token":AT,"timeout":120},timeout=180)
                        r2.raise_for_status(); raw2=r2.json(); md={}
                        for item in raw2:
                            m=item.get("musicMeta") or {}; mid=m.get("musicId") or m.get("musicName","")
                            if not mid: continue
                            if mid not in md: md[mid]={"titulo":m.get("musicName","") or "Sonido original","artista":m.get("musicAuthor","") or "—","duracion":m.get("musicDuration",0) or 0,"url_sound":m.get("musicPlay","") or "","usos":0,"likes_total":0,"plays_total":0}
                            md[mid]["usos"]+=1; md[mid]["likes_total"]+=item.get("diggCount",0) or 0; md[mid]["plays_total"]+=item.get("playCount",0) or 0
                        rows2=[{"rank":r+1,"titulo":d["titulo"],"artista":d["artista"],"duracion":d["duracion"],"usos":d["usos"],"likes_total":d["likes_total"],"plays_total":d["plays_total"],"url_sound":d["url_sound"],"trend_7d":0} for r,(mid,d) in enumerate(sorted(md.items(),key=lambda x:x[1]["usos"],reverse=True))]
                        df_au=pd.DataFrame(rows2[:n_a]); src_lbl=f"Agregado de {len(raw2)} videos trending"
                    except Exception as e2:
                        st.session_state.au_err=str(e2); df_au=None
                st.session_state.au_df=df_au; st.session_state.au_src=src_lbl
                if df_au is not None: st.session_state.au_err=None

        if st.session_state.au_err: st.error(f"Error: {st.session_state.au_err}")

        df_au=st.session_state.au_df
        if df_au is not None and not df_au.empty:
            if st.session_state.au_src:
                st.markdown(f'<div style="font-size:0.72rem;color:var(--t3);margin-bottom:12px">Fuente: {st.session_state.au_src}</div>',unsafe_allow_html=True)

            c1,c2,c3,c4=st.columns(4)
            with c1: st.markdown(kpi_c(len(df_au),"Audios únicos","Analizados",blue=True),unsafe_allow_html=True)
            with c2: st.markdown(kpi_c(fmt(df_au["usos"].max() if "usos" in df_au.columns else 0),"Máx. videos","por audio"),unsafe_allow_html=True)
            with c3: st.markdown(kpi_c(fmt(df_au.get("likes_total",pd.Series([0])).max()),"Likes","del audio top"),unsafe_allow_html=True)
            with c4: st.markdown(kpi_c(f'{df_au["duracion"].mean():.0f}s',"Duración","promedio"),unsafe_allow_html=True)

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

            tab1,tab2,tab3=st.tabs(["  Ranking  ","  Analytics  ","  Tabla  "])

            with tab1:
                st.markdown('<div style="padding:16px 0 0">', unsafe_allow_html=True)
                for _,row in df_au.iterrows():
                    td=""
                    if row.get("trend_7d"):
                        s="▲" if row["trend_7d"]>0 else "▼"; c="#22C55E" if row["trend_7d"]>0 else "#EF4444"
                        td=f'<span style="color:{c};font-size:0.75rem;font-weight:600;margin-left:8px">{s} {abs(row["trend_7d"]):.0f}% 7d</span>'
                    lnk=f'<a href="{row["url_sound"]}" target="_blank" style="font-size:0.75rem;color:var(--blue);text-decoration:none;margin-top:4px;display:inline-block">Escuchar →</a>' if row.get("url_sound") else ""
                    st.markdown(f"""
                    <div class="rc">
                        <div style="display:flex;align-items:center;gap:14px">
                            <span class="rc-rank">{int(row["rank"])}</span>
                            <div style="flex:1">
                                <div class="rc-author">{row["titulo"]}</div>
                                <div class="rc-desc" style="margin-top:2px">{row["artista"]} · {row["duracion"]}s{td}</div>
                                {lnk}
                            </div>
                            <div style="text-align:right">
                                <div class="rc-stat">{fmt(row["usos"])}</div>
                                <div class="rc-stat-lbl">videos</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with tab2:
                st.markdown('<div style="padding:16px 0 0">', unsafe_allow_html=True)
                ca,cb=st.columns(2)
                with ca:
                    st.markdown('<div class="sc"><div class="sc-title">Top sonidos · Videos</div>',unsafe_allow_html=True)
                    fig=px.bar(df_au.head(15),x="usos",y="titulo",orientation="h",color="usos",
                               color_continuous_scale=["#EEF3FF","#3457FF"],labels={"usos":"","titulo":""})
                    fig.update_layout(**PL,coloraxis_showscale=False,yaxis=dict(autorange="reversed"),height=320)
                    fig.update_xaxes(gridcolor="#F4F6FB"); fig.update_yaxes(gridcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig,use_container_width=True)
                    st.markdown('</div>',unsafe_allow_html=True)
                with cb:
                    st.markdown('<div class="sc"><div class="sc-title">Distribución de duración (seg)</div>',unsafe_allow_html=True)
                    fig2=px.histogram(df_au,x="duracion",nbins=10,color_discrete_sequence=["#3457FF"],labels={"duracion":""})
                    fig2.update_layout(**PL,height=320)
                    fig2.update_xaxes(gridcolor="#F4F6FB"); fig2.update_yaxes(gridcolor="#F4F6FB")
                    st.plotly_chart(fig2,use_container_width=True)
                    st.markdown('</div>',unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with tab3:
                st.markdown('<div style="padding:16px 0 0">', unsafe_allow_html=True)
                show=["rank","titulo","artista","usos","likes_total","plays_total","duracion","url_sound"]
                st.dataframe(df_au[[c for c in show if c in df_au.columns]],use_container_width=True,height=420,hide_index=True)
                st.download_button("Descargar CSV",df_au.to_csv(index=False).encode(),f"audio_{cc}_{datetime.now().strftime('%Y%m%d')}.csv","text/csv")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(empty("♪","Configura los filtros y presiona Buscar","Los audios virales aparecerán aquí"),unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TENDENCIAS CRUZADAS
# ══════════════════════════════════════════════════════════════════════════════
elif nav == "Tendencias Cruzadas":
    st.markdown(ph("Tendencias","Cruzadas","Compara un keyword en múltiples plataformas · Powered by TrendsMCP"), unsafe_allow_html=True)

    if not TT:
        st.warning("Configura tu **TrendsMCP API Key** en **Ajustes → APIs** para continuar.")
        st.info("Obtén tu key gratis en **trendsmcp.ai** — 100 requests/mes sin tarjeta de crédito.")
    else:
        FUENTES={"Google Search":"google search","TikTok":"tiktok","YouTube":"youtube","Reddit":"reddit","Amazon":"amazon"}

        st.markdown('<div class="fc">', unsafe_allow_html=True)
        fc1,fc2,fc3,fc4=st.columns([3,2,2,1])
        with fc1:
            st.markdown('<span class="fc-label">Keyword</span>', unsafe_allow_html=True)
            kw=st.text_input("kw","",placeholder="emprendimiento, startup chile...",label_visibility="collapsed",key="cx_kw")
        with fc2:
            st.markdown('<span class="fc-label">Plataformas</span>', unsafe_allow_html=True)
            fuentes=st.multiselect("f",list(FUENTES.keys()),default=["Google Search","TikTok","YouTube","Reddit"],label_visibility="collapsed")
        with fc3:
            st.markdown('<span class="fc-label">Período histórico</span>', unsafe_allow_html=True)
            pcx=st.select_slider("pcx",["1M","3M","6M","12M","2Y","5Y"],value="12M",label_visibility="collapsed")
        with fc4:
            st.markdown('<span class="fc-label">&nbsp;</span>', unsafe_allow_html=True)
            run_cx=st.button("Analizar",key="cx_run",disabled=not kw or not fuentes)
        st.markdown('</div>', unsafe_allow_html=True)

        def fs(k,src,period):
            try:
                r=requests.post("https://api.trendsmcp.ai/api",
                    headers={"Authorization":f"Bearer {TT}","Content-Type":"application/json"},
                    json={"keyword":k,"source":src},timeout=20)
                if r.status_code==200:
                    d=r.json(); body=d.get("body") or d
                    if isinstance(body,str): body=_json.loads(body)
                    return body if isinstance(body,list) else (body.get("data") or body.get("results") or [])
            except Exception: pass
            return []

        def fg(k,src):
            try:
                r=requests.post("https://api.trendsmcp.ai/api",
                    headers={"Authorization":f"Bearer {TT}","Content-Type":"application/json"},
                    json={"keyword":k,"source":src,"type":"growth","percent_growth":["1M","3M","12M"]},timeout=15)
                if r.status_code==200:
                    d=r.json(); body=d.get("body") or d
                    if isinstance(body,str): body=_json.loads(body)
                    return body if isinstance(body,dict) else {}
            except Exception: pass
            return {}

        def ps(series):
            dates,values=[],[]
            for pt in series:
                if isinstance(pt,dict):
                    d=pt.get("date") or pt.get("week") or pt.get("timestamp","")
                    v=pt.get("value") or pt.get("interest") or pt.get("score") or 0
                elif isinstance(pt,(list,tuple)) and len(pt)>=2: d,v=pt[0],pt[1]
                else: continue
                dates.append(d); values.append(float(v) if v else 0)
            return dates,values

        if run_cx and kw and fuentes:
            with st.spinner(f"Comparando '{kw}' en {len(fuentes)} plataformas..."):
                all_s,all_g,errs,dbg={},{},{},{}
                for lbl in fuentes:
                    src=FUENTES[lbl]; s=fs(kw,src,pcx)
                    if s: all_s[lbl]=s
                    else: errs[lbl]=True
                    g=fg(kw,src)
                    if g: all_g[lbl]=g
                    dbg[lbl]={"series_len":len(s),"growth_keys":list(g.keys())}
                st.session_state.cx_data=all_s; st.session_state.cx_growth=all_g
                st.session_state.cx_keyword=kw
                st.session_state.cx_err=list(errs.keys()) if errs else None
                st.session_state.cx_debug=dbg

        if st.session_state.cx_err:
            st.warning(f"Sin datos para: {', '.join(st.session_state.cx_err)}")
            with st.expander("Debug — respuesta API"):
                st.json(st.session_state.cx_debug)

        cx_data=st.session_state.cx_data; cx_growth=st.session_state.cx_growth; ckw=st.session_state.cx_keyword
        COLORS=["#3457FF","#0F1629","#6A87FF","#99AAFF","#C0CFFF","#5A6380"]

        if cx_data and ckw:
            st.markdown(f'<div style="font-size:0.82rem;color:var(--t2);margin-bottom:16px">Resultados para: <strong style="color:var(--t1)">{ckw}</strong></div>',unsafe_allow_html=True)

            tab1,tab2,tab3=st.tabs(["  Series de tiempo  ","  Crecimiento  ","  Datos  "])

            with tab1:
                st.markdown('<div class="sc"><div class="sc-title">Interés normalizado (0–100) por plataforma</div>',unsafe_allow_html=True)
                fig=go.Figure(); avgs={}
                for idx,(lbl,series) in enumerate(cx_data.items()):
                    d,v=ps(series)
                    if d:
                        fig.add_trace(go.Scatter(x=d,y=v,name=lbl,line=dict(color=COLORS[idx%len(COLORS)],width=2.5),mode="lines"))
                        avgs[lbl]=sum(v)/max(len(v),1)
                fig.update_layout(**PL,height=320,
                    legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color="#5A6380"),orientation="h",yanchor="bottom",y=1.02),
                    yaxis=dict(range=[0,100],gridcolor="#F4F6FB"),xaxis=dict(gridcolor="#F4F6FB"),hovermode="x unified")
                st.plotly_chart(fig,use_container_width=True)
                if avgs:
                    top=max(avgs,key=avgs.get)
                    st.markdown(f'<div class="ip" style="margin-top:8px"><div class="ip-label">Plataforma con mayor tracción</div><div class="ip-value">{top}</div><div class="ip-desc">Interés promedio {avgs[top]:.0f}/100</div></div>',unsafe_allow_html=True)
                st.markdown('</div>',unsafe_allow_html=True)

            with tab2:
                if cx_growth:
                    rows_g=[]
                    for lbl,gdata in cx_growth.items():
                        for r in (gdata.get("results") or gdata.get("data") or []):
                            if isinstance(r,dict):
                                rows_g.append({"Plataforma":lbl,"Período":r.get("period","—"),"Crecimiento":r.get("growth") or r.get("value") or 0})
                    if rows_g:
                        st.markdown('<div class="sc"><div class="sc-title">Crecimiento por período</div>',unsafe_allow_html=True)
                        df_g=pd.DataFrame(rows_g)
                        try:
                            pivot=df_g.pivot(index="Plataforma",columns="Período",values="Crecimiento")
                            fig2=px.imshow(pivot,color_continuous_scale=["#EF4444","#F8F9FD","#3457FF"],aspect="auto",text_auto=".1f")
                            fig2.update_layout(**PL,height=280); st.plotly_chart(fig2,use_container_width=True)
                        except Exception: pass
                        periodos=df_g["Período"].unique().tolist()
                        if periodos:
                            p=st.selectbox("Período",periodos,key="cx_p")
                            df_p=df_g[df_g["Período"]==p].copy()
                            df_p["color"]=df_p["Crecimiento"].apply(lambda x:"Subiendo" if x>0 else "Bajando")
                            fig3=px.bar(df_p,x="Plataforma",y="Crecimiento",color="color",
                                color_discrete_map={"Subiendo":"#3457FF","Bajando":"#EF4444"},
                                labels={"Crecimiento":"% cambio"})
                            fig3.update_layout(**PL,showlegend=False,height=260); st.plotly_chart(fig3,use_container_width=True)
                        st.markdown('</div>',unsafe_allow_html=True)
                    else: st.info("Sin datos de crecimiento.")
                else: st.info("Sin datos de crecimiento. Prueba otro keyword.")

            with tab3:
                for lbl,series in cx_data.items():
                    with st.expander(f"{lbl} · {len(series)} puntos"):
                        d,v=ps(series)
                        if d:
                            df_r=pd.DataFrame({"fecha":d,"valor":v})
                            st.dataframe(df_r,use_container_width=True,height=200,hide_index=True)
                            st.download_button(f"CSV {lbl}",df_r.to_csv(index=False).encode(),f"cx_{ckw}_{lbl.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.csv","text/csv",key=f"dl_{lbl}")
        else:
            st.markdown(empty("⊕","Ingresa un keyword y presiona Analizar","Compara el interés en Google, TikTok, YouTube y Reddit en una sola vista"),unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  AJUSTES
# ══════════════════════════════════════════════════════════════════════════════
elif nav == "Ajustes":
    st.markdown(ph("Configuración de","APIs","Gestiona tokens y conexiones de la plataforma"), unsafe_allow_html=True)

    tab1,tab2=st.tabs(["  APIs  ","  General  "])

    with tab1:
        col1,col2=st.columns(2)
        with col1:
            st.markdown('<div class="sc">', unsafe_allow_html=True)
            st.markdown('<div class="sc-title">Apify</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size:0.82rem;color:var(--t2);margin-bottom:14px">Usado en TikTok Trends, Instagram Trends y Audio Trends</div>', unsafe_allow_html=True)
            a_ok=bool(AT)
            st.markdown(f'<div style="margin-bottom:12px"><span class="dot {"dot-g" if a_ok else "dot-r"}"></span><span style="font-size:0.82rem;font-weight:600;color:{"#22C55E" if a_ok else "#EF4444"}">{"Configurado" if a_ok else "Sin token"}</span></div>', unsafe_allow_html=True)
            new_at=st.text_input("Token Apify",value=AT,type="password",placeholder="apify_api_xxxxxxxxxxxx")
            if st.button("Guardar token Apify",key="save_at"):
                st.session_state.apify_token=new_at; AT=new_at; st.success("Token guardado")
            st.markdown('<div style="font-size:0.75rem;color:var(--t3);margin-top:10px">Obtén el token en <strong>apify.com → Settings → Integrations</strong></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="sc">', unsafe_allow_html=True)
            st.markdown('<div class="sc-title">TrendsMCP</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size:0.82rem;color:var(--t2);margin-bottom:14px">Usado en Tendencias Cruzadas — Google, TikTok, YouTube, Reddit</div>', unsafe_allow_html=True)
            t_ok=bool(TT)
            dot_t = "dot-g" if t_ok else "dot-a"
            color_t = "#22C55E" if t_ok else "#9BA3BE"
            label_t = "Configurado" if t_ok else "Sin token"
            st.markdown(f'<div style="margin-bottom:12px"><span class="dot {dot_t}"></span><span style="font-size:0.82rem;font-weight:600;color:{color_t}">{label_t}</span></div>', unsafe_allow_html=True)
            new_tt=st.text_input("API Key TrendsMCP",value=TT,type="password",placeholder="tmcp_xxxxxxxxxxxx")
            if st.button("Guardar token TrendsMCP",key="save_tt"):
                st.session_state.trends_token=new_tt; TT=new_tt; st.success("Token guardado")
            st.markdown('<div style="font-size:0.75rem;color:var(--t3);margin-top:10px">Gratis en <strong>trendsmcp.ai</strong> — 100 requests/mes sin tarjeta</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sc"><div class="sc-title">Próximas integraciones</div>', unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        for col,name,desc in [(c1,"OpenAI","Análisis semántico de trends"),(c2,"Slack","Alertas automáticas"),(c3,"Google Sheets","Exportar reportes")]:
            with col:
                st.markdown(f'<div style="border:1.5px dashed var(--border);border-radius:10px;padding:18px;text-align:center"><div style="font-weight:600;color:var(--t3);font-size:0.875rem">{name}</div><div style="font-size:0.75rem;color:#C4C9D8;margin-top:4px">{desc}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="sc"><div class="sc-title">Preferencias</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.82rem;color:var(--t2);margin-bottom:16px">Estas preferencias se guardan en esta sesión</div>', unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            st.selectbox("Idioma de la interfaz",["Español","English"])
        with c2:
            st.slider("Resultados por defecto",10,100,30,step=10)
        st.info("Las preferencias de país y categorías se configuran directamente en cada módulo.")
        st.markdown('</div>', unsafe_allow_html=True)
