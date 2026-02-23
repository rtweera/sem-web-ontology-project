import streamlit as st
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
import ollama

# --- 1. System Configuration & GraphDB Setup ---
SPARQL_ENDPOINT = "http://localhost:7200/repositories/ai-ontology"
sparql = SPARQLWrapper(SPARQL_ENDPOINT)

PREFIXES = """
PREFIX ai: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
"""

@st.cache_data(show_spinner=False)
def run_query(query_string):
    """Executes a SPARQL query against GraphDB and returns a DataFrame and raw JSON."""
    try:
        sparql.setQuery(query_string)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        
        data = []
        for result in results["results"]["bindings"]:
            row = {k: v["value"].split("#")[-1] for k, v in result.items()}
            data.append(row)
        return pd.DataFrame(data), data
    except Exception as e:
        return pd.DataFrame(), str(e)

# --- 2. Agent Configuration ---
MODEL_NAME = 'llama3.2:1b'

AGENT_QUERIES = {
    "PREREQUISITES": {
        "keywords": "prerequisite, learn, before, small language models",
        "sparql": PREFIXES + "SELECT ?prerequisite WHERE { ai:small_language_models ai:hasPrerequisite+ ?prerequisite . }"
    },
    "ROLES": {
        "keywords": "role, job, career, pytorch, salary, jobs",
        "sparql": PREFIXES + "SELECT ?careerRole ?salary WHERE { ?careerRole ai:requiresSkill ai:pytorch . OPTIONAL { ?careerRole ai:averageSalary ?salary . } }"
    },
    "RAG_TOOLS": {
        "keywords": "tools, rag, retrieval augmented generation, open source",
        "sparql": PREFIXES + "SELECT ?tool ?isOpenSource WHERE { ai:retrieval_augmented_generation ai:usesTool ?tool . OPTIONAL { ?tool ai:isOpenSource ?isOpenSource . } }"
    }
}

def classify_intent(user_prompt):
    """Router: Uses the SLM to classify the user's question to the correct query category."""
    available_intents = list(AGENT_QUERIES.keys())
    system_prompt = f"""
    You are an intent classification router. Categorize the user's question into EXACTLY one of these categories: {available_intents}.
    - If the user asks about what to learn or prerequisites, output PREREQUISITES.
    - If the user asks about jobs, salaries, or PyTorch, output ROLES.
    - If the user asks about RAG, Retrieval Augmented Generation, or tools for it, output RAG_TOOLS.
    - If it does not match, output UNKNOWN.
    Respond with ONLY the category word.
    """
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': user_prompt}],
            options={'temperature': 0.0}
        )
        intent = response['message']['content'].strip().upper()
        for valid in available_intents:
            if valid in intent: return valid
        return "UNKNOWN"
    except Exception:
        return "UNKNOWN"

def generate_natural_response(user_prompt, raw_data):
    """Generator: Uses the SLM to explain the raw SPARQL JSON data."""
    if not raw_data:
        data_context = "NO DATA FOUND."
    else:
        data_context = "\n".join([f"- " + ", ".join([f"{k}: {v}" for k, v in row.items()]) for row in raw_data])
        
    system_prompt = f"""
    You are a data-to-text parser. Convert the DATA BLOCK into a direct, conversational sentence.
    RULES: Base your answer EXCLUSIVELY on the DATA BLOCK. Start directly with the answer. Output nothing else.
    DATA BLOCK:
    {data_context}
    """
    return ollama.chat(
        model=MODEL_NAME,
        messages=[{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': user_prompt}],
        stream=True,
        options={'temperature': 0.0}
    )

# --- 3. UI Layout ---
st.set_page_config(page_title="AICCO Ontology", layout="wide")
st.title("🧠 The Artificial Intelligence Ontology (AICCO)")

tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Competency Questions", 
    "🧭 Curriculum Explorer", 
    "🤖 Transparent AI Agent", 
    "💻 SPARQL Playarea"
])

# --- TAB 1: Competency Questions ---
with tab1:
    st.header("Mandatory Competency Questions")
    
    questions = {
        "1. Complete prerequisite learning path for Small Language Models?": AGENT_QUERIES["PREREQUISITES"]["sparql"],
        "2. Career roles requiring PyTorch and their average salary?": AGENT_QUERIES["ROLES"]["sparql"],
        "3. Tools used for RAG and their open-source status?": AGENT_QUERIES["RAG_TOOLS"]["sparql"],
        "4. Which GenAI concepts have a difficulty level > 7?": PREFIXES + "SELECT ?concept ?diff WHERE { ?concept a ai:Generative_AI ; ai:difficultyLevel ?diff . FILTER (?diff > 7) }"
    }
    
    selected_cq = st.selectbox("Select a question to query the Knowledge Graph:", list(questions.keys()))
    
    if st.button("Execute Competency Query", type="primary"):
        df_cq, _ = run_query(questions[selected_cq])
        if not df_cq.empty:
            st.dataframe(df_cq, use_container_width=True)
        else:
            st.info("No results found in the current ontology state.")
        with st.expander("🛠️ View SPARQL Code"):
            st.code(questions[selected_cq], language="sparql")

# --- TAB 2: Curriculum Explorer (Expanded) ---
with tab2:
    st.header("Interactive Ecosystem Dashboard")
    
    # Section 1 & 2
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📚 Path Builder")
        target_concept = st.selectbox("Target Concept:", ["retrieval_augmented_generation", "small_language_models", "collaborative_filtering", "advanced_cv"])
        if st.button("Generate Path"):
            df_path, _ = run_query(PREFIXES + f"SELECT ?prerequisite WHERE {{ ai:{target_concept} ai:hasPrerequisite+ ?prerequisite . }}")
            if not df_path.empty:
                for _, row in df_path.iterrows(): st.markdown(f"- 📘 `{row['prerequisite']}`")
            else: st.info("No prerequisites mapped.")

    with col2:
        st.subheader("💼 Skill Matcher")
        selected_tool = st.selectbox("Tool/Framework:", ["pytorch", "qdrant", "langchain", "ollama"])
        if st.button("Find Roles"):
            df_roles, _ = run_query(PREFIXES + f"SELECT ?role ?salary WHERE {{ ?role ai:requiresSkill ai:{selected_tool} . OPTIONAL {{ ?role ai:averageSalary ?salary . }} }}")
            st.dataframe(df_roles, use_container_width=True)

    st.divider()
    
    # Section 3 & 4 (New Additions)
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("⚠️ Difficulty & Resource Radar")
        st.write("Find subjects by difficulty and their recommended resources.")
        min_diff = st.slider("Minimum Difficulty Level:", 1, 10, 7)
        if st.button("Analyze Difficulty"):
            diff_query = PREFIXES + f"SELECT ?subject ?difficulty ?resource WHERE {{ ?subject a ai:AI_Subfield ; ai:difficultyLevel ?difficulty . OPTIONAL {{ ?subject ai:recommendedResource ?resource . }} FILTER (?difficulty >= {min_diff}) }}"
            df_diff, _ = run_query(diff_query)
            st.dataframe(df_diff, use_container_width=True)

    with col4:
        st.subheader("💰 Salary Threshold Analyzer")
        st.write("Discover high-paying roles and the specific knowledge they require.")
        min_salary = st.number_input("Minimum Target Salary ($):", value=100000, step=10000)
        if st.button("Analyze Salaries"):
            sal_query = PREFIXES + f"SELECT ?role ?salary ?requiredKnowledge WHERE {{ ?role a ai:Career_Role ; ai:averageSalary ?salary ; ai:needKnowldgeOf ?requiredKnowledge . FILTER (?salary >= {min_salary}) }}"
            df_sal, _ = run_query(sal_query)
            st.dataframe(df_sal, use_container_width=True)

# --- TAB 3: Transparent AI Agent ---
with tab3:
    st.header("Transparent RAG Agent")
    st.write("This chat interface explicitly demonstrates the Agentic routing, SPARQL retrieval, and SLM generation pipeline.")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # FIX: Create a scrollable, fixed-height container for the chat messages
    chat_container = st.container(height=500)

    # Render History inside the fixed container
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            with chat_container.chat_message("user"): 
                st.markdown(msg["content"])
        else:
            with chat_container.chat_message("assistant"):
                if msg.get("intent"): st.info(f"**Agent Router:** Classified intent as `{msg['intent']}`")
                if msg.get("df") is not None and not msg["df"].empty: st.dataframe(msg["df"], use_container_width=True)
                st.markdown(msg["content"])

    # The chat_input sits outside the container, locking it to the bottom
    if prompt := st.chat_input("E.g., What are the prerequisites for small language models?"):
        
        # Append and render user input inside the container
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"): 
            st.markdown(prompt)

        with chat_container.chat_message("assistant"):
            with st.spinner("Agent is classifying intent..."):
                intent = classify_intent(prompt)
                
            if intent == "UNKNOWN":
                fallback_msg = "I can only route questions regarding SLM prerequisites, PyTorch roles, and RAG tools."
                st.warning(f"**Agent Router:** Failed to classify intent. Output: `{intent}`")
                st.markdown(fallback_msg)
                st.session_state.chat_history.append({"role": "assistant", "content": fallback_msg})
            else:
                st.info(f"**Agent Router:** Classified intent as `{intent}`. Executing SPARQL...")
                
                # Execute SPARQL
                df_chat, raw_chat_data = run_query(AGENT_QUERIES[intent]["sparql"])
                st.dataframe(df_chat, use_container_width=True) 
                
                # Generate Natural Response
                response_placeholder = st.empty()
                with st.spinner("Generating natural language response from raw data..."):
                    stream = generate_natural_response(prompt, raw_chat_data)
                    full_resp = ""
                    for chunk in stream:
                        full_resp += chunk['message']['content']
                        response_placeholder.markdown(full_resp + "▌")
                    response_placeholder.markdown(full_resp)
                
                # Save complete interaction to state
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "intent": intent, 
                    "df": df_chat, 
                    "content": full_resp
                })

# --- TAB 4: SPARQL Playarea ---
with tab4:
    st.header("Live SPARQL Editor")
    
    custom_query = st.text_area(
        "Enter custom SPARQL Query:",
        value=PREFIXES + "SELECT * WHERE {\n  ?subject ?predicate ?object .\n} LIMIT 10",
        height=200
    )
    
    if st.button("Run Custom Query", type="primary"):
        with st.spinner("Executing..."):
            df_custom, raw_custom = run_query(custom_query)
            if isinstance(raw_custom, str):
                st.error(f"Query Error: {raw_custom}")
            elif not df_custom.empty:
                st.dataframe(df_custom, use_container_width=True)
            else:
                st.warning("Query executed successfully but returned no results.")