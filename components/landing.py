import streamlit as st

def render_landing():
    st.markdown("""
    <div style="text-align: center; padding: 60px 0;
        background: linear-gradient(120deg, #0072ff, #00c6ff);
        border-radius: 12px; margin-bottom: 25px;">
        <h1 style="color: white; font-size: 42px;">📊 Generative BI Assistant</h1>
        <p style="color: #f0f0f0; font-size: 18px; max-width: 600px; margin: 0 auto;">
            Chat with your data. Upload CSV/Excel and get instant insights & charts.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 Get Started"):
        return True
    return False
