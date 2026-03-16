import pandas as pd

def process_date_harmonization(df, target_columns, input_preference, output_format):
    """
    df: DataFrame to modify.
    input_preference: 'US' (monthfirst) or 'EU' (dayfirst)
    output_format: str (strftime compatible)
    """
    df_copy = df.copy()
    err_report = []
    
    day_first = True if input_preference == 'EU' else False
    
    for i, col in enumerate(target_columns):
        if col not in df_copy.columns:
            continue
        
        # Convert to datetime objects
        # errors='coerce' turns unparseable dates into NaT
        original_series = df_copy[col].copy()
        df_copy[col] = pd.to_datetime(df_copy[col], dayfirst=day_first, errors='coerce')
        
        # Find NaT values that weren't originally null
        failed_mask = df_copy[col].isna() & original_series.notna()
        failed_indices = df_copy.index[failed_mask].tolist()
        
        if failed_indices:
            err_report.append(f"Column '{col}': Failed to parse {len(failed_indices)} rows (e.g., row {failed_indices[0]+1})")
        
        # Format back to string
        # We use dt.strftime but keep NaT as empty strings
        df_copy[col] = df_copy[col].dt.strftime(output_format).fillna("")
        
    return df_copy, err_report
