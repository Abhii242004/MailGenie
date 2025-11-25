📧 AI Application Email Automator

This project delivers a complete workflow to generate, review, and send highly personalized job-application emails, leveraging LLMs for deep alignment between a Job Description (JD) and your resume.

Built for ultra-low latency using Groq’s Llama-3.3-70B-Versatile model, it includes both a CLI tool and a full Streamlit web application.

🚀 Features
🔥 AI-Powered Personalization

Uses Groq’s LPU inference for fast, high-quality email drafts.

Deeply analyzes job requirements and aligns them with your resume.

🧠 Structured Output with LangChain

Uses JsonOutputParser for dependable extraction of job details.

Ensures consistent formatting and stable generation.

💌 Automated Email Sending

Built-in SMTP integration for sending emails directly from the app.

Enforces mandatory PDF resume attachment before sending.

🌐 Interactive Streamlit UI

Input JD & resume → Generate → Edit → Configure → Send.

Real-time preview and error validation.

🧰 Two Usage Modes

CLI (email_generator.py) → Fast draft generation

Streamlit App (main.py) → Complete UI workflow

⚙️ Installation & Setup
1. Clone the Repository
git clone <your-repo-url>
cd <your-project-folder>

2. Create a Virtual Environment
python -m venv venv
source venv/bin/activate       # macOS/Linux
# venv\Scripts\activate        # Windows

3. Install Dependencies
pip install -r requirements.txt

4. Set Required Environment Variables
Groq API Key
export GROQ_API_KEY="your_api_key"        # macOS/Linux
# setx GROQ_API_KEY "your_api_key"        # Windows

Optional: Gmail App Password (for SMTP sending)
export EMAIL_PASSWORD="your_app_password"

🖥️ Usage
🔧 1. Using the CLI
python email_generator.py \
  --resume resume.txt \
  --jd job_description.txt

🌐 2. Running the Streamlit App
streamlit run main.py


Inside the UI, you can:

Paste JD & resume text

Generate AI-personalized email

Edit & refine the draft

Add sender/recipient details

Attach resume PDF

Send the final email

🏗️ Project Structure
.
├── chains.py              # LangChain parsing logic
├── email_generator.py     # CLI tool
├── main.py                # Streamlit UI
├── utils/                 # Helper functions
├── assets/                # (Optional) Icons, screenshots
└── requirements.txt

🔍 Architecture Overview

JD + Resume → LangChain Parser → Groq LLM → Structured Draft Email → UI/CLI → SMTP → Sent Email

📜 License

This project is licensed under the MIT License.

```bash
# Create and activate a virtual environment (Recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies from requirements.txt
pip install -r requirements.txt
