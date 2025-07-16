from neo4j import GraphDatabase

# Neo4j configuration (same as in neo4j_connector.py)
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4jneo4j"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


# Query diseases that match one or more symptoms
def query_diseases(symptom_list):
    with driver.session() as session:
        query = """
        MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)
        WHERE s.name IN $symptoms
        RETURN d.name AS disease, count(s) AS matchedSymptoms
        ORDER BY matchedSymptoms DESC
        """
        result = session.run(query, symptoms=symptom_list)

        diseases = []
        for record in result:
            diseases.append((record["disease"], record["matchedSymptoms"]))
        return diseases


def close_connection():
    driver.close()


# 🧪 Test block
if __name__ == "__main__":
    user_symptoms = ["Fever", "Cough"]
    results = query_diseases(user_symptoms)

    print("\nDiseases that match your symptoms:")
    for disease, count in results:
        print(f"- {disease} (matched {count} symptom{'s' if count > 1 else ''})")

    close_connection()

