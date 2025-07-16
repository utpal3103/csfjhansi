# utils/pipeline_utils.py (or wherever you prefer)

from csfdata.utils.clean_utils import clean_dataframe_cells, infer_and_convert_column_types

def run_simple_cleaning_pipeline(raw_df, verbose=True):
    """
    Cleans the DataFrame and infers/converts column data types.

    Args:
        raw_df (pd.DataFrame): Raw loaded DataFrame.
        verbose (bool): Whether to print progress.

    Returns:
        pd.DataFrame: Cleaned and typed DataFrame.
    """
    if verbose:
        print("🔹 Cleaning cells...")
    cleaned_df = clean_dataframe_cells(raw_df)

    if verbose:
        print("🔹 Inferring and converting data types...")
    typed_df, inferred_types = infer_and_convert_column_types(cleaned_df, verbose=verbose)

    if verbose:
        print("✅ Cleaning pipeline complete.")
    return typed_df