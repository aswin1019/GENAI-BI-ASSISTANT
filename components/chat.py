import streamlit as st

def chat_bubble(role, content):
    css_class = "user-bubble" if role == "user" else "ai-bubble"
    st.markdown(f"<div class='chat-bubble {css_class}'>{content}</div>", unsafe_allow_html=True)
