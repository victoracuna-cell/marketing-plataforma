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
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding: 80px 20px;">
    <div style="font-size: 3.5rem; margin-bottom: 16px;">🚀</div>
    <div style="font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; font-weight: 700; color: #f0f0f5; margin-bottom: 12px;">
        Social Trends Platform
    </div>
    <div style="font-size: 1rem; color: #555; margin-bottom: 40px;">
        Análisis de tendencias en redes sociales para LATAM · Powered by Apify
    </div>
    <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
        <div style="background: rgba(254,44,85,0.08); border: 1px solid rgba(254,44,85,0.2); border-radius: 16px; padding: 28px 36px;">
            <div style="font-size: 2rem;">🎵</div>
            <div style="font-family: 'Space Grotesk', sans-serif; color: #f0f0f5; font-weight: 700; margin-top: 8px;">TikTok Trends</div>
            <div style="color: #555; font-size: 0.82rem; margin-top: 4px;">Módulo 1</div>
        </div>
        <div style="background: rgba(220,39,67,0.08); border: 1px solid rgba(220,39,67,0.2); border-radius: 16px; padding: 28px 36px;">
            <div style="font-size: 2rem;">📸</div>
            <div style="font-family: 'Space Grotesk', sans-serif; color: #f0f0f5; font-weight: 700; margin-top: 8px;">Instagram Trends</div>
            <div style="color: #555; font-size: 0.82rem; margin-top: 4px;">Módulo 2</div>
        </div>
    </div>
    <div style="margin-top: 40px; color: #333; font-size: 0.85rem;">
        Usa el menú de la izquierda para navegar entre módulos ←
    </div>
</div>
""", unsafe_allow_html=True)
