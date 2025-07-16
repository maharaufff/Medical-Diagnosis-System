import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from medical_diagnosis_system import MedicalDiagnosisSystem
import time

# Page configuration
st.set_page_config(
    page_title="Medical Diagnosis System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Admin Configuration ---
ADMIN_PASSWORD = "admin" 

# --- Custom CSS for a new modern dark theme ---
st.markdown("""
<style>
    /* General Body Style */
    body {
        background-color: #1a1a2e; /* Dark blue-purple background */
    }

    /* Main container */
    .main-container {
        background-color: #1a1a2e;
        color: #e0e0e0;
    }

    /* Main Header */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #ffffff;
        margin-bottom: 1rem;
        padding: 1.5rem;
        background: linear-gradient(90deg, #162232, #2a3b4c);
        border-radius: 12px;
        border: 1px solid #3a4b5c;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .sub-header-text {
        text-align: center; 
        font-size: 1.1rem; 
        color: #a0a0b0; 
        margin-bottom: 3rem;
    }

    /* Section Headers */
    .section-header {
        font-size: 1.75rem;
        color: #ffffff;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        font-weight: bold;
        border-bottom: 2px solid #1abc9c;
        padding-bottom: 0.5rem;
    }

    /* Metric Cards on Dashboard */
    .metric-card {
        background: #2a3b4c;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #3a4b5c;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        color: #e0e0e0;
        text-align: center;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(26, 188, 156, 0.2);
    }

    /* Cards for Diseases and Symptoms */
    .info-card {
        background-color: #2a3b4c;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        border-left: 4px solid #1abc9c;
        color: #e0e0e0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: all 0.2s ease-in-out;
    }
    .info-card:hover {
        background-color: #3a4b5c;
    }
    
    /* Symptom tags */
    .symptom-tag-container {
        padding: 1rem;
        background-color: #2a3b4c;
        border-radius: 8px;
        border: 1px solid #3a4b5c;
    }
    .symptom-tag {
        background-color: #3a4b5c;
        padding: 0.5rem 0.75rem;
        margin: 0.25rem;
        border-radius: 15px;
        display: inline-block;
        color: #e0e0e0;
        font-weight: 500;
        font-size: 0.9rem;
        border: 1px solid #4a5b6c;
    }

    /* Diagnosis result card */
    .diagnosis-result-card {
        background: #2a3b4c;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-radius: 12px;
        border: 1px solid #3a4b5c;
        transition: all 0.3s ease;
    }
    .diagnosis-result-card:hover {
        border-color: #1abc9c;
    }

    /* Probability Bar */
    .probability-bar-container {
        width: 100%;
        background-color: #3a4b5c;
        border-radius: 5px;
        margin-top: 0.5rem;
        height: 10px;
        overflow: hidden;
    }
    .probability-bar-fill {
        height: 100%;
        border-radius: 5px;
        background: linear-gradient(90deg, #1abc9c, #2ecc71);
        transition: width 0.5s ease-in-out;
    }

    /* Message boxes */
    .message-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-width: 1px;
        border-style: solid;
        font-weight: bold;
    }
    .success-message {
        background-color: rgba(26, 188, 156, 0.1);
        color: #1abc9c;
        border-color: #1abc9c;
    }
    .warning-message {
        background-color: rgba(241, 196, 15, 0.1);
        color: #f1c40f;
        border-color: #f1c40f;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'system_initialized' not in st.session_state:
    st.session_state.system_initialized = False
if 'mds' not in st.session_state:
    st.session_state.mds = None
if 'bayesian_model' not in st.session_state:
    st.session_state.bayesian_model = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None # Can be 'user' or 'admin'
if 'widget_key_id' not in st.session_state:
    st.session_state.widget_key_id = 0

def initialize_system(force_reload=False):
    """Initialize or reload the medical diagnosis system"""
    spinner_text = "🔄 Reloading Medical Diagnosis System..." if force_reload else "🔄 Initializing Medical Diagnosis System..."
    with st.spinner(spinner_text):
        mds = MedicalDiagnosisSystem()
        knowledge = mds.read_knowledge_file('project AI/knowledge.txt')
        mds.process_knowledge(knowledge)
        mds.create_neo4j_nodes_and_relationships()
        bayesian_model = mds.build_bayesian_network()
        
        st.session_state.mds = mds
        st.session_state.bayesian_model = bayesian_model
        st.session_state.system_initialized = True
        st.session_state.widget_key_id += 1 # Increment key to force widget refresh
    st.toast("System is ready!", icon="✅")

def show_login_screen():
    """Displays the login form to determine user role."""
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">🔑 Welcome to the Diagnosis System</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header-text">Please select your role to proceed.</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("👤 User Access")
        st.write("Access the diagnosis tool to check symptoms.")
        if st.button("Continue as User", key="user_login"):
            st.session_state.user_role = 'user'
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.subheader("🔑 Admin Access")
        password = st.text_input("Enter Admin Password:", type="password", key="admin_pass")
        if st.button("Login as Admin", key="admin_login"):
            if password == ADMIN_PASSWORD:
                st.session_state.user_role = 'admin'
                st.rerun()
            elif password:
                st.error("Incorrect password.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    if not st.session_state.user_role:
        show_login_screen()
        return

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🏥 Medical Diagnosis System</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header-text">AI-Powered Disease Diagnosis using Knowledge Graphs and Bayesian Networks</p>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🔧 System Controls")
    
    if st.session_state.user_role:
        st.sidebar.info(f"Logged in as: **{st.session_state.user_role.capitalize()}**")

    if not st.session_state.system_initialized:
        if st.sidebar.button("🚀 Initialize System", type="primary"):
            initialize_system()
            st.rerun()
    else:
        st.sidebar.success("✅ System Ready")
        
        # Logout Button
        if st.sidebar.button("Logout"):
            st.session_state.user_role = None
            st.session_state.system_initialized = False # Also reset system
            st.rerun()

        # Define tabs based on role
        if st.session_state.user_role == 'admin':
            tab_titles = ["🏠 Dashboard", "🔍 Diagnosis", "📊 Statistics", "⚙️ Admin Panel", "ℹ️ About"]
            tab1, tab2, tab3, tab4, tab5 = st.tabs(tab_titles)
        else: # User role
            tab_titles = ["🔍 Diagnosis", "ℹ️ About"]
            tab2, tab5 = st.tabs(tab_titles)

        if st.session_state.user_role == 'admin':
            with tab1:
                show_dashboard()
            with tab2:
                show_diagnosis()
            with tab3:
                show_statistics()
            with tab4:
                show_admin_panel()
            with tab5:
                show_about()
        else: # User view
            with tab2:
                show_diagnosis()
            with tab5:
                show_about()

    st.markdown('</div>', unsafe_allow_html=True)

def show_dashboard():
    """Display the main dashboard"""
    st.markdown('<h2 class="section-header">📊 System Overview</h2>', unsafe_allow_html=True)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    metrics = {
        "Diseases": len(st.session_state.mds.diseases),
        "Symptoms": len(st.session_state.mds.symptoms),
        "Relationships": sum(len(s) for s in st.session_state.mds.disease_symptom_map.values()),
        "Bayesian Edges": len(st.session_state.bayesian_model.edges())
    }
    
    for col, (label, value) in zip([col1, col2, col3, col4], metrics.items()):
        with col:
            st.markdown(f'<div class="metric-card"><h3>{label}</h3><h2>{value}</h2></div>', unsafe_allow_html=True)

    st.markdown('<h2 class="section-header">📋 Knowledge Base Preview</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏥 Sample Diseases")
        sample_diseases = sorted(list(st.session_state.mds.diseases))[:10]
        for disease in sample_diseases:
            symptoms = st.session_state.mds.disease_symptom_map.get(disease, [])
            st.markdown(f'''
                <div class="info-card">
                    <strong>{disease}</strong><br>
                    <small style="color: #a0a0b0;">Common symptoms: {", ".join(symptoms[:3])}...</small>
                </div>
            ''', unsafe_allow_html=True)
    
    with col2:
        st.subheader("🤒 Common Symptoms")
        sample_symptoms = sorted(list(st.session_state.mds.symptoms))[:15]
        symptoms_html = ""
        for symptom in sample_symptoms:
            symptoms_html += f'<span class="symptom-tag">{symptom}</span>'
        st.markdown(f'<div class="symptom-tag-container">{symptoms_html}</div>', unsafe_allow_html=True)

def show_diagnosis():
    """Show the diagnosis interface"""
    st.markdown('<h2 class="section-header">🔍 Start Diagnosis</h2>', unsafe_allow_html=True)
    
    all_symptoms = sorted(list(st.session_state.mds.symptoms))
    
    selected_symptoms = st.multiselect(
        "Select your symptoms from the list below:",
        all_symptoms,
        placeholder="Start typing to search for symptoms...",
        key=f"symptom_selector_{st.session_state.widget_key_id}"
    )
    
    if selected_symptoms:
        st.markdown(f'''
            <div class="message-box success-message">
                Selected {len(selected_symptoms)} symptoms: {", ".join(selected_symptoms)}
            </div>
        ''', unsafe_allow_html=True)
        
        if st.button("🔬 Run Diagnosis", type="primary", key="run_diagnosis"):
            with st.spinner("🧠 Analyzing symptoms with AI..."):
                neo4j_results = st.session_state.mds.query_diseases_by_symptoms(selected_symptoms)
                bayesian_results = st.session_state.mds.diagnose_with_bayesian_network(
                    st.session_state.bayesian_model, selected_symptoms
                )
            
            st.markdown('<h2 class="section-header">💡 Diagnosis Results</h2>', unsafe_allow_html=True)
            
            results_tab1, results_tab2 = st.tabs(["🧠 Bayesian Network Analysis", "🗄️ Knowledge Graph Matches"])
            
            with results_tab1:
                if bayesian_results:
                    top_results = bayesian_results[:7]
                    
                    for disease, prob in top_results:
                        disease_symptoms = st.session_state.mds.disease_symptom_map.get(disease, [])
                        matching_symptoms = set(disease_symptoms).intersection(set(selected_symptoms))
                        
                        st.markdown(f'''
                            <div class="diagnosis-result-card">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <strong style="font-size: 1.2rem;">{disease}</strong>
                                    <span style="font-size: 1.2rem; font-weight: bold; color: #1abc9c;">{prob:.1f}%</span>
                                </div>
                                <div class="probability-bar-container">
                                    <div class="probability-bar-fill" style="width: {prob}%;"></div>
                                </div>
                                <div style="margin-top: 0.75rem; font-size: 0.9rem;">
                                    <span style="color: #a0a0b0;">Matching symptoms ({len(matching_symptoms)} of {len(disease_symptoms)}): 
                                    {", ".join(matching_symptoms)}</span>
                                </div>
                            </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="message-box warning-message">⚠️ No Bayesian analysis results available.</div>', unsafe_allow_html=True)

            with results_tab2:
                if neo4j_results:
                    for i, result in enumerate(neo4j_results[:5], 1):
                        disease = result['disease']
                        matched_symptoms = set(result['symptoms']).intersection(set(selected_symptoms))
                        
                        # Get all symptoms for the disease to calculate an accurate percentage
                        all_symptoms_for_disease = st.session_state.mds.disease_symptom_map.get(disease, [])
                        
                        if all_symptoms_for_disease:
                            match_percentage = (len(matched_symptoms) / len(all_symptoms_for_disease)) * 100
                        else:
                            match_percentage = 0
                        
                        st.markdown(f'''
                            <div class="info-card">
                                <strong style="font-size: 1.1rem;">{i}. {disease}</strong>
                                <small style="float: right; color: #a0a0b0;">{match_percentage:.1f}% symptom match</small>
                                <br>
                                <span style="font-size: 0.9rem; color: #a0a0b0;">
                                Matching symptoms: {", ".join(matched_symptoms)}
                                </span>
                            </div>
                        ''', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="message-box warning-message">⚠️ No diseases found with these symptoms in the knowledge graph.</div>', unsafe_allow_html=True)

def show_statistics():
    """Show system statistics"""
    st.markdown('<h2 class="section-header">📈 System Statistics</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Diseases by Symptom Count")
        disease_symptom_counts = sorted(
            [(d, len(s)) for d, s in st.session_state.mds.disease_symptom_map.items()],
            key=lambda x: x[1], reverse=True
        )
        df_diseases = pd.DataFrame(disease_symptom_counts, columns=['Disease', 'Symptom Count'])
        
        fig = px.bar(df_diseases.head(15), x='Symptom Count', y='Disease', orientation='h',
                     color='Symptom Count', color_continuous_scale='Teal')
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Most Common Symptoms")
        symptom_freq = pd.Series([s for sym_list in st.session_state.mds.disease_symptom_map.values() for s in sym_list]).value_counts()
        df_symptoms = pd.DataFrame({'Symptom': symptom_freq.index, 'Frequency': symptom_freq.values}).head(15)
        
        fig2 = px.pie(df_symptoms, values='Frequency', names='Symptom', hole=0.4,
                      color_discrete_sequence=px.colors.sequential.Teal_r)
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
        st.plotly_chart(fig2, use_container_width=True)

def show_about():
    """Show about information"""
    st.markdown('<h2 class="section-header">ℹ️ About the System</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card" style="border-left-color: #3498db;">
        <h3 style="color: #ffffff;">🏥 AI-Powered Medical Diagnosis System</h3>
        <p style="color: #a0a0b0;">
        This is an advanced diagnostic tool that leverages the power of Knowledge Graphs and Bayesian Networks to provide intelligent, data-driven insights into medical conditions based on patient-reported symptoms.
        </p>
        <hr style="border-color: #3a4b5c;">
        <h4 style="color: #ffffff;">Key Technologies</h4>
        <ul>
            <li><strong>Neo4j Knowledge Graph</strong>: Intricately stores and manages the complex web of relationships between diseases and their corresponding symptoms.</li>
            <li><strong>pgmpy Bayesian Network</strong>: Implements a probabilistic model to calculate the likelihood of various diseases based on observed evidence (symptoms).</li>
            <li><strong>spaCy NLP</strong>: Powers the initial knowledge extraction phase, parsing medical texts to build the foundational dataset.</li>
            <li><strong>Streamlit Frontend</strong>: Provides a seamless, interactive, and user-friendly interface for both patients and medical professionals.</li>
        </ul>
        <hr style="border-color: #3a4b5c;">
        <p style="color: #f1c40f; font-weight: bold;">
        ⚠️ Disclaimer: This system is a proof-of-concept for educational and research purposes. It is not a substitute for professional medical advice, diagnosis, or treatment.
        </p>
    </div>
    """, unsafe_allow_html=True)

def show_admin_panel():
    """Shows the admin panel for managing the knowledge base."""
    st.markdown('<h2 class="section-header">⚙️ Admin Panel</h2>', unsafe_allow_html=True)
    
    # --- Section 1: Add New Knowledge ---
    st.subheader("➕ Add New Medical Knowledge")
    with st.form(key="add_knowledge_form"):
        new_disease = st.text_input("Enter Disease Name:")
        new_symptoms_str = st.text_area("Enter Symptoms (comma-separated):")
        submit_button = st.form_submit_button(label="Add to Knowledge Base")

        if submit_button:
            if new_disease and new_symptoms_str:
                # Check if disease already exists
                if new_disease in st.session_state.mds.diseases:
                    st.error(f"Disease '{new_disease}' already exists. Please use the 'Manage Existing Knowledge' section to update it.")
                else:
                    symptoms_list = [s.strip() for s in new_symptoms_str.split(',') if s.strip()]
                    if symptoms_list:
                        try:
                            st.session_state.mds.add_knowledge_to_file(new_disease, symptoms_list)
                            st.success(f"Successfully added '{new_disease}'. Please reload the system to apply changes.")
                        except Exception as e:
                            st.error(f"Failed to add knowledge: {e}")
                    else:
                        st.warning("Please enter at least one valid symptom.")
            else:
                st.warning("Disease name and symptoms cannot be empty.")
    
    st.markdown("<hr style='border-color: #3a4b5c; margin: 2rem 0;'>", unsafe_allow_html=True)

    # --- Section 2: Manage Existing Knowledge ---
    st.subheader("📝 Manage Existing Knowledge")
    
    # Create an editable copy of the disease map
    editable_disease_map = st.session_state.mds.disease_symptom_map.copy()
    
    search_term = st.text_input("Search for a disease to manage:", "")
    
    for disease, symptoms in editable_disease_map.items():
        if search_term.lower() in disease.lower():
            with st.expander(f"{disease} ({len(symptoms)} symptoms)"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    symptoms_str = st.text_area(
                        "Symptoms:", 
                        ", ".join(symptoms), 
                        key=f"symptoms_{disease}"
                    )
                with col2:
                    if st.button("Update Symptoms", key=f"update_{disease}"):
                        updated_symptoms = [s.strip() for s in symptoms_str.split(',') if s.strip()]
                        st.session_state.mds.update_knowledge(disease, updated_symptoms)
                        st.success(f"'{disease}' updated. Reload to apply changes.")
                    
                    if st.button("❌ Delete Disease", key=f"delete_{disease}"):
                        st.session_state.mds.delete_knowledge(disease)
                        st.success(f"'{disease}' deleted. Reload to apply changes.")
                        # We need to rerun to remove the expander from the UI
                        time.sleep(1)
                        st.rerun()

    st.markdown("<hr style='border-color: #3a4b5c; margin: 2rem 0;'>", unsafe_allow_html=True)

    # --- Section 3: System Reload ---
    st.subheader("🔄 System Reload")
    st.warning("This is required after any change. Reloading rebuilds the entire knowledge graph and Bayesian network.")
    if st.button("Reload System Now", type="primary"):
        initialize_system(force_reload=True)
        st.success("System has been successfully reloaded with the latest knowledge.")
        time.sleep(1) # Give user a moment to see the message
        st.rerun()

if __name__ == "__main__":
    main() 