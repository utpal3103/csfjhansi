# duckdb Tutorial

### Different data types: Numeric Types, Date and Time, String Types, Boolean, Complex and Special Types

| **Type**     | **Description**                       | **Type**      | **Description**               |
| ------------ | ------------------------------------- | ------------- | ----------------------------- |
| TINYINT      | 1-byte integer (-128 to 127)          | **DATE**      | Date only (YYYY-MM-DD)        |
| SMALLINT     | 2-byte integer                        | TIME          | Time only (HH:MM:SS)          |
| **INTEGER**  | 4-byte integer                        | **TIMESTAMP** | Date and time                 |
| **BIGINT**   | 8-byte integer                        | TIMESTAMP_TZ  | Timestamp with timezone       |
| HUGEINT      | 128-bit integer (very large)          | INTERVAL      | Time interval                 |
| UTINYINT     | Unsigned tiny integer                 | **Type**      | **Description**               |
| USMALLINT    | Unsigned small integer                | **VARCHAR**   | Variable-length UTF-8 string  |
| UINTEGER     | Unsigned integer                      | BLOB          | Binary Large Object           |
| UBIGINT      | Unsigned big integer                  | **Type**      | **Description**               |
| FLOAT        | 32-bit float                          | UUID          | Universally Unique Identifier |
| **DOUBLE**   | 64-bit float (most common)            | JSON          | JSON values                   |
| DECIMAL(p,s) | Fixed-point numeric (precision/scale) | MAP           | Key-value pairs               |
| **Type**     | **Description**                       | LIST          | Arrays / lists                |
| BOOLEAN      | True/False                            | ENUM          | Enumerated values             |






# duckdb Vs Pandas
## Data Type Inference & Enforcement

**DuckDB strengths:**

- You can **declare types up front** (CAST).
- Once saved in a .duckdb table or Parquet, types are enforced.
- Much faster on big CSV/Parquet because it uses a **vectorized columnar engine**.
- No more re-guessing types every time you reload.

**Pandas limitations:**

- Always starts by reading into object types if unsure.
- You often have to do:
```python
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
df['date'] = pd.to_datetime(df['date'], errors='coerce')
```

**Verdict:** **DuckDB is superior** for typing and casting cleanly in one step.

### **Row Filtering and Conditional Logic**


✅ **DuckDB:**

- SQL WHERE, CASE WHEN are extremely fast.
- Good for deterministic logic.

✅ **Pandas:**

- More expressive for complex logic:
```python
df.loc[df["amount"] < 0, "amount"] = 0
df["region_standardized"] = df["region"].str.lower().map(mapping_dict)
```

- Easier for regex, string parsing, applying lambdas.

**Verdict:**

**Pandas is often easier for very custom row-wise transformations**, especially if you want Python functions or mapping dictionaries.


### **Handling Large Datasets**

**DuckDB:**

- Can process **datasets far bigger than memory** by streaming from disk.
- Especially performant on Parquet and CSV.

**Pandas:**

- Everything loads in memory.
- Even moderately big files (2–5 GB) can get slow or crash without careful tuning.

**Verdict:** **DuckDB wins** when data doesn’t fit in RAM.

### **Deduplication and Joins**

**DuckDB:**

- SQL DISTINCT, JOIN, GROUP BY are optimized.
- SQL syntax makes deduplication declarative.

**Pandas:**
- merge(), drop_duplicates() are powerful.
- Syntax can be more verbose for joins.

**Verdict:** **Either is fine**, but DuckDB can be much faster on big joins.

### **Complex Text Parsing & Custom Functions**

**DuckDB:**

- Can do TRIM(), REPLACE(), but no arbitrary Python functions.
- Limited regex capabilities compared to Pandas.

**Pandas:**

- Full Python string methods and re module.
- Can .apply() any function.

**Verdict:** **Pandas is better** when you need heavy text munging, NLP, or custom Python logic.

### **What Do People Use in Industry?**

**Data Engineering (ETL pipelines):**

- DuckDB increasingly popular for:
    - Ingesting CSV/Parquet  
    - Pre-typing
    - Initial filtering
    - Saving to Parquet/DB

- Spark or SQL engines (BigQuery, Redshift) also common at scale.

**Data Science / Analytics:**

- Often:
    - Initial cleaning and typing in DuckDB 
    - Load cleaned data into Pandas or Polars for analysis, plotting, modeling.

**Enterprise workflows:**

- A **hybrid approach** is very common:
    - DuckDB for _fast, typed, repeatable transforms_.
    - Pandas for _flexible downstream manipulation_.

## ** Suggested Strategy for You**

**Hybrid Flow (Best of Both Worlds):**

**DuckDB:**

- Read CSVs.
- CAST columns.
- Filter invalid rows.
- Compute derived columns (like quarters, IDs).
- Save to .duckdb or Parquet.

**Pandas:**

- Load the cleaned, typed dataset.
- Do custom text parsing, imputation (filling in missing values), encoding (**Converting categorical data into numeric form.**).
- Create visuals, build ML pipelines.

Side note: **Common imputation strategies:**
- **Mean imputation:** Fill with the column’s average.
- **Median imputation:** Fill with the median value.
- **Constant imputation:** Fill with 0, -1, or "Unknown".
- **Model-based imputation:** Predict missing values using ML.

This way:

- **Types are enforced early (DuckDB).**
- **Flexibility is retained later (Pandas).**
- **You avoid re-cleaning every time.**

✅ **TL;DR:**

- You are exactly right: **hybrid DuckDB + Pandas** is becoming the default best practice.
- DuckDB is unbeatable for typing, deduplication, large-file ingestion.
- Pandas remains unbeatable for custom Python logic, string cleaning, and modeling.