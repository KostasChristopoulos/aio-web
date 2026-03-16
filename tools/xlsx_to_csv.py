import pandas as pd
import io

def get_sheet_names(file_obj):
    """
    Returns a list of sheet names in an Excel file.
    file_obj: Streamlit BytesIO object.
    """
    try:
        xl = pd.ExcelFile(file_obj)
        return xl.sheet_names
    except Exception:
        return []

def process_xlsx_convert(file_obj, sheet_name="All"):
    """
    Converts Excel sheets to a dictionary of {name: DataFrame}.
    file_obj: Streamlit BytesIO object.
    """
    results = {}
    if sheet_name == "All":
        dict_df = pd.read_excel(file_obj, sheet_name=None)
        results = dict_df
    else:
        df = pd.read_excel(file_obj, sheet_name=sheet_name)
        results = {sheet_name: df}
    return results
