# app.py
import streamlit as st
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
from competency_questions import QUERIES
import agent

# --- GraphDB Connection ---
SPARQL_ENDPOINT = "http://localhost:7200/repositories/ai-ontology"
sparql = SPARQLWrapper(SPARQL_ENDPOINT)

def run_query(query_string):
    sparql.setQuery(query_string)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    data = []
    for result in results["results"]["bindings"]:
        row = {k: v["value"].split("#")[-1] for k, v in result.items()}
        data.append(row)
    return data

# --- UI Setup ---
st.title("🧠 Modular AI Ontology Agent")
st.write("Powered by GraphDB & local Llama 3.2 1B")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Main Application Flow ---
if prompt := st.chat_input("Ask about prerequisites or PyTorch roles..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        with st.spinner("Agent is classifying intent..."):
            # 1. Agent routes the request
            intent = agent.classify_intent(prompt)
        
        if intent == "UNKNOWN":
            msg = "I can only answer questions about Small Language Model prerequisites or roles requiring PyTorch right now."
            response_placeholder.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})
        else:
            # 2. Retrieve the data based on intent
            sparql_query = QUERIES[intent]["sparql"]
            with st.spinner(f"Running SPARQL query for '{intent}'..."):
                raw_data = run_query(sparql_query)
            
            # Show the under-the-hood process to the examiner
            with st.expander(f"🛠️ Under the Hood: Agent Routed to '{intent}'"):
                st.write("**Executed SPARQL:**")
                st.code(sparql_query, language="sparql")
                st.write("**Raw GraphDB Result:**")
                st.dataframe(pd.DataFrame(raw_data))

            # 3. Agent generates the final response
            with st.spinner("Agent is generating response..."):
                response_stream = agent.generate_natural_response(prompt, raw_data)
                
                full_response = ""
                for chunk in response_stream:
                    full_response += chunk['message']['content']
                    response_placeholder.markdown(full_response + "▌")
                
                response_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})