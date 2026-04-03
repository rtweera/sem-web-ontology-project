# Semantic Web Ontology Project (AI Career Domain)

This repository contains an ontology-driven project for modeling the Artificial Intelligence domain, including:

- AI subfields and foundational prerequisites
- Career roles and required skills
- Learning resources and difficulty levels
- SPARQL competency questions
- A Streamlit app to explore and query the knowledge graph

## Repository Structure

- `ontology/ai-ontology.rdf` — main ontology file (RDF/XML)
- `ontology/COMPETENCY_QUESTIONS.md` — core competency question definitions
- `app/app.py` — main Streamlit interface
- `app/competency_questions_enhanced.py` — enhanced SPARQL query set
- `app/test_enhanced_queries.py` — script to execute/query competency checks
- `app/reload_ontology.py` — utility to reload ontology data into GraphDB
- `docs/` — summaries and result documentation
- `to_submit/` — submission-ready package variant

## Prerequisites

- Python `>=3.11, <3.14`
- [GraphDB](https://graphdb.ontotext.com/) running locally
- A GraphDB repository named `ai-ontology`
- [Ollama](https://ollama.com/) running locally with model `llama3.2:1b`

## Install Dependencies

This project is configured with Poetry:

```bash
poetry install
```

## Load / Reload Ontology into GraphDB

From the repository root:

```bash
python app/reload_ontology.py
```

The script checks GraphDB health, verifies repository availability, clears existing statements, uploads `ontology/ai-ontology.rdf`, and performs basic verification.

## Run the Streamlit App

```bash
poetry run streamlit run app/app.py
```

Default SPARQL endpoint used by the app:

`http://localhost:7200/repositories/ai-ontology`

## Test Competency Queries

```bash
python app/test_enhanced_queries.py
```

This executes the enhanced competency query set against your local GraphDB repository.

## Notes

- Some scripts and queries use ontology terms such as `ai:needKnowldgeOf` exactly as defined in the ontology.
- `archive/` contains older or experimental files retained for reference.

## License

See `LICENSE`.
