#!/usr/bin/env python3
"""
Reload the updated AI ontology into GraphDB
"""
import sys
import json
import io
from pathlib import Path
from SPARQLWrapper import SPARQLWrapper, DIGEST

# GraphDB Configuration
GRAPHDB_URL = "http://localhost:7200"
REPOSITORY_ID = "ai-ontology"
ENDPOINT = f"{GRAPHDB_URL}/repositories/{REPOSITORY_ID}"

# Ontology file path
ONTOLOGY_FILE = Path(__file__).parent.parent / "ontology" / "ai-ontology.rdf"

def clear_repository():
    """Clear all data from the repository"""
    print("Clearing repository...")
    try:
        sparql = SPARQLWrapper(ENDPOINT)
        sparql.setMethod("POST")
        sparql.setQuery("""
            DELETE { 
                ?s ?p ?o 
            } WHERE { 
                ?s ?p ?o 
            }
        """)
        sparql.query()
        print("[OK] Repository cleared successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to clear repository: {e}")
        return False

def upload_ontology():
    """Upload the ontology file to GraphDB"""
    print(f"Uploading ontology from {ONTOLOGY_FILE}...")
    try:
        with open(ONTOLOGY_FILE, 'r', encoding='utf-8') as f:
            ontology_content = f.read()
        
        # Split namespace definition to use proper namespace 
        sparql = SPARQLWrapper(ENDPOINT)
        sparql.setMethod("POST")
        
        # Use SPARQL INSERT to load RDF/XML data
        # Note: This is a simplified approach - full RDF/XML parsing requires RDF parser
        # We'll use a different approach: construct INSERT statements from the RDF
        print("[INFO] GraphDB repository configured for SPARQL updates")
        print(f"[INFO] Ontology file size: {len(ontology_content)} bytes")
        
        # For a more direct approach, we can use the GraphDB statement endpoint
        print("[INFO] Using direct RDF upload endpoint...")
        
        import urllib.request
        import urllib.error
        
        # Use GraphDB's RDF upload endpoint
        upload_url = f"{GRAPHDB_URL}/repositories/{REPOSITORY_ID}/statements"
        
        req = urllib.request.Request(
            upload_url,
            data=ontology_content.encode('utf-8'),
            headers={'Content-Type': 'application/rdf+xml'},
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                print(f"[OK] Ontology uploaded successfully (Status: {response.status})")
                return True
        except urllib.error.HTTPError as e:
            print(f"[ERROR] HTTP Error {e.code}: {e.reason}")
            print(f"[ERROR] {e.read().decode('utf-8')}")
            return False
            
    except FileNotFoundError:
        print(f"[ERROR] Ontology file not found: {ONTOLOGY_FILE}")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to upload ontology: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_data():
    """Verify that the data was loaded"""
    print("\nVerifying data upload...")
    try:
        sparql = SPARQLWrapper(ENDPOINT)
        sparql.setReturnFormat("json")
        
        # Count all triples
        sparql.setQuery("SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }")
        results = sparql.query().convert()
        
        count = int(results["results"]["bindings"][0]["count"]["value"])
        print(f"[OK] Total triples in repository: {count}")
        
        # Check for new individuals
        sparql.setQuery("""
            PREFIX ai-ontology: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
            SELECT DISTINCT ?individual WHERE {
                VALUES ?individual {
                    ai-ontology:ml_engineer
                    ai-ontology:vision_engineer
                    ai-ontology:neural_network_basics
                    ai-ontology:data_scientist_senior
                }
                ?individual ?p ?o .
            }
        """)
        results = sparql.query().convert()
        
        found_individuals = len(results["results"]["bindings"])
        expected_individuals = 4
        
        print(f"[INFO] Found {found_individuals}/{expected_individuals} new individuals")
        for binding in results["results"]["bindings"]:
            individual = binding["individual"]["value"].split("#")[1]
            print(f"  - {individual}")
        
        return found_individuals > 0
        
    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
        return False

def main():
    print("=" * 80)
    print("GRAPHDB ONTOLOGY RELOAD UTILITY")
    print("=" * 80)
    
    # Step 1: Clear repository
    if not clear_repository():
        print("[ERROR] Failed to clear repository. Exiting.")
        return 1
    
    # Step 2: Upload ontology
    if not upload_ontology():
        print("[ERROR] Failed to upload ontology. Exiting.")
        return 1
    
    # Step 3: Verify
    if not verify_data():
        print("[WARNING] Verification returned no new individuals, but upload may have succeeded")
    
    print("\n" + "=" * 80)
    print("Ontology reload completed!")
    print("=" * 80)
    return 0

if __name__ == "__main__":
    sys.exit(main())
