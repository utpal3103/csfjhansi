from utils.llm_utils import call_openai
from utils.data_utils import batch_items

def translate_headers_via_llm(headers, batch_size=5, model="gpt-4"):
    """
    Translates a list of column headers (Hindi or English) into structured JSON with
    translated names and short, snake_case aliases using the OpenAI API.

    Args:
        headers (list of str): List of column headers to translate
        batch_size (int): Number of headers per API call
        model (str): OpenAI model to use

    Returns:
        List of dicts: [{original_name, translated_name, short_name}, ...]
    """
    results = []
    system_prompt = """You are a helpful assistant that translates Hindi column headers and generates short, snake_case names.
For each of the following column headers, return a JSON list with:
- "original_name": the original name
- "translated_name": a clear English translation
- "short_name": a concise, snake_case identifier usable in Python
"""

    for batch in batch_items(headers, batch_size):
        user_prompt = "Column Headers:\n" + "\n".join([f"- {h}" for h in batch])
    
        print("\n🧪 Sending batch to OpenAI:")
        print(user_prompt)

        response = call_openai(system_prompt=system_prompt, user_prompt=user_prompt, model=model)

        print("\n🟢 Raw OpenAI Response:")
        print(response)

        try:
            parsed_batch = eval(response)  # temporary
            results.extend(parsed_batch)
        except Exception as e:
            print(f"[ERROR] Failed to parse response:\n{response}\nError: {e}")

    return results