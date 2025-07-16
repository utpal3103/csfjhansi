

import os
import pandas as pd


# Save a pandas DataFrame to a CSV file, creating folder if needed.
def save_dataframe_to_csv(
    df: pd.DataFrame,
    folder_path: str,
    filename: str,
    index: bool = False,
    encoding: str = "utf-8-sig",
    verbose: bool = True
) -> str:
    """
    Save a pandas DataFrame to a CSV file, creating folder if needed.

    Args:
        df (pd.DataFrame): The dataframe to save.
        folder_path (str): Directory where the file will be saved.
        filename (str): Name of the file (with or without .csv).
        index (bool): Whether to include the dataframe index.
        encoding (str): Encoding to use (default: 'utf-8-sig' for Excel compatibility).

    Returns:
        str: Full path of the saved file.
    """
    # Ensure folder exists
    os.makedirs(folder_path, exist_ok=True)

    # Ensure .csv extension
    if not filename.lower().endswith(".csv"):
        filename += ".csv"

    # Full file path
    file_path = os.path.join(folder_path, filename)

    # Save CSV
    df.to_csv(file_path, index=index, encoding=encoding)

    if verbose:
        print(f"[✅] Saved CSV to {file_path}")
    
    return file_path


# Save a pandas DataFrame to a CSV file, creating folder if needed.
def save_data_to_csv_by_col_seq(
    data_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    folder_path: str,
    filename: str,
    index: bool = False,
    encoding: str = "utf-8-sig",
    verbose: bool = True
) -> str:
    """
    Save a pandas DataFrame to a CSV file, after reordering columns based on metadata.

    Args:
        data_df (pd.DataFrame): The dataframe to save.
        metadata_df (pd.DataFrame): The metadata dataframe.
        folder_path (str): Directory where the file will be saved.
        filename (str): Name of the file (with or without .csv).
        index (bool): Whether to include the dataframe index.
        encoding (str): Encoding to use (default: 'utf-8-sig' for Excel compatibility).

    Returns:
        str: Full path of the saved file.
    """
    # Get the ordered column names
    ordered_columns = (
        metadata_df
        .sort_values("pre_enrichment_col_seq")
        ["column_name"]
        .tolist()
    )
    # Reorder the data_df
    data_df_ordered = data_df.reindex(columns=ordered_columns)

    filepath = save_dataframe_to_csv(data_df_ordered, folder_path, filename, index, encoding, verbose)
    
    return filepath

# Save a pandas DataFrame to a CSV file, creating folder if needed.
def save_metadata_to_csv_by_col_seq(
    metadata_df: pd.DataFrame,
    folder_path: str,
    filename: str,
    index: bool = False,
    encoding: str = "utf-8-sig",
    verbose: bool = True
) -> str:
    """
    Save a pandas DataFrame to a CSV file, after reordering columns based on pre_enrichment_col_seq in metadata.

    Args:
        metadata_df (pd.DataFrame): The metadata dataframe.
        folder_path (str): Directory where the file will be saved.
        filename (str): Name of the file (with or without .csv).
        index (bool): Whether to include the dataframe index.
        encoding (str): Encoding to use (default: 'utf-8-sig' for Excel compatibility).

    Returns:
        str: Full path of the saved file.
    """
    metadata_df_ordered = metadata_df.sort_values("pre_enrichment_col_seq")
    filepath = save_dataframe_to_csv(metadata_df_ordered, folder_path, filename, index, encoding, verbose)
    
    return filepath


# Batch items into smaller chunks
def batch_items(items, batch_size):
    """
    Yield successive batches of a list.

    Args:
        items (list): The list to be batched
        batch_size (int): Number of items per batch

    Yields:
        list: A batch of items
    """
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]


# Clean a list of strings by stripping whitespace, removing newlines,
# and replacing/removing unwanted characters.
def clean_string_list(items):
    """
    Clean a list of strings by stripping whitespace, removing newlines,
    and replacing/removing unwanted characters.

    Args:
        items (list of str): Any list of strings (headers, values, etc.)

    Returns:
        list of str: Cleaned strings
    """
    cleaned = []
    for item in items:
        if not isinstance(item, str):
            item = str(item)
        item = item.strip()
        item = item.replace("\n", " ").replace("\r", "")
        item = item.replace("?", "").replace(":", "").replace("/", "-")
        item = item.replace("  ", " ")
        cleaned.append(item)
    return cleaned


# Clean a single cell value by stripping unwanted characters if it's a string.
def clean_cell_preserve_type(value):
    """
    Clean a single cell value by stripping unwanted characters if it's a string.
    Preserves original type for non-strings.

    Args:
        value: Any cell value (str, int, float, etc.)

    Returns:
        Cleaned value with original type preserved where possible.
    """
    if isinstance(value, str):
        value = value.strip().replace("\n", " ").replace("\r", "")
        value = value.replace("  ", " ")
        return value
    return value

# Convert column dtype to int, float, or datetime
import pandas as pd

def convert_column_dtype(series, target_type="auto", date_format=None):
    """
    Cleans and converts a pandas Series to the target data type if needed.

    Args:
        series (pd.Series): The column to convert
        target_type (str): 'int', 'float', 'datetime', or 'auto'
        date_format (str): Optional date format string (for datetime)

    Returns:
        pd.Series: Cleaned and converted column
    """
    if series.dtype in ["int64", "float64", "datetime64[ns]"]:
        return series  # Already clean

    # Step 1: Clean the string if it's not a known type
    series = series.astype(str).str.strip()

    try:
        if target_type == "auto":
            try:
                # Try numeric conversion first
                return pd.to_numeric(series, errors="raise")
            except:
                # Try datetime conversion if numeric fails
                return pd.to_datetime(series, format=date_format, errors="raise")

        elif target_type == "int":
            return pd.to_numeric(series, errors="raise").astype("Int64")

        elif target_type == "float":
            return pd.to_numeric(series, errors="raise")

        elif target_type == "datetime":
            return pd.to_datetime(series, format=date_format, errors="raise")

        else:
            print(f"Unsupported target_type: {target_type}")
            return series

    except Exception as e:
        print(f"[WARN] Conversion failed for column '{series.name}': {e}")
        return series  # Return original if conversion fails


# Save column mapping to CSV
import os
import pandas as pd

def save_column_mapping(mapping_list, output_path="../data/interim/column_mapping1.csv"):
    """
    Saves a list of column header mappings (with original, translated, and short names) to a CSV file.

    Args:
        mapping_list (list of dict): Each dict should contain 'original_name', 'translated_name', 'short_name'
        output_path (str): Path where the CSV will be saved

    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Convert list of dicts to DataFrame
        df = pd.DataFrame(mapping_list)

        # Save to CSV
        df.to_csv(output_path, index=False)

        print(f"✅ Column mapping saved to: {output_path}")
        return True

    except Exception as e:
        print(f"❌ Failed to save column mapping: {e}")
        return False


# Rename columns based on mapping CSV

import pandas as pd
   
def rename_columns_from_mapping(df, mapping_path):
    """
    Renames DataFrame columns using a mapping CSV containing original_name and short_name.

    Args:
        df (pd.DataFrame): The raw DataFrame with original column names
        mapping_path (str): Path to the CSV with 'original_name' and 'short_name' columns

    Returns:
        pd.DataFrame: New DataFrame with renamed columns
    """
    mapping_df = pd.read_csv(mapping_path)
    
    # Build rename dictionary
    rename_dict = dict(zip(mapping_df['original_name'], mapping_df['short_name']))
    
    # Rename columns
    df_renamed = df.rename(columns=rename_dict)
    
    return df_renamed

# Rename columns based on order instead of name match
def rename_columns_by_index(df, new_column_names):
    """
    Rename columns based on order instead of name match.
    `new_column_names` should be a list of the same length as df.columns
    """
    if len(df.columns) != len(new_column_names):
        raise ValueError("Column count mismatch between DataFrame and new names")
    
    df.columns = new_column_names
    return df