import streamlit as st

def render_sidebar(history):
    st.sidebar.title("⚡ BI Assistant")
    st.sidebar.write("Ask me questions about your data in **plain English**.")
    st.sidebar.markdown("---")
    theme_choice = st.sidebar.selectbox("🎨 Theme", ["Light", "Dark"])
    st.sidebar.info("Built with **Groq + Streamlit** by Aswin M")

    # Query history
    st.sidebar.markdown("### 🕑 Query History")
    if history:
        for i, item in enumerate(reversed(history), 1):
            st.sidebar.write(f"**Q{i}:** {item['q']}")
            st.sidebar.write(item['a'])

    return theme_choice
