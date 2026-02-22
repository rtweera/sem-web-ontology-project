# agent.py
import ollama
from competency_questions import QUERIES

# Make sure you have pulled the model: ollama pull llama3.2:1b
MODEL_NAME = 'llama3.2:1b'

def classify_intent(user_prompt):
    """Uses the SLM to route the user's question to the correct SPARQL query."""
    
    available_intents = list(QUERIES.keys())
    
    system_prompt = f"""
    You are an intent classification router for an AI career database. 
    Categorize the user's question into EXACTLY one of these categories: {available_intents}.
    If the user asks about what to learn before something, output PREREQUISITES.
    If the user asks about jobs, salaries, or PyTorch, output ROLES.
    If it does not match, output UNKNOWN.
    Respond with ONLY the category word and nothing else.
    """
    
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
    )
    
    # Clean the output just in case the 1B model adds extra spaces or punctuation
    intent = response['message']['content'].strip().upper()
    
    # Fallback validation
    for valid_intent in available_intents:
        if valid_intent in intent:
            return valid_intent
            
    return "UNKNOWN"

def generate_natural_response(user_prompt, raw_data):
    """Uses the SLM to explain the raw SPARQL JSON data."""
    system_prompt = f"""
    You are a helpful AI career advisor. Use ONLY the following raw JSON data retrieved from our Knowledge Graph to answer the user's question. 
    Format the answer nicely in natural language. Do not invent information.
    Raw Data: {raw_data}
    """
    
    response_stream = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        stream=True
    )
    return response_stream