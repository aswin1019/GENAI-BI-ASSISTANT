# 📊 Generative BI Assistant

A Streamlit app powered by **Groq LLM + Python** that lets you upload datasets (CSV) and **chat with your data** in plain English.  
The assistant generates **code, tables, and charts** automatically.

## 🚀 Features
- Upload any CSV file
- Ask questions in plain English
- AI generates **Python (pandas) code**
- Automatic visualizations (Bar, Line, Pie, Histogram)
- Auto-detects time queries (monthly, yearly, weekly)

## 🛠️ Tech Stack
- Python, Pandas, Numpy
- Streamlit
- Groq LLM
- Matplotlib

## 🔧 Setup
```bash
git clone https://github.com/yourusername/bi-assistant.git
cd bi-assistant
pip install -r requirements.txt
streamlit run app.py
