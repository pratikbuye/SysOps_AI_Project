# 🤖 Smart SysOps & AI Document Analyzer Agent

A dual-purpose Streamlit dashboard powered by local AI (**Ollama / Qwen2:0.5b**) for real-time system diagnostics and document/data analysis.

---

## 🚀 Features

### 🖥️ Tab 1: System Diagnostics & Smart Log Agent
* **Live Hardware Metrics:** Tracks CPU, RAM, and Disk utilization in real-time using `psutil`.
* **Automatic Database Logging:** Auto-saves hardware stats to an `SQLite` database (`sysops.db`).
* **Threshold Alerts:** Real-time warning banners for high CPU (>80%) or RAM (>85%) usage.
* **Interactive Trend Charts:** Displays historical CPU vs RAM usage using interactive line charts.
* **SysOps AI Assistant:** Connects to local Ollama (`qwen2:0.5b`) to answer live health queries in English, Hindi, Hinglish, or Marathi.
* **Raw Log Viewer & CSV Export:** Displays database logs with built-in CSV export options.

### 📄 Tab 2: AI Document & Data Analyzer Agent
* **PDF Resume Reviewer:** Extracts text from uploaded resumes and provides a detailed score, pros, and cons based on the target job role.
* **CSV & Excel Data Analyzer:** Automatically parses tabular datasets, answers query-based questions (e.g., counting names by letter), and provides concise AI summaries.
* **Exportable Reports:** Download AI-generated analysis reports directly as `.txt` files.

---

## 🛠️ Setup & Installation

### 1. Prerequisites
* Python 3.10 or higher
* [Ollama](https://ollama.com/) installed and running locally

### 2. Pull the AI Model
Open your terminal and run:
```bash
ollama run qwen2:0.5b

3. Install Dependencies
Clone or download this repository, navigate to the folder, and install required libraries:

pip install -r requirements.txt

4. Run the Application
Start the Streamlit app with:

streamlit run app.py


Project Structure :

├── app.py              # Main Streamlit Application
├── sysops.db           # SQLite Database (Auto-generated)
├── requirements.txt    # Python dependencies
└── README.md           # Project Documentation


