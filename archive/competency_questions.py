# competency_questions.py

QUERIES = {
    "PREREQUISITES": {
        "description": "Finds the prerequisite chain for Small Language Models.",
        "sparql": """
            PREFIX ai: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
            SELECT ?prerequisite WHERE {
              ai:small_language_models ai:hasPrerequisite+ ?prerequisite .
            }
        """
    },
    "ROLES": {
        "description": "Finds career roles that require PyTorch and their average salary.",
        "sparql": """
            PREFIX ai: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
            SELECT ?careerRole ?salary WHERE {
              ?careerRole ai:requiresSkill ai:pytorch .
              ?careerRole ai:averageSalary ?salary .
            }
        """
    }
}