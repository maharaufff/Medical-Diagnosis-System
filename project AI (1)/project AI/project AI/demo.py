from main import MedicalDiagnosisSystem
import time

def print_header(text):
    print("\n" + "="*50)
    print(text)
    print("="*50 + "\n")

def print_diagnosis_results(results, symptoms):
    print(f"Patient Symptoms: {', '.join(symptoms)}\n")
    
    print("1. Knowledge Graph Analysis:")
    print("-" * 30)
    for match in results["knowledge_graph_matches"]:
        print(f"Disease: {match['disease']}")
        print(f"Matching Symptoms: {', '.join(match['matched_symptoms'])}")
        print(f"Confidence Score: {match['match_score']*100:.1f}%")
        print()
    
    print("2. Probabilistic Analysis (Bayesian Network):")
    print("-" * 30)
    # Sort diseases by probability
    prob_matches = sorted(
        results["probabilistic_matches"],
        key=lambda x: x["probability"],
        reverse=True
    )
    
    # Show top 5 most likely diseases
    for match in prob_matches[:5]:
        print(f"Disease: {match['disease']}")
        print(f"Probability: {match['probability']*100:.1f}%")
        print()

def main():
    print_header("Medical Diagnosis System Demonstration")
    print("Initializing the system...")
    system = MedicalDiagnosisSystem()
    
    # Load the knowledge base
    print("Loading medical knowledge base...")
    system.load_knowledge_base()
    print("Knowledge base loaded successfully!")
    
    # Demo Case 1: Flu-like symptoms
    print_header("Case 1: Patient with Flu-like Symptoms")
    symptoms1 = ["Fever", "Cough", "Fatigue"]
    results1 = system.diagnose_patient(symptoms1)
    print_diagnosis_results(results1, symptoms1)
    
    # Demo Case 2: COVID-19 symptoms
    print_header("Case 2: Patient with COVID-19 Symptoms")
    symptoms2 = ["Fever", "Cough", "Loss of Taste", "Loss of Smell"]
    results2 = system.diagnose_patient(symptoms2)
    print_diagnosis_results(results2, symptoms2)
    
    # Demo Case 3: Allergies symptoms
    print_header("Case 3: Patient with Allergy Symptoms")
    symptoms3 = ["Sneezing", "Runny Nose", "Itchy Eyes"]
    results3 = system.diagnose_patient(symptoms3)
    print_diagnosis_results(results3, symptoms3)
    
    # Interactive Demo
    print_header("Interactive Diagnosis")
    print("Available symptoms:")
    all_symptoms = sorted(list(system.bayesian.get_all_symptoms()))
    for i, symptom in enumerate(all_symptoms, 1):
        print(f"{i}. {symptom}")
    
    print("\nEnter symptom numbers (comma-separated) or 'q' to quit")
    while True:
        user_input = input("\nSelect symptoms (e.g., 1,3,5): ")
        if user_input.lower() == 'q':
            break
            
        try:
            # Convert input to symptom names
            selected_indices = [int(i.strip()) - 1 for i in user_input.split(',')]
            selected_symptoms = [all_symptoms[i] for i in selected_indices]
            
            # Get diagnosis
            results = system.diagnose_patient(selected_symptoms)
            print_diagnosis_results(results, selected_symptoms)
            
        except (ValueError, IndexError) as e:
            print("Invalid input! Please enter valid symptom numbers.")
    
    system.neo4j.close()

if __name__ == "__main__":
    main() 