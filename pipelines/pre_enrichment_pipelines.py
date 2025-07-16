from utils.clean_utils import (
    clean_dataframe_cells,
    infer_and_convert_column_types,
    enforce_metadata_string_dtypes
)
from utils.metadata_utils import (
    fill_original_column_name_metadata,
    fill_desc_en_metadata,
    fill_data_type_metadata,
    fill_count_metadata,
    fill_original_col_seq_metadata,
    fill_is_identifier_metadata,
    fill_is_categorical_metadata,
    fill_category_values_metadata,
    fill_analysis_category_metadata,
    fill_pre_enrichment_col_seq_metadata
)
from utils.data_utils import save_dataframe_to_csv  

def run_pre_enrichment_pipeline(
    data_df,
    metadata_df,
    save_data_folder: str,
    save_metadata_folder: str,
    base_filename: str,
    verbose: bool = True
):
    """
    Run the full pre-enrichment pipeline:
    cleaning, type conversion, metadata filling, saving.

    Args:
        data_df (pd.DataFrame): Raw dataset.
        metadata_df (pd.DataFrame): Metadata dataframe.
        save_data_folder (str): Directory to save processed data.
        save_metadata_folder (str): Directory to save processed metadata.
        base_filename (str): Base name for saved files.
        verbose (bool): Whether to print progress messages.
    Returns:
        tuple: (Cleaned data_df, metadata_df)
    """
    if verbose:
        print("[🚀] Starting pre-enrichment pipeline...")

    # 1. Clean cells
    if verbose:
        print("[1️⃣] Cleaning dataframe cells...")
    data_df = clean_dataframe_cells(data_df)
    if verbose:
        print("[✅] Cleaning complete.")

    # 2. Infer + convert column types
    if verbose:
        print("[2️⃣] Inferring and converting column data types...")
    data_df, inferred_types = infer_and_convert_column_types(data_df, verbose=False)
    if verbose:
        print("[✅] Type inference complete.")

    # Enforce string dtypes for metadata columns
    if verbose:
        print("[3️⃣] Enforcing string dtypes for metadata columns...")
    metadata_df = enforce_metadata_string_dtypes(metadata_df, verbose=False)
    if verbose:
        print("[✅] String dtypes enforcement complete.")

    # 3. Fill metadata
    if verbose:
        print("[3️⃣] Filling metadata fields...")

    metadata_df = fill_original_column_name_metadata(metadata_df) # Fills original_column_name 
    metadata_df = fill_desc_en_metadata(metadata_df) # Fills desc_en  
    metadata_df = fill_data_type_metadata(data_df, metadata_df) # Fills data_type
    metadata_df = fill_count_metadata(data_df, metadata_df) # Fills count
    metadata_df = fill_original_col_seq_metadata(data_df, metadata_df) # Fills original_col_seq
    metadata_df = fill_is_identifier_metadata(data_df, metadata_df) # Fills is_identifier
    metadata_df, unique_values_dict = fill_is_categorical_metadata(data_df, metadata_df) # Fills is_categorical
    metadata_df = fill_category_values_metadata(data_df, metadata_df, unique_values_dict) # Fills category_values
    metadata_df = fill_analysis_category_metadata(data_df, metadata_df) # Fills analysis_category
    metadata_df = fill_pre_enrichment_col_seq_metadata(data_df, metadata_df) # Fills pre_enrichment_col_seq

    if verbose:
        print("[✅] Metadata filling complete.")

    # 4. Save cleaned data
    if verbose:
        print("[💾] Saving cleaned data...")
    save_dataframe_to_csv(
        df=data_df,
        folder_path=save_data_folder,
        filename=f"{base_filename}_pre_enrichment_data.csv"
    )

    # 5. Save metadata
    if verbose:
        print("[💾] Saving metadata...")
    save_dataframe_to_csv(
        df=metadata_df,
        folder_path=save_metadata_folder,
        filename=f"{base_filename}_pre_enrichment_metadata.csv"
    )

    if verbose:
        print("[🏁] Pre-enrichment pipeline complete.")

    return data_df, metadata_df