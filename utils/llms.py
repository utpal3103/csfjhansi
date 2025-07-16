import os
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletion

# Load environment variables from .env file (once per session)
load_dotenv()

# Now your key is available to `os.getenv()`
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_openai(
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4",
    temperature: float = 0.2
) -> str:
    """
    Wrapper to call OpenAI Chat API (new SDK) with system and user prompts.

    Args:
        system_prompt (str): Instruction to the assistant.
        user_prompt (str): Task or input message from user.
        model (str): OpenAI model to use (default: gpt-4).
        temperature (float): Randomness in output (0 = deterministic).

    Returns:
        str: Text content from the assistant's reply.
    """
    try:
        response: ChatCompletion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"[OpenAI API Error] {e}")
        return ""



# call_GROW_API function

import os
from dotenv import load_dotenv
from groq import Groq
from groq.types.chat import ChatCompletion

# Load environment variables from .env
load_dotenv()

# Initialize Groq client with your API key
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def call_groq(
    system_prompt: str,
    user_prompt: str,
    model: str = "mixtral-8x7b",
    temperature: float = 0.2
) -> str:
    """
    Wrapper to call Groq (Mixtral) Chat API.

    Args:
        system_prompt (str): System instruction.
        user_prompt (str): User prompt text.
        model (str): Model to use (default: Mixtral).
        temperature (float): Randomness in output.

    Returns:
        str: The content of the assistant's reply.
    """
    try:
        response: ChatCompletion = groq_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"[Groq API Error] {e}")
        return ""

# Call Deepseek API

# utils/deepseek_utils.py

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load your DeepSeek API key from .env
load_dotenv()

# Initialize DeepSeek client
deepseek_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

def call_deepseek(
    system_prompt: str,
    user_prompt: str,
    model: str = "deepseek-chat",
    temperature: float = 0.2
) -> str:
    """
    Wrapper to call DeepSeek Chat API with system and user prompts.

    Args:
        system_prompt (str): Instruction to the assistant.
        user_prompt (str): Task or input message from user.
        model (str): DeepSeek model to use (default: deepseek-chat).
        temperature (float): Randomness in output.

    Returns:
        str: Text content from the assistant's reply.
    """
    try:
        response = deepseek_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[DeepSeek API Error] {e}")
        return ""