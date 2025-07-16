import pandas as pd
import numpy as np

def clean_dataframe_cells(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans up all string cells in the dataframe:
    - Strips whitespace
    - Replaces ?, :, /, newlines
    - Replaces double spaces
    - Normalizes null-like values to np.nan
    """
    null_values = {"", "NA", "N/A", "na", "n/a", "null", "None", "-"}

    for col in df.columns:
        if df[col].dtype == object:
            cleaned = []
            for val in df[col]:
                if not isinstance(val, str):
                    val = str(val)
                val = val.strip()
                val = val.replace("\n", " ").replace("\r", "")
                val = val.replace("?", "").replace(":", "").replace("/", "-")
                val = val.replace("  ", " ")
                if val in null_values:
                    val = np.nan
                cleaned.append(val)
            df[col] = cleaned
    return df

# Infer and convert column types
from typing import Tuple, Dict
import warnings
warnings.filterwarnings("ignore", category=pd.errors.PerformanceWarning)

def infer_and_convert_column_types(
    df: pd.DataFrame, sample_size: int = 100, verbose: bool = False
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Infers data types for each column and converts them in the DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame with cleaned string cells.
        sample_size (int): Number of rows to sample for inferring data type.
        verbose (bool): Whether to print logs of what was inferred.

    Returns:
        Tuple[pd.DataFrame, Dict[str, str]]:
            - Converted DataFrame.
            - Dictionary mapping column names to inferred types.
    """
    inferred_types = {}
    df_converted = df.copy()

    for col in df.columns:
        sample = df[col].dropna()
        if sample.empty:
            inferred_types[col] = "string"
            df_converted[col] = df[col].astype(str)
            if verbose:
                print(f"[{col}] All values empty or NaN, defaulting to string.")
            continue

        sample = sample.sample(
            min(len(sample), sample_size), random_state=42
        )

        # Try integer
        try:
            converted = pd.to_numeric(sample, errors="raise", downcast="integer")
            if not converted.isna().all():
                df_converted[col] = pd.to_numeric(df[col], errors="coerce", downcast="integer")
                inferred_types[col] = "integer"
                if verbose:
                    print(f"[{col}] Inferred as integer.")
                continue
        except Exception:
            pass

        # Try float
        try:
            converted = pd.to_numeric(sample, errors="raise", downcast="float")
            if not converted.isna().all():
                df_converted[col] = pd.to_numeric(df[col], errors="coerce", downcast="float")
                inferred_types[col] = "float"
                if verbose:
                    print(f"[{col}] Inferred as float.")
                continue
        except Exception:
            pass

        # Try datetime
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                converted = pd.to_datetime(sample, errors="raise")
            if not converted.isna().all():
                df_converted[col] = pd.to_datetime(df[col], errors="coerce")
                inferred_types[col] = "datetime"
                if verbose:
                    print(f"[{col}] Inferred as datetime.")
                continue
        except Exception:
            pass

        # Default to string
        try:
            inferred_types[col] = "string"
            df_converted[col] = df[col].astype(str)
            if verbose:
                print(f"[{col}] Defaulting to string.")
        except Exception:
            pass

    return df_converted, inferred_types


def enforce_metadata_string_dtypes(metadata_df, verbose=False):
    """
    Ensures critical metadata columns have string dtype to avoid dtype conflicts during fills.

    Args:
        metadata_df (pd.DataFrame): The metadata DataFrame to modify in-place.
        verbose (bool): If True, prints confirmation messages.

    Returns:
        pd.DataFrame: The DataFrame with enforced string dtypes.
    """
    # List of metadata columns you want as strings
    string_columns = [
        "is_identifier",
        "is_categorical",
        "category_values",
        "analysis_category",
        "stakeholder_category",
    ]

    for col in string_columns:
        if col in metadata_df.columns:
            metadata_df[col] = metadata_df[col].astype(str)
            if verbose:
                print(f"[enforce_metadata_string_dtypes] Casted '{col}' to string dtype.")

    return metadata_df


import duckdb

def clean_duckdb_table_with_metadata(
    con: duckdb.DuckDBPyConnection,
    data_table: str,
    metadata_table: str,
    null_replacements: list = ["nan", "NaN", "N/A", ""],
    lowercase_categoricals: bool = False,
    verbose: bool = False
):
    """
    Cleans a DuckDB table by:
    - Trimming whitespace in VARCHAR columns
    - Standardizing null-like values
    - Optionally lowercasing categorical columns
    """
    # Step 1: Fetch metadata
    meta_df = con.execute(f"SELECT column_name, data_type, is_categorical FROM {metadata_table}").fetchdf()

    # Step 2: Identify VARCHAR columns
    varchar_cols = meta_df.loc[meta_df["data_type"].str.upper() == "VARCHAR", "column_name"].tolist()

    if verbose:
        print(f"Found {len(varchar_cols)} VARCHAR columns to clean: {varchar_cols}")

    # Step 3: Build and execute TRIM updates
    for col in varchar_cols:
        # Trim whitespace
        trim_sql = f"""
        UPDATE {data_table}
        SET "{col}" = TRIM("{col}")
        WHERE "{col}" IS NOT NULL;
        """
        con.execute(trim_sql)
        if verbose:
            print(f"Trimmed column '{col}'")

        # Standardize null-like values
        for val in null_replacements:
            null_sql = f"""
            UPDATE {data_table}
            SET "{col}" = NULL
            WHERE "{col}" = '{val}';
            """
            con.execute(null_sql)
        if verbose:
            print(f"Standardized null-like values in column '{col}'")

        # Optionally lowercase categoricals
        if lowercase_categoricals:
            is_cat = meta_df.loc[meta_df["column_name"] == col, "is_categorical"].values[0]
            if str(is_cat).strip().lower() == "true":
                lower_sql = f"""
                UPDATE {data_table}
                SET "{col}" = LOWER("{col}")
                WHERE "{col}" IS NOT NULL;
                """
                con.execute(lower_sql)
                if verbose:
                    print(f"Lowercased values in categorical column '{col}'")

    if verbose:
        print("✅ Cleaning complete.")