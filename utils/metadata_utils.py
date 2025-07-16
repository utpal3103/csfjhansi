"""
Metadata Utilities
-------------------
Functions to fill and update metadata columns in the metadata DataFrame.
"""

import pandas as pd
from typing import Optional, List, Dict, Union

# _original_column_name_method helper function - to be designed for other usecases
def _original_column_name_method(column_name: str) -> str:
    """
    Placeholder function for original column name.
    Replace with actual logic or LLM call later.
    """
    return column_name  # fallback to short_name

# Fill original_column_name metadata
def fill_original_column_name_metadata(
    metadata_df: pd.DataFrame,
    columns: list[str] | None = None
) -> pd.DataFrame:
    """
    Fill original_column_name metadata field.
    If already filled, skip.
    If empty, use _original_column_name_method.
    """
    cols_to_process = columns or metadata_df["column_name"].tolist()

    for col in cols_to_process:
        current_val = metadata_df.loc[
            metadata_df["column_name"] == col, "original_column_name"
        ].values[0]

        if pd.isna(current_val) or current_val == "":
            orig_name = _original_column_name_method(col)
            metadata_df.loc[
                metadata_df["column_name"] == col, "original_column_name"
            ] = orig_name

    return metadata_df

# _desc_en_filler helper function - to be designed for other usecases
def _desc_en_method(column_name: str) -> str:
    """
    Placeholder function to generate descriptions.
    Replace with actual logic or LLM call later.
    """
    return "Description to be added later"

# Fill desc_en metadata
def fill_desc_en_metadata(
    metadata_df: pd.DataFrame,
    columns: list[str] | None = None
) -> pd.DataFrame:
    """
    Fill description_en metadata field.
    If already filled, skip.
    If empty, use _desc_en_method.
    """
    cols_to_process = columns or metadata_df["column_name"].tolist()

    for col in cols_to_process:
        current_val = metadata_df.loc[
            metadata_df["column_name"] == col, "desc_en"
        ].values[0]

        if pd.isna(current_val) or current_val == "":
            description = _desc_en_method(col)
            metadata_df.loc[
                metadata_df["column_name"] == col, "desc_en"
            ] = description

    return metadata_df

# Fill data_type metadata
def fill_data_type_metadata(
    data_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    columns: Optional[Union[str, List[str]]] = None
) -> pd.DataFrame:
    """
    Fill 'data_type' column in metadata_df by inferring from data_df dtypes.
    Only fills empty cells.
    """
    if columns is None or (isinstance(columns, list) and len(columns) == 0):
        target_cols = data_df.columns.tolist()
    elif isinstance(columns, str):
        target_cols = [columns]
    else:
        target_cols = columns

    for col in target_cols:
        if 'data_type' not in metadata_df.columns:
            raise ValueError("'data_type' column does not exist in metadata_df.")

        # Skip if already filled
        if pd.notna(metadata_df.loc[metadata_df["column_name"] == col, "data_type"]).any():
            continue

        dtype = data_df[col].dtype
        dtype_str = str(dtype)

        # Convert pandas dtype to friendly string
        if "int" in dtype_str:
            dtype_str = "integer"
        elif "float" in dtype_str:
            dtype_str = "float"
        elif "datetime" in dtype_str:
            dtype_str = "datetime"
        else:
            dtype_str = "string"

        metadata_df.loc[metadata_df["column_name"] == col, "data_type"] = dtype_str

    return metadata_df

# Fill COUNT metadata
def fill_count_metadata(
    data_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    columns: Optional[Union[str, List[str]]] = None
) -> pd.DataFrame:
    """
    Fill 'count' column in metadata_df with non-null counts.
    Only fills empty cells.
    """
    if columns is None or (isinstance(columns, list) and len(columns) == 0):
        target_cols = data_df.columns.tolist()
    elif isinstance(columns, str):
        target_cols = [columns]
    else:
        target_cols = columns

    for col in target_cols:
        if 'count' not in metadata_df.columns:
            raise ValueError("'count' column does not exist in metadata_df.")

        # Skip if already filled
        if pd.notna(metadata_df.loc[metadata_df["column_name"] == col, "count"]).any():
            continue

        count = data_df[col].count()
        metadata_df.loc[metadata_df["column_name"] == col, "count"] = count

    return metadata_df

# Fill ORIGINAL_COL_SEQ metadata
def fill_original_col_seq_metadata(data_df, metadata_df, verbose=False):
    """
    Populate 'original_col_seq' and 'count' in metadata_df based on data_df.
    
    - original_col_seq = sequence number of the column
    - count = number of non-null entries in the column

    Args:
        metadata_df (pd.DataFrame): Metadata dataframe to update.
        data_df (pd.DataFrame): Cleaned, typed data.
        verbose (bool): Print details if True.

    Returns:
        pd.DataFrame: Updated metadata dataframe.
    """
    for idx, col in enumerate(data_df.columns, start=1):
        # Find metadata row matching this column
        row_mask = metadata_df["column_name"] == col
        
        # original_col_seq
        if "original_col_seq" in metadata_df.columns:
            existing_seq = metadata_df.loc[row_mask, "original_col_seq"].values
            if len(existing_seq) == 0 or pd.isna(existing_seq[0]):
                metadata_df.loc[row_mask, "original_col_seq"] = idx
                if verbose:
                    print(f"[{col}] original_col_seq set to {idx}.")

    return metadata_df

# Fill IS_IDENTIFIER metadata
def fill_is_identifier_metadata(data_df, metadata_df, columns=None, verbose=False):
    """
    For each column, fill is_identifier=True if all non-null values are unique.
    """
    if columns is None:
        columns = data_df.columns.tolist()
    
    for col in columns:
        # Skip if already filled
        if col not in metadata_df["column_name"].values:
            print("🚨 Column not found in metadata_df:", repr(col))
            raise ValueError(f"Column '{col}' not present in metadata dataframe.")
        current_value = metadata_df.loc[metadata_df["column_name"] == col, "is_identifier"]
        val = current_value.iloc[0]
        val_str = str(val).strip().lower()
        if val_str not in ("", "nan"):
            if verbose:
                print(f"[{col}] is_identifier already populated: {val}")
            continue
        
        n_unique = data_df[col].nunique(dropna=True)
        n_notnull = data_df[col].notnull().sum()
        
        is_identifier = n_unique == n_notnull and n_unique > 0
        
        metadata_df.loc[metadata_df["column_name"] == col, "is_identifier"] = str(is_identifier)
        
        if verbose:
            print(f"[{col}] Filled is_identifier = {is_identifier}")

    return metadata_df

# Fill IS_CATEGORICAL metadata and also return unique values as a dictionary: the list of unique values for each column
def fill_is_categorical_metadata(data_df, metadata_df, columns=None, unique_threshold=50):
    """
    Fill 'is_categorical' metadata for columns in metadata_df.

    Args:
        data_df (pd.DataFrame): The main data table.
        metadata_df (pd.DataFrame): The metadata table.
        columns (list or None): Which columns to fill. If None, fill for all columns.
        unique_threshold (int): Max number of unique values to consider categorical.

    Returns:
        metadata_df (pd.DataFrame): Updated metadata.
        dict: {col_name: list of unique values}
    """
    if columns is None:
        columns = data_df.columns.tolist()

    unique_values_dict = {}

    for col in columns:
        # Only fill if empty
        # current_value = metadata_df.loc[metadata_df["column_name"] == col, "is_categorical"]
        # print("Current_value: ", current_value)
        # print("Type of value:", type(current_value.iloc[0]))
        # print("Condition: ", not current_value.isna().all() and current_value.iloc[0] != "")
        # if not current_value.isna().all() and current_value.iloc[0] != "":
        #     # Already filled
        #     continue
        current_value = metadata_df.loc[metadata_df["column_name"] == col, "is_categorical"]
        val = current_value.iloc[0]
        val_str = str(val).strip().lower()
        if val_str not in ("", "nan"):
            continue
        
        n_unique = data_df[col].nunique(dropna=True)
        if n_unique <= unique_threshold:
            metadata_df.loc[metadata_df["column_name"] == col, "is_categorical"] = str(True)
            unique_values = sorted(data_df[col].dropna().unique().tolist())
            unique_values_dict[col] = unique_values
        else:
            metadata_df.loc[metadata_df["column_name"] == col, "is_categorical"] = str(False)

    return metadata_df, unique_values_dict


# Fill category_values metadata using the unique values dictionary received from fill_is_categorical_metadata function
def fill_category_values_metadata(data_df, metadata_df, unique_values_dict, columns=None, verbose=False):
    """
    Fill 'category_values' metadata for columns in metadata_df.

    Args:
        data_df (pd.DataFrame): Main data table. (Not used but kept for consistent signature)
        metadata_df (pd.DataFrame): The metadata table.
        unique_values_dict (dict): {col_name: list of unique values}
        columns (list or None): Which columns to fill. If None, fill for all columns in the dict.
        verbose (bool): If True, print progress.

    Returns:
        metadata_df (pd.DataFrame): Updated metadata.
    """
    if columns is None:
        cols_to_fill = list(unique_values_dict.keys())
    else:
        # Only include columns that actually have unique values calculated
        cols_to_fill = [col for col in columns if col in unique_values_dict]

    for col in cols_to_fill:
        current_value = metadata_df.loc[metadata_df["column_name"] == col, "category_values"]
        val = current_value.iloc[0]
        val_str = str(val).strip().lower()
        if val_str not in ("", "nan"):
            if verbose:
                print(f"[{col}] category_values already populated.")
            continue

        metadata_df.loc[
            metadata_df["column_name"] == col, "category_values"
        ] = str(unique_values_dict[col])

        if verbose:
            print(f"[{col}] category_values filled with {len(unique_values_dict[col])} unique values.")

    return metadata_df

# Fill _default_analysis_category_method helper function - to be designed for other usecases
def _default_analysis_category_method(col_name, data_df, metadata_df):
    """
    Dummy fallback that returns a placeholder.
    Later, you can replace this with a real implementation.
    """
    return "unclassified"

# Fill analysis_category metadata
def fill_analysis_category_metadata(
    data_df,
    metadata_df,
    columns=None
):
    """
    Fills 'analysis_category' metadata column.
    If already populated, keeps existing.
    If missing, fills using _default_analysis_category_method.
    
    Args:
        data_df (pd.DataFrame): The main dataset.
        metadata_df (pd.DataFrame): The metadata table.
        columns (list of str or None): Which columns to fill; if None, fills all.
    
    Returns:
        pd.DataFrame: Updated metadata.
    """
    if columns is None:
        cols_to_fill = metadata_df["column_name"].tolist()
    else:
        cols_to_fill = columns

    for col in cols_to_fill:
        # Retrieve current value
        existing = metadata_df.loc[metadata_df["column_name"] == col, "analysis_category"]

        if pd.notnull(existing).any() and existing.iloc[0] != "":
            # Already populated
            continue

        # Otherwise, fill using fallback method
        value = _default_analysis_category_method(col, data_df, metadata_df)

        metadata_df.loc[metadata_df["column_name"] == col, "analysis_category"] = value

    return metadata_df

# _pre_enrichment_seq_method helper function - to be designed for other usecases
def _pre_enrichment_seq_method(column_name: str) -> int:
    """
    Dummy helper to assign pre-enrichment sequence.
    You can replace this logic later.

    Args:
        column_name (str): Column name.

    Returns:
        int: Sequence number.
    """
    # For now, simply use 999 as placeholder
    return 999

# Fill pre_enrichment_col_seq metadata
def fill_pre_enrichment_col_seq_metadata(
    data_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Fill the 'pre_enrichment_col_seq' metadata column.

    If already present, keeps the existing value.
    If missing, uses a helper function (dummy by default) to fill in a value.

    Args:
        data_df (pd.DataFrame): The cleaned raw data.
        metadata_df (pd.DataFrame): The metadata DataFrame.
        columns (Optional[List[str]]): List of column names to process. If None, all columns.

    Returns:
        pd.DataFrame: Updated metadata DataFrame.
    """
    # If no columns specified, default to all columns
    if columns is None:
        columns = data_df.columns.tolist()

    # For each column, check & fill
    for col in columns:
        existing_value = metadata_df.loc[metadata_df["column_name"] == col, "pre_enrichment_col_seq"].values
        if existing_value.size > 0 and pd.notnull(existing_value[0]):
            # Already filled, skip
            continue

        # Call dummy function
        seq = _pre_enrichment_seq_method(col)

        # Fill in metadata
        metadata_df.loc[metadata_df["column_name"] == col, "pre_enrichment_col_seq"] = seq

    return metadata_df

