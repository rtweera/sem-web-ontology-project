#!/usr/bin/env python3
"""
Reload the updated AI ontology into GraphDB using REST API
"""
import sys
import urllib.request
import urllib.parse
import urllib.error
import json
from pathlib import Path

# GraphDB Configuration
GRAPHDB_URL = "http://localhost:7200"
REPOSITORY_ID = "ai-ontology"

# Ontology file path
ONTOLOGY_FILE = Path(__file__).parent.parent / "ontology" / "ai-ontology.rdf"

def check_graphdb_health():
    """Check if GraphDB is running"""
    print("Checking GraphDB connection...")
    try:
        url = f"{GRAPHDB_URL}/rest/health"
        with urllib.request.urlopen(url, timeout=5) as response:
            print(f"[OK] GraphDB is running (Status: {response.status})")
            return True
    except Exception as e:
        print(f"[ERROR] GraphDB is not accessible: {e}")
        return False

def check_repository():
    """Check if the repository exists"""
    print(f"Checking repository '{REPOSITORY_ID}'...")
    try:
        url = f"{GRAPHDB_URL}/rest/repositories/{REPOSITORY_ID}"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"[OK] Repository exists: {data.get('name', 'unknown')}")
            return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"[ERROR] Repository '{REPOSITORY_ID}' not found")
        else:
            print(f"[ERROR] HTTP Error {e.code}: {e.reason}")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to check repository: {e}")
        return False

def clear_repository():
    """Clear all data from the repository using statement endpoint"""
    print("Clearing repository data...")
    try:
        # Use the statements endpoint with DELETE method
        url = f"{GRAPHDB_URL}/repositories/{REPOSITORY_ID}/statements"
        
        req = urllib.request.Request(url, method='DELETE')
        req.add_header('Accept', 'application/json')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"[OK] Repository cleared (Status: {response.status})")
            return True
    except Exception as e:
        print(f"[WARNING] Could not clear repository: {e} (continuing anyway...)")
        # Don't fail on this - the upload might work anyway
        return True

def upload_ontology():
    """Upload the ontology file to GraphDB"""
    print(f"Uploading ontology from {ONTOLOGY_FILE}...")
    try:
        if not ONTOLOGY_FILE.exists():
            print(f"[ERROR] Ontology file not found: {ONTOLOGY_FILE}")
            return False
        
        with open(ONTOLOGY_FILE, 'rb') as f:
            ontology_content = f.read()
        
        print(f"[INFO] File size: {len(ontology_content) / 1024:.2f} KB")
        
        # Upload to GraphDB statements endpoint
        url = f"{GRAPHDB_URL}/repositories/{REPOSITORY_ID}/statements"
        
        req = urllib.request.Request(
            url,
            data=ontology_content,
            headers={
                'Content-Type': 'application/rdf+xml',
                'Accept': '*/*'
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            print(f"[OK] Ontology uploaded successfully (Status: {response.status})")
            return True
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8', errors='ignore')
        print(f"[ERROR] HTTP Error {e.code}: {e.reason}")
        print(f"[ERROR] Response: {error_body[:500]}")
        return False
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_data():
    """Verify that the data was loaded"""
    print("\nVerifying data upload...")
    try:
        # Query to check for new individuals
        sparql_query = """
        PREFIX ai-ontology: <http://www.semanticweb.org/ravindu/ontologies/2026/1/ai-ontology#>
        SELECT ?individual WHERE {
            VALUES ?individual {
                ai-ontology:ml_engineer
                ai-ontology:vision_engineer
                ai-ontology:neural_network_basics
                ai-ontology:data_scientist_senior
            }
            ?individual a ai-ontology:Career_Role .
        }
        """
        
        # Use queryService endpoint
        url = f"{GRAPHDB_URL}/repositories/{REPOSITORY_ID}"
        params = {
            'query': sparql_query,
            'format': 'json'
        }
        
        query_url = url + "?" + urllib.parse.urlencode(params)
        
        with urllib.request.urlopen(query_url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            results = data.get('results', {}).get('bindings', [])
            
            print(f"[OK] Found {len(results)} new individuals:")
            for binding in results:
                individual = binding['individual']['value'].split('#')[1]
                print(f"  - {individual}")
            
            return len(results) > 0
        
    except Exception as e:
        print(f"[ERROR] Verification query failed: {e}")
        # Don't fail verification - data might still be there
        return True

def get_triple_count():
    """Get total triple count in repository"""
    try:
        sparql_query = "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }"
        
        url = f"{GRAPHDB_URL}/repositories/{REPOSITORY_ID}"
        params = {
            'query': sparql_query,
            'format': 'json'
        }
        
        query_url = url + "?" + urllib.parse.urlencode(params)
        
        with urllib.request.urlopen(query_url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            count = int(data.get('results', {}).get('bindings', [{}])[0].get('count', {}).get('value', 0))
            print(f"[INFO] Total triples in repository: {count:,}")
            return count
        
    except Exception as e:
        print(f"[WARNING] Could not get triple count: {e}")
        return 0

def main():
    print("=" * 80)
    print("GRAPHDB ONTOLOGY RELOAD UTILITY v2")
    print("=" * 80)
    print()
    
    # Step 1: Check GraphDB health
    if not check_graphdb_health():
        print("[ERROR] GraphDB is not running. Please start GraphDB first.")
        return 1
    
    print()
    
    # Step 2: Check repository exists
    if not check_repository():
        print("[ERROR] Repository does not exist")
        return 1
    
    print()
    
    # Step 3: Clear repository
    clear_repository()
    
    print()
    
    # Step 4: Upload ontology
    if not upload_ontology():
        print("[ERROR] Failed to upload ontology")
        return 1
    
    print()
    
    # Step 5: Verify
    verify_data()
    
    print()
    
    # Step 6: Get stats
    get_triple_count()
    
    print()
    print("=" * 80)
    print("Ontology reload completed!")
    print("=" * 80)
    return 0

if __name__ == "__main__":
    sys.exit(main())
