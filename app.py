import streamlit as st

st.set_page_config(
    page_title="Social Trends Platform",
    page_icon="🚀",
    layout="wide",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=Inter:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0a0a0f 0%, #12121f 100%); }
    section[data-testid="stSidebar"] { background: #0d0d1a; border-right: 1px solid rgba(255,255,255,0.06); }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; color: #f0f0f5; }

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.4rem;
        font-weight: 700;
        color: #f0f0f5;
        text-align: center;
        margin-bottom: 8px;
    }
    .hero-sub {
        color: #555;
        font-size: 0.95rem;
        text-align: center;
        margin-bottom: 48px;
    }

    /* Ocultar label de page_link y estilizar el botón */
    .stPageLink a {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 16px !important;
        padding: 32px 24px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        text-decoration: none !important;
        transition: border-color 0.2s, background 0.2s !important;
        height: 100% !important;
    }
    .stPageLink a:hover {
        border-color: rgba(254,44,85,0.5) !important;
        background: rgba(254,44,85,0.06) !important;
    }
    .stPageLink p {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        color: #f0f0f5 !important;
        font-size: 1.1rem !important;
        margin: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ── HEADER ──
st.markdown("<div style='padding-top: 60px;'></div>", unsafe_allow_html=True)
st.markdown("<div class='hero-title'>🚀 Social Trends Platform</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-sub'>Análisis de tendencias en redes sociales para LATAM · Powered by Apify</div>", unsafe_allow_html=True)

# ── CARDS CLICKEABLES ──
col1, col_gap, col2 = st.columns([5, 1, 5])

with col1:
    st.markdown("""
    <div style="background: rgba(254,44,85,0.06); border: 1px solid rgba(254,44,85,0.2);
         border-radius: 16px; padding: 32px; text-align: center; margin-bottom: 8px;">
        <div style="font-size: 2.5rem; margin-bottom: 12px;">🎵</div>
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.2rem; font-weight: 700; color: #f0f0f5;">TikTok Trends</div>
        <div style="color: #555; font-size: 0.82rem; margin-top: 6px;">Módulo 1 · Videos virales por país y categoría</div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_TikTok_Trends.py", label="→ Ir a TikTok Trends", icon="🎵")

with col2:
    st.markdown("""
    <div style="background: rgba(220,39,67,0.06); border: 1px solid rgba(188,24,136,0.2);
         border-radius: 16px; padding: 32px; text-align: center; margin-bottom: 8px;">
        <div style="font-size: 2.5rem; margin-bottom: 12px;">📸</div>
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.2rem; font-weight: 700; color: #f0f0f5;">Instagram Trends</div>
        <div style="color: #555; font-size: 0.82rem; margin-top: 6px;">Módulo 2 · Posts y Reels por hashtag</div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/2_Instagram_Trends.py", label="→ Ir a Instagram Trends", icon="📸")

st.markdown("<div style='text-align:center; margin-top: 48px; color: #2a2a3a; font-size: 0.8rem;'>v1.0 · Social Trends Platform</div>", unsafe_allow_html=True)
