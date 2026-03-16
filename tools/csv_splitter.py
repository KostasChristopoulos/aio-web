import pandas as pd
import io

def process_split(df, rows_per_batch, unique_col=None, create_test_file=True, drop_true_duplicates=True):
    """
    Splits a DataFrame into batches. 返回 (batches, report, dropped_df)
    """
    batches = []
    reports = []
    dropped_df = pd.DataFrame()
    
    # --- Duplicate check ---
    df_clean = df.copy()
    if drop_true_duplicates:
        count_before = len(df_clean)
        # Keep track of what we are dropping
        is_duplicate = df_clean.duplicated(keep="first")
        dropped_df = df_clean[is_duplicate]
        
        df_clean = df_clean.drop_duplicates(keep="first")
        dropped = len(dropped_df)
        if dropped > 0:
            reports.append(f"Dropped {dropped} true duplicate row(s).")
            
    partial_dup_ids = []
    if unique_col and unique_col in df_clean.columns:
        mask_not_null = df_clean[unique_col].notna()
        df_with_id = df_clean[mask_not_null]
        partial_dup_ids = df_with_id[df_with_id.duplicated(subset=[unique_col], keep=False)][unique_col].unique().tolist()
        if partial_dup_ids:
            reports.append(f"Found IDs that appear in multiple rows for column '{unique_col}': {', '.join(str(x) for x in partial_dup_ids)}")

    df_original = df_clean.reset_index(drop=True)
    
    if create_test_file:
        df_test = df_original.iloc[:10]
        batches.append(("_Test.csv", df_test))
        df_splitting = df_original.iloc[10:]
    else:
        df_splitting = df_original
    
    total_rows = len(df_splitting)
    num_batches = (total_rows // rows_per_batch) + (1 if total_rows % rows_per_batch != 0 else 0)
    
    for i in range(num_batches):
        start_idx = i * rows_per_batch
        end_idx = start_idx + rows_per_batch
        batch_df = df_splitting.iloc[start_idx:end_idx]
        batches.append((f"_Batch{i+1}.csv", batch_df))
        
    return batches, "\n".join(reports), dropped_df
