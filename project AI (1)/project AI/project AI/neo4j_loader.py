from neo4j import GraphDatabase
from typing import List, Dict, Tuple
import os
from dotenv import load_dotenv

class Neo4jLoader:
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        """
        Initialize Neo4j connection. If no credentials provided, uses default values.
        """
        # Use the provided credentials for your database
        self.uri = uri or 'bolt://localhost:7687'
        self.user = user or 'neo4j'
        self.password = password or 'neo4jneo4j'
        
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        """Close the Neo4j driver connection."""
        self.driver.close()

    def create_disease_symptom(self, disease: str, symptoms: List[str]):
        """
        Create disease and symptom nodes and relationships between them.
        
        Args:
            disease (str): Name of the disease
            symptoms (List[str]): List of symptoms associated with the disease
        """
        with self.driver.session() as session:
            session.write_transaction(self._create_and_link, disease, symptoms)

    @staticmethod
    def _create_and_link(tx, disease: str, symptoms: List[str]):
        """
        Create disease and symptom nodes and relationships in a single transaction.
        """
        query = """
        MERGE (d:Disease {name: $disease})
        WITH d
        UNWIND $symptoms AS symptom
        MERGE (s:Symptom {name: symptom})
        MERGE (d)-[:HAS_SYMPTOM]->(s)
        """
        tx.run(query, disease=disease, symptoms=symptoms)

    def get_diseases_by_symptoms(self, symptoms: List[str], threshold: float = 0.5) -> List[Dict]:
        """
        Find diseases that match the given symptoms.
        
        Args:
            symptoms (List[str]): List of observed symptoms
            threshold (float): Minimum proportion of matching symptoms required
            
        Returns:
            List[Dict]: List of diseases with matching symptoms and match scores
        """
        with self.driver.session() as session:
            return session.read_transaction(self._find_matching_diseases, symptoms, threshold)

    @staticmethod
    def _find_matching_diseases(tx, symptoms: List[str], threshold: float) -> List[Dict]:
        query = """
        MATCH (d:Disease)
        WITH d, COUNT {(d)-[:HAS_SYMPTOM]->(:Symptom)} as total_symptoms
        MATCH (d)-[:HAS_SYMPTOM]->(s:Symptom)
        WHERE s.name IN $symptoms
        WITH d, total_symptoms, collect(s.name) as matched_symptoms,
             count(s) as matching_count
        WHERE toFloat(matching_count) / total_symptoms >= $threshold
        RETURN d.name as disease,
               matched_symptoms,
               toFloat(matching_count) / total_symptoms as match_score
        ORDER BY match_score DESC
        """
        result = tx.run(query, symptoms=symptoms, threshold=threshold)
        return [dict(record) for record in result]

    def clear_database(self):
        """Remove all nodes and relationships from the database."""
        with self.driver.session() as session:
            session.write_transaction(lambda tx: tx.run("MATCH (n) DETACH DELETE n"))

    def get_all_symptoms(self) -> List[str]:
        """
        Get all symptoms in the database.
        
        Returns:
            List[str]: List of all symptom names
        """
        with self.driver.session() as session:
            result = session.read_transaction(
                lambda tx: tx.run("MATCH (s:Symptom) RETURN s.name as name")
            )
            return [record["name"] for record in result]

    def get_disease_details(self, disease_name: str) -> Dict:
        """
        Get detailed information about a specific disease.
        
        Args:
            disease_name (str): Name of the disease
            
        Returns:
            Dict: Disease details including all associated symptoms
        """
        with self.driver.session() as session:
            result = session.read_transaction(self._get_disease_info, disease_name)
            return result[0] if result else None

    @staticmethod
    def _get_disease_info(tx, disease_name: str) -> List[Dict]:
        query = """
        MATCH (d:Disease {name: $disease})-[:HAS_SYMPTOM]->(s:Symptom)
        RETURN d.name as disease,
               collect(s.name) as symptoms
        """
        result = tx.run(query, disease=disease_name)
        return [dict(record) for record in result] 