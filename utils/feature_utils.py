
import pandas as pd
from utils.llm_utils import (
    translate_list_with_llm,
    translate_list_and_infer_sentiment_with_llm,
    infer_sentiment_with_llm,
)
import ast

# Translate and replace categorical columns
def translate_and_replace_categorical_columns(
    data_df,
    metadata_df,
    llm_function,
    columns=None,
    verbose=False
):
    """
    Replaces categorical column values with their translations,
    keeping the same column names, and updates metadata.

    Args:
        data_df (pd.DataFrame): Main data.
        metadata_df (pd.DataFrame): Metadata.
        llm_function (callable): LLM translator function.
        columns (list or None): Which columns to process.
        verbose (bool): Print progress.

    Returns:
        pd.DataFrame: Updated data_df.
        pd.DataFrame: Updated metadata_df.
    """
    if columns is None:
        columns = metadata_df.loc[
            metadata_df["is_categorical"].astype(str).str.lower() == "true",
            "column_name"
        ].tolist()
    
    for col in columns:
        if verbose:
            print(f"\n🔹 Processing column: {col}")
        
        # Retrieve category_values
        cat_values_str = metadata_df.loc[
            metadata_df["column_name"] == col, "category_values"
        ].values[0]
        
        if pd.isna(cat_values_str) or cat_values_str.strip() == "":
            if verbose:
                print(f"⚠️ No category_values for {col}. Skipping.")
            continue
        
        try:
            original_values = ast.literal_eval(cat_values_str)
        except Exception as e:
            print(f"❌ Error parsing category_values for {col}: {e}")
            continue
        
        if not original_values:
            if verbose:
                print(f"⚠️ Empty category_values list for {col}. Skipping.")
            continue
        
        # Call LLM to translate
        translated_values = llm_function(original_values)
        
        if verbose:
            print(f"✅ Translated values: {translated_values}")
        
        mapping = dict(zip(original_values, translated_values))
        
        # Replace values in the column
        data_df[col] = data_df[col].map(mapping).fillna(data_df[col])
        
        # Update metadata category_values
        metadata_df.loc[
            metadata_df["column_name"] == col, "category_values"
        ] = str(translated_values)
        
        if verbose:
            print(f"🟢 Replaced values in column '{col}' and updated metadata.")
    
    return data_df, metadata_df

# Translate and add sentiment   
def translate_and_add_sentiment_column(data_df, metadata_df, llm_function, columns=None, verbose=False):
    """
    Translates categorical values and adds a sentiment column.
    Replaces original column values with translations.
    Also updates metadata category_values.
    """
    if columns is None:
        # Auto-pick categorical columns
        columns = metadata_df.loc[
            metadata_df["is_categorical"].str.lower() == "true",
            "column_name"
        ].tolist()

    for col in columns:
        if verbose:
            print(f"\n🔹 Processing column: {col}")
        
        # Get unique non-null values
        unique_values = sorted(data_df[col].dropna().unique().tolist())

        # Get column description from metadata
        desc = metadata_df.loc[
            metadata_df["column_name"] == col, "desc_en"
        ].values[0]

        # Call LLM
        response = llm_function(unique_values, desc)
        parsed = safe_parse_llm_dict(response)
        
        translated = parsed["translated_value"]
        sentiments = parsed["sentiment"]

        # Create mapping
        mapping = dict(zip(unique_values, translated))
        sentiment_mapping = dict(zip(unique_values, sentiments))

        # Replace in dataframe
        data_df[col] = data_df[col].map(mapping)
        # Add sentiment column
        sentiment_col = f"{col}_sentiment"
        data_df[sentiment_col] = data_df[col].map(sentiment_mapping)

        # Update metadata
        metadata_df.loc[
            metadata_df["column_name"] == col, "category_values"
        ] = str(translated)

        if verbose:
            print(f"✅ {col} replaced and {sentiment_col} added.")

    return data_df, metadata_df



# Process translation and sentiment
def process_translation_and_sentiment_old(data_df, metadata_df, columns=None, verbose=False):
    """
    Process categorical columns by translating Hindi text and/or inferring sentiment.

    Depending on metadata columns 'lang' and 'sentiment_required', performs:
    - Translation only
    - Translation + sentiment inference
    - Sentiment inference only
    - No action (English + no sentiment)

    Args:
        data_df (pd.DataFrame): Your dataset.
        metadata_df (pd.DataFrame): Metadata table.
        columns (list or None): If None, applies to all columns marked categorical.
        verbose (bool): Print progress messages.

    Returns:
        tuple: (data_df, metadata_df)
    """
    # Select columns to process
    if columns is None:
        columns = metadata_df.loc[
            metadata_df["is_categorical"].astype(str).str.lower() == "true",
            "column_name"
        ].tolist()
        if verbose:
            print(f"[🔍] Found {len(columns)} categorical columns to process.")

    for col in columns:
        if verbose:
            print(f"\n⚙️ Processing column: '{col}'")

        # Get language and sentiment flags
        lang = metadata_df.loc[metadata_df["column_name"] == col, "lang"].iloc[0].strip().lower()
        sentiment = metadata_df.loc[metadata_df["column_name"] == col, "sentiment_required"].iloc[0].strip().lower()

        # Get description and analysis_category
        desc = metadata_df.loc[metadata_df["column_name"] == col, "desc_en"].iloc[0].strip()
        analysis_category = metadata_df.loc[metadata_df["column_name"] == col, "analysis_category"].iloc[0].strip()
        pre_seq = metadata_df.loc[metadata_df["column_name"] == col, "pre_enrichment_col_seq"].iloc[0]

        # Get category values from metadata
        cat_values_str = metadata_df.loc[metadata_df["column_name"] == col, "category_values"].iloc[0]
        if pd.isna(cat_values_str) or cat_values_str.strip() == "":
            if verbose:
                print(f"⚠️ Skipping column '{col}' — no category_values.")
            continue
        unique_values = ast.literal_eval(cat_values_str)

        # CASE 1: Hindi + Translation only
        if lang == "hi" and sentiment == "no":
            if verbose:
                print("📝 Case: Hindi + Translation only")
            translated = translate_list_with_llm(unique_values)
            lookup = dict(zip(unique_values, translated))
            data_df[col] = data_df[col].map(lookup)

            metadata_df.loc[metadata_df["column_name"] == col, "category_values"] = str(translated)
            if verbose:
                print(f"✅ Replaced column '{col}' with translated values.")

        # CASE 2: Hindi + Translation + Sentiment
        elif lang == "hi" and sentiment == "yes":
            if verbose:
                print("📝 Case: Hindi + Translation + Sentiment")
            response = translate_list_and_infer_sentiment_with_llm(unique_values, desc)
            translated = response["translated_value"]
            sentiments = response["sentiment"]

            # Replace column with translated values
            lookup_trans = dict(zip(unique_values, translated))
            data_df[col] = data_df[col].map(lookup_trans)
            metadata_df.loc[metadata_df["column_name"] == col, "category_values"] = str(translated)

            # Create sentiment column
            sentiment_col = f"{col}_sentiment"
            lookup_sent = dict(zip(unique_values, sentiments))
            data_df[sentiment_col] = data_df[col].map(lambda x: lookup_sent.get(x, "unknown"))

            # Append new row to metadata
            metadata_df = pd.concat([
                metadata_df,
                pd.DataFrame({
                    "column_name": [sentiment_col],
                    "desc_en": [f"Sentiment: {desc}"],
                    "analysis_category": [analysis_category],
                    "pre_enrichment_col_seq": [str(float(pre_seq) + 0.1)],
                })
            ], ignore_index=True)

            if verbose:
                print(f"✅ Added sentiment column '{sentiment_col}'.")

        # CASE 3: English + Sentiment only
        elif lang == "en" and sentiment == "yes":
            if verbose:
                print("📝 Case: English + Sentiment only")
            sentiments = infer_sentiment_with_llm(unique_values, desc)
            sentiment_col = f"{col}_sentiment"
            lookup_sent = dict(zip(unique_values, sentiments))
            data_df[sentiment_col] = data_df[col].map(lambda x: lookup_sent.get(x, "unknown"))

            metadata_df = pd.concat([
                metadata_df,
                pd.DataFrame({
                    "column_name": [sentiment_col],
                    "desc_en": [f"Sentiment: {desc}"],
                    "analysis_category": [analysis_category],
                    "pre_enrichment_col_seq": [str(float(pre_seq) + 0.1)],
                })
            ], ignore_index=True)

            if verbose:
                print(f"✅ Added sentiment column '{sentiment_col}'.")

        # CASE 4: English + No action
        else:
            if verbose:
                print("ℹ️ Skipping column (English + No sentiment). No action needed.")

    return data_df, metadata_df


    from utils.llm_utils import (
    translate_list_with_llm,
    translate_list_and_infer_sentiment_with_llm
)
import ast

def process_translation_and_sentiment(
    data_df,
    metadata_df,
    columns=None,
    verbose=False
):
    """
    For each column:
    - If CATEGORICAL == True:
        - If LANG == HI:
            - If sentiment == True: translate and create sentiment column
            - If sentiment == False: translate only
        - If LANG == EN:
            - If sentiment == True: infer sentiment only
            - If sentiment == False: do nothing
    """
    if columns is None:
        columns = metadata_df["column_name"].tolist()

    for col in columns:
        # Get metadata row
        meta_row = metadata_df.loc[metadata_df["column_name"] == col]

        if meta_row.empty:
            if verbose:
                print(f"[⚠️] Column '{col}' not found in metadata. Skipping.")
            continue

        is_categorical = str(meta_row["is_categorical"].values[0]).strip().lower() == "true"
        lang = str(meta_row["lang"].values[0]).strip().lower()
        sentiment_required = str(meta_row["sentiment_required"].values[0]).strip().lower() == "yes"
        col_desc = str(meta_row["desc_en"].values[0]).strip()

        if not is_categorical:
            if verbose:
                print(f"[ℹ️] Skipping '{col}': not categorical.")
            continue

        # Get current category_values
        current_value = metadata_df.loc[metadata_df["column_name"] == col, "category_values"]
        val = current_value.iloc[0]
        val_str = str(val).strip().lower()

        # Determine whether to skip re-translation
        if sentiment_required:
            skip_translation = False
        else:
            skip_translation = val_str not in ("", "nan")

        # Get unique values from the data if needed
        if skip_translation:
            try:
                unique_values = ast.literal_eval(val)
            except Exception as e:
                if verbose:
                    print(f"[⚠️] Failed to parse category_values for {col}: {e}. Will re-translate.")
                unique_values = sorted(data_df[col].dropna().unique().tolist())
                skip_translation = False
        else:
            unique_values = sorted(data_df[col].dropna().unique().tolist())

        if verbose:
            print(
                f"[📝] Processing '{col}': LANG={lang.upper()} SENTIMENT={sentiment_required} "
                f"Unique: {len(unique_values)} Skip Translation: {skip_translation}"
            )

        # Determine what action to take
        translated = unique_values
        sentiments = ["unknown"] * len(unique_values)

        if lang == "hi" and sentiment_required:
            # Translate + sentiment
            result = translate_list_and_infer_sentiment_with_llm(unique_values, col_desc)
            translated = result["translated_value"]
            sentiments = result["sentiment"]

        elif lang == "hi" and not sentiment_required:
            if not skip_translation:
                translated = translate_list_with_llm(unique_values)

        elif lang == "en" and sentiment_required:
            sentiments = infer_sentiment_with_llm(unique_values, col_desc)

        elif lang == "en" and not sentiment_required:
            if verbose:
                print(f"[ℹ️] '{col}' is EN with no sentiment required. Skipping.")
            continue

        # Build lookup
        lookup_trans = dict(zip(unique_values, translated))
        data_df[col] = data_df[col].map(lookup_trans)

        # Update metadata category_values
        metadata_df.loc[metadata_df["column_name"] == col, "category_values"] = str(translated)

        if sentiment_required:
            # Map sentiments
            lookup_sentiment = dict(zip(translated, sentiments))
            sentiment_col = f"{col}_sentiment"
            data_df[sentiment_col] = data_df[col].map(lookup_sentiment)

            # Create metadata entry for sentiment column
            new_row = metadata_df.loc[metadata_df["column_name"] == col].copy()
            new_row["column_name"] = sentiment_col
            orig_desc = new_row["desc_en"].values[0]
            new_row["desc_en"] = f"Sentiment: {orig_desc}"
            orig_seq = float(new_row["pre_enrichment_col_seq"].values[0])
            new_row["pre_enrichment_col_seq"] = orig_seq + 0.1
            # Mark this column as non-categorical
            new_row["is_categorical"] = "False"
            new_row["category_values"] = str(sorted(set(sentiments)))
            # Append to metadata
            metadata_df = pd.concat([metadata_df, new_row], ignore_index=True)

            if verbose:
                print(f"[✅] Added sentiment column '{sentiment_col}'.")

        else:
            if verbose:
                print(f"[✅] Translated '{col}' with {len(unique_values)} unique values.")

    return data_df, metadata_df