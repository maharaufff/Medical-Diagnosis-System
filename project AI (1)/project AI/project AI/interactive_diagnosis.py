import os
from medical_diagnosis_system import MedicalDiagnosisSystem
from bayesian_model import predict_disease_probabilities

class InteractiveDiagnosisSystem:
    def __init__(self):
        self.mds = MedicalDiagnosisSystem()
        self.setup_system()
        
    def setup_system(self):
        """Initialize the medical diagnosis system"""
        print("\n🏥 Initializing Medical Diagnosis System...")
        
        # Read and process knowledge
        knowledge = self.mds.read_knowledge_file('project AI/knowledge.txt')
        self.mds.process_knowledge(knowledge)
        
        # Setup Neo4j graph
        self.mds.create_neo4j_nodes_and_relationships()
        
        # Build Bayesian network
        self.bayesian_model = self.mds.build_bayesian_network()
        
        print("\n✅ System initialized successfully!")
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_menu(self):
        """Display the main menu"""
        self.clear_screen()
        print("\n🏥 Medical Diagnosis System")
        print("=" * 50)
        print("\n1. View available symptoms")
        print("2. Start diagnosis")
        print("3. View system information")
        print("4. Exit")
        print("\nEnter your choice (1-4): ")
    
    def display_symptoms(self):
        """Display all available symptoms"""
        self.clear_screen()
        print("\n📋 Available Symptoms")
        print("=" * 50)
        sorted_symptoms = sorted(list(self.mds.symptoms))
        for i, symptom in enumerate(sorted_symptoms, 1):
            print(f"{i}. {symptom}")
        input("\nPress Enter to continue...")
    
    def get_user_symptoms(self):
        """Get symptoms from user input"""
        self.clear_screen()
        print("\n🤒 Symptom Input")
        print("=" * 50)
        
        # Display symptoms with numbers
        sorted_symptoms = sorted(list(self.mds.symptoms))
        for i, symptom in enumerate(sorted_symptoms, 1):
            print(f"{i}. {symptom}")
        
        print("\nEnter symptom numbers (comma-separated) or 'done' to finish:")
        selected_symptoms = []
        
        while True:
            user_input = input("> ").strip().lower()
            if user_input == 'done':
                break
            
            try:
                # Parse comma-separated numbers
                selections = [int(x.strip()) for x in user_input.split(',')]
                for selection in selections:
                    if 1 <= selection <= len(sorted_symptoms):
                        symptom = sorted_symptoms[selection - 1]
                        if symptom not in selected_symptoms:
                            selected_symptoms.append(symptom)
                            print(f"Added: {symptom}")
                    else:
                        print(f"Invalid selection: {selection}")
            except ValueError:
                print("Please enter valid numbers separated by commas.")
        
        return selected_symptoms
    
    def display_diagnosis_results(self, symptoms):
        """Display diagnosis results from both Neo4j and Bayesian analysis"""
        self.clear_screen()
        print("\n🔍 Diagnosis Results")
        print("=" * 50)
        print(f"\nAnalyzing symptoms: {', '.join(symptoms)}")
        print("\n1. Knowledge Graph Analysis (Neo4j):")
        print("-" * 50)
        
        # Get Neo4j results
        neo4j_results = self.mds.query_diseases_by_symptoms(symptoms)
        for i, result in enumerate(neo4j_results[:5], 1):
            disease = result['disease']
            matched_symptoms = set(result['symptoms']).intersection(set(symptoms))
            print(f"\n{i}. {disease}")
            print(f"   Matching symptoms: {', '.join(matched_symptoms)}")
        
        print("\n2. Bayesian Network Analysis:")
        print("-" * 50)
        
        # Prepare evidence for Bayesian network
        evidence = {}
        all_symptoms = list(self.mds.symptoms)
        for symptom in all_symptoms:
            evidence[symptom] = 1 if symptom in symptoms else 0
        
        # Get Bayesian network results
        bayesian_results = self.mds.diagnose_with_bayesian_network(
            self.bayesian_model, evidence
        )
        
        # Display top 5 probable diseases
        for i, (disease, prob) in enumerate(bayesian_results[:5], 1):
            print(f"\n{i}. {disease}")
            print(f"   Probability: {prob:.1f}%")
        
        input("\nPress Enter to continue...")
    
    def display_system_info(self):
        """Display system information and statistics"""
        self.clear_screen()
        print("\n📊 System Information")
        print("=" * 50)
        print(f"\nTotal Diseases: {len(self.mds.diseases)}")
        print(f"Total Symptoms: {len(self.mds.symptoms)}")
        print(f"Total Relationships: {sum(len(symptoms) for symptoms in self.mds.disease_symptom_map.values())}")
        print("\nTop 5 Diseases by Number of Symptoms:")
        
        # Sort diseases by number of symptoms
        sorted_diseases = sorted(
            self.mds.disease_symptom_map.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
        
        for i, (disease, symptoms) in enumerate(sorted_diseases[:5], 1):
            print(f"\n{i}. {disease}")
            print(f"   Symptoms: {len(symptoms)}")
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Main loop for the interactive system"""
        while True:
            self.display_menu()
            choice = input().strip()
            
            if choice == '1':
                self.display_symptoms()
            elif choice == '2':
                symptoms = self.get_user_symptoms()
                if symptoms:
                    self.display_diagnosis_results(symptoms)
            elif choice == '3':
                self.display_system_info()
            elif choice == '4':
                print("\n👋 Thank you for using the Medical Diagnosis System!")
                self.mds.close_connection()
                break
            else:
                print("\n❌ Invalid choice. Please try again.")
                input("\nPress Enter to continue...")

def main():
    try:
        system = InteractiveDiagnosisSystem()
        system.run()
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Please ensure Neo4j is running and try again.")

if __name__ == "__main__":
    main() 