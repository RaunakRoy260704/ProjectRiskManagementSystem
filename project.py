import json
import streamlit as st
from fpdf import FPDF
import google.generativeai as genai

# --- Gemini API Configuration ---
GEMINI_API_KEY = "AIzaSyA43TpsIHDxyw97yYlxV-YiczkvytGYcr4"  # Replace with your actual Gemini API Key
genai.configure(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.0-flash"

# --- Streamlit UI Config ---
st.set_page_config(page_title="🚀 AI-Powered Risk Management", layout="wide")

# --- Initialize Chat History ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Sidebar Settings ---
with st.sidebar:
    st.title("🔧 Settings")
    theme = st.radio("Select Theme:", ["Light", "Dark"], index=0)

    if st.button("🧹 Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

# --- Apply Full Dark Mode ---
if theme == "Dark":
    st.markdown(
        """
        <style>
        body, .appview-container {background-color: #121212 !important; color: white !important;}
        .stTextInput > label, .stTextArea > label, .stRadio > label {color: white !important;}
        .stButton > button {background-color: #333 !important; color: white !important; border-radius: 5px;}
        [data-testid="stSidebar"], .stSidebar {background-color: #1e1e1e !important;}
        [data-testid="stSidebarContent"] * {color: white !important;}
        </style>
        """,
        unsafe_allow_html=True
    )

# --- Gemini API Call ---
def query_gemini(prompt):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"

# --- AI Agents ---
def risk_analysis_agent(project_desc):
    return query_gemini(f"Very briefly ,Identify potential risks for this project:\n\n{project_desc}")

def mitigation_agent(risks):
    return query_gemini(f"Very briefly ,Suggest mitigation strategies for these risks:\n\n{risks}")

def finance_agent(project_desc, risks):
    return query_gemini(f"Very briefly ,Analyze financial risks related to the project and how to solve:\n\nProject: {project_desc}\nRisks: {risks}")

def planning_agent(project_desc, risks):
    return query_gemini(f"Very briefly ,Identify scheduling risks based on the project description and how to solve:\n\nProject: {project_desc}\nRisks: {risks}")

def reporting_agent(risks, mitigations, finance, planning):
    return query_gemini(f"Combine these insights into a structured risk report :\n\nRisks: {risks}\n\nMitigation Strategies: {mitigations}\n\nFinancial Risks: {finance}\n\nScheduling Risks: {planning}")


# --- Determine Which Agent to Use Based on User Query ---
def select_agent(user_query):
    query = user_query.lower()
    if any(word in query for word in ["risk", "threat", "danger"]):
        return "Risk Analysis Agent", risk_analysis_agent
    elif any(word in query for word in ["mitigation", "solution", "resolve"]):
        return "Mitigation Expert", mitigation_agent
    elif any(word in query for word in ["budget", "cost", "finance", "financial"]):
        return "Finance Advisor", lambda q: finance_agent(q, risk_analysis_agent(q))
    elif any(word in query for word in ["schedule", "timeline", "delay", "deadline"]):
        return "Planning Agent", lambda q: planning_agent(q, risk_analysis_agent(q))
    else:
        return "General Assistant", query_gemini

# --- User Input Section ---
st.title("🚀 AI-Powered Project Risk Management Chatbot")
project_description = st.text_area("✍️ Enter project details:", height=150, placeholder="Describe your project challenges...")

if st.button("🔍 Comprehensive Risk Report Analysis") and project_description:
    with st.spinner("Report Generator agent is working on it..."):
        risks = risk_analysis_agent(project_description)
        mitigations = mitigation_agent(risks)
        finance_risks = finance_agent(project_description, risks)
        planning_risks = planning_agent(project_description, risks)
        final_report = reporting_agent(risks, mitigations, finance_risks, planning_risks)

      
        st.subheader("📄 AI-Generated Risk Report")
        st.write(final_report)

        st.session_state.chat_history.extend([
            {"role": "assistant", "content": f"[Report Generator]: {final_report}"}
        ])

# --- Chatbot Section ---
st.subheader("💬 Chat with AI Agents")
user_query = st.text_input("Ask about risks, mitigation, finance, or project planning...")

if user_query:
    selected_agent_name, agent_function = select_agent(user_query)

    with st.spinner(f"{selected_agent_name} is responding..."):
        try:
            if selected_agent_name == "General Assistant":
                response = agent_function(user_query)
            else:
                response = agent_function(user_query)
        except Exception as e:
            response = f"⚠️ Error: {str(e)}"

        st.subheader(f"🤖 Response by: {selected_agent_name}")
        st.write(response)

        st.session_state.chat_history.append({"role": "user", "content": user_query})
        st.session_state.chat_history.append({"role": "assistant", "content": f"[{selected_agent_name}]: {response}"})

# --- Display Chat History ---
st.subheader("📜 Chat History")
for message in st.session_state.chat_history:
    if message['role'] == "user":
        st.write(f"👤 **You:** {message['content']}")
    else:
        st.write(f"🤖 {message['content']}")

# --- Download Chat History as PDF ---
if st.button("📥 Download Chat History as PDF"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "AI-Powered Project Risk Management Chat History", ln=True, align='C')
    pdf.ln(10)

    for message in st.session_state.chat_history:
        pdf.multi_cell(0, 10, f"{message['role'].capitalize()}: {message['content']}")
        pdf.ln(5)

    pdf_file = "chat_history.pdf"
    pdf.output(pdf_file, "F")

    with open(pdf_file, "rb") as file:
        st.download_button("Download Chat as PDF", data=file, file_name="chat_history.pdf", mime="application/pdf")
