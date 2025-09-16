import os
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# Load API key
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Streamlit page config
st.set_page_config(
    page_title="Generative BI Assistant",
    page_icon="📊",
    layout="wide"
)

# ---- Initialize session state ----
if "history" not in st.session_state:
    st.session_state["history"] = []
if "started" not in st.session_state:
    st.session_state["started"] = False

# Sidebar
st.sidebar.title("⚡ BI Assistant")
st.sidebar.write("Ask me questions about your data in **plain English**.")
st.sidebar.markdown("---")
theme_choice = st.sidebar.selectbox("🎨 Theme", ["Light", "Dark"])
st.sidebar.info("Built with **Groq + Streamlit** by Aswin M")

# Query History in Sidebar
st.sidebar.markdown("### 🕑 Query History")
if st.session_state["history"]:
    for i, item in enumerate(reversed(st.session_state["history"]), 1):
        st.sidebar.write(f"**Q{i}:** {item['q']}")
        st.sidebar.write(item['a'])

# ---- Theme Styling + Matplotlib Style ----
if theme_choice == "Light":
    plt.style.use("default")
    st.markdown("""
        <style>
        body { background: linear-gradient(to right, #f7f9fc, #eef3f7); }
        .main { background: transparent; }
        .stApp { background-color: #f5f7fa; }
        .card {
            background: white; padding: 20px; border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.08); margin: 20px 0;
        }
        .scroll-box {
            max-height: 200px; overflow-y: auto; padding: 10px;
            border: 1px solid #ddd; border-radius: 8px;
            background-color: #fafafa;
        }
        .chat-bubble { padding: 12px 16px; border-radius: 16px;
            margin: 10px 0; max-width: 75%; font-size: 15px; line-height: 1.4; }
        .user-bubble { background: #00796b; color: white;
            margin-left: auto; text-align: right; }
        .ai-bubble { background: #f1f3f4; color: #222;
            margin-right: auto; text-align: left; }
        .stButton button {
            background: linear-gradient(to right, #0072ff, #00c6ff); color: white;
            border: none; padding: 10px 20px; border-radius: 8px;
            font-size: 16px; font-weight: bold; cursor: pointer;
            transition: 0.3s ease;
        }
        .stButton button:hover {
            background: linear-gradient(to right, #0059b3, #00a6c7);
        }
        footer { text-align: center; color: #555; font-size: 14px; margin-top: 40px; }
        footer a { color: #0072ff; text-decoration: none; margin: 0 5px; }
        footer a:hover { text-decoration: underline; }
        </style>
    """, unsafe_allow_html=True)
else:  # Dark Theme
    plt.style.use("dark_background")
    st.markdown("""
        <style>
        body { background: #121212; color: #e0e0e0; }
        .main { background: transparent; }
        .stApp { background-color: #181818; }
        .card {
            background: #1f1f1f; padding: 20px; border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5); margin: 20px 0; color: #eee;
        }
        .scroll-box {
            max-height: 200px; overflow-y: auto; padding: 10px;
            border: 1px solid #444; border-radius: 8px;
            background-color: #2a2a2a; color: #f5f5f5;
        }
        h1, h2, h3, h4, h5, h6, label, p, span {
            color: #f5f5f5 !important;
        }
        .stRadio div[role="radiogroup"] label {
            color: #f5f5f5 !important;
            font-weight: 600 !important;
            font-size: 15px !important;
        }
        .chat-bubble { padding: 12px 16px; border-radius: 16px;
            margin: 10px 0; max-width: 75%; font-size: 15px; line-height: 1.4; }
        .user-bubble { background: #00bfa5; color: white;
            margin-left: auto; text-align: right; }
        .ai-bubble { background: #333333; color: #f1f1f1;
            margin-right: auto; text-align: left; }
        .stButton button {
            background: linear-gradient(to right, #00c6ff, #0072ff); color: white;
            border: none; padding: 10px 20px; border-radius: 8px;
            font-size: 16px; font-weight: bold; cursor: pointer;
            transition: 0.3s ease;
        }
        .stButton button:hover {
            background: linear-gradient(to right, #00a6c7, #0059b3);
        }
        footer { text-align: center; color: #aaa; font-size: 14px; margin-top: 40px; }
        footer a { color: #00c6ff; text-decoration: none; margin: 0 5px; }
        footer a:hover { text-decoration: underline; }
        </style>
    """, unsafe_allow_html=True)

# ---- Helper: Chat bubbles ----
def chat_bubble(role, content):
    css_class = "user-bubble" if role == "user" else "ai-bubble"
    st.markdown(f"<div class='chat-bubble {css_class}'>{content}</div>", unsafe_allow_html=True)

# ---- Landing Page ----
if not st.session_state["started"]:
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
        st.session_state["started"] = True
        st.rerun()
else:
    # ---- File Upload OR Sample ----
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 📂 Choose Your Data")
    data_option = st.radio(
        "Select how you want to start:",
        ("📊 Use Sample Superstore Data", "⬆️ Upload My Own CSV")
    )

    df = None
    if data_option == "📊 Use Sample Superstore Data":
        df = pd.read_csv("superstore.csv", encoding="latin1")
        st.success("Loaded sample dataset: Superstore 📦")
    elif data_option == "⬆️ Upload My Own CSV":
        file = st.file_uploader("Upload your CSV file", type=["csv"])
        if file:
            df = pd.read_csv(file, encoding="latin1")
            st.success(f"✅ Your dataset **{file.name}** has been uploaded successfully!")
    st.markdown("</div>", unsafe_allow_html=True)

    # ---- Main Logic ----
    if df is not None:
        # Cleaning
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].mean())
            else:
                df[col] = df[col].fillna("Unknown")

        for col in df.columns:
            if "date" in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                except:
                    pass

        # Preview
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

        # Chat Section
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("💬 Chat with your Data")
        query = st.text_input("Ask a question:")

        if st.button("Ask AI 🚀"):
            if query.strip():
                chat_bubble("user", query)

                prompt = f"""
                You are a Python data analyst.
                The dataframe is called df and has these columns: {list(df.columns)}.

                RULES:
                - Only return Python code (no explanations, no text).
                - Always assign the final output to a variable called result.
                - Never use print() or display().
                Example:
                    result = df['Profit'].sum()
                Question: "{query}"
                """

                with st.spinner("🤖 Thinking..."):
                    time.sleep(1)
                    chat_completion = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt}]
                    )

                code_answer = chat_completion.choices[0].message.content.strip()
                if "```" in code_answer:
                    code_answer = "".join([p for p in code_answer.split("```") if not p.strip().startswith("python")])

                if "result" not in code_answer:
                    lines = code_answer.strip().split("\n")
                    if lines and lines[-1].strip():
                        lines[-1] = f"result = {lines[-1]}"
                        code_answer = "\n".join(lines)

                try:
                    local_vars = {}
                    exec(code_answer, {"df": df, "pd": pd, "np": np}, local_vars)

                    if "result" in local_vars:
                        result = local_vars["result"]
                        st.session_state["history"].append({"q": query, "a": str(result)})
                        if len(st.session_state["history"]) > 5:
                            st.session_state["history"].pop(0)

                        chat_bubble("assistant", "Here are your results:")

                        if isinstance(result, pd.DataFrame):
                            st.dataframe(result, height=250)

                            if result.shape[1] >= 2:
                                st.subheader("📊 Visualization")
                                fig, ax = plt.subplots()
                                result.plot(ax=ax)
                                st.pyplot(fig)

                            csv = result.to_csv(index=False).encode("utf-8")
                            st.download_button("⬇️ Download CSV", csv, "result.csv", "text/csv")
                        else:
                            st.write(result)
                    else:
                        chat_bubble("assistant", "⚠️ AI did not return a valid result.")
                except Exception as e:
                    chat_bubble("assistant", f"❌ Error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

# ---- Footer ----
st.markdown("""
<footer>
    <p>Built by <b>Aswin M</b> | Powered by <b>Groq + Streamlit</b></p>
    <p>
        <a href="https://github.com/aswin1019" target="_blank">GitHub</a> |
        <a href="https://www.linkedin.com/in/aswin-m-53aa001a8" target="_blank">LinkedIn</a>
    </p>
</footer>
""", unsafe_allow_html=True)
