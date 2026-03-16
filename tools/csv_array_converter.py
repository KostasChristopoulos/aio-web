import pandas as pd
import ast

def array_to_pipe(value):
    if isinstance(value, list):
        return "|".join(map(str, value))

    if isinstance(value, str):
        value_stripped = value.strip()
        if value_stripped.startswith("[") and value_stripped.endswith("]"):
            try:
                parsed = ast.literal_eval(value_stripped)
                if isinstance(parsed, list):
                    return "|".join(map(str, parsed))
            except Exception:
                pass
    return value

def process_convert(df):
    """
    Converts array-like columns in a DataFrame to pipe-delimited strings.
    """
    # Use map if available, else applymap
    if hasattr(df, 'map'):
        df_result = df.map(array_to_pipe)
    else:
        df_result = df.applymap(array_to_pipe)
    return df_result
