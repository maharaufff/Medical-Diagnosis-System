#!/usr/bin/env python3
"""
Test script for Medical Diagnosis System
Tests all major components: Neo4j, spaCy, pgmpy, and knowledge processing
"""

import sys
import traceback

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import spacy
        print("✅ spaCy imported successfully")
    except ImportError as e:
        print(f"❌ spaCy import failed: {e}")
        return False
    
    try:
        from neo4j import GraphDatabase
        print("✅ Neo4j imported successfully")
    except ImportError as e:
        print(f"❌ Neo4j import failed: {e}")
        return False
    
    try:
        from pgmpy.models import DiscreteBayesianNetwork
        from pgmpy.factors.discrete import TabularCPD
        from pgmpy.inference import VariableElimination
        print("✅ pgmpy imported successfully")
    except ImportError as e:
        print(f"❌ pgmpy import failed: {e}")
        return False
    
    return True

def test_spacy_model():
    """Test if spaCy English model is available"""
    print("\n🔍 Testing spaCy model...")
    
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy English model loaded successfully")
        
        # Test basic NLP
        doc = nlp("Flu has symptoms Fever, Cough.")
        print(f"✅ NLP processing test passed: {len(doc)} tokens")
        return True
    except Exception as e:
        print(f"❌ spaCy model test failed: {e}")
        return False

def test_neo4j_connection():
    """Test Neo4j connection"""
    print("\n🔍 Testing Neo4j connection...")
    
    try:
        from neo4j import GraphDatabase
        
        # Test connection
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "neo4jneo4j"))
        
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            test_value = result.single()["test"]
            print(f"✅ Neo4j connection successful: {test_value}")
        
        driver.close()
        return True
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        return False

def test_knowledge_file():
    """Test if knowledge.txt exists and can be read"""
    print("\n🔍 Testing knowledge file...")
    
    try:
        with open('knowledge.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            print(f"✅ Knowledge file read successfully: {len(lines)} lines")
            return True
    except FileNotFoundError:
        print("❌ knowledge.txt file not found")
        return False
    except Exception as e:
        print(f"❌ Knowledge file read failed: {e}")
        return False

def test_bayesian_network():
    """Test Bayesian Network creation"""
    print("\n🔍 Testing Bayesian Network...")
    
    try:
        from pgmpy.models import DiscreteBayesianNetwork
        from pgmpy.factors.discrete import TabularCPD
        
        # Create simple test network
        model = DiscreteBayesianNetwork([('Fever', 'Flu'), ('Cough', 'Flu')])
        
        # Create CPDs
        cpd_fever = TabularCPD(variable='Fever', variable_card=2, values=[[0.8], [0.2]])
        cpd_cough = TabularCPD(variable='Cough', variable_card=2, values=[[0.9], [0.1]])
        cpd_flu = TabularCPD(variable='Flu', variable_card=2, 
                            values=[[0.7, 0.9, 0.8, 0.1], [0.3, 0.1, 0.2, 0.9]], 
                            evidence=['Fever', 'Cough'], evidence_card=[2, 2])
        
        model.add_cpds(cpd_fever, cpd_cough, cpd_flu)
        print("✅ Bayesian Network created successfully")
        return True
    except Exception as e:
        print(f"❌ Bayesian Network test failed: {e}")
        return False

def run_complete_test():
    """Run all tests"""
    print("🧪 MEDICAL DIAGNOSIS SYSTEM - COMPONENT TESTS")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_spacy_model,
        test_neo4j_connection,
        test_knowledge_file,
        test_bayesian_network
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\n🚀 You can now run:")
        print("   python medical_diagnosis_system.py")
        print("   python interactive_diagnosis.py")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    print("=" * 50)

if __name__ == "__main__":
    run_complete_test() 