import pandas as pd

def process_drop(df, columns_raw):
    """
    Drops columns from a DataFrame.
    """
    cols_to_drop = [col.strip() for col in columns_raw.split(';') if col.strip()]
    
    missing_cols = [col for col in cols_to_drop if col not in df.columns]
    warning_msg = ""
    if missing_cols:
        warning_msg = f"Skipped non-existent columns: {', '.join(missing_cols)}"
    
    df_result = df.drop(columns=cols_to_drop, inplace=False, errors='ignore')
    
    return df_result, warning_msg
