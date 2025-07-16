# Project Functions Reference

This document provides a comprehensive reference of all utility functions across the project.

## Table of Contents
- [Clean Utilities](#clean-utilities)
- [DuckDB Utilities](#duckdb-utilities)
- [Feature Utilities](#feature-utilities)
- [Metadata Utilities](#metadata-utilities)

## Clean Utilities

### `clean_dataframe_cells(df: pd.DataFrame) -> pd.DataFrame`
Cleans up all string cells in the dataframe by:
- Stripping whitespace
- Replacing special characters (?, :, /, newlines)
- Replacing double spaces
- Normalizing null-like values to np.nan

### `infer_and_convert_column_types(df: pd.DataFrame, sample_size: int = 100, verbose: bool = False) -> Tuple[pd.DataFrame, Dict[str, str]]`
Infers data types for each column in a DataFrame by sampling rows and attempts to convert columns to the most appropriate type (integer, float, datetime, or string). Returns the converted DataFrame and a dictionary mapping column names to inferred types.

### `enforce_metadata_string_dtypes(metadata_df, verbose=False)`
Enforces string dtype on specific metadata columns to avoid dtype conflicts. Modifies the metadata DataFrame in place and returns it.

### `clean_duckdb_table_with_metadata(con: duckdb.DuckDBPyConnection, data_table: str, metadata_table: str, null_replacements: list = ["nan", "NaN", "N/A", ""], lowercase_categoricals: bool = False, verbose: bool = False)`
Cleans a DuckDB table by trimming whitespace in VARCHAR columns, standardizing null-like values to NULL, and optionally lowercasing categorical columns based on metadata. Uses SQL UPDATE statements executed via DuckDB connection.

## DuckDB Utilities

### `load_csv_to_duckdb_with_schema_csv(con: duckdb.DuckDBPyConnection, csv_path: str, schema_csv_path: str, table_name: str, overwrite: bool = False, verbose: bool = True)`
Loads a CSV into DuckDB using a schema CSV file that specifies column names and data types. The schema CSV must have 'metadata_field' and 'data_type' columns.

### `load_csv_to_duckdb_with_metadata_df(con: duckdb.DuckDBPyConnection, csv_path: str, metadata_df: pd.DataFrame, table_name: str, if_exists: str = "fail", verbose: bool = True)`
Loads a CSV into DuckDB using column names and data types from a metadata DataFrame. Supports 'fail', 'replace', or 'append' modes.

## Feature Utilities

### `translate_and_replace_categorical_columns(data_df, metadata_df, llm_function, columns=None, verbose=False)`
Replaces categorical column values with their translations using the provided LLM function, keeping the same column names, and updates metadata.

### `translate_and_add_sentiment_column(data_df, metadata_df, llm_function, columns=None, verbose=False)`
Translates categorical values and adds a sentiment column. Replaces original column values with translations and updates metadata category_values.

### `process_translation_and_sentiment_old(data_df, metadata_df, columns=None, verbose=False)`
Processes categorical columns by translating Hindi text and/or inferring sentiment based on metadata columns 'lang' and 'sentiment_required'.

### `process_translation_and_sentiment(data_df, metadata_df, columns=None, verbose=False)`
Processes columns based on their language and sentiment requirements, handling translation and sentiment analysis as needed.

## Metadata Utilities

### `fill_original_column_name_metadata(metadata_df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame`
Fills the original_column_name metadata field using a helper method if not already populated.

### `fill_desc_en_metadata(metadata_df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame`
Fills the description_en metadata field using a helper method if not already populated.

### `fill_data_type_metadata(data_df: pd.DataFrame, metadata_df: pd.DataFrame, columns: Optional[Union[str, List[str]]] = None) -> pd.DataFrame`
Fills the 'data_type' column in metadata_df by inferring from data_df dtypes. Only fills empty cells.

### `fill_count_metadata(data_df: pd.DataFrame, metadata_df: pd.DataFrame, columns: Optional[Union[str, List[str]]] = None) -> pd.DataFrame`
Fills the 'count' column in metadata_df with non-null counts. Only fills empty cells.

### `fill_original_col_seq_metadata(data_df, metadata_df, verbose=False)`
Populates 'original_col_seq' and 'count' in metadata_df based on data_df column order and non-null counts.

### `fill_is_identifier_metadata(data_df, metadata_df, columns=None, verbose=False)`
For each column, fills is_identifier=True if all non-null values are unique.

### `fill_is_categorical_metadata(data_df, metadata_df, columns=None, unique_threshold=50)`
Fills 'is_categorical' metadata for columns based on the number of unique values.

### `fill_category_values_metadata(data_df, metadata_df, unique_values_dict, columns=None, verbose=False)`
Fills 'category_values' metadata for columns using the provided dictionary of unique values.

### `fill_analysis_category_metadata(data_df, metadata_df, columns=None)`
Fills 'analysis_category' metadata column using a default method if not already populated.

### `fill_pre_enrichment_col_seq_metadata(data_df: pd.DataFrame, metadata_df: pd.DataFrame, columns: Optional[List[str]] = None)`
Fills the 'pre_enrichment_col_seq' metadata column using a helper function if not already populated.

## Helper Functions

### `_original_column_name_method(column_name: str) -> str`
Helper function to determine original column names.

### `_desc_en_method(column_name: str) -> str`
Helper function to generate English descriptions for columns.

### `_default_analysis_category_method(col_name, data_df, metadata_df)`
Helper function to determine analysis categories for columns.

### `_pre_enrichment_seq_method(column_name: str)`
Helper function to assign pre-enrichment sequence numbers to columns.
