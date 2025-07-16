#### Steps to take

1. List original columns of the raw dataset.

2. Generate the alias or short_name for each column using an LLM model.

3. RENAME the column name to alias or short_name in the original raw file and save it as original_columns_renamed JSON/CSV file or db table. This will now act as the raw file and JOIN with the zero_order_metadata via the alias column.

4. CREATE temp_metadata_with_original_column_name JSON file.

5. LOAD the column names (this is now the alias or the short_name - which acts as the column name) from the original_columns_renamed JSON/CSV file or db table.

6. Refer to the following definitions to sequence the metadata fields:

```json{
    mandatory": "Mandatory for all columns and features",
    "zero_order_metadata": "Metadata that is only dependent on the original column name (e.g., alias, column_name_original, desc_en)",
    "first_order_metadata": "Metadata that is dependent on the values in the original column (e.g., is_numeric, is_identifier, is_categorical, is_text)",
    "second_order_metadata": "Metadata that is dependent on the values in the original column and the first order metadata",
    "third_order_metadata": "Metadata that is dependent on the values in the original column and the first and second order metadata",
    "fourth_order_metadata": "Metadata that is dependent on the values in the original column and the first, second and third order metadata"
}
```

7. LIST all the metadata fields [with mandatory = True (Mandatory for all columns and features) and Order = 0 (Zero Order Metadata, i.e)] using the metadata_schema json template.

```json
{
  "metadata_fields": [
    {
      "name": "original_column_name",
      "data_type": "string",
      "description": "The original identifier or name of the field in the raw dataset.",
      "mandatory": true,
      "order": 0,
      "method_for_metadata_value": "Original column name",
      "allowed_values": null
    },
    {
      "name": "short_name",
      "data_type": "string",
      "description": "A concise alias or label for the field, useful for code or analysis.",
      "mandatory": true,
      "allowed_values": null
    },
    {
      "name": "description_en",
      "data_type": "string",
      "description": "Clear English explanation of what this field represents.",
      "applicability": "All data types.",
      "mandatory": true,
      "allowed_values": null
    },
    {
      "name": "description_hi",
      "data_type": "string",
      "description": "Hindi or regional language description for multilingual contexts.",
      "applicability": "When multilingual documentation is required.",
      "mandatory": false,
      "allowed_values": null
    },
    {
      "name": "is_derived",
      "data_type": "boolean",
      "description": "Indicates whether this field is derived or directly observed.",
      "applicability": "All data types.",
      "mandatory": true,
      "allowed_values": [true, false]
    },
    {
      "name": "derivation_tier",
      "data_type": "integer",
      "description": "Indicates the derivation depth relative to the original dataset (0 = raw, 1 = derived from raw, 2 = derived from tier 1, etc.).",
      "applicability": "All data types, recommended for tabular and graph data.",
      "mandatory": true,
      "allowed_values": null
    },
    {
      "name": "parent_columns",
      "data_type": "list",
      "description": "List of columns or fields this derived field depends on.",
      "applicability": "Only if is_derived = true.",
      "mandatory": false,
      "allowed_values": null
    },
    {
      "name": "enrichment_method",
      "data_type": "string",
      "description": "Method used to derive this field (e.g., LLM, aggregation, rule-based).",
      "applicability": "Derived fields only.",
      "mandatory": false,
      "allowed_values": [
        "LLM",
        "rule_based",
        "aggregation",
        "transformation",
        "other"
      ]
    },
    {
      "name": "prompt_template",
      "data_type": "string",
      "description": "Prompt template if the field was enriched via LLM.",
      "applicability": "Derived fields enriched via LLM.",
      "mandatory": false,
      "allowed_values": null
    },
    {
      "name": "nullable",
      "data_type": "boolean",
      "description": "Indicates whether this field can contain null or missing values.",
      "applicability": "All data types.",
      "mandatory": true,
      "allowed_values": [true, false]
    },
    {
      "name": "enum_values",
      "data_type": "list",
      "description": "Possible enumerated values if the field is categorical.",
      "applicability": "Categorical fields only.",
      "mandatory": false,
      "allowed_values": null
    },
    {
      "name": "field_origin",
      "data_type": "string",
      "description": "Where this field originated: raw data source, external dataset, human annotation.",
      "applicability": "All data types.",
      "mandatory": false,
      "allowed_values": ["raw", "external", "human_annotation", "LLM_generated"]
    }
  ]
}
```

8. CREATE zero_order_metadata_blueprint JSON:

   - Identify the zero order metadata that is only dependent on the original column name (e.g., alias, column_name_original, desc_en)
   - SET order = 0
   - ARTICULATE the method to calculate the value of the metadata column. Use the following metadata blueprint json template.

```json
{
    "metadata_value1": {
        "desc": "Description of the column",
        "order": 0,
        "method": "Description of the method to calculate the value of the metadata column",       }
    ...
    "metadata_valueN": {
        "desc": "Description of the column",
        "order": 0,
        "method": "Description of the method to calculate the value of the metadata column",
    }
}
```

9. IMPLEMENT the zero_order_metadata_blueprint by CREATING and RUNNING the required functions and scripts to calculate the value of the metadata columns.

10. SAVE the zero_order_metadata as zero_order_metadata JSON/CSV file or db table.

11. RENAME the column name to alias in the original raw file and save it as original_columns_renamed JSON/CSV file or db table. This will now act as the raw file and JOIN with the zero_order_metadata via the alias column.

12. CREATE first_order_metadata_blueprint JSON:

    - Identify the first order metadata that is only dependent on the values in the original column (e.g., is_numeric, is_identifier, is_categorical, is_text)
    - SET order = 1
    - ARTICULATE the method to calculate the value of the metadata column. Use the following metadata blueprint json template.

```json
{
    "metadata_value1": {
        "desc": "Description of the column",
        "order": 1,
        "method": "Description of the method to calculate the value of the metadata column",
        },
    ...
    "metadata_valueN": {
        "desc": "Description of the column",
        "order": 1,
        "method": "Description of the method to calculate the value of the metadata column",
    }
}
```

13. IMPLEMENT the first_order_metadata_blueprint by CREATING and RUNNING the required functions and scripts to calculate the value of the metadata columns.

14. SAVE the first_order_metadata as first_order_metadata JSON/CSV file or db table.

15. MERGE the zero_order_metadata and first_order_metadata to create the pre_enrichment_metadata JSON/CSV file or db table.

16. IDENTIFY and list the new features.

17. CREATE new_features_metadata_blueprint JSON: Create the new_features_metadata-blueprint for the new features:

- Identify short descriptive feature name.
- Articulate the description of the new feature.
- Set is_derived to True
- Identify the derivation tier of the new feature:
  - Choose between: [0, 1, 2, 3, 4]
  - Is it the tier 0 (which means, depends on only the original columns)
  - Is it the tier 1 (which means, depends on the original columns and the 1st tier dataset)
  - Is it the tier 2 (which means, depends on the original columns and the 1st and 2nd tier datasets)
  - Is it the tier 3 (which means, depends on the original columns and the 1st, 2nd and 3rd tier datasets)
  - Is it the tier 4 (which means, depends on the original columns and the 1st, 2nd, 3rd and 4th tier datasets)
- Identify the enrichment_type of the new feature:
  - Choose between: [origin, identifier, transformation, translation, concatenation, observation, opinion, classification, ranking, calculation, inferred_sentiment_classification, rubric_based_classification, rubric_score, rubric_sentiment]
- Identify the enrichment_level of the new feature:
  - Choose between: [cell, row, column, range, dataset, cross_dataset]
  - Is it cell level (which means, depends on only one row and one column)
  - Is it row level (which means, depends on multiple rows and one column)
  - Is it column level (which means, depends on one row and multiple columns)
  - Is it range level (which means, depends on multiple rows and multiple columns)
  - Is it dataset level (which means, depends on the entire dataset)
  - Is it cross-dataset level (which means, depends on multiple datasets)
- Identify the list of all features needed as inputs to FIND the value of the new feature.
- Articulate the method to calculate the value of the new feature.
- Create the lookup values for the new feature as a JSON file.
- Use the following json template to blueprint the metadata for the new features

```json
{
    "feature_name": {
        "desc": "Description of the feature",
        "dependent_on": "Column name or values in the column using ENUM = [column_name, values_in_column]",
        "method": "Description of the method to calculate the value of the metadata column",
    },
    ...
    "feature_nameN": {
        "desc": "Description of the column",
        "dependent_on": "Column name or values in the column using ENUM = [column_name, values_in_column]",
        "method": "Description of the method to calculate the value of the metadata column",
    }
}
```

6. Create the metadata for the stakeholder perspective
