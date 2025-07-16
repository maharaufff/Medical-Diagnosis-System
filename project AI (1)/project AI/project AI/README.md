# Medical Diagnosis System using Neo4j and Bayesian Networks

This project implements a medical diagnostic system that combines Knowledge Graphs (Neo4j) and Bayesian Networks to predict diseases based on observed symptoms. The system uses both graph-based pattern matching and probabilistic inference to provide comprehensive diagnostic suggestions.

## Features

- Knowledge Graph representation of diseases and symptoms using Neo4j
- Bayesian Network for probabilistic disease inference
- Natural Language Processing for parsing medical knowledge
- Combined diagnosis using both graph-based and probabilistic approaches
- Support for loading medical knowledge from text files
- Configurable matching thresholds and probabilities

## Prerequisites

- Python 3.8+
- Neo4j Database (Desktop or Aura)
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd medical-diagnosis-system
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

3. Install spaCy English language model:
```bash
python -m spacy download en_core_web_sm
```

4. Set up Neo4j:
   - Install Neo4j Desktop or create an Aura instance
   - Create a new database
   - Note down the connection URI, username, and password

5. Configure environment variables:
   Create a `.env` file in the project root with:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

## Usage

1. Prepare your medical knowledge:
   - Edit `knowledge.txt` to include disease-symptom relationships
   - Each line should follow the format:
     ```
     Disease has symptoms Symptom1, Symptom2, Symptom3.
     ```

2. Run the system:
```bash
python main.py
```

The system will:
- Load the medical knowledge into Neo4j and build the Bayesian Network
- Run a sample diagnosis with test symptoms
- Display results from both the Knowledge Graph and Bayesian Network

## Example Output

```
Loading knowledge base...
Knowledge base loaded successfully!

Diagnosing patient with symptoms: ['Fever', 'Cough', 'Fatigue']

Knowledge Graph Matches:
Disease: Flu
Matched Symptoms: ['Fever', 'Cough', 'Fatigue']
Match Score: 0.75

Disease: COVID-19
Matched Symptoms: ['Fever', 'Cough']
Match Score: 0.60

Bayesian Network Probabilities:
Disease: Flu
Probability: 85.2%

Disease: COVID-19
Probability: 67.8%
```

## Project Structure

- `main.py`: Main application entry point and system integration
- `neo4j_loader.py`: Neo4j database operations and queries
- `nlp_parser.py`: Natural language processing for medical knowledge
- `bayesian_network.py`: Bayesian Network implementation
- `knowledge.txt`: Medical knowledge base
- `requirements.txt`: Python package dependencies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 