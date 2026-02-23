import streamlit as st
import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON

# 1. Connect to your local GraphDB Endpoint
# Make sure the repository ID at the end matches exactly what you named it in Step 1
SPARQL_ENDPOINT = "http://localhost:7200/repositories/ai-ontology"
sparql = SPARQLWrapper(SPARQL_ENDPOINT)

# Helper function to run SPARQL and convert to a Pandas DataFrame
def run_query(query_string):
    sparql.setQuery(query_string)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    # Parse the JSON into a flat list of dictionaries
    data = []
    for result in results["results"]["bindings"]:
        # We split by '#' to remove the long URL prefix and just show the snake_case names
        row = {k: v["value"].split("#")[-1] for k, v in result.items()}
        data.append(row)
        
    return pd.DataFrame(data)

# 2. Build the Streamlit UI
st.title("🧠 AI Career & Learning Navigator")
st.write("Discover prerequisites, roles, and tools in the Artificial Intelligence field.")

# 3. Interactive Component: Find Roles by Tool
st.subheader("Skill Requirement Search")
st.write("Which career roles require PyTorch?")

# The SPARQL Query (CQ3) - Using snake_case for instances
query_roles = """
PREFIX ai: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
SELECT ?careerRole ?salary
WHERE {
  ?careerRole ai:requiresSkill ai:pytorch .
  ?careerRole ai:averageSalary ?salary .
}
"""

if st.button("Search Roles"):
    with st.spinner("Querying the ontology..."):
        df = run_query(query_roles)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No roles found for this skill.")

# 4. Interactive Component: View High-Difficulty Subjects
st.subheader("Advanced Subjects Filter")
st.write("View AI subfields with a difficulty level greater than 6.")

# The SPARQL Query (CQ4)
query_difficulty = """
PREFIX ai: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
SELECT ?subfield ?difficulty
WHERE {
  ?subfield ai:difficultyLevel ?difficulty .
  FILTER (?difficulty > 6)
}
"""

if st.button("Filter Subjects"):
    with st.spinner("Querying the ontology..."):
        df_diff = run_query(query_difficulty)
        if not df_diff.empty:
            st.table(df_diff)
        else:
            st.warning("No subjects found matching this criteria.")