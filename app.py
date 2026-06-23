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
    .nav-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #f0f0f5;
        margin-bottom: 4px;
    }
    .nav-sub { font-size: 0.75rem; color: #444; margin-bottom: 20px; }
    .stRadio > label { color: #888 !important; font-size: 0.8rem; }
    .stRadio [data-testid="stMarkdownContainer"] p { color: #f0f0f5 !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="nav-title">🚀 Social Trends</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-sub">Plataforma de análisis LATAM</div>', unsafe_allow_html=True)
    st.markdown("---")
    modulo = st.radio(
        "Módulo",
        options=["🎵 TikTok Trends", "📸 Instagram Trends"],
        index=0,
    )
    st.markdown("---")
    st.markdown("<span style='color:#333; font-size:0.7rem;'>v1.0 · Powered by Apify</span>", unsafe_allow_html=True)

if modulo == "🎵 TikTok Trends":
    exec(open("tiktok_trends.py").read())
else:
    exec(open("instagram_trends.py").read())
