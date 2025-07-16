import spacy
import re
from neo4j import GraphDatabase
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
import pandas as pd

# === CONFIGURATION ===
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4jneo4j"

# === DRIVER SETUP ===
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# === NLP SETUP ===
print("🔄 Loading spaCy model...")
nlp = spacy.load("en_core_web_sm")
print("✅ spaCy model loaded successfully!")

class MedicalDiagnosisSystem:
    def __init__(self):
        self.diseases = set()
        self.symptoms = set()
        self.disease_symptom_map = {}
        
    def read_knowledge_file(self, filename='project AI/knowledge.txt'):
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
        """Extract diseases and symptoms from a sentence using a robust regex."""
        # This single regex is more robust and handles different phrasing and complex names.
        # It captures the disease name (group 1) and the symptoms string (group 2).
        pattern = re.compile(r'^(.*?)\s+(?:has symptoms|symptoms include)\s+(.*)', re.IGNORECASE)
        match = pattern.search(sentence.strip())
        
        if match:
            # The disease is everything before "has symptoms"
            disease = match.group(1).strip()
            # The symptoms are everything after
            symptoms_text = match.group(2).strip().rstrip('.')
            
            symptoms = [s.strip() for s in symptoms_text.split(',')]
            return disease, symptoms
        
        return None, []
    
    def process_knowledge(self, knowledge_lines):
        """Process knowledge lines and extract entities"""
        print("🔍 Processing knowledge with NLP...")
        
        for i, line in enumerate(knowledge_lines):
            if line.strip():
                disease, symptoms = self.extract_entities_and_relationships(line)
                if disease and symptoms:
                    self.diseases.add(disease)
                    for symptom in symptoms:
                        self.symptoms.add(symptom)
                    self.disease_symptom_map[disease] = symptoms
                    if i < 5:  # Show first 5 for progress
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
    
    def build_bayesian_network(self):
        """Build a causal Bayesian Network (Disease -> Symptom)"""
        print("🧠 Building Causal Bayesian Network...")
        
        edges = []
        for disease, symptoms in self.disease_symptom_map.items():
            for symptom in symptoms:
                edges.append((disease, symptom))
        
        model = DiscreteBayesianNetwork(edges)
        
        # --- Define CPDs ---
        
        # 1. Disease prior probabilities (a small chance for each disease)
        for disease in self.diseases:
            cpd = TabularCPD(
                variable=disease,
                variable_card=2,
                values=[[0.99], [0.01]]  # 1% chance of having any given disease
            )
            model.add_cpds(cpd)
            
        # 2. Symptom conditional probabilities
        for symptom in self.symptoms:
            # Find all diseases that cause this symptom
            parent_diseases = [d for d, s_list in self.disease_symptom_map.items() if symptom in s_list]
            
            if not parent_diseases:
                # Symptom with no parent disease (unlikely but handle it)
                cpd = TabularCPD(variable=symptom, variable_card=2, values=[[0.95], [0.05]])
                model.add_cpds(cpd)
                continue

            # This defines P(Symptom | Disease1, Disease2, ...)
            variable_card = 2
            evidence = parent_diseases
            evidence_card = [2] * len(parent_diseases)
            
            # Probability table:
            # P(Symptom=True | combination of parent diseases)
            # We use a noisy-OR model logic here.
            
            num_states = 2 ** len(parent_diseases)
            prob_symptom_true_values = []
            
            # The probability of the symptom being present, even if no parent disease is active.
            # This represents other causes or random occurrence.
            leak_probability = 0.05 

            # Probability of symptom being present if a single parent disease is active.
            prob_symptom_if_disease = 0.85
            
            for i in range(num_states):
                # Convert i to its binary representation to get parent states
                parent_states = [int(bit) for bit in format(i, f'0{len(parent_diseases)}b')]
                
                # Noisy-OR calculation:
                # 1 - Product_{d_i=true} (1 - P(S|d_i)) * (1 - leak)
                
                # Start with probability of NOT having the symptom if no diseases are present
                prob_not_symptom = 1.0 - leak_probability
                
                for is_present, disease in zip(parent_states, parent_diseases):
                    if is_present:
                        # If a disease is present, it reduces the probability of the symptom being absent
                        prob_not_symptom *= (1.0 - prob_symptom_if_disease)
                
                prob_symptom_true = 1.0 - prob_not_symptom
                prob_symptom_true_values.append(prob_symptom_true)

            values = [
                [1 - p for p in prob_symptom_true_values], # P(Symptom=False | ...)
                prob_symptom_true_values                  # P(Symptom=True | ...)
            ]
            
            cpd = TabularCPD(
                variable=symptom,
                variable_card=variable_card,
                values=values,
                evidence=evidence,
                evidence_card=evidence_card
            )
            model.add_cpds(cpd)

        print(f"✅ Built Bayesian Network with {len(model.edges())} edges and {len(model.cpds)} CPDs")
        model.check_model() # Verify the model is valid
        return model
    
    def add_knowledge_to_file(self, disease, symptoms, filename='project AI/knowledge.txt'):
        """Appends a new disease and its symptoms to the knowledge file."""
        print(f"✍️ Adding new knowledge to {filename}: {disease}")
        # Format: "Disease has symptoms Symptom1, Symptom2, ..."
        new_line = f"\n{disease} has symptoms {', '.join(symptoms)}."
        
        try:
            with open(filename, 'a', encoding='utf-8') as file:
                file.write(new_line)
            print("✅ Knowledge successfully added to file.")
        except Exception as e:
            print(f"❌ Failed to write to {filename}: {e}")
            raise e
    
    def _rewrite_knowledge_file(self, filename='project AI/knowledge.txt'):
        """Rewrites the entire knowledge file from the current disease_symptom_map, ensuring clean and consistent formatting."""
        print("🔄 Rewriting knowledge file with current data...")
        
        # Sort diseases alphabetically for consistency
        sorted_diseases = sorted(self.disease_symptom_map.keys())
        
        lines_to_write = []
        for disease in sorted_diseases:
            symptoms = self.disease_symptom_map[disease]
            if disease and symptoms:
                # Standardize the format: "Disease has symptoms Symptom1, Symptom2."
                # Clean up symptoms to ensure no extra whitespace
                cleaned_symptoms = [s.strip() for s in symptoms]
                line = f"{disease.strip()} has symptoms {', '.join(cleaned_symptoms)}."
                lines_to_write.append(line)
        
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write("\n".join(lines_to_write))
            print("✅ Knowledge file successfully rewritten with standardized format.")
        except Exception as e:
            print(f"❌ Failed to rewrite knowledge file: {e}")
            raise e
            
    def update_knowledge(self, disease_to_update, new_symptoms):
        """Updates the symptoms for a given disease and rewrites the file."""
        if disease_to_update in self.disease_symptom_map:
            print(f"🔄 Updating knowledge for '{disease_to_update}'...")
            self.disease_symptom_map[disease_to_update] = new_symptoms
            self._rewrite_knowledge_file()
        else:
            print(f"⚠️ Attempted to update non-existent disease: {disease_to_update}")

    def delete_knowledge(self, disease_to_delete):
        """Deletes a disease from the knowledge base and rewrites the file."""
        if disease_to_delete in self.disease_symptom_map:
            print(f"🗑️ Deleting knowledge for '{disease_to_delete}'...")
            del self.disease_symptom_map[disease_to_delete]
            self._rewrite_knowledge_file()
        else:
            print(f"⚠️ Attempted to delete non-existent disease: {disease_to_delete}")

    def query_diseases_by_symptoms(self, symptoms):
        """Query Neo4j for diseases based on symptoms"""
        print(f"🔍 Querying diseases for symptoms: {symptoms}")
        
        with driver.session() as session:
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
    
    def diagnose_with_bayesian_network(self, model, observed_symptoms):
        """Diagnose using Bayesian Network"""
        print("🧠 Running Bayesian Network analysis...")
        
        # Prepare evidence for all symptoms
        evidence = {}
        for symptom in self.symptoms:
            evidence[symptom] = 1 if symptom in observed_symptoms else 0
        
        # Create inference engine
        inference = VariableElimination(model)
        
        # Get probabilities for all diseases
        results = []
        for disease in self.diseases:
            try:
                query = inference.query(variables=[disease], evidence=evidence)
                prob = query.values[1]  # Probability of disease = True
                results.append((disease, round(prob * 100, 2)))
            except:
                results.append((disease, 0.0))
        
        # Sort by probability
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    
    def run_complete_system(self):
        """Run the complete medical diagnosis system"""
        print("🚀 Starting Medical Diagnosis System...")
        
        try:
            # Read and process knowledge
            knowledge = self.read_knowledge_file()
            self.process_knowledge(knowledge)
            
            # Setup Neo4j graph
            self.create_neo4j_nodes_and_relationships()
            
            # Build Bayesian network
            bayesian_model = self.build_bayesian_network()
            
            print("\n✅ System initialization complete!")
            print(f"📊 Knowledge Base: {len(self.diseases)} diseases, {len(self.symptoms)} symptoms")
            print("🎯 Ready for diagnosis queries!")
            
            return bayesian_model
            
        except Exception as e:
            print(f"❌ Error during system initialization: {e}")
            return None
    
    def close_connection(self):
        """Close Neo4j connection"""
        driver.close()

def main():
    # Create and run the medical diagnosis system
    system = MedicalDiagnosisSystem()
    
    try:
        bayesian_model = system.run_complete_system()
        
        if bayesian_model:
            # Test the system
            test_symptoms = ['Fever', 'Cough']
            print(f"\n🧪 Testing with symptoms: {test_symptoms}")
            
            # Neo4j query
            neo4j_results = system.query_diseases_by_symptoms(test_symptoms)
            print(f"\n📊 Neo4j Results: {len(neo4j_results)} diseases found")
            
            # Bayesian analysis
            bayesian_results = system.diagnose_with_bayesian_network(bayesian_model, test_symptoms)
            print(f"\n🧠 Bayesian Results: Top 3 probabilities")
            for disease, prob in bayesian_results[:3]:
                print(f"  {disease}: {prob}%")
        
        system.close_connection()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        system.close_connection()

if __name__ == "__main__":
    main() 