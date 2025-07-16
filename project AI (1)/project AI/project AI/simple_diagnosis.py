import re
from neo4j import GraphDatabase
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

# === CONFIGURATION ===
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4jneo4j"

# === DRIVER SETUP ===
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

class SimpleDiagnosisSystem:
    def __init__(self):
        self.diseases = set()
        self.symptoms = set()
        self.disease_symptom_map = {}
        
    def read_knowledge_file(self, filename='knowledge.txt'):
        """Read knowledge from text file"""
        print("📖 Reading knowledge from file...")
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                knowledge = file.readlines()
            print(f"✅ Successfully read {len(knowledge)} lines from {filename}")
            return knowledge
        except FileNotFoundError:
            print(f"❌ File {filename} not found!")
            return []
    
    def extract_entities_and_relationships(self, sentence):
        """Extract diseases and symptoms from sentence using regex"""
        disease = None
        symptoms = []
        
        # Pattern: "Disease has symptoms Symptom1, Symptom2"
        has_pattern = r'(\w+)\s+has\s+symptoms?\s+(.+)'
        match = re.search(has_pattern, sentence, re.IGNORECASE)
        
        if match:
            disease = match.group(1).strip()
            symptoms_text = match.group(2).strip()
            symptoms = [s.strip() for s in symptoms_text.split(',')]
        
        return disease, symptoms
    
    def process_knowledge(self, knowledge_lines):
        """Process knowledge lines and extract entities"""
        print("🔍 Processing knowledge...")
        
        for line in knowledge_lines:
            if line.strip():
                disease, symptoms = self.extract_entities_and_relationships(line)
                if disease and symptoms:
                    self.diseases.add(disease)
                    for symptom in symptoms:
                        self.symptoms.add(symptom)
                    self.disease_symptom_map[disease] = symptoms
                    print(f"📋 Found: {disease} -> {symptoms}")
        
        print(f"✅ Extracted {len(self.diseases)} diseases and {len(self.symptoms)} symptoms")
    
    def create_neo4j_nodes_and_relationships(self):
        """Create nodes and relationships in Neo4j"""
        print("🗄️ Creating Neo4j knowledge graph...")
        
        with driver.session() as session:
            # Clear existing data
            session.run("MATCH (n) DETACH DELETE n")
            print("🧹 Cleared existing data")
            
            # Create disease and symptom nodes
            for disease in self.diseases:
                session.run("""
                    CREATE (d:Disease {name: $disease})
                """, disease=disease)
            
            for symptom in self.symptoms:
                session.run("""
                    CREATE (s:Symptom {name: $symptom})
                """, symptom=symptom)
            
            # Create relationships
            for disease, symptoms in self.disease_symptom_map.items():
                for symptom in symptoms:
                    session.run("""
                        MATCH (d:Disease {name: $disease})
                        MATCH (s:Symptom {name: $symptom})
                        CREATE (d)-[:HAS_SYMPTOM]->(s)
                    """, disease=disease, symptom=symptom)
            
            print(f"✅ Created {len(self.diseases)} disease nodes, {len(self.symptoms)} symptom nodes, and relationships")
    
    def query_diseases_by_symptoms(self, symptoms):
        """Query Neo4j for diseases based on symptoms"""
        print(f"🔍 Querying diseases for symptoms: {symptoms}")
        
        with driver.session() as session:
            # Build query for multiple symptoms
            symptom_conditions = " OR ".join([f"s.name='{symptom}'" for symptom in symptoms])
            query = f"""
                MATCH (d:Disease)-[:HAS_SYMPTOM]->(s:Symptom)
                WHERE {symptom_conditions}
                RETURN d.name as disease, collect(s.name) as symptoms
                ORDER BY size(collect(s.name)) DESC
            """
            
            result = session.run(query)
            diseases = []
            for record in result:
                diseases.append({
                    'disease': record['disease'],
                    'symptoms': record['symptoms']
                })
            
            return diseases
    
    def close_connection(self):
        """Close Neo4j connection"""
        driver.close()

def main():
    # Create and run the simple diagnosis system
    system = SimpleDiagnosisSystem()
    
    try:
        # Read and process knowledge
        knowledge = system.read_knowledge_file('knowledge.txt')
        system.process_knowledge(knowledge)
        
        # Setup Neo4j graph
        system.create_neo4j_nodes_and_relationships()
        
        # Test query
        test_symptoms = ['Fever', 'Cough']
        results = system.query_diseases_by_symptoms(test_symptoms)
        
        print(f"\n🔍 Test Results for symptoms {test_symptoms}:")
        for result in results[:5]:
            print(f"- {result['disease']}: {result['symptoms']}")
        
        system.close_connection()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        system.close_connection()

if __name__ == "__main__":
    main() 