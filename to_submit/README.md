# Career in AI Ontology

## Introduction

This folder contains the ontology, competency questions, SPARQL queries, and a Streamlit app for exploring the AI domain. The ontology models key concepts like career roles, AI subfields, skills, learning resources, and tools. The competency questions validate that the ontology can answer relevant queries about careers, learning paths, and market insights in AI.

## Contents

- `competency_questions.sparql`: SPARQL queries for the 10 competency questions.
- `competency_questions_explained.md`: Explanation of each competency question and what it validates.
- `ai-ontology.rdf`: The main ontology file in Turtle format.
- `app.py`: Streamlit app to interactively explore the ontology and run queries.
- `README.md`: This file, providing an overview of the project and its components.
- `poetry.lock`: Dependency lock file for the Python environment.
- `pyproject.toml`: Python project configuration file with dependencies and metadata.
- `215565L_ontology_assignment.mp4`: A video presentation explaining the ontology and its competency questions.
- `results/`: A folder containing query results from the competency questions.

## How to Run

1. Install dependencies: `poetry install` in the project directory.
2. Upload the `ai-ontology.rdf` file to a SPARQL endpoint (e.g., using GraphDB). Ensure the endpoint matches the URL `http://localhost:7200/repositories/ai-ontology`.
3. Ensure you have ollama installed and running with `llama3.2:1B` available.
4. Run the Streamlit app: `poetry run streamlit run app.py` from project root.
5. Use the app to select and run competency questions, view results, and explore the ontology.

## Links

- GitHub Repository: [sem-web-ontology-project](https://github.com/rtweera/sem-web-ontology-project)
