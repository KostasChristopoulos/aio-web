import streamlit as st
import pandas as pd
import io
import os
import zipfile
import time

# --- LOGIC IMPORTS ---
from tools.csv_splitter import process_split
from tools.csv_dropper import process_drop
from tools.csv_array_converter import process_convert
from tools.csv_concat import get_common_columns, process_concat
from tools.xlsx_to_csv import process_xlsx_convert, get_sheet_names
from tools.date_harmonizer import process_date_harmonization

# ==========================================
# 0. CONFIG & STYLING
# ==========================================
st.set_page_config(
    page_title="AIO Web Tool v2.8.4",
    page_icon="assets/icon.png" if os.path.exists("assets/icon.png") else None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #0E1117;
    }
    
    /* Better Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #1A1C23;
        border-right: 1px solid #333;
    }
    
    .sidebar-header {
        font-size: 22px;
        font-weight: 700;
        color: #fff;
        margin-bottom: 20px;
        text-align: center;
        letter-spacing: -0.5px;
    }
    
    /* Cards for tool sections */
    .st-emotion-cache-12w0qpk {
        background-color: #1E1E2E;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Button Hover Effect */
    .stButton>button {
        background-color: #4CAF50 !important;
        border: none !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        font-weight: 600 !important;
        color: white !important;
    }
    .stButton>button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3) !important;
    }
    
    /* Log Section */
    .log-container {
        background-color: #000;
        color: #E0E0E0;
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        padding: 15px;
        border-radius: 8px;
        font-size: 12px;
        border: 1px solid #333;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. SHARED UTILITIES
# ==========================================
def show_preview(df, title="Preview"):
    if df is not None:
        st.subheader(title)
        st.dataframe(df.head(20), use_container_width=True)
        st.caption(f"Showing first 20 of {len(df):,} rows.")

def to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# ==========================================
# 2. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("<div class='sidebar-header'>AIO Tools</div>", unsafe_allow_html=True)
    
    tool_option = st.radio(
        "Navigation",
        ["CSV Splitter", "Column Dropper", "Array Converter", "CSV Concat", "Excel to CSV", "Date Harmonizer"],
        label_visibility="collapsed"
    )
    
    st.divider()
    st.markdown("**Version 2.8.4**")
    st.caption("Secure in-memory processing.")

# ==========================================
# 3. PAGE CONTENT
# ==========================================

# ----------------- CSV SPLITTER -----------------
if tool_option == "CSV Splitter":
    st.title("CSV Batch Splitter")
    st.markdown("Split large files into smaller batches with duplicate detection and validation.")
    
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file, low_memory=False)
        cols = ["(None)"] + df.columns.tolist()
        
        col1, col2 = st.columns(2)
        with col1:
            rows_per_batch = st.number_input("Rows per batch", min_value=1, value=5000)
            unique_id_col = st.selectbox("Unique ID Column", options=cols)
        with col2:
            create_test = st.checkbox("Create Test Batch (10 rows)", value=True)
            drop_dups = st.checkbox("Remove True Duplicates", value=True)

        if st.button("Process Split", use_container_width=True):
            with st.spinner("Processing..."):
                target_col = unique_id_col if unique_id_col != "(None)" else None
                batches, report, dropped_df = process_split(df, rows_per_batch, target_col, create_test, drop_dups)
                
                if report:
                    st.info(report)
                
                if dropped_df is not None and not dropped_df.empty:
                    with st.expander("View Dropped Duplicates"):
                        st.dataframe(dropped_df, use_container_width=True)
                        st.caption(f"Total dropped: {len(dropped_df)} rows.")

                # Create ZIP
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for filename, batch_df in batches:
                        zf.writestr(filename, batch_df.to_csv(index=False))
                
                st.success(f"Successfully generated {len(batches)} files.")
                st.download_button(
                    label="Download All Batches (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}_batches.zip",
                    mime="application/zip",
                    use_container_width=True
                )
        show_preview(df)

# ----------------- COLUMN DROPPER -----------------
elif tool_option == "Column Dropper":
    st.title("Column Dropper")
    st.markdown("Select and remove specific columns from your dataset.")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        selected_cols = st.multiselect("Select columns to remove:", options=df.columns.tolist())
        
        if st.button("Process and Download", use_container_width=True):
            if not selected_cols:
                st.error("Please select at least one column.")
            else:
                target_str = ";".join(selected_cols)
                df_res, warn = process_drop(df, target_str)
                if warn: st.warning(warn)
                st.success(f"Removed {len(selected_cols)} column(s).")
                st.download_button(
                    "Download Result",
                    to_csv(df_res),
                    f"{uploaded_file.name.rsplit('.', 1)[0]}_modified.csv",
                    "text/csv",
                    use_container_width=True
                )
                show_preview(df_res, "Modified Result")
        else:
            show_preview(df)

# ----------------- ARRAY CONVERTER -----------------
elif tool_option == "Array Converter":
    st.title("Array Converter")
    st.markdown("Clean up columns containing array-like strings (e.g. `[1, 2, 3]`) into pipe-delimited text.")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if st.button("Convert Columns", use_container_width=True):
            df_res = process_convert(df)
            st.success("Conversion complete.")
            st.download_button(
                "Download Converted File",
                to_csv(df_res),
                f"{uploaded_file.name.rsplit('.', 1)[0]}_converted.csv",
                "text/csv",
                use_container_width=True
            )
            show_preview(df_res, "Result")
        else:
            show_preview(df)

# ----------------- CSV CONCAT -----------------
elif tool_option == "CSV Concat":
    st.title("CSV Concatenator")
    st.markdown("Combine multiple CSV files into a single master document.")

    uploaded_files = st.file_uploader("Upload CSV Files", type=["csv"], accept_multiple_files=True)
    if uploaded_files:
        dfs = [pd.read_csv(f) for f in uploaded_files]
        common = get_common_columns(dfs)
        
        target_col = st.selectbox("Merging Strategy", options=["All Columns"] + common)
        
        if st.button("Merge Files", use_container_width=True):
            final_target = None if target_col == "All Columns" else target_col
            df_res = process_concat(dfs, final_target)
            
            if df_res is not None:
                st.success(f"Merged {len(uploaded_files)} files.")
                st.download_button(
                    "Download Merged File",
                    to_csv(df_res),
                    "combined_export.csv",
                    "text/csv",
                    use_container_width=True
                )
                show_preview(df_res, "Merged Result")
            else:
                st.error("Concatenation failed. Please check your files.")

# ----------------- EXCEL TO CSV -----------------
elif tool_option == "Excel to CSV":
    st.title("Excel to CSV")
    st.markdown("Convert Excel sheets into standard CSV format.")

    uploaded_file = st.file_uploader("Upload Workbook", type=["xlsx", "xls"])
    if uploaded_file:
        sheets = get_sheet_names(uploaded_file)
        target_sheet = st.selectbox("Select Sheet", options=["All Sheets"] + sheets)
        
        if st.button("Process Extraction", use_container_width=True):
            sheet_param = "All" if target_sheet == "All Sheets" else target_sheet
            results = process_xlsx_convert(uploaded_file, sheet_param)
            
            if len(results) == 1:
                s_name, s_df = next(iter(results.items()))
                st.success(f"Extracted: {s_name}")
                st.download_button(
                    "Download CSV",
                    to_csv(s_df),
                    f"{s_name}.csv",
                    "text/csv",
                    use_container_width=True
                )
                show_preview(s_df, f"Preview: {s_name}")
            else:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for s_name, s_df in results.items():
                        zf.writestr(f"{s_name}.csv", s_df.to_csv(index=False))
                
                st.success(f"Extracted {len(results)} sheets.")
                st.download_button(
                    label="Download All Sheets (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="excel_export.zip",
                    mime="application/zip",
                    use_container_width=True
                )

# ----------------- DATE HARMONIZER -----------------
elif tool_option == "Date Harmonizer":
    st.title("Date Harmonizer")
    st.markdown("Unify date formats across multiple columns automatically.")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            target_cols = st.multiselect("Date Columns:", options=df.columns.tolist())
        with col2:
            pref = st.selectbox("Input Order", options=["US (MM/DD)", "EU (DD/MM)"])
        with col3:
            fmt = st.selectbox("Standardized Format", options=[
                "YYYY-MM-DD", "DD-MM-YYYY", "MM-DD-YYYY", "DD/MM/YYYY", "MM/DD/YYYY", "DD-MMM-YYYY"
            ])
        
        fmt_map = {
            "YYYY-MM-DD": "%Y-%m-%d",
            "DD-MM-YYYY": "%d-%m-%Y",
            "MM-DD-YYYY": "%m-%d-%Y",
            "DD/MM/YYYY": "%d/%m/%Y",
            "MM/DD/YYYY": "%m/%d/%Y",
            "DD-MMM-YYYY": "%d-%b-%Y"
        }
        
        if st.button("Apply Harmonization", use_container_width=True):
            if not target_cols:
                st.error("Please pick at least one column.")
            else:
                input_p = "US" if "US" in pref else "EU"
                df_res, errors = process_date_harmonization(df, target_cols, input_p, fmt_map[fmt])
                
                if errors:
                    st.warning("\n".join(errors))
                
                st.success("Dates standardized successfully.")
                st.download_button(
                    "Download Harmonized File",
                    to_csv(df_res),
                    "standardized_dates.csv",
                    "text/csv",
                    use_container_width=True
                )
                show_preview(df_res, "Result")
        else:
            show_preview(df)
