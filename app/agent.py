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

# def generate_natural_response(user_prompt, raw_data):
#     """Uses the SLM to explain the raw SPARQL JSON data."""
#     system_prompt = f"""
#     You are a helpful AI career advisor. Use ONLY the following raw JSON data retrieved from our Knowledge Graph to answer the user's question. 
#     Format the answer nicely in natural language. Do not invent information.
#     Raw Data: {raw_data}
#     """
    
#     response_stream = ollama.chat(
#         model=MODEL_NAME,
#         messages=[
#             {'role': 'system', 'content': system_prompt},
#             {'role': 'user', 'content': user_prompt}
#         ],
#         stream=True
#     )
#     return response_stream

# def generate_natural_response(user_prompt, raw_data):
#     """Uses the SLM to explain the raw SPARQL JSON data with strict grounding."""
    
#     # 1. Strict constraint prompt with XML data separation
#     system_prompt = f"""
#     You are a strict data-to-text assistant. Your ONLY job is to explain the provided JSON data in natural language.
    
#     CRITICAL INSTRUCTIONS:
#     1. You must ONLY use the exact information present in the <data> block below.
#     2. DO NOT use any outside knowledge, pre-trained information, or assumptions.
#     3. DO NOT add extra job roles, industries, skills, or contexts that are not explicitly written in the <data>.
#     4. If the <data> is empty, simply reply with: "I don't have that information in the knowledge graph."

#     <data>
#     {raw_data}
#     </data>
#     """
    
#     # 2. Drop temperature to 0.0 for deterministic factual output
#     response_stream = ollama.chat(
#         model=MODEL_NAME,
#         messages=[
#             {'role': 'system', 'content': system_prompt},
#             {'role': 'user', 'content': user_prompt}
#         ],
#         stream=True,
#         options={'temperature': 0.0}
#     )
#     return response_stream

# def generate_natural_response(user_prompt, raw_data):
#     """Uses the SLM to explain the raw SPARQL JSON data with strict few-shot grounding."""
    
#     # 1. Format the JSON data into a clean text string to prevent formatting confusion
#     if not raw_data:
#         data_context = "NO DATA FOUND."
#     else:
#         # Converts [{'careerRole': 'ml_engineer', 'salary': '120000'}] into "- careerRole: ml_engineer, salary: 120000"
#         data_context = "\n".join([f"- " + ", ".join([f"{k}: {v}" for k, v in row.items()]) for row in raw_data])
        
#     # 2. Strict constraint prompt using Few-Shot Examples and Negative Constraints
#     system_prompt = f"""
#     You are a strict data reporter for an AI career database. Your ONLY job is to read the DATA BLOCK and state exactly what is inside it.

#     CRITICAL RULES:
#     1. NEVER use outside knowledge or pre-trained information.
#     2. If a job, skill, or industry is not explicitly written in the DATA BLOCK, you MUST NOT mention it.
#     3. Keep your answer brief and factual.

#     DATA BLOCK:
#     {data_context}

#     ---
#     EXAMPLE 1:
#     User: What are the jobs that involve pytorch?
#     DATA BLOCK:
#     - careerRole: ml_engineer, salary: 120000
#     Response: According to the database, the only role that requires PyTorch is 'ml_engineer', which has an average salary of 120000.

#     EXAMPLE 2:
#     User: What are the prerequisites?
#     DATA BLOCK:
#     NO DATA FOUND.
#     Response: I don't have that information in the knowledge graph.
#     ---
#     """
    
#     # 3. Drop temperature to 0.0 to remove creative freedom and force deterministic outputs
#     response_stream = ollama.chat(
#         model=MODEL_NAME,
#         messages=[
#             {'role': 'system', 'content': system_prompt},
#             {'role': 'user', 'content': user_prompt}
#         ],
#         stream=True,
#         options={'temperature': 0.0}
#     )
#     return response_stream

def generate_natural_response(user_prompt, raw_data):
    """Uses the SLM to explain the raw SPARQL JSON data with strict positive formatting."""
    
    if not raw_data:
        data_context = "NO DATA FOUND."
    else:
        # Converts the JSON list into a flat text format
        data_context = "\n".join([f"- " + ", ".join([f"{k}: {v}" for k, v in row.items()]) for row in raw_data])
        
    # Shifting from Negative Constraints to Positive Structural Constraints
    system_prompt = f"""
    You are a data-to-text parser. Your task is to convert the DATA BLOCK into a single, direct sentence.

    RULES:
    1. Base your answer EXCLUSIVELY on the DATA BLOCK.
    2. Start your response directly with the answer. 
    3. Output nothing else. No introductions, no explanations.

    DATA BLOCK:
    {data_context}

    ---
    EXAMPLE 1:
    User: What are the jobs that involve pytorch?
    DATA BLOCK:
    - careerRole: ml_engineer, salary: 120000
    Response: The only role that requires PyTorch is 'ml_engineer', which has an average salary of 120000.

    EXAMPLE 2:
    User: What are the prerequisites?
    DATA BLOCK:
    NO DATA FOUND.
    Response: I don't have that information in the knowledge graph.
    ---
    """
    
    response_stream = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        stream=True,
        options={'temperature': 0.0}
    )
    return response_stream