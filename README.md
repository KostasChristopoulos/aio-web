# AIO Web Tool

A web-based tool for CSV and Excel processing.

## Getting Started

### 1. Installation
Clone the repository and install the dependencies:
```bash
pip install -r requirements.txt
```

### 2. Launch the Application
Start the local development server:
```bash
streamlit run app.py
```

---

## 🛠 Features
- **CSV Splitter**: High-speed in-memory splitting with duplicate detection and preview logs.
- **Column Dropper**: Interactive multi-select interface for cleaning datasets.
- **Array Converter**: Automatically converts array-like strings to pipe-delimited text.
- **CSV Concatenator**: Merge multiple files with auto-matching or specific column targets.
- **Excel to CSV**: Extract individual sheets or bulk-export workbooks to ZIP.
- **Date Harmonizer**: Standardize date formats across multiple columns simultaneously.
