import streamlit as st

def render_data_preview(df):
    with st.container():
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("📂 Preview of Data")
            st.dataframe(df.head(), height=200)
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("📌 Dataset Info")
            st.markdown(f"**Rows:** {df.shape[0]} | **Columns:** {df.shape[1]}")
            st.markdown("**Columns:**")
            st.markdown(f"<div class='scroll-box'>{'<br>'.join(df.columns)}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
