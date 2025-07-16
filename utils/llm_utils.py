from utils.llms import call_deepseek
import ast

def safe_parse_llm_response(response):
    """
    Clean LLM output and safely parse to dict.
    """
    cleaned = response.strip()
    if cleaned.startswith("```"):
        # Remove any code fences
        cleaned = "\n".join(
            line for line in cleaned.splitlines() if not line.strip().startswith("```")
        )
    return ast.literal_eval(cleaned)

def translate_list_with_llm(values):
    """
    Example: translate Hindi strings to English.
    """
    prompt = (
        f"The following values are part of dataset that records a mentor's visit to schools during a monitoring excercise for the field whose description is:\n" 
        f"{values}\n"
        "Translate the Hindi entries in Values list to English. \n"
        "Return the list of translations with the Hindi entries translated. \n"
        "Do not add any additional text to the response.\n\n"
    )
    
    response = call_deepseek(
        system_prompt="You are a Hindi to English translator.",
        user_prompt=prompt
    )

    return safe_parse_llm_response(response)


from utils.llms import call_deepseek
import ast

def infer_sentiment_with_llm(values, col_desc):
    """
    Given a list of values, return a list of inferred sentiments.
    
    Args:
        values (list): List of strings (unique values from the column).
        col_desc (str): Description of the column (to provide context).

    Returns:
        dict: {'sentiment': [list of sentiments]}
    """
    prompt = (
        f"The following values are part of a dataset that records a mentor's visit to schools during a monitoring exercise.\n"
        f"Column Description: {col_desc}\n"
        f"Values: {values}\n"
        "For each entry in the list, infer whether the sentiment is positive, negative, neutral, or unknown. "
        "If the value is nan, set sentiment to 'unknown'.\n\n"
        "Output Format: Python dictionary with exactly this structure:\n"
        "{'sentiment': [list of sentiments]}\n"
        "Do not add any other text."
    )
    
    response = call_deepseek(
        system_prompt="You are a helpful sentiment classification assistant.",
        user_prompt=prompt
    )

    # print("[🔍] Raw response:\n", response)

    # Parse response
    parsed = safe_parse_llm_response(response)

    return parsed


def translate_list_and_infer_sentiment_with_llm(values, col_desc):
    """
    Example: translate Hindi strings to English.
    """
    prompt = (
        f"The following values are part of dataset that records a mentor's visit to schools during a monitoring excercise for the field whose description is:\n" 
        f"Column Description: {col_desc} \n"
        f"Values: {values}\n"
        "Translate the Hindi entries in Values list to English. \n"
        "For each entry in the list infer whether it is positive, negative, neutral or unknown. For nan values set it to unknown. \n"
        "Output Format: JSON containing the list of translations and sentiments. \n"
        "{'translated_value': [list of translations for each value], 'sentiment': [list of sentiment for each value]}"
        "Do not add any additional text to the response.\n\n"
    )
    
    response = call_deepseek(
        system_prompt="You are a Hindi to English translator.",
        user_prompt=prompt
    )

    return safe_parse_llm_response(response)