from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from typing import Dict, List, Set, Tuple
import numpy as np

class MedicalBayesianNetwork:
    def __init__(self):
        """Initialize an empty Bayesian Network for medical diagnosis."""
        self.model = DiscreteBayesianNetwork()
        self.symptoms: Set[str] = set()
        self.diseases: Set[str] = set()
        self.inference_engine = None
        self.disease_symptom_map = {}

    def add_disease_symptoms(self, disease: str, symptoms: List[str], 
                           base_probability: float = 0.01):
        """
        Add a disease and its symptoms to the Bayesian Network.
        
        Args:
            disease (str): Name of the disease
            symptoms (List[str]): List of symptoms associated with the disease
            base_probability (float): Prior probability of the disease
        """
        # Add disease and symptoms to our tracking sets
        self.diseases.add(disease)
        self.symptoms.update(symptoms)
        self.disease_symptom_map[disease] = symptoms
        
        # Add nodes to the network if they don't exist
        if disease not in self.model.nodes():
            self.model.add_node(disease)
        
        for symptom in symptoms:
            if symptom not in self.model.nodes():
                self.model.add_node(symptom)
            # In this model, diseases are parents of symptoms
            if (disease, symptom) not in self.model.edges():
                self.model.add_edge(disease, symptom)

    def build_network(self):
        """
        Build the complete Bayesian Network and prepare it for inference.
        Should be called after all diseases and symptoms are added.
        """
        try:
            # Add CPDs for diseases (prior probabilities)
            for disease in self.diseases:
                disease_cpd = TabularCPD(
                    variable=disease,
                    variable_card=2,  # Binary: Present/Absent
                    values=[[0.99], [0.01]]  # Prior probability
                )
                self.model.add_cpds(disease_cpd)

            # Add CPDs for symptoms
            for symptom in self.symptoms:
                # Find all diseases that cause this symptom
                related_diseases = [
                    disease for disease, symptoms in self.disease_symptom_map.items()
                    if symptom in symptoms
                ]
                
                if not related_diseases:
                    continue

                # Create CPD for the symptom
                n_diseases = len(related_diseases)
                n_states = 2 ** n_diseases
                
                # Create probability table
                # Default probability of symptom when no disease is present
                prob_table = np.zeros((2, n_states))
                prob_table[0] = 0.9  # Probability of symptom being absent
                prob_table[1] = 0.1  # Probability of symptom being present
                
                # Adjust probabilities based on disease presence
                for i in range(1, n_states):
                    # More diseases present = higher probability of symptom
                    n_diseases_present = bin(i).count('1')
                    prob_present = min(0.1 + 0.8 * (n_diseases_present / n_diseases), 0.99)
                    prob_table[1, i] = prob_present
                    prob_table[0, i] = 1 - prob_present

                symptom_cpd = TabularCPD(
                    variable=symptom,
                    variable_card=2,
                    values=prob_table,
                    evidence=related_diseases,
                    evidence_card=[2] * n_diseases
                )
                self.model.add_cpds(symptom_cpd)

            self.model.check_model()
            self.inference_engine = VariableElimination(self.model)
            print("Bayesian Network built successfully!")
            
        except Exception as e:
            print(f"Error building network: {str(e)}")
            raise

    def diagnose(self, observed_symptoms: Dict[str, bool]) -> Dict[str, float]:
        """
        Perform inference to diagnose diseases given observed symptoms.
        
        Args:
            observed_symptoms (Dict[str, bool]): Dictionary mapping symptom names
                to their observed states (True for present, False for absent)
                
        Returns:
            Dict[str, float]: Dictionary mapping disease names to their probabilities
        """
        if not self.inference_engine:
            raise RuntimeError("Network not built. Call build_network() first.")
            
        evidence = {
            symptom: int(present)
            for symptom, present in observed_symptoms.items()
        }
        
        results = {}
        for disease in self.diseases:
            try:
                query_result = self.inference_engine.query(
                    variables=[disease],
                    evidence=evidence
                )
                # Get probability of disease being present (state 1)
                results[disease] = query_result.values[1]
            except Exception as e:
                print(f"Error querying disease {disease}: {str(e)}")
                results[disease] = None
                
        return results

    def get_all_symptoms(self) -> Set[str]:
        """Get all symptoms in the network."""
        return self.symptoms

    def get_all_diseases(self) -> Set[str]:
        """Get all diseases in the network."""
        return self.diseases

    def get_disease_symptoms(self, disease: str) -> Set[str]:
        """Get all symptoms associated with a specific disease."""
        return set(self.disease_symptom_map.get(disease, set())) 