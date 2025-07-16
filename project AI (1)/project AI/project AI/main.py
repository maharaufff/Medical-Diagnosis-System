from neo4j_loader import Neo4jLoader
from nlp_parser import MedicalKnowledgeParser
from bayesian_network import MedicalBayesianNetwork
from typing import List, Dict
import os
from dotenv import load_dotenv

class MedicalDiagnosisSystem:
    def __init__(self):
        """Initialize the medical diagnosis system components."""
        self.neo4j = Neo4jLoader()
        self.parser = MedicalKnowledgeParser()
        self.bayesian = MedicalBayesianNetwork()

    def load_knowledge_base(self, filename: str = "knowledge.txt"):
        """
        Load medical knowledge from file into Neo4j and Bayesian Network.
        
        Args:
            filename (str): Path to the knowledge file
        """
        print("Loading knowledge base...")
        
        # Clear existing data
        self.neo4j.clear_database()
        
        # Read and process each line
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                # Parse the line
                disease, symptoms = self.parser.extract_entities_relations(line)
                if disease and symptoms:
                    # Add to Neo4j
                    self.neo4j.create_disease_symptom(disease, symptoms)
                    # Add to Bayesian Network
                    self.bayesian.add_disease_symptoms(disease, symptoms)
        
        # Build the Bayesian Network
        self.bayesian.build_network()
        print("Knowledge base loaded successfully!")

    def diagnose_patient(self, symptoms: List[str], threshold: float = 0.5) -> Dict:
        """
        Diagnose patient based on observed symptoms using both Neo4j and Bayesian inference.
        
        Args:
            symptoms (List[str]): List of observed symptoms
            threshold (float): Minimum match score threshold for Neo4j
            
        Returns:
            Dict: Diagnosis results from both methods
        """
        # Get matching diseases from Neo4j (knowledge graph approach)
        graph_matches = self.neo4j.get_diseases_by_symptoms(symptoms, threshold)
        
        # Prepare symptoms for Bayesian inference
        observed_symptoms = {
            symptom: True for symptom in symptoms
        }
        # Add known absent symptoms (from all possible symptoms)
        all_symptoms = self.bayesian.get_all_symptoms()
        for symptom in all_symptoms:
            if symptom not in symptoms:
                observed_symptoms[symptom] = False
        
        # Get disease probabilities from Bayesian network
        probabilistic_matches = self.bayesian.diagnose(observed_symptoms)
        
        # Combine and format results
        return {
            "knowledge_graph_matches": graph_matches,
            "probabilistic_matches": [
                {"disease": disease, "probability": prob}
                for disease, prob in probabilistic_matches.items()
                if prob is not None  # Filter out any failed queries
            ]
        }

    def close(self):
        """Clean up resources."""
        self.neo4j.close()

def main():
    """Main function to demonstrate the system."""
    system = MedicalDiagnosisSystem()
    
    try:
        # Load the knowledge base
        system.load_knowledge_base()
        
        # Example diagnosis
        test_symptoms = ["Fever", "Cough", "Fatigue"]
        print(f"\nDiagnosing patient with symptoms: {test_symptoms}")
        
        results = system.diagnose_patient(test_symptoms)
        
        # Print Knowledge Graph results
        print("\nKnowledge Graph Matches:")
        for match in results["knowledge_graph_matches"]:
            print(f"Disease: {match['disease']}")
            print(f"Matched Symptoms: {match['matched_symptoms']}")
            print(f"Match Score: {match['match_score']:.2f}")
            print()
        
        # Print Bayesian Network results
        print("\nBayesian Network Probabilities:")
        for match in sorted(
            results["probabilistic_matches"],
            key=lambda x: x["probability"],
            reverse=True
        ):
            print(f"Disease: {match['disease']}")
            print(f"Probability: {match['probability']:.2%}")
            print()
            
    finally:
        system.close()

if __name__ == "__main__":
    main() 