import os
import warnings
from dotenv import load_dotenv
from litellm import completion

# Suppress Pydantic warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Load API key from .env
load_dotenv()
api_key = os.getenv("API_KEY")

if not api_key:
    raise ValueError("API_KEY is not set in the .env file")

def main():
    response = completion(
        model="gemini/gemini-2.0-flash",
        messages=[
            {"role": "user", "content": "Who is the founder of Pakistan?"}
        ],
        api_key=api_key
    )
    print(response['choices'][0]['message']['content'])

if __name__ == "__main__":
    main()
