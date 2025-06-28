from dotenv import load_dotenv
import os

# load env variables from .env file
load_dotenv()

# Access the API_KEY environment variable
api_key = os.getenv("GEMINI_API_KEY")

# Check if the API_KEY is set and print it
if api_key:
    print("API_KEY is set.")
    print(f"API_KEY: {api_key[-5:]}")
else:
    print("API_KEY is not set")