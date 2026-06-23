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
    div[data-testid="stButton"] button {
        width: 100%;
        padding: 14px;
        border-radius: 12px;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1rem;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div style='padding-top: 60px;'></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; font-family:Space Grotesk; font-size:2.4rem; font-weight:700; color:#f0f0f5;'>🚀 Social Trends Platform</div>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center; color:#555; font-size:0.95rem; margin-bottom:48px;'>Análisis de tendencias en redes sociales para LATAM · Powered by Apify</div>", unsafe_allow_html=True)

col1, col_gap, col2 = st.columns([5, 1, 5])

with col1:
    st.markdown("""
    <div style="background: rgba(254,44,85,0.06); border: 1px solid rgba(254,44,85,0.2);
         border-radius: 16px; padding: 32px; text-align: center; margin-bottom: 16px;">
        <div style="font-size: 2.5rem; margin-bottom: 12px;">🎵</div>
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.2rem; font-weight: 700; color: #f0f0f5;">TikTok Trends</div>
        <div style="color: #555; font-size: 0.82rem; margin-top: 6px;">Módulo 1 · Videos virales por país y categoría</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("→ Ir a TikTok Trends", key="btn_tiktok"):
        st.switch_page("pages/1_TikTok_Trends.py")

with col2:
    st.markdown("""
    <div style="background: rgba(220,39,67,0.06); border: 1px solid rgba(188,24,136,0.2);
         border-radius: 16px; padding: 32px; text-align: center; margin-bottom: 16px;">
        <div style="font-size: 2.5rem; margin-bottom: 12px;">📸</div>
        <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.2rem; font-weight: 700; color: #f0f0f5;">Instagram Trends</div>
        <div style="color: #555; font-size: 0.82rem; margin-top: 6px;">Módulo 2 · Posts y Reels por hashtag</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("→ Ir a Instagram Trends", key="btn_instagram"):
        st.switch_page("pages/2_Instagram_Trends.py")

st.markdown("<div style='text-align:center; margin-top: 48px; color: #2a2a3a; font-size: 0.8rem;'>v1.0 · Social Trends Platform</div>", unsafe_allow_html=True)
