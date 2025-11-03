# ============================================================
# Imports
# ============================================================

import os
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA

# ============================================================
# NVIDIA NIM LLM Client Initialization
# ============================================================

def get_nim_llm():

    # Load environment variables from .env file
    load_dotenv()

    # Ensure NVIDIA API key is set in environment for authentication
    if os.environ.get("NVIDIA_API_KEY") is None:
        raise EnvironmentError("NVIDIA_API_KEY not found in .env file.")

    # Initialize the ChatNVIDIA LLM client with the specified model
    # You can swap out the model name as needed
    llm = ChatNVIDIA(
        model="meta/llama3-70b-instruct",
        temperature=0.1,
        max_tokens=1024
    )

    return llm
