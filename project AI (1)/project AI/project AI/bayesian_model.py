from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

# Create the Bayesian model with proper structure
model = DiscreteBayesianNetwork([
    ('Fever', 'Flu'),
    ('Cough', 'Flu'),
    ('Fatigue', 'Flu'),
    ('Fever', 'COVID'),
    ('Cough', 'COVID'),
    ('Fatigue', 'COVID'),
    ('Fever', 'Cold'),
    ('Cough', 'Cold'),
    ('Fatigue', 'Cold'),
])

# Define symptom CPDs (prior probabilities)
cpd_fever = TabularCPD(variable='Fever', variable_card=2, values=[[0.3], [0.7]])
cpd_cough = TabularCPD(variable='Cough', variable_card=2, values=[[0.4], [0.6]])
cpd_fatigue = TabularCPD(variable='Fatigue', variable_card=2, values=[[0.5], [0.5]])

# Conditional probabilities of diseases given symptoms
cpd_flu = TabularCPD(
    variable='Flu', variable_card=2,
    values=[[0.9, 0.8, 0.7, 0.6, 0.6, 0.4, 0.3, 0.1],
            [0.1, 0.2, 0.3, 0.4, 0.4, 0.6, 0.7, 0.9]],
    evidence=['Fever', 'Cough', 'Fatigue'],
    evidence_card=[2, 2, 2]
)

cpd_covid = TabularCPD(
    variable='COVID', variable_card=2,
    values=[[0.85, 0.7, 0.6, 0.4, 0.3, 0.2, 0.1, 0.05],
            [0.15, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9, 0.95]],
    evidence=['Fever', 'Cough', 'Fatigue'],
    evidence_card=[2, 2, 2]
)

cpd_cold = TabularCPD(
    variable='Cold', variable_card=2,
    values=[[0.7, 0.6, 0.4, 0.3, 0.4, 0.3, 0.2, 0.1],
            [0.3, 0.4, 0.6, 0.7, 0.6, 0.7, 0.8, 0.9]],
    evidence=['Fever', 'Cough', 'Fatigue'],
    evidence_card=[2, 2, 2]
)

# Add CPDs to the model
model.add_cpds(cpd_fever, cpd_cough, cpd_fatigue, cpd_flu, cpd_covid, cpd_cold)

# Verify the model
assert model.check_model()

# Inference
inference = VariableElimination(model)

# 🔮 Function to calculate probabilities
def predict_disease_probabilities(symptom_values):
    diseases = ['Flu', 'COVID', 'Cold']
    result = {}
    for disease in diseases:
        query = inference.query(variables=[disease], evidence=symptom_values)
        prob = query.values[1]  # Probability of disease = True
        result[disease] = round(prob * 100, 2)
    return result

# 🧪 Test the model
if __name__ == "__main__":
    # Example: Fever=Yes, Cough=Yes, Fatigue=No
    evidence = {"Fever": 1, "Cough": 1, "Fatigue": 0}
    result = predict_disease_probabilities(evidence)
    print("Disease Probabilities:")
    for disease, prob in result.items():
        print(f"{disease}: {prob}%")
