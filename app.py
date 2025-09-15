import os
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

# Sidebar
st.sidebar.title("⚡ BI Assistant")
st.sidebar.write("Ask me questions about your data in **plain English**.")
st.sidebar.markdown("---")
st.sidebar.info("Built with **Groq + Streamlit** by Aswin M")

# Main Title
st.title("📊 Generative BI Assistant (Powered by Groq)")
st.markdown("Upload a dataset and **chat with your data like ChatGPT** — get answers, tables, and charts.")

# ---- Auto chart selection ----
def auto_plot(result, query):
    """Decide chart type based on query and result shape."""
    fig, ax = plt.subplots()
    query_lower = query.lower()

    try:
        if "trend" in query_lower or "over time" in query_lower or "monthly" in query_lower:
            result.plot(kind="line", x=result.columns[0], y=result.columns[1], ax=ax, marker="o")
            ax.set_title("📈 Trend over Time")

        elif "share" in query_lower or "percentage" in query_lower:
            result.set_index(result.columns[0])[result.columns[1]].plot(kind="pie", autopct='%1.1f%%', ax=ax)
            ax.set_ylabel("")
            ax.set_title("🥧 Share / Distribution")

        elif "distribution" in query_lower or "histogram" in query_lower:
            result[result.columns[1]].plot(kind="hist", bins=10, ax=ax)
            ax.set_title("📊 Distribution")

        else:
            result.plot(kind="bar", x=result.columns[0], y=result.columns[1], ax=ax)
            ax.set_title("📊 Comparison")

        st.pyplot(fig)
    except Exception as e:
        st.warning(f"⚠️ Could not generate chart: {e}")


# ---- Auto time aggregation ----
def auto_time_aggregation(df, query, result):
    """Check query for time keywords and aggregate if possible."""
    query_lower = query.lower()
    if not isinstance(result, pd.DataFrame):
        return result

    # Detect datetime column
    date_cols = [c for c in result.columns if "date" in c.lower()]
    if not date_cols:
        return result

    date_col = date_cols[0]

    try:
        if "monthly" in query_lower or "month" in query_lower:
            result[date_col] = pd.to_datetime(result[date_col], errors="coerce")
            result = result.groupby(result[date_col].dt.to_period("M")).sum().reset_index()
            result[date_col] = result[date_col].astype(str)

        elif "yearly" in query_lower or "year" in query_lower:
            result[date_col] = pd.to_datetime(result[date_col], errors="coerce")
            result = result.groupby(result[date_col].dt.year).sum().reset_index()
            result.rename(columns={date_col: "Year"}, inplace=True)

        elif "weekly" in query_lower or "week" in query_lower:
            result[date_col] = pd.to_datetime(result[date_col], errors="coerce")
            result = result.groupby(result[date_col].dt.to_period("W")).sum().reset_index()
            result[date_col] = result[date_col].astype(str)

    except Exception as e:
        st.warning(f"⚠️ Could not auto-aggregate time: {e}")

    return result


# ---- File Upload ----
file = st.file_uploader("📂 Upload your CSV file", type=["csv"])
if file:
    # Parse CSV and auto-convert date columns
    df = pd.read_csv(file, encoding="latin1")
    for col in df.columns:
        if "date" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
            except:
                pass
    
    # Layout with two columns
    col1, col2 = st.columns([2,1])

    with col1:
        st.subheader("👀 Preview of Data")
        st.dataframe(df.head())

    with col2:
        st.subheader("📌 Dataset Info")
        st.write(f"Rows: {df.shape[0]} | Columns: {df.shape[1]}")
        st.write("**Columns:**", list(df.columns))

    # Chat with Data
    st.markdown("## 💬 Chat with your Data")
    query = st.text_input("Type your question here:")

    if st.button("Ask AI") and query:
        # Prompt for Groq (stricter)
        prompt = f"""
        You are a Python data analyst.
        The dataframe is called df and has these columns: {list(df.columns)}.

        RULES:
        - Only return Python code (no explanations, no text).
        - Always assign the final output to a variable called result.
        - Never use print() or display().
        - Example format:
            result = df['Profit'].sum()
        Question: "{query}"
        """

        # AI Call
        chat_completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )

        code_answer = chat_completion.choices[0].message.content.strip()

        # Clean markdown fences
        if "```" in code_answer:
            parts = code_answer.split("```")
            code_answer = ""
            for p in parts:
                if not p.strip().startswith("python"):
                    code_answer += p.strip() + "\n"

        # Ensure result = exists
        if "result" not in code_answer:
            lines = code_answer.strip().split("\n")
            if lines:
                last_line = lines[-1]
                if last_line.strip() != "":
                    lines[-1] = f"result = {last_line}"
                    code_answer = "\n".join(lines)

        # Final check → skip empty/broken code
        if not code_answer.strip() or code_answer.strip() == "result =":
            st.error("⚠️ AI did not return valid code. Try rephrasing your question.")
        else:
            st.subheader("🤖 AI Generated Code")
            st.code(code_answer, language="python")

            try:
                # Safe execution with globals
                local_vars = {}
                global_vars = {"df": df, "pd": pd, "np": np}
                exec(code_answer, global_vars, local_vars)

                if "result" in local_vars:
                    result = local_vars["result"]
                    st.success("✅ Query executed successfully!")

                    # Apply auto time aggregation if needed
                    result = auto_time_aggregation(df, query, result)

                    st.write(result)

                    # Auto chart
                    if isinstance(result, pd.DataFrame) and result.shape[1] >= 2:
                        st.subheader("📊 Visualization")
                        auto_plot(result, query)
                else:
                    st.warning("⚠️ AI did not return a 'result' variable.")

            except Exception as e:
                st.error(f"❌ Error running AI-generated code: {e}")
