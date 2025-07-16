import spacy
from typing import Tuple, List, Optional

class MedicalKnowledgeParser:
    def __init__(self):
        # Load English language model
        self.nlp = spacy.load("en_core_web_sm")
    
    def extract_entities_relations(self, sentence: str) -> Tuple[Optional[str], Optional[List[str]]]:
        """
        Extract disease and symptoms from a sentence in the format:
        "Disease has symptoms Symptom1, Symptom2, ..."
        
        Args:
            sentence (str): Input sentence
            
        Returns:
            Tuple[Optional[str], Optional[List[str]]]: (disease, list of symptoms) or (None, None) if parsing fails
        """
        try:
            # Split on "has symptoms"
            if "has symptoms" not in sentence:
                return None, None
                
            disease_part, symptoms_part = sentence.split("has symptoms")
            
            # Clean disease name
            disease = disease_part.strip()
            
            # Split symptoms on comma and clean
            symptoms = [
                symptom.strip().strip('.')  # Remove spaces and trailing periods
                for symptom in symptoms_part.split(',')
                if symptom.strip()
            ]
            
            return disease, symptoms
            
        except Exception as e:
            print(f"Error parsing sentence: {sentence}")
            print(f"Error: {str(e)}")
            return None, None
    
    def parse_patient_symptoms(self, text: str) -> List[str]:
        """
        Extract symptoms from patient description text.
        
        Args:
            text (str): Patient's symptom description
            
        Returns:
            List[str]: List of identified symptoms
        """
        doc = self.nlp(text)
        # This is a simple implementation - in a real system, you'd want more sophisticated NLP
        symptoms = []
        for token in doc:
            # Add your symptom recognition logic here
            # This could involve named entity recognition, pattern matching, etc.
            if token.text in ["Fever", "Cough", "Fatigue", "Pain"]:  # Example symptoms
                symptoms.append(token.text)
        return symptoms

    def normalize_symptom(self, symptom: str) -> str:
        """
        Normalize symptom text to standard form.
        
        Args:
            symptom (str): Raw symptom text
            
        Returns:
            str: Normalized symptom text
        """
        # Convert to lowercase and strip whitespace
        normalized = symptom.lower().strip()
        
        # Add more normalization rules as needed
        # For example, mapping common variations to standard forms
        symptom_mapping = {
            "difficulty breathing": "shortness of breath",
            "cant breathe": "shortness of breath",
            "tired": "fatigue",
            "exhausted": "fatigue",
            # Add more mappings as needed
        }
        
        return symptom_mapping.get(normalized, normalized) 