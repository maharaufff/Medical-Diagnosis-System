from neo4j import GraphDatabase

# === CONFIGURATION ===
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4jneo4j"  # Replace with your password

# === DRIVER SETUP ===
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# === FUNCTION TO CREATE NODES AND RELATIONSHIPS ===
def create_disease_symptom_relationship(disease, symptom):
    with driver.session() as session:
        # Create Disease node if not exists
        session.run("""
            MERGE (d:Disease {name: $disease})
        """, disease=disease)

        # Create Symptom node if not exists
        session.run("""
            MERGE (s:Symptom {name: $symptom})
        """, symptom=symptom)

        # Create Relationship
        session.run("""
            MATCH (d:Disease {name: $disease})
            MATCH (s:Symptom {name: $symptom})
            MERGE (d)-[:HAS_SYMPTOM]->(s)
        """, disease=disease, symptom=symptom)

def test_connection():
    try:
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            print("✅ Connected to Neo4j! Result:", result.single()["test"])
    except Exception as e:
        print("❌ Failed to connect to Neo4j:", e)


# === Close the driver ===
def close_driver():
    driver.close()

if __name__ == "__main__":
    test_connection()
    close_driver()

