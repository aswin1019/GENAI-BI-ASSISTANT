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

# ---- Initialize session state ----
if "history" not in st.session_state:
    st.session_state["history"] = []

# Sidebar
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

# Main Title
st.title("📊 Generative BI Assistant (Powered by Groq)")
st.markdown("Upload a dataset or use a sample and **chat with your data like ChatGPT** — get answers, tables, and charts.")

# ---- Auto chart selection + manual override ----
def auto_plot(result, query, manual_chart=None):
    """Decide chart type based on query, result shape, or manual selection."""
    fig, ax = plt.subplots()
    query_lower = query.lower()

    # Decide chart type
    chart_type = None
    if manual_chart and manual_chart != "Auto":
        chart_type = manual_chart
    else:
        if "trend" in query_lower or "over time" in query_lower or "monthly" in query_lower:
            chart_type = "Line"
        elif "share" in query_lower or "percentage" in query_lower:
            chart_type = "Pie"
        elif "distribution" in query_lower or "histogram" in query_lower:
            chart_type = "Histogram"
        elif "scatter" in query_lower:
            chart_type = "Scatter"
        elif "heatmap" in query_lower:
            chart_type = "Heatmap"
        else:
            chart_type = "Bar"

    try:
        if chart_type == "Line":
            result.plot(kind="line", x=result.columns[0], y=result.columns[1], ax=ax, marker="o")
        elif chart_type == "Pie":
            result.set_index(result.columns[0])[result.columns[1]].plot(kind="pie", autopct='%1.1f%%', ax=ax)
            ax.set_ylabel("")
        elif chart_type == "Histogram":
            result[result.columns[1]].plot(kind="hist", bins=10, ax=ax)
        elif chart_type == "Scatter":
            if result.shape[1] >= 2:
                result.plot(kind="scatter", x=result.columns[0], y=result.columns[1], ax=ax)
        elif chart_type == "Heatmap":
            import seaborn as sns
            corr = result.corr(numeric_only=True)
            sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        elif chart_type == "Stacked Bar":
            result.plot(kind="bar", stacked=True, ax=ax)
        else:  # Default Bar
            result.plot(kind="bar", x=result.columns[0], y=result.columns[1], ax=ax)

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
        st.success("✅ Your dataset has been uploaded successfully!")

# ---- Main Logic ----
if df is not None:
    # Auto-convert date columns
    for col in df.columns:
        if "date" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
            except:
                pass

    # ---- Sidebar Filters ----
    st.sidebar.markdown("### 🔍 Data Filters")
    filters = {}
    for col in df.columns:
        if df[col].dtype == "object" and df[col].nunique() <= 20:
            options = ["All"] + list(df[col].unique())
            choice = st.sidebar.selectbox(f"Filter by {col}", options)
            if choice != "All":
                filters[col] = choice
        elif "date" in col.lower():
            date_range = st.sidebar.date_input(f"Filter by {col}", [])
            if len(date_range) == 2:
                filters[col] = date_range

    # Apply filters
    for col, val in filters.items():
        if isinstance(val, list) and len(val) == 2:  # date range
            df = df[(df[col] >= pd.to_datetime(val[0])) & (df[col] <= pd.to_datetime(val[1]))]
        else:  # categorical
            df = df[df[col] == val]

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

        # Use spinner while AI is generating code
        with st.spinner("🤖 Thinking... Generating Python code for your query..."):
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
                # Use spinner while executing
                with st.spinner("⚡ Running AI-generated code on your dataset..."):
                    local_vars = {}
                    global_vars = {"df": df, "pd": pd, "np": np}
                    exec(code_answer, global_vars, local_vars)

                if "result" in local_vars:
                    result = local_vars["result"]
                    st.success("✅ Query executed successfully!")

                    # Save to history
                    st.session_state["history"].append(
                        {"q": query, "a": result.head(5) if isinstance(result, pd.DataFrame) else result}
                    )
                    if len(st.session_state["history"]) > 5:
                        st.session_state["history"].pop(0)

                    # Apply auto time aggregation if needed
                    result = auto_time_aggregation(df, query, result)

                    st.write(result)

                    # Auto chart + manual override
                    if isinstance(result, pd.DataFrame) and result.shape[1] >= 2:
                        st.subheader("📊 Visualization")
                        chart_choice = st.selectbox(
                            "Choose chart type (or leave Auto):",
                            ["Auto", "Bar", "Line", "Pie", "Histogram", "Scatter", "Heatmap", "Stacked Bar"]
                        )
                        auto_plot(result, query, manual_chart=chart_choice)
                else:
                    st.warning("⚠️ AI did not return a 'result' variable.")

            except Exception as e:
                st.warning(f"⚠️ First attempt failed: {e}")
                st.info("🔄 Retrying with stricter instructions...")

                retry_prompt = prompt + "\n\nMake sure the code runs without errors. Fix mistakes."
                retry_completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": retry_prompt}]
                )
                retry_code = retry_completion.choices[0].message.content.strip()

                try:
                    local_vars = {}
                    exec(retry_code, {"df": df, "pd": pd, "np": np}, local_vars)

                    if "result" in local_vars:
                        result = local_vars["result"]
                        st.success("✅ Retry successful!")

                        # Save to history
                        st.session_state["history"].append(
                            {"q": query, "a": result.head(5) if isinstance(result, pd.DataFrame) else result}
                        )
                        if len(st.session_state["history"]) > 5:
                            st.session_state["history"].pop(0)

                        st.write(result)

                        if isinstance(result, pd.DataFrame) and result.shape[1] >= 2:
                            st.subheader("📊 Visualization")
                            chart_choice = st.selectbox(
                                "Choose chart type (or leave Auto):",
                                ["Auto", "Bar", "Line", "Pie", "Histogram", "Scatter", "Heatmap", "Stacked Bar"]
                            )
                            auto_plot(result, query, manual_chart=chart_choice)
                    else:
                        st.error("❌ Retry also failed: AI did not return a valid 'result'.")

                except Exception as e2:
                    st.error(f"❌ Retry also failed: {e2}")
