import streamlit as st
import json
from langchain_community.llms import Ollama

# -----------------------
# Config
# -----------------------
EXIT_KEYWORDS = {"exit", "quit", "bye", "stop", "end"}
STORAGE_FILE = "candidates.json"

# Use a local instruct model (Mistral or LLaMA 3 recommended)
MODEL_NAME = "mistral"   # or "llama3"

# Init Ollama LLM
llm = Ollama(
    model=MODEL_NAME,
    temperature=0.2  # keep responses focused
)

# -----------------------
# Helpers
# -----------------------
def save_candidate(data):
    """Save candidate info to local JSON file."""
    try:
        with open(STORAGE_FILE, "r") as f:
            db = json.load(f)
    except FileNotFoundError:
        db = []
    db.append(data)
    with open(STORAGE_FILE, "w") as f:
        json.dump(db, f, indent=2)

def generate_questions(tech_stack):
    """Generate structured technical questions in ENGLISH."""
    prompt = f"""
    Candidate tech stack: {tech_stack}.
    For each technology, generate exactly 3 short interview questions in ENGLISH.
    Respond strictly in JSON format like this:
    {{
      "Python": ["Question1", "Question2", "Question3"],
      "Django": ["Question1", "Question2", "Question3"]
    }}
    No explanations, no extra text, only valid JSON.
    """

    response = llm.invoke(prompt)

    # Try to parse clean JSON
    try:
        return json.loads(response)
    except:
        cleaned = response.strip().split("```")[-1]
        try:
            return json.loads(cleaned)
        except:
            return {"Error": [response]}

def chat_response(user_input):
    """Wraps user input in instruction prompt so model gives answers (not repeats)."""
    prompt = f"""
    You are TalentScout Hiring Assistant.
    Always answer clearly in English.
    Do NOT repeat or rephrase the user question, only provide the best possible answer.

    Question: {user_input}
    Answer:
    """
    response_chunks = []
    for chunk in llm.stream(prompt):
        response_chunks.append(chunk)
    return "".join(response_chunks)

def estimate_skill_levels(qa_history, tech_stack):
    """Estimate skill levels (Beginner / Intermediate / Expert) based on candidate answers."""
    answers = "\n".join(
        f"Q: {q}\nA: {a}" 
        for role, msg in qa_history 
        if role == "Assistant" or role == "You" 
        for q, a in [(msg, "")] if role == "You"
    )

    prompt = f"""
    Candidate tech stack: {tech_stack}
    Candidate interview answers:
    {answers}

    Based on the answers, estimate the candidate's skill level for each technology 
    in this stack. Use only these labels: Beginner, Intermediate, Expert.
    Respond strictly in JSON format like this:
    {{
      "Python": "Intermediate",
      "Django": "Beginner"
    }}
    """
    response = llm.invoke(prompt)
    try:
        return json.loads(response)
    except:
        return {"Error": response}

# -----------------------
# Streamlit UI
# -----------------------
st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🤖")

st.title("🤖 TalentScout Hiring Assistant")
st.write("""
Welcome to the **TalentScout Hiring Assistant**.  

I will:
- Collect your professional details (experience, skills, and career interests)  
- Generate tailored **technical interview questions** based on your tech stack  
- Conduct a structured Q&A session where you can respond to questions or ask clarifications  
- Provide a skill-level estimation (Beginner / Intermediate / Expert) for each technology  
- Maintain a transcript of the conversation for review  

At any time, type **exit**, **quit**, or **end** to finish the interview.  
""")

# Session state
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []
if "candidate_info" not in st.session_state:
    st.session_state.candidate_info = {}
if "chat_input" not in st.session_state:
    st.session_state.chat_input = ""
if "skill_levels" not in st.session_state:
    st.session_state.skill_levels = {}

# -----------------------
# Candidate Info Form
# -----------------------
with st.form("candidate_form"):
    st.subheader("📋 Candidate Information")
    name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    phone = st.text_input("Phone Number")
    exp = st.number_input("Years of Experience", min_value=0, step=1)
    position = st.text_input("Desired Position(s)")
    location = st.text_input("Current Location")
    tech_stack = st.text_area("Tech Stack (e.g., Python, Django, MySQL)")

    submitted = st.form_submit_button("Submit")
    if submitted:
        st.session_state.candidate_info = {
            "name": name,
            "email": email,
            "phone": phone,
            "experience": exp,
            "position": position,
            "location": location,
            "tech_stack": tech_stack,
        }
        save_candidate(st.session_state.candidate_info)
        st.success("✅ Information saved! Scroll down to see your technical questions.")

# -----------------------
# Generate questions if candidate info available
# -----------------------
if st.session_state.candidate_info.get("tech_stack"):
    st.subheader("🧑‍💻 Technical Questions")

    with st.spinner("Generating questions..."):
        questions_dict = generate_questions(st.session_state.candidate_info["tech_stack"])

    if "Error" in questions_dict:
        st.error("⚠️ Could not parse questions properly. Raw output:")
        st.write(questions_dict["Error"])
    else:
        for tech, qs in questions_dict.items():
            st.markdown(f"**{tech}**")
            for i, q in enumerate(qs, 1):
                st.write(f"{i}. {q}")

# -----------------------
# Chatbox for conversation (fixed with on_change)
# -----------------------
st.subheader("💬 Chat with Assistant")

def process_input():
    """Handles user input when submitted."""
    user_input = st.session_state.chat_input.strip()
    if not user_input:
        return

    cleaned = user_input.lower()

    # ✅ Exit keywords
    if cleaned in EXIT_KEYWORDS:
        st.session_state.qa_history.append(("You", user_input))
        st.session_state.qa_history.append(("Assistant", "👋 Thank you for your time! We’ll contact you with next steps."))
        st.session_state.chat_input = ""  # clears input
        return

    # Otherwise → normal chat flow
    with st.spinner("Assistant is typing..."):
        final_response = chat_response(user_input)

    st.session_state.qa_history.append(("You", user_input))
    st.session_state.qa_history.append(("Assistant", final_response))

    # Clear input box after processing
    st.session_state.chat_input = ""

# Input box with callback
st.text_input(
    "Your message:",
    key="chat_input",
    on_change=process_input,
)

# Clear conversation button
if st.button("🗑️ Clear Conversation"):
    st.session_state.qa_history = []
    st.session_state.skill_levels = {}
    st.success("Conversation cleared!")

# Display transcript
for role, msg in st.session_state.qa_history:
    if role == "You":
        st.markdown(f"**🧑 {role}:** {msg}")
    else:
        st.markdown(f"**🤖 {role}:** {msg}")

# -----------------------
# Skill Level Estimation
# -----------------------
if st.button("📊 Estimate Skill Levels"):
    if st.session_state.qa_history and st.session_state.candidate_info.get("tech_stack"):
        with st.spinner("Analyzing candidate answers..."):
            st.session_state.skill_levels = estimate_skill_levels(
                st.session_state.qa_history,
                st.session_state.candidate_info["tech_stack"]
            )
        st.subheader("📌 Skill Level Estimation")
        st.json(st.session_state.skill_levels)
    else:
        st.warning("⚠️ Please complete candidate details and provide some answers first.")
