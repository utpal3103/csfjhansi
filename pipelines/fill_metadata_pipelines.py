import pandas as pd
from utils.metadata_utils import (
    fill_data_type_metadata,
    fill_count_metadata,
    fill_original_col_seq_metadata,
    fill_is_identifier_metadata,
    fill_is_categorical_metadata,
    fill_category_values_metadata,
    fill_analysis_category_metadata,
    fill_pre_enrichment_col_seq_metadata,
    fill_desc_en_metadata,
    fill_original_column_name_metadata
)

def run_zero_stage_metadata_pipeline(
    data_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    columns: list[str] | None = None,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Pipeline to fill zero-stage mandatory and optional metadata.

    Args:
        data_df (pd.DataFrame): Cleaned data DataFrame with correct dtypes.
        metadata_df (pd.DataFrame): Metadata DataFrame to be enriched.
        columns (list[str] or None): Specific columns to process. If None, all columns are processed.
        verbose (bool): Whether to print progress logs.

    Returns:
        pd.DataFrame: Updated metadata DataFrame.
    """
    if verbose:
        print("=== Filling Zero-Stage Mandatory Metadata ===")
    metadata_df = fill_data_type_metadata(data_df, metadata_df, columns)

    if verbose:
        print("\n=== Filling Zero-Stage Optional Metadata ===")
    metadata_df = fill_original_col_seq_metadata(data_df, metadata_df, columns)
    metadata_df = fill_count_metadata(data_df, metadata_df, columns)
    metadata_df = fill_desc_en_metadata(metadata_df, columns)
    metadata_df = fill_original_column_name_metadata(metadata_df, columns)
    metadata_df, unique_values_dict = fill_is_categorical_metadata(data_df, metadata_df, columns)

    metadata_df = fill_is_identifier_metadata(data_df, metadata_df, columns)
    metadata_df = fill_category_values_metadata(metadata_df, unique_values_dict, columns)
    metadata_df = fill_analysis_category_metadata(metadata_df, columns)
    metadata_df = fill_pre_enrichment_col_seq_metadata(metadata_df, columns)
    

    if verbose:
        print("\n✅ Zero-stage metadata pipeline complete.")

    return metadata_df