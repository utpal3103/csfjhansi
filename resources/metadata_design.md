# Metadata Design

## General Instruction

### Step 1: Change the column name to short_name

input: [cleaned_dataset, original_column_name_to_short_name mapping]
output: [renamed_cleaned_dataset]

### Step 2: DESIGN metadata blueprint using metadata_schema json template and Lookup values

input: [renamed_cleaned_dataset, metadata_schema, lookup_values, original_column_name_to_short_name mapping]
output: [metadata_blueprint, zero_order_metadata, zero_order_dataset]

```json
<! --- metadata_schema json template -->
{
    "metadata_name": {
            "data_type": "States the data_type of the metadata",
            "description": "Description of the metadata",
            "mandatory_for": "List of 'original' and 'derived' for which the metadata is mandatory. Empty list to make the metadata as optional",
            "is_seq": "True for metadata that is a seq of columns and False for metadata that is not a seq of columns",
            "stage": "Integer: 0, 1; 0 for metadata at original level and 1 for metadata at derived level.",
            "method": "HUMAN or Python script generated from short_name and original_column_name mapping CSV file",
            "allowed_values": "All allowed values"
        },
}
```

**Metadata structure**

The csv file with metadata values for all columns must in the following one row per column format:

| column_name | metadata1 | metadata2 | metadata3 | ... | metadataN |

where metadata1, metadata2, metadata3, ... metadataN are the metadata fields as per the metadata_schema json template.

**Lookup Values**

```json
    <! --- lookup_values json template -->
    {
    "measurement_categories": [
        "school_identity",
        "school_student_counts",
        "school_teacher_count",
        "school_inputs_obs",
        "class_identifiers",
        "observation_of_classroom",
        "observation_of_student",
        "teacher_preparedness_general",
        "teacher_preparedness_for_class",
        "teacher_student_interaction",
        "class_activity_level_obs",
        "class_activity_2a_obs",
        "class_activity_2b_obs",
        "class_activity_2c_obs",
        "class_activity_2d_obs",
        "class_activity_2e_obs",
        "class_activity_2f_obs",
        "class_lesson_4a_obs",
        "class_lesson_4b_obs",
        "mentor_teacher_feedback",
        "mentor_demo",
        "convo_with_staff"
    ],
    "domain_areas": [
        "school_info",
        "teacher_observation",
        "infrastructure",
        "mentor_influence",
        "teacher_influence"
    ],
    "relevance": [
        "teacher_performance",
        "school_environment",
        "infrastructure",
        "mentor_influence",
        "teacher_influence"
    ]
    }
```

##### Step 2.1: IDENTIFY metadata fields for ORIGINAL COLUMNS [zero_stage] and NEW FEATURES [first_stage]

input: [renamed_cleaned_dataset, lookup_values, original_column_name_to_short_name mapping]
output: [List of metadata_fields]

```python
zero_stage_mandatory_metadata:  List = ["column_name", "desc_en", "data_type"]
zero_stage_optional_metadata: List = ["original_col_seq", "count", "is_identifier", "is_categorical", "category_values", "stakeholder_category", "measurement_category", "pre_enrichment_col_seq"]
first_stage_mandatory_metadata: List = ["derivation_tier", "derivation_type", "derivation_feed_level", "parent_columns""derivation_method"]
```

##### Step 2.2: CREATE the metadata blueprint

input: [List of metadata_fields, metadata_schema, lookup_values, renamed_cleaned_dataset]
output: [metadata_blueprint]

```json
{
    "zero_stage_mandatory_metadata": [
        "original_column_name": {
            "data_type": "string",
            "description": "The original identifier or name of the field in the raw dataset.",
            "mandatory_for": ["original", "derived"],
            "is_seq": false,
            "stage": 0,
            "method": "HUMAN or Python script generated from short_name and original_column_name mapping CSV file",
            "allowed_values": null
        },
        "desc_en": {
            "data_type": "string",
            "description": "Clear English explanation of what this field represents.",
            "mandatory_for": ["original", "derived"],
            "is_seq": false,
            "stage": 0,
            "method": "HUMAN or LLM generated description of the column",
            "allowed_values": null
        }
        "data_type": {
            "data_type": "string",
            "description": "The original identifier or name of the field in the raw dataset.",
            "mandatory_for": ["original", "derived"],
            "is_seq": false,
            "stage": 0,
            "method": "Python script generated using the values of column data_type",
            "allowed_values": null
        },
    ],
    "zero_stage_optional_metadata": [
        "original_col_seq": {
            "data_type": "integer",
            "description": "The original sequence number of the field in the raw dataset.",
            "mandatory_for": [],
            "is_seq": true,
            "stage": 0,
            "method": "HUMAN or Python script generated original column sequence number",
            "allowed_values": null
        },
        "count": {
            "data_type": "integer",
            "description": "Count of the number of values in the column.",
            "mandatory_for": [],
            "is_seq": false,
            "stage": 0,
            "method": "Python script to calculate the count of the values in the column",
            "allowed_values": null
        },
        "is_identifier": {
            "data_type": "boolean",
            "description": "The original identifier or name of the field in the raw dataset.",
            "mandatory_for": [],
            "is_seq": false,
            "stage": 0,
            "method": "HUMAN identified or LLM inferred using the values of columns or Python script referencing the lookup table. True if the column is an identifier.",
            "allowed_values": [true, false]
        },
        "is_categorical": {
            "data_type": "boolean",
            "description": "True if the allowed values for this column is a distinct set of values. False if not",
            "mandatory_for": [],
            "is_seq": false,
            "stage": 0,
            "method": "Using LLM and python script to check if the values of the column are distinct and the LLM inference from description of the column",
            "allowed_values": [true, false]
        },
        "category_values": {
            "data_type": "List[str]",
            "description": "If is_categorical = True, then this metadata will have the list of allowed values for the column.",
            "mandatory_for": [],
            "is_seq": false,
            "stage": 0,
            "method": "Using LLM and python script to find the unique values in the column",
            "allowed_values": null
        },
        "stakeholder_category": {
            "data_type": "List of stakeholder_category",
            "description": "Does the column pertain to a stakeholder? If yes, then this metadata will have the stakeholder_category for the column.",
            "mandatory_for": [],
            "is_seq": false,
            "stage": 0,
            "method": "Using LLM to infer from the description of the column and the stakeholder_category lookup table",
            "allowed_values": [mentor, teacher, school_admin, block_admin, district_admin, state_admin]
        },
        "analysis_category": {
            "data_type": "List of analysis_category",
            "description": "Does the column pertain to an analysis_category? If yes, then this metadata will have the analysis_category for the column.",
            "mandatory_for": [],
            "is_seq": false,
            "stage": 0,
            "method": "Python script to map the column to the analysis_category using the lookup table",
            "allowed_values": [row_identity, mentor_identity, school_identity, school_student_counts, school_teacher_count, school_inputs_obs, class_identity, observation_of_classroom, observation_of_student, teacher_preparedness_general, teacher_preparedness_for_class, teacher_student_interaction, class_activity_level_obs, class_activity_2a_obs, class_activity_2b_obs, class_activity_2c_obs, class_activity_2d_obs, class_activity_2e_obs, class_activity_2f_obs, class_lesson_4a_obs, class_lesson_4b_obs, mentor_teacher_feedback, mentor_demo, convo_with_staff]
        },
        "pre_enrichment_col_seq": {
            "data_type": "integer",
            "description": "The sequence number of the column after grouping columns based on category_values.",
            "mandatory_for": [],
            "is_seq": true,
            "stage": 0,
            "method": "HUMAN or Python script generated column sequence number after grouping columns based on category_values",
            "allowed_values": null
        }
    ],
    "first_stage_mandatory_metadata" = [
        "derivation_tier": {
            "data_type": "integer",
            "description": "The derivation tier of the column/feature: tier 0 = original columns, tier 1 = derived from tier 0, tier 2 = derived from tier 1, etc.",
            "mandatory_for": ["derived"],
            "is_seq": false,
            "stage": 1,
            "method": "HUMAN or LLM generated using the derivation tier definition look up table",
            "allowed_values": [0, 1, 2, 3, 4, 5]
        },
        "derivation_type": {
            "data_type": "string",
            "description": "The type of derivation of the column/feature: origin = original columns, transformation = transformation columns, translation = translation columns, concatenation = concatenation columns, classification = classification columns, ranking = ranking columns, score = score columns, rule_based = rule_based columns.",
            "mandatory_for": ["derived"],
            "is_seq": false,
            "stage": 1,
            "method": "HUMAN or LLM generated using the derivation type definition look up table",
            "allowed_values": [origin, transformation, translation, concatenation, classification, ranking, score, rule_based]
        },
        "derivation_feed_level": {
            "data_type": "String",
            "description": "The type of feed level of the column/feature: cell = cell level, row = row level, column = column level, range = range level, dataset = dataset level, cross_dataset = cross_dataset level.",
            "mandatory_for": ["derived"],
            "is_seq": false,
            "stage": 1,
            "method": "HUMAN or LLM generated using the derivation type definition look up table",
            "allowed_values": [cell, row, column, range, dataset, cross_dataset]
        },
        "derivation_method": {
            "data_type": "String",
            "description": "The method to calculate the values of the derived feature.",
            "mandatory_for": ["derived"],
            "is_seq": false,
            "stage": 1,
            "method": "HUMAN or LLM generated method to calculate the values of the derived feature",
            "allowed_values": null
        },
        "parent_columns": {
            "data_type": "list",
            "description": "List of columns or fields this derived field is dependent on.",
            "mandatory_for": ["derived"],
            "is_seq": false,
            "stage": 1,
            "method": "All the columns that feeds into the derivation method to calculate the values of the derived feature",
            "allowed_values": List of column with column [derivation_tier < current_column.derivation_tier]
        },
    ]
}
```

##### Step 2.3: IMPLEMENT metadata blueprint using method mentioned in the metadata blueprint

input: [renamed_cleaned_dataset, metadata blueprint]
output: [zero_stage_metadata (JSON/CSV file or db table) for ORIGINAL COLUMNS]

##### Step 2.4: Rearrange columns in the dataset based on pre_enrichment_col_seq [optional] and rename file

input: [renamed_cleaned_dataset, zero_stage_metadata]
output: [zero_stage_dataset (JSON/CSV file or db table or pandas dataframe object)]

### Step 3: ENRICHMENT: ADD derivation_tier = 1 Features using zero_stage and first_stage mandatory metadata using the following metadata blueprint

input: [zero_stage_dataset, metadata_blueprint, feature_design_template]
output: [feature_metadata (JSON/CSV file or db table or pandas dataframe object)]

```json
<! -- feature_design_template -->
    {
        "feature 1": {
            "column_name": "feature 1",
            "desc_en": "Feature 1",
            "data_type": "string",
            "derivation_type": "translation",
            "derivation_tier": 1,
            "derivation_feed_level": "cell",
            "derivation_method": "LLM",
            "parent_columns": ["column_name"]
        }
    }
```

##### Step 3.1: CREATE feature_blueprint JSON file using metadata_blueprint

input: [zero_stage_dataset, feature_design_template,metadata_blueprint (zero_stage_mandatory_metadata, first_stage_mandatory_metadata)]
output: [feature_blueprint (JSON/CSV file or db table or pandas dataframe object)]

[Loop over all new features]

##### Step 3.2: IMPLEMENT feature_blueprint using derivation_method mentioned in the feature_blueprint

input: [zero_stage_dataset, feature_blueprint]
output: [<feature_name>\_column_added_dataset (JSON/CSV file or db table or pandas dataframe object)]

##### Step 3.3: IMPLEMENT feature_metadata using method mentioned in the feature_metadata

input: [zero_stage_dataset, metadata_blueprint (zero_stage_optional_metadata), feature_blueprint (already contains the zero_stage_mandatory_metadata and first_stage_mandatory_metadata)]
output: [<feature_name>\_metadata (JSON/CSV file or db table or pandas dataframe object)]

[end loop]

##### Step 3.4: MERGE all feature_metadata with pre_enrichment_metadata to create the tier_1_metadata and tier_1_dataset JSON/CSV file or db table or pandas dataframe object

input: [pre_enrichment_metadata, feature_metadata]
output: [tier_1_metadata and tier_1_dataset JSON/CSV file or db table or pandas dataframe object]

### Step 4: ENRICHMENT: ADD derivation_tier = 2 Features using all the sub_steps in Step 3 to create tier_2_metadata and tier_2_dataset JSON/CSV file or db table. Repeat this step for derivation_tier = 3, 4, 5, ...

input: [tier_1_metadata and tier_1_dataset JSON/CSV file or db table or pandas dataframe object]
output: [tier_2_metadata and tier_2_dataset JSON/CSV file or db table or pandas dataframe object]

#### Step 5: Pre-analysis dataset engineering by stipping the dataset to only include the columns that are required for the analysis.

input: [tier_2_metadata and tier_2_dataset JSON/CSV file or db table or pandas dataframe object]
output: [pre_analysis_dataset JSON/CSV file or db table or pandas dataframe object]

# Analysis Plan

### Duration of data

```json
{
  "1": "Oct 2022 - Dec 2022",
  "2": "Jan 2023 - Mar 2023",
  "3": "Apr 2023 - Jun 2023",
  "4": "Jul 2023 - Sep 2023",
  "5": "Oct 2023 - Dec 2023",
  "6": "Jan 2024 - Mar 2024",
  "7": "Apr 2024 - Jun 2024",
  "8": "Jul 2024 - Sep 2024"
}
```

### Step 1: Conceptual Synthesis

Given your context, here is how I’d think about main uses of this data:

##### 1️⃣ Descriptive Monitoring

    •	How many visits occurred per school?
    •	Which observations (e.g., TLM usage, active libraries) are most frequently positive or negative?
    •	Where are there persistent gaps?

##### 2️⃣ Diagnostic Insight

    •	Which areas (teacher practices, classroom materials, student participation) are most lagging?
    •	Are there specific mentors, schools, or blocks consistently scoring low?

##### 3️⃣ Progress Tracking

    •	How have observations evolved month over month?
    •	Are interventions (trainings, resource provision) improving sentiment and practice?

##### 4️⃣ Feedback & Reflection

    •	Teacher-specific reports (e.g., which practices were noted positive/negative over time).
    •	Mentor-specific patterns (e.g., mentors who frequently do demos, or spend longer time).

### Step 2: Thematic Clusters to Drive Visualizations

Below is a conceptual grouping of your columns by analysis_category.

| Analysis Category              | Purpose                             | Example Visualizations                                                  |
| ------------------------------ | ----------------------------------- | ----------------------------------------------------------------------- |
| school_identity                | Filter/group reports by school      | Counts, maps, filters                                                   |
| school_student_counts          | Enrollment, attendance, inclusivity | Line charts over time, stacked bars of boys/girls present vs registered |
| school_teacher_count           | Staffing                            | Bar charts of male/female teacher counts                                |
| school_inputs_obs              | Infrastructure readiness            | Pie charts of functional equipment, library usage sentiment             |
| observation_of_classroom       | Classroom environment               | Sentiment trend lines, heatmaps by school                               |
| teacher_preparedness_general   | Preparedness of lesson plans        | Proportion of positive/negative                                         |
| teacher_preparedness_for_class | Lesson planning quality             | Same as above                                                           |
| teacher_student_interaction    | Participation & inclusion           | Positive/negative counts, improvement trends                            |
| class_activity_level_obs       | Activity-based observations         | Sankey diagrams: which activities, what participation, what sentiment   |
| mentor_teacher_feedback        | Mentoring practices                 | Word clouds of feedback text, counts of feedback given                  |
| mentor_demo                    | Demos conducted                     | Bar charts of methods used in demos                                     |
| convo_with_staff               | Staff dialogue and action planning  | Timeline of follow-up actions                                           |

⸻

### Step 3: Potential Aggregations & Reports

Here are concrete report ideas you could generate:

##### 📘 1. School Profile Report

Audience: School Admin, Mentor
Contents:

- Total visits (count)
- Average sentiment across observations
- Student enrollment & attendance snapshot
- Teacher counts
- Infrastructure readiness (library, TLMs, sports equipment)
- Recent observations (positive & negative)

Visuals:

- Radar chart of strengths vs. gaps
- Sentiment trend line

⸻

##### 📗 2. Mentor Performance Dashboard

Audience: Block/District Admin
Contents:

- Number of schools visited
- Frequency of demos
- Average time spent
- Sentiment distributions across their visits

Visuals:

- Mentor leaderboard
- Time spent distribution

⸻

##### 📙 3. Block/District Overview

Audience: District Admin
Contents:

- Aggregate sentiment trends
- Comparison across blocks
- Common challenges (e.g., library use, TLMs)

Visuals:

- Block-level bar charts
- Treemap of observation categories

⸻

##### 📒 4. Thematic Reports

Audience: All stakeholders
Themes:

- Classroom Practices: Participation, materials, teaching plan adherence
- Infrastructure: Libraries, sports equipment
- Teacher Preparedness

Visuals:

- Heatmaps by school/block
- Sentiment distributions
- Trend lines over time

⸻

##### 📕 5. Action Planning Reports

Audience: Mentors & Teachers
Contents:

- Highlights of positive practices
- Recommendations
- Next steps recorded in upcoming_work_action_points

⸻

### Step 4: Next Steps

Suggestions for you: 1. Review these report concepts. 2. Think about which audiences are your highest priority. 3. Consider what level of aggregation vs. school-level detail you prefer.

Once you share your reflections, we can:
• Prioritize which reports to build first.
• Design their structure.
• Plan which aggregations and visualizations you want.

## Analysis Aggregations

### Design Aggregation Tables based on Stakeholder Perspective, domain and analysis category

### Implement Aggregation Tables

### Visualization of Aggregation Tables

## Stakeholder Perspectives and Dashboards
