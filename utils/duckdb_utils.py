# Load from CSV and type cast data and load in duckdb
import duckdb
import pandas as pd

def load_csv_to_duckdb_with_schema_csv(
    con: duckdb.DuckDBPyConnection,
    csv_path: str,
    schema_csv_path: str,
    table_name: str,
    overwrite: bool = False,
    verbose: bool = True
):
    """
    Load a CSV into DuckDB using a schema CSV file, casting all columns as specified.

    schema_csv must have columns:
        - metadata_field: column name in the CSV
        - data_type: DuckDB type (e.g., VARCHAR, INTEGER)

    Args:
        con: DuckDB connection
        csv_path: path to CSV file
        schema_csv_path: path to schema CSV file
        table_name: name of target DuckDB table
        overwrite: drop table if it exists
        verbose: print messages

    Returns:
        DuckDB relation
    """

    # Load schema CSV
    schema_df = pd.read_csv(schema_csv_path)
    if "metadata_field" not in schema_df.columns or "data_type" not in schema_df.columns:
        raise ValueError("Schema CSV must have 'metadata_field' and 'data_type' columns.")

    # Build list of cast expressions
    cast_expressions = []
    for _, row in schema_df.iterrows():
        col = row["metadata_field"]
        dtype = row["data_type"]
        cast_expressions.append(f'CAST("{col}" AS {dtype}) AS "{col}"')

    # Compose SQL
    select_clause = ",\n    ".join(cast_expressions)

    sql = f"""
        CREATE OR REPLACE TABLE "{table_name}" AS
        SELECT
            {select_clause}
        FROM
            read_csv_auto('{csv_path}', ALL_VARCHAR=TRUE, HEADER=TRUE)
    """

    # Optionally drop first
    if overwrite:
        con.execute(f'DROP TABLE IF EXISTS "{table_name}"')
        if verbose:
            print(f"[ℹ️] Dropped table '{table_name}'.")

    # Create table
    con.execute(sql)
    if verbose:
        print(f"[✅] Created table '{table_name}' with casted columns from '{csv_path}'.")

    return con.table(table_name)


# Load from CSV and type cast data and load in duckdb from a metadata DataFrame
def load_csv_to_duckdb_with_metadata_df(
    con: duckdb.DuckDBPyConnection,
    csv_path: str,
    metadata_df: pd.DataFrame,
    table_name: str,
    if_exists: str = "fail",
    verbose: bool = True
):
    """
    Load CSV into DuckDB using column names and types from metadata DataFrame.
    
    Args:
        con: DuckDB connection
        csv_path: Path to the CSV file
        metadata_df: DataFrame with columns 'column_name' and 'data_type'
        table_name: Name of the target table
        if_exists: 'fail' (default), 'replace', or 'append'
        verbose: print logs
    """
    if if_exists not in ("fail", "replace", "append"):
        raise ValueError("if_exists must be 'fail', 'replace', or 'append'.")

    # Build column casts with aliasing to preserve names
    col_defs = ",\n  ".join(
        f'CAST("{row["column_name"]}" AS {row["data_type"]}) AS "{row["column_name"]}"'
        for _, row in metadata_df.iterrows()
    )

    # Build SELECT statement
    select_sql = f"""
    SELECT
      {col_defs}
    FROM read_csv_auto('{csv_path}', header=True)
    """

    if verbose:
        print(f"🔹 Generated SELECT SQL:\n{select_sql.strip()}")

    # Decide what to do
    if if_exists == "fail":
        create_sql = f"CREATE TABLE {table_name} AS {select_sql}"
    elif if_exists == "replace":
        create_sql = f"CREATE OR REPLACE TABLE {table_name} AS {select_sql}"
    elif if_exists == "append":
        # Create temp table to cast and then insert into existing table
        temp_table = f"{table_name}_temp_load"
        con.execute(f"CREATE OR REPLACE TABLE {temp_table} AS {select_sql}")
        con.execute(f"INSERT INTO {table_name} SELECT * FROM {temp_table}")
        con.execute(f"DROP TABLE {temp_table}")
        if verbose:
            print(f"[✅] Appended data to existing table '{table_name}'.")
        return

    # Execute CREATE (fail or replace)
    con.execute(create_sql)
    if verbose:
        action = "Created" if if_exists == "fail" else "Replaced"
        print(f"[✅] {action} table '{table_name}' with loaded data.")  