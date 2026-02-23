#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for enhanced SPARQL competency queries.
Executes all queries against the GraphDB ontology and reports results.
"""

import sys
import os
from pathlib import Path
from SPARQLWrapper import SPARQLWrapper, JSON
import json
from typing import List, Dict, Tuple
import time

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Configuration
SPARQL_ENDPOINT = "http://localhost:7200/repositories/ai-ontology"
MAX_TIMEOUT = 30

# SPARQL Queries (Enhanced with complex features)
QUERIES = {
    "Q1": {
        "name": "Career Pathway Planning",
        "query": """
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
    "Q2": {
        "name": "Tool and Skill Requirements",
        "query": """
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
    "Q3": {
        "name": "Prerequisites Hierarchy",
        "query": """
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
    "Q4": {
        "name": "Competency-Based Job Matching",
        "query": """
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
    "Q5": {
        "name": "Recommended Learning Path",
        "query": """
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
    "Q6": {
        "name": "Salary and Compensation Analysis",
        "query": """
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
    "Q7": {
        "name": "Tool Adoption and Versioning",
        "query": """
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
    "Q8": {
        "name": "Similarity and Related Concepts",
        "query": """
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
    "Q9": {
        "name": "Type Hierarchy and Classification",
        "query": """
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
    "Q10": {
        "name": "Disjointness and Mutual Exclusivity",
        "query": """
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
    "Q11": {
        "name": "Multi-Criteria Optimization",
        "query": """
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
    "Q12": {
        "name": "Skill Gap Analysis",
        "query": """
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
    "Q13": {
        "name": "Educational Pathway Validation",
        "query": """
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
    "Q14": {
        "name": "Ontology Class Instance Discovery",
        "query": """
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
    "Q15": {
        "name": "Cross-Domain Relationship Discovery",
        "query": """
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
    "Q16": {
        "name": "Reasoning Over Open World",
        "query": """
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
    "Q17": {
        "name": "Competency Validation Against Standards",
        "query": """
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


def test_graphdb_connection() -> bool:
    """Test if GraphDB is accessible."""
    try:
        sparql = SPARQLWrapper(SPARQL_ENDPOINT)
        sparql.setQuery("SELECT ?s WHERE { ?s ?p ?o } LIMIT 1")
        sparql.setReturnFormat(JSON)
        sparql.setTimeout(5)
        sparql.query()
        return True
    except Exception as e:
        print(f"[FAILED] GraphDB Connection Failed: {e}")
        return False


def execute_query(query_id: str, query_text: str) -> Tuple[bool, int, str]:
    """
    Execute a single SPARQL query.
    Returns (success, result_count, message)
    """
    try:
        sparql = SPARQLWrapper(SPARQL_ENDPOINT)
        sparql.setQuery(query_text)
        sparql.setReturnFormat(JSON)
        sparql.setTimeout(MAX_TIMEOUT)
        
        start_time = time.time()
        results = sparql.query().convert()
        elapsed = time.time() - start_time
        
        result_count = len(results.get("results", {}).get("bindings", []))
        message = f"[OK] Success - {result_count} results in {elapsed:.2f}s"
        return True, result_count, message
        
    except Exception as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower():
            message = f"[TIMEOUT] Timeout after {MAX_TIMEOUT}s"
        elif "not found" in error_msg.lower() or "undefined" in error_msg.lower():
            message = f"[WARN] Undefined entity/property: {error_msg[:100]}"
        else:
            message = f"[ERROR] Error: {error_msg[:100]}"
        return False, 0, message


def run_all_tests():
    """Run all test queries and generate report."""
    print("=" * 80)
    print("ENHANCED SPARQL COMPETENCY QUERIES - TEST REPORT")
    print("=" * 80)
    print()
    
    # Test connection
    print("Testing GraphDB connection...")
    if not test_graphdb_connection():
        print(f"\n[NOTICE] GraphDB is not accessible at {SPARQL_ENDPOINT}")
        print("Please ensure GraphDB is running and the ontology is loaded.")
        return
    
    print("[OK] GraphDB connection successful!\n")
    print("=" * 80)
    print()
    
    # Run tests
    results_summary = []
    succeeded = 0
    failed = 0
    
    for query_id in sorted(QUERIES.keys()):
        query_info = QUERIES[query_id]
        query_name = query_info["name"]
        query_text = query_info["query"]
        
        print(f"Running {query_id}: {query_name}...")
        success, count, message = execute_query(query_id, query_text)
        
        results_summary.append({
            "id": query_id,
            "name": query_name,
            "success": success,
            "count": count,
            "message": message
        })
        
        print(f"  {message}\n")
        
        if success:
            succeeded += 1
        else:
            failed += 1
    
    # Print summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Queries: {len(QUERIES)}")
    print(f"Succeeded: {succeeded}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {succeeded/len(QUERIES)*100:.1f}%")
    print()
    
    # Detailed results
    print("DETAILED RESULTS:")
    print("-" * 80)
    for result in results_summary:
        status = "[OK]" if result["success"] else "[FAIL]"
        print(f"{status} {result['id']:3} | {result['name']:40} | {result['message']}")
    
    print()
    print("=" * 80)
    
    # Save report to JSON
    report_file = Path(__file__).parent / "query_test_report.json"
    with open(report_file, 'w') as f:
        json.dump({
            "summary": {
                "total": len(QUERIES),
                "succeeded": succeeded,
                "failed": failed,
                "success_rate": f"{succeeded/len(QUERIES)*100:.1f}%"
            },
            "results": results_summary
        }, f, indent=2)
    
    print(f"Report saved to: {report_file}")
    print()


if __name__ == "__main__":
    run_all_tests()
