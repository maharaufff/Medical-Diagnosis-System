from nlp_parser import extract_disease_and_symptoms
from neo4j_connector import create_disease_symptom_relationship, close_driver


def load_knowledge(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        disease, symptoms = extract_disease_and_symptoms(line)
        if disease and symptoms:
            for symptom in symptoms:
                create_disease_symptom_relationship(disease, symptom)
                print(f"Added: {disease} -> {symptom}")
        else:
            print(f"Skipped invalid line: {line.strip()}")


if __name__ == "__main__":
    # Path to your knowledge file
    load_knowledge("knowledge.txt")
    close_driver()
