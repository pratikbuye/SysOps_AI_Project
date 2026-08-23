import streamlit as st
import psutil
import requests
import pandas as pd
import sqlite3
import re
import os
from datetime import datetime
from pypdf import PdfReader
from groq import Groq

# Page Configuration
st.set_page_config(page_title="Autonomous SysOps AI Agent", layout="wide")

# Main Title
st.title("🖥️ Autonomous SysOps & Data Automation AI Agent")
st.caption("Powered by Local LLM (Qwen2) | System Diagnostics • Database Intelligence • Multi-Format Analyzer")

# ---------------- SIDEBAR: SYSTEM DIAGNOSTICS & OLLAMA STATUS ----------------
st.sidebar.title("⚙️ Control Panel")
st.sidebar.markdown("---")

# 1. Live Ollama Engine Connection Check
st.sidebar.subheader("🤖 Local LLM Engine")
try:
        ollama_check = requests.get("http://localhost:11434/api/tags", timeout=1)
        if ollama_check.status_code == 200:
            st.sidebar.success("🟢 Ollama Engine Active")
            st.sidebar.caption("Active Model: **qwen2:1.5b**")
        else:
            st.sidebar.warning("🟡 Ollama Status Unknown")
except Exception:
    # Jab Local Ollama unreachable ho (Cloud par ya Local closed par)
    st.sidebar.success("🟢 Cloud LLM Engine Active")
    st.sidebar.caption("Active Provider: **Groq Cloud API**")

st.sidebar.markdown("---")

# 2. Live Hardware Resources (CPU & RAM)
st.sidebar.subheader("📊 System Metrics")

cpu_percent = psutil.cpu_percent(interval=0.1)
ram_percent = psutil.virtual_memory().percent

st.sidebar.text(f"CPU Load: {cpu_percent}%")
st.sidebar.progress(cpu_percent / 100)

st.sidebar.text(f"RAM Usage: {ram_percent}%")
st.sidebar.progress(ram_percent / 100)

st.sidebar.markdown("---")

# 3. Quick Rerun / Refresh Action
if st.sidebar.button("🔄 Refresh App Status", use_container_width=True):
    st.rerun()

# ================= DATABASE SETUP =================
DB_FILE = "sysops.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hardware_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            cpu_usage REAL,
            ram_usage REAL,
            disk_usage REAL,
            status TEXT
        )
    ''')
    cursor.execute("SELECT COUNT(*) FROM hardware_logs")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ("2026-08-07 08:00:00", 35.2, 45.0, 50.1, "Healthy"),
            ("2026-08-07 09:00:00", 42.1, 52.3, 50.1, "Healthy"),
            ("2026-08-07 10:00:00", 88.5, 91.2, 50.2, "Overloaded"),
            ("2026-08-07 11:00:00", 65.0, 78.4, 50.2, "Healthy"),
            ("2026-08-07 12:00:00", 92.0, 89.0, 50.3, "Overloaded")
        ]
        cursor.executemany("INSERT INTO hardware_logs (timestamp, cpu_usage, ram_usage, disk_usage, status) VALUES (?, ?, ?, ?, ?)", sample_data)
        conn.commit()
    conn.close()

def log_hardware_data(cpu, ram, disk, status):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO hardware_logs (timestamp, cpu_usage, ram_usage, disk_usage, status) VALUES (?, ?, ?, ?, ?)",
        (now, cpu, ram, disk, status)
    )
    conn.commit()
    conn.close()

init_db()

# Clean 2-Tab Layout
tab1, tab2 = st.tabs(["📊 System Diagnostics & Smart AI Agent", "📄 Document Analyzer"])

# ================= TAB 1: SYSTEM DIAGNOSTICS & SMART LOG AGENT =================
with tab1:
    st.subheader("🖥️ Live Hardware Metrics")

    if st.button("🔄 Refresh Stats"):
        st.rerun()

    cpu_usage = psutil.cpu_percent(interval=1)
    ram_info = psutil.virtual_memory()
    disk_info = psutil.disk_usage('/')
    status = "Healthy" if cpu_usage < 70 and ram_info.percent < 85 else "Overloaded"

    # Auto-log live metrics to DB
    log_hardware_data(cpu_usage, ram_info.percent, disk_info.percent, status)

    # 1. THRESHOLD ALERT SYSTEM
    if cpu_usage > 80 or ram_info.percent > 85:
        st.error("⚠️ **CRITICAL ALERT:** High Resource Utilization Detected! Check high-volume processes.")
    elif cpu_usage > 60 or ram_info.percent > 70:
        st.warning("⚡ **WARNING:** Moderate load on system resources.")

    # Live Metrics Display
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="CPU Usage", value=f"{cpu_usage}%")
        st.progress(int(cpu_usage))
    with col2:
        st.metric(label="RAM Usage", value=f"{ram_info.percent}%")
        st.progress(int(ram_info.percent))
    with col3:
        st.metric(label="Disk Usage", value=f"{disk_info.percent}%")
        st.progress(int(disk_info.percent))

    st.caption(f"✅ Current metrics auto-logged to `sysops.db` at {datetime.now().strftime('%H:%M:%S')}")

    # 2. LIVE TREND CHART (Past 15 Logs)
    st.markdown("---")
    st.subheader("📈 Resource Usage History Trend")
    try:
        conn = sqlite3.connect(DB_FILE)
        df_chart = pd.read_sql_query("SELECT timestamp, cpu_usage, ram_usage FROM hardware_logs ORDER BY id DESC LIMIT 15", conn)
        conn.close()

        if not df_chart.empty:
            df_chart = df_chart.iloc[::-1]  # Chronological order
            df_chart.set_index('timestamp', inplace=True)
            st.line_chart(df_chart)
    except Exception as e:
        st.error(f"Chart Load Failed: {e}")

    # AI Assistant Block
    st.markdown("---")
    st.subheader("🤖 Smart SysOps AI Assistant")
    st.write("Write below to ask for live system status or check past logs:")

    user_query = st.text_input(
        "Ask AI Agent a Question:",
        value="How is the current system health status?",
        placeholder="e.g. Is the system healthy right now?"
    )

    if st.button("🤖 Run AI Diagnostic"):
        with st.spinner("AI Agent analyzing..."):
            prompt = f"""You are a SysOps assistant. Give a direct 1-2 sentence system health summary based on these live metrics.
Respond in the EXACT same language as the user (English, Hindi, Hinglish, Marathi).

Live Metrics: CPU {cpu_usage}%, RAM {ram_info.percent}%, Disk {disk_info.percent}%, Status: {status}
User Question: {user_query}
Answer:"""

            try:
                # 1. Local Ollama Fallback
                res = requests.post(
                    "http://localhost:11434/api/generate",
                    json={"model": "qwen2:1.5b", "prompt": prompt, "stream": False},
                    timeout=60
                )
                if res.status_code == 200:
                    st.info(res.json().get("response", "").strip())
                else:
                    raise Exception("Ollama failed")
            except Exception:
                # 2. Cloud Groq Fallback
                try:
                    groq_api_key = st.secrets["GROQ_API_KEY"]
                except Exception:
                    groq_api_key = os.getenv("GROQ_API_KEY")
                if groq_api_key:
                    try:
                        client = Groq(api_key=groq_api_key)
                        completion = client.chat.completions.create(
                            model="openai/gpt-oss-120b",
                            messages=[{"role": "user", "content": prompt}],
                        )
                        st.info(completion.choices[0].message.content.strip())
                    except Exception as groq_err:
                        st.error(f"Groq API Error: {groq_err}")
                else:
                    st.error("Neither Ollama nor Groq API is available.")

    with st.expander("📁 View Raw Database Logs (sysops.db)"):
        conn = sqlite3.connect(DB_FILE)
        df_logs = pd.read_sql_query("SELECT * FROM hardware_logs ORDER BY id DESC LIMIT 10", conn)
        conn.close()
        st.dataframe(df_logs)

# ================= TAB 2: DOCUMENT & DATA ANALYZER AGENT =================
with tab2:
    st.subheader("📄 AI Document & Data Analyzer Agent")
    st.write("Upload a PDF resume, CSV, or Excel file and get instant analysis from AI!")

    uploaded_file = st.file_uploader("Upload File (PDF, CSV, XLSX)", type=["pdf", "csv", "xlsx"])

    if uploaded_file is not None:
        file_extension = uploaded_file.name.split('.')[-1].lower()
        is_resume = False  # Pre-declare to avoid NameError

        # ---------------- 1. SMART PDF DOCUMENT & RESUME ANALYZER ----------------
        if file_extension == "pdf":
            pdf_reader = PdfReader(uploaded_file)
            pdf_text = ""
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    pdf_text += extracted + "\n"

            # Check if uploaded PDF is a Resume using Keyword Classifier
            resume_keywords = ["experience", "education", "skills", "projects", "resume", "curriculum vitae", "work history"]
            is_resume = sum(1 for kw in resume_keywords if kw in pdf_text.lower()) >= 2

            if is_resume:
                st.success("📄 PDF Resume Uploaded!")
                job_role = st.text_input("Target Job Role:", value="Software Engineer")

                if st.button("⚡ Run Resume Assessment"):
                    with st.spinner("Analyzing Resume..."):
                        prompt = f"""You are an ATS Resume Reviewer.
Job Role: {job_role}
Resume Content: {pdf_text[:3000]}

Provide a clean review with:
1. Overall Rating (out of 10)
2. Key Strengths
3. Key Improvements Needed"""

                        try:
                            res = requests.post("http://localhost:11434/api/generate",
                                                json={"model": "qwen2:1.5b", "prompt": prompt, "stream": False},
                                                timeout=60)
                            if res.status_code == 200:
                                st.subheader("📄 Auto AI Resume Assessment")
                                st.success(res.json().get("response", ""))
                            else:
                                raise Exception("Ollama failed")
                        except Exception:
                            try:
                                groq_api_key = st.secrets["GROQ_API_KEY"]
                            except Exception:
                                groq_api_key = os.getenv("GROQ_API_KEY")
                            if groq_api_key:
                                try:
                                    client = Groq(api_key=groq_api_key)
                                    completion = client.chat.completions.create(
                                        model="openai/gpt-oss-120b",
                                        messages=[{"role": "user", "content": prompt}],
                                    )
                                    st.subheader("📄 Auto AI Resume Assessment")
                                    st.success(completion.choices[0].message.content)
                                except Exception as groq_err:
                                    st.error(f"Groq API Error: {groq_err}")
                            else:
                                st.error("Neither Ollama nor Groq API is available.")
            else:
                st.success("📑 General Document PDF Loaded!")

            # --- ALWAYS SHOW DEEP SEARCH AGENT FOR ALL PDFs ---
            st.markdown("---")
            st.subheader("🔍 Smart AI Deep Search & Analysis")
            doc_query = st.text_input(
                "Enter your analysis prompt or question about this document:",
                value="Summarize the main content of this document."
            )

            if st.button("⚡ Run Deep AI Analysis"):
                with st.spinner("Analyzing Document..."):
                    prompt = f"""You are a professional Document & Resume Analyst.
Document Text Context: {pdf_text[:3000]}

User Question: {doc_query}

Instructions:
Answer accurately based ONLY on the provided document text. Be clear and direct."""

                    try:
                        res = requests.post("http://localhost:11434/api/generate",
                                            json={"model": "qwen2:1.5b", "prompt": prompt, "stream": False},
                                            timeout=60)
                        if res.status_code == 200:
                            ai_ans = res.json().get("response", "").strip()
                            st.subheader("💡 AI Answer")
                            st.success(ai_ans)

                            st.download_button(
                                label="📥 Download Detailed Analysis (.txt)",
                                data=f"Query: {doc_query}\n\nAI Answer:\n{ai_ans}",
                                file_name="pdf_analysis_report.txt",
                                mime="text/plain"
                            )
                        else:
                            raise Exception("Ollama failed")
                    except Exception:
                        try:
                            groq_api_key = st.secrets["GROQ_API_KEY"]
                        except Exception:
                            groq_api_key = os.getenv("GROQ_API_KEY")
                        if groq_api_key:
                            try:
                                client = Groq(api_key=groq_api_key)
                                completion = client.chat.completions.create(
                                    model="openai/gpt-oss-120b",
                                    messages=[{"role": "user", "content": prompt}],
                                )
                                ai_ans = completion.choices[0].message.content.strip()
                                st.subheader("💡 AI Answer")
                                st.success(ai_ans)

                                st.download_button(
                                    label="📥 Download Detailed Analysis (.txt)",
                                    data=f"Query: {doc_query}\n\nAI Answer:\n{ai_ans}",
                                    file_name="pdf_analysis_report.txt",
                                    mime="text/plain"
                                )
                            except Exception as groq_err:
                                st.error(f"Groq API Error: {groq_err}")
                        else:
                            st.error("Neither Ollama nor Groq API is available.")

        # ---------------- 2. SMART CSV / XLSX DATASET ANALYZER ----------------
        elif file_extension in ["csv", "xlsx"]:
            st.success("📊 Data File Successfully Loaded!")
            df = pd.read_csv(uploaded_file) if file_extension == "csv" else pd.read_excel(uploaded_file)
            
            # Auto-Fix Unnamed Header Columns (e.g. Column_1, Column_2)
            df.columns = [f"Column_{i+1}" if "Unnamed" in str(col) else col for i, col in enumerate(df.columns)]

            # --- METRICS CARDS ---
            st.markdown("### 📈 Dataset Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Rows", df.shape[0])
            col2.metric("Total Columns", df.shape[1])
            col3.metric("Missing Values", df.isnull().sum().sum())

            # --- DATA PREVIEW ---
            with st.expander("👀 View Dataset Preview", expanded=True):
                st.dataframe(df.head(10), use_container_width=True)

            st.markdown("---")
            # --- DEEP SEARCH AGENT ---
            st.subheader("🔍 Smart AI Deep Search & Analysis")
            doc_query = st.text_input(
                "Enter your analysis prompt or question:",
                value="How many people are named Vedant and what are their full names?"
            )

            if st.button("⚡ Run Deep AI Analysis"):
                with st.spinner("Analyzing dataset..."):
                    
                    # Comprehensive Stopwords List
                    STOPWORDS = {
                        "how", "many", "people", "person", "persons", "are", "named", "name", "names", 
                        "and", "what", "their", "full", "is", "the", "a", "an", "of", "in", "to", "for", 
                        "with", "on", "at", "from", "by", "about", "as", "into", "like", "through", "after", 
                        "over", "between", "out", "against", "during", "without", "before", "under", 
                        "around", "among", "show", "find", "get", "give", "list", "search", "count", 
                        "who", "where", "which", "when", "student", "students", "record", "records", 
                        "data", "dataset", "file", "details", "detail", "there", "any", "set", "number", 
                        "naam", "log", "kya", "hain", "ke", "kitne", "aur", "unke", "konse", "par", 
                        "kaun", "ka", "ki", "ko", "mein", "hai", "bhi"
                    }
                    
                    # Clean Search Terms using Regex
                    raw_words = re.findall(r'\b[a-zA-Z0-9]+\b', doc_query)
                    search_terms = [w for w in raw_words if len(w) > 2 and w.lower() not in STOPWORDS]

                    if not search_terms:
                        search_terms = [w for w in raw_words if len(w) > 2]

                    # Exact Word Boundary Match (\bterm\b)
                    mask = pd.Series([False] * len(df))
                    for col in df.columns:
                        for term in search_terms:
                            pattern = r'\b' + re.escape(term) + r'\b'
                            mask |= df[col].astype(str).str.contains(pattern, case=False, na=False)

                    matched_df = df[mask]

                    if not matched_df.empty:
                        records_list = []
                        for idx, row in matched_df.iterrows():
                            row_values = [str(val).strip() for val in row.values if pd.notnull(val) and str(val).strip() != ""]
                            records_list.append(" ".join(row_values))

                        context_summary = f"Total exact matches found: {len(matched_df)}.\nMatched Records List:\n" + "\n".join([f"- {r}" for r in records_list])
                    else:
                        context_summary = f"No direct matches found for search terms: {search_terms}. Total rows in dataset: {df.shape[0]}."

                    # Strict Prompt
                    prompt = f"""You are a strict data assistant. Answer the user query using ONLY the provided matched data facts.

Matched Data Facts:
{context_summary}

User Question: {doc_query}

INSTRUCTIONS:
1. State the exact total count of matching records.
2. List each record's full row details in a clean 1-line format (e.g., "1. Vedant Prakash Deshmukh").
3. Do NOT split columns into multiple bullet points per person.
4. Do NOT imagine or fabricate non-existent details.
5. Keep the response clean and direct."""

                    try:
                        res = requests.post(
                            "http://localhost:11434/api/generate",
                            json={"model": "qwen2:1.5b", "prompt": prompt, "stream": False},
                            timeout=60
                        )
                        if res.status_code == 200:
                            ai_report = res.json().get("response", "").strip()

                            st.subheader("💡 AI Answer")
                            st.success(ai_report)

                            if not matched_df.empty:
                                st.markdown("##### 📌 Exact Matched Records:")
                                st.dataframe(matched_df, use_container_width=True)

                            st.download_button(
                                label="📥 Download Detailed Analysis (.txt)",
                                data=f"Query: {doc_query}\n\nAI Answer:\n{ai_report}\n\nMatched Records:\n{matched_df.to_string()}",
                                file_name="data_analysis_report.txt",
                                mime="text/plain"
                            )
                        else:
                            raise Exception("Ollama failed")
                    except Exception:
                        try:
                            groq_api_key = st.secrets["GROQ_API_KEY"]
                        except Exception:
                            groq_api_key = os.getenv("GROQ_API_KEY")
                        if groq_api_key:
                            try:
                                client = Groq(api_key=groq_api_key)
                                completion = client.chat.completions.create(
                                    model="openai/gpt-oss-120b",
                                    messages=[{"role": "user", "content": prompt}],
                                )
                                ai_report = completion.choices[0].message.content.strip()

                                st.subheader("💡 AI Answer")
                                st.success(ai_report)

                                if not matched_df.empty:
                                    st.markdown("##### 📌 Exact Matched Records:")
                                    st.dataframe(matched_df, use_container_width=True)

                                st.download_button(
                                    label="📥 Download Detailed Analysis (.txt)",
                                    data=f"Query: {doc_query}\n\nAI Answer:\n{ai_report}\n\nMatched Records:\n{matched_df.to_string()}",
                                    file_name="data_analysis_report.txt",
                                    mime="text/plain"
                                )
                            except Exception as groq_err:
                                st.error(f"Groq API Error: {groq_err}")
                        else:
                            st.error("Neither Ollama nor Groq API is available.")