import os
import duckdb
import pandas as pd


def build_aggregation_table(
    path_to_aggre_db: str,
    path_to_data_db: str,
    aggre_sql: str,
    aggre_table_name: str,
    if_exists: str = 'fail',
    verbose: bool = False
) -> int:
    """
    Build an aggregation table in the aggregation database.

    Args:
        path_to_aggre_db (str): Path to the aggregation database file.
        path_to_data_db (str): Path to the data database file.
        aggre_sql (str): SQL query to generate the aggregation table.
            Must be a SELECT statement with tables referenced using the 'data_db' alias (e.g., data_db.table_name).
        aggre_table_name (str): Name of the aggregation table to create.
        if_exists (str, optional): What to do if table exists. One of:
            - 'fail': Raise a ValueError (default)
            - 'replace': Drop the table before creating new one
            - 'append': Insert into existing table (schema must match)
        verbose (bool, optional): If True, print progress messages. Defaults to False.

    Raises:
        ValueError: If if_exists is not one of 'fail', 'replace', or 'append'.
        FileNotFoundError: If either database file doesn't exist.
        duckdb.Error: For database-related errors during execution.
    """
    # Input validation
    if if_exists not in ('fail', 'replace', 'append'):
        raise ValueError(f"if_exists must be one of 'fail', 'replace', or 'append', got '{if_exists}'")

    if not os.path.exists(path_to_data_db):
        raise FileNotFoundError(f"Data database file not found: {path_to_data_db}")

    # Create directory for aggregation DB if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(path_to_aggre_db)), exist_ok=True)

    # Compare the two databases
    same_db = os.path.abspath(path_to_data_db) == os.path.abspath(path_to_aggre_db)

    try:
        # Connect to aggregation database
        if verbose:
            print(f"Connecting to aggregation database: {path_to_aggre_db}")
        aggre_db_con = duckdb.connect(database=path_to_aggre_db, read_only=False)

        # Only attach if different DBs
        if not same_db:
            if verbose:
                print(f"Attaching data database: {path_to_data_db}")
            aggre_db_con.execute(f"ATTACH '{path_to_data_db}' AS data_db;")

        # Check if table exists and handle according to if_exists parameter
        if verbose:
            print(f"Checking if table '{aggre_table_name}' exists...")
        table_exists = aggre_db_con.execute(
            f"SELECT count(*) FROM information_schema.tables WHERE table_name = '{aggre_table_name}'").fetchone()[0] > 0

        if table_exists:
            if if_exists == 'fail':
                raise ValueError(f"Table '{aggre_table_name}' already exists. Set if_exists='replace' or 'append' to override.")
            elif if_exists == 'replace':
                if verbose:
                    print(f"Dropping existing table: {aggre_table_name}")
                aggre_db_con.execute(f"DROP TABLE IF EXISTS {aggre_table_name}")

        # Create the aggregation table
        if verbose:
            print(f"Creating aggregation table: {aggre_table_name}")
            
        if table_exists and if_exists == 'append':
            # For append, we need to use INSERT INTO instead of CREATE TABLE AS
            aggre_db_con.execute(f"INSERT INTO {aggre_table_name} {aggre_sql}")
        else:
            aggre_db_con.execute(f"CREATE TABLE {aggre_table_name} AS {aggre_sql}")

        if verbose:
            # Get row count for logging
            row_count = aggre_db_con.execute(f"SELECT COUNT(*) FROM {aggre_table_name}").fetchone()[0]
            print(f"Successfully created/updated table '{aggre_table_name}' with {row_count:,} rows")
        
        row_count = aggre_db_con.execute(f"SELECT COUNT(*) FROM {aggre_table_name}").fetchone()[0]
    
    except duckdb.Error as e:
        raise RuntimeError(f"Database error occurred: {str(e)}")
    finally:
        # Ensure connection is properly closed
        if 'aggre_db_con' in locals():
            aggre_db_con.close()
    
    return row_count
    