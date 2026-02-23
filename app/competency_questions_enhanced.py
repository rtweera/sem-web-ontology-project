# Enhanced Competency Questions for AI Ontology
# All 17 queries have been enhanced with complex features:
# - OPTIONAL clauses for optional properties
# - GROUP BY and aggregate functions (COUNT, MIN, MAX, SAMPLE, GROUP_CONCAT)
# - FILTER conditions for value constraints
# - UNION to combine alternative patterns
# - MINUS to exclude results
# - Transitive property operators (hasPrerequisite*)

QUERIES = {
    "Q1_CAREER_PATHWAY": {
        "description": "Career Pathway Planning with tool aggregation and difficulty analysis",
        "sparql": """
PREFIX ai: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?subfield ?prerequisite (COUNT(DISTINCT ?tool) as ?toolCount) 
       (MIN(?difficulty) as ?minDifficulty) (MAX(?difficulty) as ?maxDifficulty)
WHERE {
  ai:ml_engineer ai:needKnowldgeOf ?subfield .
  ?subfield ai:hasPrerequisite ?prerequisite .
  OPTIONAL { ?subfield ai:usesTool ?tool }
  OPTIONAL { ?subfield ai:difficultyLevel ?difficulty }
}
GROUP BY ?subfield ?prerequisite
ORDER BY DESC(?toolCount)
LIMIT 50
        """
    },
    "Q2_TOOLS_SKILLS": {
        "description": "Tool and Skill Requirements with UNION for multiple framework types",
        "sparql": """
PREFIX ai: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?framework ?openSource (COUNT(?skill) as ?skillCount)
WHERE {
  {
    ?framework rdf:type ai:Deep_Learning_Framework ;
               ai:isOpenSource ?openSource .
    ai:vision_engineer ai:requiresSkill ?skill .
    FILTER (?openSource = true)
  }
  UNION
  {
    ?framework rdf:type ai:Deep_Learning_Framework ;
               ai:isOpenSource ?openSource .
    FILTER (?openSource = false)
  }
  OPTIONAL { ai:vision_engineer ai:requiresSkill ?skill }
}
GROUP BY ?framework ?openSource
ORDER BY DESC(?skillCount)
LIMIT 50
        """
    },
    "Q3_PREREQUISITES": {
        "description": "Prerequisites Hierarchy with transitive closure and usage counting",
        "sparql": """
PREFIX ai: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?prerequisite (COUNT(?user) as ?usageCount)
WHERE {
  ai:deep_neural_networks ai:hasPrerequisite* ?prerequisite .
  ?prerequisite rdf:type ai:Foundational_Subject .
  OPTIONAL { ?topic ai:hasPrerequisite ?prerequisite . BIND(?topic as ?user) }
}
GROUP BY ?prerequisite
ORDER BY DESC(?usageCount)
LIMIT 50
        """
    },
    "Q4_JOB_MATCHING": {
        "description": "Competency-Based Job Matching with salary filtering and knowledge area counting",
        "sparql": """
PREFIX ai: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?role (COALESCE(?salary, 0) as ?avgSalary) (COUNT(?knowledgeArea) as ?matchCount)
WHERE {
  ?role rdf:type ai:Career_Role ;
        ai:needKnowldgeOf ai:neural_network_basics .
  OPTIONAL { ?role ai:averageSalary ?salary . FILTER (?salary > 200000) }
  ?subfield ai:usesTool ai:python ;
            ai:suitableForLevel ai:intermediate ;
            rdf:type ?knowledgeArea .
}
GROUP BY ?role ?salary
HAVING (COUNT(?knowledgeArea) > 0)
ORDER BY DESC(?matchCount) DESC(?avgSalary)
LIMIT 50
        """
    },
    "Q5_LEARNING_PATH": {
        "description": "Recommended Learning Path with relevance score calculation",
        "sparql": """
PREFIX ai: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?resource ?level (COUNT(?relatedTopic) as ?relevanceScore)
WHERE {
  ai:image_classification rdf:type ai:Computer_Vision ;
                          ai:recommendedResource ?resource ;
                          ai:suitableForLevel ?level .
  ?resource rdf:type ai:Learning_Resource .
  OPTIONAL { ai:image_classification ai:relatedTo ?relatedTopic }
  OPTIONAL { ?resource ai:resourceURL ?url . FILTER(BOUND(?url)) }
}
GROUP BY ?resource ?level
ORDER BY DESC(?relevanceScore) ?level
LIMIT 50
        """
    },
    "Q6_SALARY_ANALYSIS": {
        "description": "Salary and Compensation Analysis with specialization counting",
        "sparql": """
PREFIX ai: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?role ?salary (COUNT(DISTINCT ?knowledge) as ?specializationCount)
       (SAMPLE(?knowledge) as ?example)
WHERE {
  ?role rdf:type ai:Career_Role ;
        ai:averageSalary ?salary ;
        ai:needKnowldgeOf ?knowledge .
  FILTER (?salary > 300000)
  OPTIONAL { ?knowledge rdf:type ai:AI_Subfield }
}
GROUP BY ?role ?salary
HAVING (COUNT(DISTINCT ?knowledge) >= 1)
ORDER BY DESC(?salary) DESC(?specializationCount)
LIMIT 50
        """
    },
    "Q7_TOOL_ADOPTION": {
        "description": "Tool Adoption with UNION for framework filtering and prerequisite chain depth",
        "sparql": """
PREFIX ai: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?subfield ?tool (COUNT(?prerequisites) as ?prerequisiteChainLength)
WHERE {
  ?subfield rdf:type ai:AI_Subfield ;
            ai:usesTool ?tool ;
            ai:hasPrerequisite* ?prerequisites .
  {
    FILTER (?tool = ai:pytorch)
  }
  UNION
  {
    FILTER (?tool = ai:tensorflow)
  }
}
GROUP BY ?subfield ?tool
ORDER BY DESC(?prerequisiteChainLength)
LIMIT 50
        """
    },
    "Q8_RELATED_CONCEPTS": {
        "description": "Similarity and Related Concepts with MINUS clause for exclusion",
        "sparql": """
PREFIX ai: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?topic ?level (COUNT(?tool) as ?toolCount)
WHERE {
  ai:fuzzy_logic_1 ai:relatedTo ?topic .
  OPTIONAL { ?topic ai:difficultyLevel ?level }
  OPTIONAL { ?topic ai:usesTool ?tool }
  MINUS { ?topic ai:suitableForLevel ai:advanced }
}
GROUP BY ?topic ?level
ORDER BY ?level DESC(?toolCount)
LIMIT 50
        """
    },
    "Q9_TYPE_HIERARCHY": {
        "description": "Type Hierarchy with complex OPTIONAL UNION patterns",
        "sparql": """
PREFIX ai: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?resourceType ?instance (COUNT(?attribute) as ?attributeCount)
WHERE {
  ?resourceType rdfs:subClassOf ai:Learning_Resource .
  ?instance rdf:type ?resourceType .
  OPTIONAL { 
    { ?instance ai:difficultyLevel ?attribute }
    UNION
    { ?instance ai:resourceURL ?attribute }
    UNION
    { ?instance ai:suitableForLevel ?attribute }
  }
}
GROUP BY ?resourceType ?instance
ORDER BY DESC(?attributeCount)
LIMIT 50
        """
    },
    "Q10_DISJOINTNESS": {
        "description": "Disjointness Verification with aggregation across class hierarchies",
        "sparql": """
PREFIX ai: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?subfield (COUNT(?subfield_uses) as ?subfield_tools) 
       ?role (COUNT(?role_needs) as ?role_requirements)
WHERE {
  ?subfield rdf:type ai:AI_Subfield .
  OPTIONAL { ?subfield ai:usesTool ?subfield_uses }
  ?role rdf:type ai:Career_Role .
  OPTIONAL { ?role ai:needKnowldgeOf ?role_needs }
}
GROUP BY ?subfield ?role
ORDER BY DESC(?subfield_tools) DESC(?role_requirements)
LIMIT 20
        """
    },
    "Q11_MULTI_CRITERIA": {
        "description": "Multi-Criteria Optimization with open-source tool counting",
        "sparql": """
PREFIX ai: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?role ?salary (COUNT(DISTINCT ?tool) as ?toolCount) 
       (COUNT(DISTINCT ?openSourceTool) as ?openSourceCount)
WHERE {
  ?role rdf:type ai:Career_Role ;
        ai:needKnowldgeOf ?subfield ;
        ai:averageSalary ?salary ;
        ai:requiresSkill ?tool .
  ?subfield rdf:type ai:Computer_Vision .
  FILTER (?salary > 350000)
  OPTIONAL { 
    ?tool ai:isOpenSource true .
    BIND(?tool as ?openSourceTool)
  }
}
GROUP BY ?role ?salary
ORDER BY DESC(?salary) DESC(?openSourceCount)
LIMIT 50
        """
    },
    "Q12_SKILL_GAP": {
        "description": "Skill Gap Analysis with COALESCE and frequency counting",
        "sparql": """
PREFIX ai: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?skill (COALESCE(?openSource, false) as ?isOpenSource) ?skillType 
       (COUNT(?skill) as ?frequency)
WHERE {
  ai:data_scientist ai:requiresSkill ?skill .
  ?skill rdf:type ?skillType .
  OPTIONAL { ?skill ai:isOpenSource ?openSource }
}
GROUP BY ?skill ?openSource ?skillType
ORDER BY DESC(?frequency) ?openSource DESC(?skillType)
LIMIT 50
        """
    },
    "Q13_PATHWAY_VALIDATION": {
        "description": "Educational Pathway Validation with GROUP_CONCAT aggregation",
        "sparql": """
PREFIX ai: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?vision_resource (COUNT(?prerequisiteChain) as ?chainDepth)
       (GROUP_CONCAT(?tool; separator=",") as ?requiredTools)
WHERE {
  ai:linear_algebra_1 rdf:type ai:Linear_Algebra .
  ai:pytorch rdf:type ai:Deep_Learning_Framework .
  ?vision rdf:type ai:Computer_Vision ;
          ai:hasPrerequisite* ?prerequisiteChain ;
          ai:usesTool ai:pytorch ;
          ai:recommendedResource ?vision_resource .
  OPTIONAL { ?vision ai:usesTool ?tool }
}
GROUP BY ?vision_resource
ORDER BY DESC(?chainDepth)
LIMIT 50
        """
    },
    "Q14_CLASS_INSTANCES": {
        "description": "Ontology Class Instance Discovery with property aggregation",
        "sparql": """
PREFIX ai: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?instance ?difficulty (COUNT(?resource) as ?resourceCount) 
       (COUNT(?tool) as ?toolCount) (GROUP_CONCAT(?tool; separator=",") as ?toolList)
WHERE {
  ?instance rdf:type ai:Generative_AI .
  OPTIONAL { ?instance ai:difficultyLevel ?difficulty }
  OPTIONAL { ?instance ai:recommendedResource ?resource }
  OPTIONAL { ?instance ai:usesTool ?tool }
}
GROUP BY ?instance ?difficulty
ORDER BY ?difficulty DESC(?resourceCount)
LIMIT 50
        """
    },
    "Q15_CROSS_DOMAIN": {
        "description": "Cross-Domain Relationship Discovery with UNION patterns",
        "sparql": """
PREFIX ai: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?resource (COUNT(?domain) as ?domainCoverage) 
       (GROUP_CONCAT(?relatedDomain; separator=",") as ?relatedDomains)
WHERE {
  ?resource rdf:type ai:Learning_Resource ;
            ai:suitableForLevel ai:intermediate .
  {
    ?neural rdf:type ai:Neural_Networks ;
            ai:recommendedResource ?resource .
    BIND("Neural_Networks" as ?domain)
    OPTIONAL { ?neural ai:relatedTo ?relatedDomain }
  }
  UNION
  {
    ?fuzzy rdf:type ai:Fuzzy_Logic ;
           ai:recommendedResource ?resource .
    BIND("Fuzzy_Logic" as ?domain)
    OPTIONAL { ?fuzzy ai:relatedTo ?relatedDomain }
  }
}
GROUP BY ?resource
ORDER BY DESC(?domainCoverage)
LIMIT 50
        """
    },
    "Q16_OPEN_WORLD": {
        "description": "Reasoning Over Open World with GROUP_CONCAT and COALESCE",
        "sparql": """
PREFIX ai: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?role (GROUP_CONCAT(DISTINCT ?subfield; separator=", ") as ?subfields) 
       (COALESCE(?salary, 0) as ?salaryTier) (COUNT(?subfield) as ?knowledgeAreaCount)
WHERE {
  ?role rdf:type ai:Career_Role .
  OPTIONAL {
    ?role ai:needKnowldgeOf ?subfield .
    ?subfield rdf:type ai:AI_Subfield .
  }
  OPTIONAL { ?role ai:averageSalary ?salary }
}
GROUP BY ?role ?salary
ORDER BY DESC(?knowledgeAreaCount) DESC(?salary)
LIMIT 50
        """
    },
    "Q17_VALIDATION": {
        "description": "Competency Validation with enforcement of multiple constraints",
        "sparql": """
PREFIX ai: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?subfield (COUNT(DISTINCT ?tool) as ?toolCount) 
       (COUNT(DISTINCT ?prerequisite) as ?prerequisiteCount)
WHERE {
  ?subfield rdf:type ai:AI_Subfield ;
            ai:usesTool ?tool ;
            ai:hasPrerequisite ?prerequisite .
}
GROUP BY ?subfield
ORDER BY DESC(?toolCount) DESC(?prerequisiteCount)
LIMIT 50
        """
    }
}


# Alternative simpler queries for basic use cases
SIMPLE_QUERIES = {
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
