import os
import pandas as pd
from utils.clean_utils import (
    clean_dataframe_cells,
    infer_and_convert_column_types,
    enforce_metadata_string_dtypes
)
from utils.feature_utils import process_translation_and_sentiment
from utils.data_utils import save_data_to_csv_by_col_seq, save_metadata_to_csv_by_col_seq

def run_translate_and_sentiment_enrichment_pipeline(
    data_csv_path: str,
    metadata_csv_path: str,
    save_data_folder: str,
    save_metadata_folder: str,
    base_filename: str = "enriched_dataset",
    verbose: bool = True
):
    """
    Pipeline: Translate and enrich dataset with sentiment analysis.

    This pipeline performs:
    - Loading pre-enrichment dataset and metadata.
    - Cleaning data cells and enforcing string dtypes.
    - Inferring column types.
    - Translating categorical columns (Hindi -> English).
    - Inferring sentiment where specified.
    - Updating metadata with translated categories and sentiment columns.
    - Saving enriched dataset and metadata to CSV files.

    Args:
        data_csv_path (str): Path to pre-enrichment data CSV.
        metadata_csv_path (str): Path to pre-enrichment metadata CSV.
        save_data_folder (str): Directory where enriched data will be saved.
        save_metadata_folder (str): Directory where enriched metadata will be saved.
        base_filename (str): Base filename to use for output CSVs.
        verbose (bool): Whether to print progress messages.

    Returns:
        tuple[str, str]: Paths to saved enriched data CSV and metadata CSV.
    """
    if verbose:
        print("[🚀] Starting enrichment pipeline...")

    # Load data
    data_df = pd.read_csv(data_csv_path)
    metadata_df = pd.read_csv(metadata_csv_path, na_values=["nan", "NaN", ""])

    if verbose:
        print(f"[✅] Loaded data ({data_df.shape}) and metadata ({metadata_df.shape}).")

    # Clean data cells
    data_df = clean_dataframe_cells(data_df)
    if verbose:
        print("[✅] Cleaned data cells.")

    # Infer and convert column types
    data_df, _ = infer_and_convert_column_types(data_df, verbose=False)
    if verbose:
        print("[✅] Inferred column types.")

    # Enforce string dtypes in metadata
    metadata_df = enforce_metadata_string_dtypes(metadata_df, verbose=False)
    if verbose:
        print("[✅] Enforced string dtypes in metadata.")

    # Enrichment step
    data_df, metadata_df = process_translation_and_sentiment(
        data_df,
        metadata_df,
        verbose=verbose
    )

    if verbose:
        print("[✅] Enrichment (translation and sentiment) complete.")

    # Save enriched data and metadata
    data_path = save_data_to_csv_by_col_seq(
        data_df,
        metadata_df,
        folder_path=save_data_folder,
        filename=f"{base_filename}_data"
    )

    metadata_path = save_metadata_to_csv_by_col_seq(
        metadata_df,
        folder_path=save_metadata_folder,
        filename=f"{base_filename}_metadata"
    )

    if verbose:
        print("[✅] Saved enriched data and metadata.")

    return data_path, metadata_path