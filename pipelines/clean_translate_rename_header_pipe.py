import pandas as pd
import os

from utils.data_utils import clean_string_list, rename_columns_from_mapping, save_column_mapping
from utils.llm_utils import translate_headers_via_llm
from utils.file_utils import ensure_directory

def clean_translate_rename_headers_pipe(
    df: pd.DataFrame,
    column_mapping_path: str,
    output_path: str,
    batch_size: int = 5,
    model: str = "gpt-4",
    use_existing_mapping: bool = True
) -> pd.DataFrame:
    """
    Cleans, translates, and renames column headers of a DataFrame. 
    Saves the column mapping and the cleaned DataFrame to disk.

    Args:
        df (pd.DataFrame): Raw input DataFrame
        column_mapping_path (str): Path to save or load column mapping CSV
        output_path (str): Path to save the final cleaned DataFrame
        batch_size (int): Batch size for LLM translation
        model (str): Model to use for LLM
        use_existing_mapping (bool): If True, skips LLM call and loads mapping from file

    Returns:
        pd.DataFrame: Updated DataFrame with cleaned and renamed headers
    """
    print("🔹 Cleaning headers...")
    cleaned_headers = clean_string_list(df.columns.tolist())
    df.columns = cleaned_headers

    if use_existing_mapping and os.path.exists(column_mapping_path):
        print(f"✅ Using existing mapping from: {column_mapping_path}")
        mapping_df = pd.read_csv(column_mapping_path)
    else:
        print("🔹 Translating headers via LLM...")
        header_map = translate_headers_via_llm(cleaned_headers, batch_size=batch_size, model=model)
        mapping_df = pd.DataFrame(header_map)
        save_column_mapping(mapping_df, column_mapping_path)
        print(f"✅ Column mapping saved to: {column_mapping_path}")

    print("🔹 Renaming columns using mapping...")
    df = rename_columns_from_mapping(df, mapping_df)

    print("🔹 Saving cleaned DataFrame...")
    ensure_directory(output_path)
    df.to_csv(output_path, index=False)
    print(f"✅ Cleaned DataFrame saved to: {output_path}")

    return df