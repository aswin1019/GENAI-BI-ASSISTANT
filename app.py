import os
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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

# ---- Styling ----
st.markdown("""
    <style>
    .chat-bubble {
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        max-width: 75%;
    }
    .user-bubble {
        background-color: #DCF8C6;
        margin-left: auto;
    }
    .ai-bubble {
        background-color: #E6E6E6;
        margin-right: auto;
    }
    .card {
        background: white;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        margin: 16px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ---- Helpers ----
def chat_bubble(role, content):
    css_class = "user-bubble" if role == "user" else "ai-bubble"
    st.markdown(f"<div class='chat-bubble {css_class}'>{content}</div>", unsafe_allow_html=True)

# Duration Cleaner
def clean_duration(df):
    if "duration" in df.columns:
        df["duration_num"] = (
            df["duration"].astype(str)
            .str.extract(r"(\d+)")
            .astype(float)
        )
        df["duration_unit"] = df["duration"].astype(str).apply(
            lambda x: "Season" if "Season" in x else "Minute"
        )
    return df

# Add Decade Column
def add_decade(df):
    if "release_year" in df.columns:
        df["decade"] = (df["release_year"] // 10) * 10
    return df

# Heatmap Plotter
def make_heatmap(df, col1, col2):
    import seaborn as sns
    pivot = pd.crosstab(df[col1], df[col2])
    fig, ax = plt.subplots(figsize=(8,6))
    sns.heatmap(pivot, annot=True, fmt="d", cmap="Blues", ax=ax)
    st.pyplot(fig)

# Auto Plot
def auto_plot(result, query):
    fig, ax = plt.subplots()
    query_lower = query.lower()

    try:
        if "heatmap" in query_lower and result.shape[1] >= 2:
            make_heatmap(result, result.columns[0], result.columns[1])
        elif "trend" in query_lower or "over time" in query_lower or "monthly" in query_lower:
            result.plot(kind="line", x=result.columns[0], y=result.columns[1], ax=ax, marker="o")
            st.pyplot(fig)
        elif "share" in query_lower or "percentage" in query_lower:
            result.set_index(result.columns[0])[result.columns[1]].plot(kind="pie", autopct='%1.1f%%', ax=ax)
            ax.set_ylabel("")
            st.pyplot(fig)
        elif "distribution" in query_lower or "histogram" in query_lower:
            result[result.columns[1]].plot(kind="hist", bins=10, ax=ax)
            st.pyplot(fig)
        elif "scatter" in query_lower:
            if result.shape[1] >= 2:
                result.plot(kind="scatter", x=result.columns[0], y=result.columns[1], ax=ax)
                st.pyplot(fig)
        else:
            if result.shape[1] >= 2:
                result.plot(kind="bar", x=result.columns[0], y=result.columns[1], ax=ax)
                st.pyplot(fig)
    except Exception as e:
        st.warning(f"⚠️ Could not generate chart: {e}")

# ---- Sidebar ----
st.sidebar.title("⚡ BI Assistant")
st.sidebar.write("Ask me questions about your data in **plain English**.")
st.sidebar.markdown("---")
st.sidebar.info("Built with **Groq + Streamlit** by Aswin M")

# Query History in Sidebar
st.sidebar.markdown("### 🕑 Query History")
if st.session_state["history"]:
    for i, item in enumerate(reversed(st.session_state["history"]), 1):
        st.sidebar.write(f"**Q{i}:** {item['q']}")
        st.sidebar.write(item['a'])

# ---- Landing Section ----
st.markdown("""
<div style="text-align: center; padding: 40px 0; background: linear-gradient(to right, #4facfe, #00f2fe); border-radius: 12px; margin-bottom: 25px;">
    <h1 style="color: white;">📊 Generative BI Assistant</h1>
    <p style="color: #f0f0f0; font-size: 18px;">Upload your dataset or use the sample. Ask questions. Get instant insights & charts.</p>
</div>
""", unsafe_allow_html=True)

# ---- File Upload OR Sample ----
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

# ---- Main Logic ----
if df is not None:
    # Clean dataset
    df = clean_duration(df)
    df = add_decade(df)

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].mean())
        else:
            df[col] = df[col].fillna("Unknown")

    # Preview + Info
    with st.container():
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("👀 Preview of Data")
            st.dataframe(df.head())
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("📌 Dataset Info")
            st.write(f"Rows: {df.shape[0]} | Columns: {df.shape[1]}")
            st.write("**Columns:**", list(df.columns))
            st.markdown("</div>", unsafe_allow_html=True)

    # Chat Section
    st.markdown("## 💬 Chat with your Data")
    query = st.text_input("Ask a question:")

    if st.button("Ask AI") and query:
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
                    st.dataframe(result)
                else:
                    st.write(result)

                # Auto chart (no dropdown)
                if isinstance(result, pd.DataFrame) and result.shape[1] >= 2:
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.subheader("📊 Visualization")
                    auto_plot(result, query)
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                chat_bubble("assistant", "⚠️ AI did not return a valid result.")
        except Exception as e:
            chat_bubble("assistant", f"❌ Error: {e}")
