import pandas as pd
import io

def get_common_columns(dataframes):
    """
    Given a list of DataFrames, returns common column names (case-insensitive).
    """
    if not dataframes:
        return []

    # Map each DataFrame to its set of uppercase column names
    sets = [set(c.upper() for c in df.columns) for df in dataframes]
    
    # Intersection of all column sets
    common_set = set.intersection(*sets) if sets else set()
    return sorted(list(common_set))

def process_concat(dataframes, target_column=None):
    """
    Concatenates a list of DataFrames. Returns the merged DataFrame.
    """
    if not dataframes:
        return None

    all_dfs = []
    for df in dataframes:
        # Copy to avoid side-effects on the original uploaded data
        temp_df = df.copy()

        if target_column:
            # Case-insensitively find the target_column
            matched_col = next((c for c in temp_df.columns if c.upper() == target_column.upper()), None)
            if matched_col:
                temp_df = temp_df[[matched_col]]
                temp_df.columns = [target_column.upper()]
                all_dfs.append(temp_df)
            else:
                continue
        else:
            # Normal concat
            all_dfs.append(temp_df)

    if not all_dfs:
        return None

    combined_df = pd.concat(all_dfs, ignore_index=True)
    return combined_df
