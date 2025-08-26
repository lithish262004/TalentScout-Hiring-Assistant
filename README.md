# TalentScout Hiring Assistant 🤖

An AI-powered interview assistant built with Streamlit and LLM (Mistral)  to streamline the hiring process.
This assistant collects candidate details, generates tailored technical questions, enables live Q&A, and even estimates skill levels (Beginner / Intermediate / Expert).

# Features

✅Candidate Info Collection
Name, contact details, experience, skills, and job interests

✅ Dynamic Technical Questions
Generates 3 questions per technology in the candidate’s tech stack

✅ Interactive Chat Mode
Conversational Q&A with an AI assistant
Exit instantly using exit, quit, bye, stop, end

✅ Skill-Level Estimation
Labels each skill as Beginner / Intermediate / Expert based on answers

✅ Clear Conversation
HR/interviewer can reset the chat transcript anytime

✅ Persistent Storage
Candidate details are stored in candidates.json

✅ User-Friendly UI
Built with Streamlit → clean, simple, and professional

# Project Structure
TalentScout-Hiring-Assistant/
│
├── app.py                # Main Streamlit app
├── requirements.txt      # Python dependencies
├── candidates.json       # Stores candidate data (auto-generated)
└── README.md             # Project documentation

# Installation
1. Clone the Repository
git clone https://github.com/lithish262004/TalentScout-Hiring-Assistant.git
cd TalentScout-Hiring-Assistant

2. Create a Virtual Environment (recommended)
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

3. Install Dependencies
pip install -r requirements.txt

4. Run the App
streamlit run app.py

