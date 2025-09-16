import os
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from dotenv import load_dotenv
from utils.groq_client import client
from utils.theme import load_light_theme, load_dark_theme
from utils.helpers import clean_dataframe
from components.chat import chat_bubble
from components.sidebar import render_sidebar
from components.landing import render_landing
from components.data_preview import render_data_preview

# Streamlit config
st.set_page_config(page_title="Generative BI Assistant", page_icon="📊", layout="wide")

# ---- Init session state ----
if "history" not in st.session_state:
    st.session_state["history"] = []
if "started" not in st.session_state:
    st.session_state["started"] = False

# Sidebar
theme_choice = render_sidebar(st.session_state["history"])

# Load theme
if theme_choice == "Light":
    st.markdown(load_light_theme(), unsafe_allow_html=True)
    plt.style.use("default")
else:
    st.markdown(load_dark_theme(), unsafe_allow_html=True)
    plt.style.use("dark_background")

# Landing Page
if not st.session_state["started"]:
    if render_landing():
        st.session_state["started"] = True
        st.rerun()
else:
    # File Upload / Sample
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 📂 Choose Your Data")
    data_option = st.radio("Select how you want to start:", ("📊 Use Sample Superstore Data", "⬆️ Upload My Own CSV"))

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

    # Main Logic
    if df is not None:
        df = clean_dataframe(df)

        # Preview + Dataset Info
        render_data_preview(df)

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

# Footer
st.markdown("""
<footer>
    <p>Built by <b>Aswin M</b> | Powered by <b>Groq + Streamlit</b></p>
    <p>
        <a href="https://github.com/aswin1019" target="_blank">GitHub</a> |
        <a href="https://www.linkedin.com/in/aswin-m-53aa001a8" target="_blank">LinkedIn</a>
    </p>
</footer>
""", unsafe_allow_html=True)
