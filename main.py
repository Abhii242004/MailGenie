import os
import streamlit as st
import smtplib
import time
import socket
from email.message import EmailMessage
import io # NEW: Import io for file handling

# Assuming Chain and clean_text are defined in their respective files or scopes
# Ensure you have chains.py and utils.py in the same directory
from chains import Chain
from utils import clean_text

# Define the user's resume content as the default for the input area
DEFAULT_RESUME_TEXT = """
YOUR_RESUME_HERE
"""

# --- Configuration for SMTP Server ---
SMTP_SERVER = "smtp.gmail.com" 
SMTP_PORT = 465 # SSL port for secure connection

def parse_llm_output(email_content):
    """Parses the LLM output string to separate subject and body."""
    lines = email_content.split('\n')
    subject = "Application Email Draft" # Default subject
    body = email_content # Default body is the whole thing

    # Look for a line starting with 'Subject:'
    for i, line in enumerate(lines):
        if line.lower().startswith("subject:"):
            # Extract subject, strip 'Subject:' prefix, and clean whitespace
            subject = line[len("subject:"):].strip()
            # The body is everything after the subject line, joined back together
            body = "\n".join(lines[i+1:]).strip()
            break
    
    # If no specific subject line was found, ensure the first few lines aren't just empty space
    if not subject or subject == "Application Email Draft":
        first_line = lines[0].strip() if lines else subject
        if first_line:
            # Use the first non-empty line as a default subject if no "Subject:" tag was used
            subject = first_line[:50] + "..." if len(first_line) > 50 else first_line
            body = "\n".join(lines[1:]).strip()

    return subject, body

# UPDATED: Added pdf_attachment_data and pdf_filename arguments
def send_generated_email(sender_email, sender_password, recipient_email, recipient_name, subject, body, pdf_attachment_data, pdf_filename):
    """
    Connects to the SMTP server and sends the LLM-generated email with a PDF attachment.
    """
    
    msg = EmailMessage()
    # Use the LLM-generated subject
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email
    
    # Set the body content
    msg.set_content(body)

    # NEW: Attach the PDF file if data is provided
    if pdf_attachment_data and pdf_filename:
        # Since we expect a PDF, use application/pdf subtype.
        # Streamlit file uploader returns bytes, which is what add_attachment needs.
        msg.add_attachment(
            pdf_attachment_data,
            maintype='application',
            subtype='pdf',
            filename=pdf_filename
        )


    try:
        # Check network connectivity first
        socket.create_connection((SMTP_SERVER, SMTP_PORT), timeout=10)
        
        # Connect to the secure SMTP server and send the email
        with st.spinner(f'Connecting to {SMTP_SERVER} and sending email...'):
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
                st.success(f"✅ Success! Email titled '{subject}' sent to {recipient_email}. Resume '{pdf_filename}' attached.")
                return True
                
    except smtplib.AuthenticationError:
        st.error("🛑 Authentication Failed! Please check your Sender Email and App Password.")
        st.caption("Hint: If using Gmail, ensure you are using a 16-character App Password.")
        return False
    except socket.error as e:
        st.error(f"🌐 Network Error! Could not connect to the server ({SMTP_SERVER}). Check your internet connection or VPN.")
        st.caption(f"Details: {e}")
        return False
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {e}")
        return False


# --- Streamlit Application UI ---

def create_streamlit_app(llm, clean_text):
    
    # Initialize session state for storing the draft
    if 'generated_email_content' not in st.session_state:
        st.session_state.generated_email_content = None
    
    st.title("📧 Personalized Application Email Automator")
    st.markdown("---")

    # =========================================================================
    # STEP 1: DRAFT GENERATION
    # =========================================================================
    st.header("Step 1: Generate Draft")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Input 1: Job Description
        jd_input = st.text_area(
            "Target Job Description Text:", 
            height=280, 
            value="Job Title: Mid-Level Python/AI Developer at GenCorp. Requirements: Strong experience in Python, LLM integration, and Streamlit dashboard creation. Focus on model deployment and testing."
        )
    
    with col2:
        # Input 2: Resume Text (Defaulted to Abhinav Prasad's resume)
        # NOTE: This text area is for the LLM to read and personalize the email.
        resume_input = st.text_area(
            "Your Resume Text (for AI analysis):", 
            height=280, 
            value=DEFAULT_RESUME_TEXT,
            help="The AI uses this text content to tailor the email draft to the job description. This is NOT the file attachment."
        )
    
    if st.button("🚀 Generate Personalized Email Draft", type="primary", use_container_width=True):
        if not jd_input or not resume_input:
            st.error("Please provide both the Job Description and Resume text.")
            return

        st.info("Analyzing provided job description and resume...")
        
        try:
            with st.spinner('1/3: Cleaning and preparing job description text...'):
                job_description_text = clean_text(jd_input)
            
            with st.spinner('2/3: Analyzing and structuring job requirements...'):
                jobs = llm.extract_jobs(job_description_text)
            
            with st.spinner('3/3: Drafting the personalized application email...'):
                if jobs:
                    # We usually only process the first job found
                    job = jobs[0]
                    email_content_raw = llm.write_mail(job, resume_input) 
                    
                    subject, body = parse_llm_output(email_content_raw)
                    
                    st.session_state.generated_email_content = {
                        "subject": subject, 
                        "body": body,
                        "job_title": job.get('title', 'N/A'),
                        "company": job.get('company', 'N/A')
                    }
                    st.success(f"✅ Draft Generated! Review below and proceed to Step 2.")
                else:
                    st.error("Could not extract job details from the provided description.")
        except Exception as e:
            st.error(f"❌ An Error Occurred during generation: {e}")


    # =========================================================================
    # STEP 2: REVIEW AND SEND
    # =========================================================================
    st.markdown("---")
    st.header("Step 2: Review and Send")

    if st.session_state.generated_email_content:
        draft = st.session_state.generated_email_content
        
        st.subheader(f"Draft for: {draft['job_title']} at {draft['company']}")

        # Editable fields for subject and body
        st.session_state.final_subject = st.text_input("Final Email Subject:", value=draft['subject'])
        st.session_state.final_body = st.text_area("Final Email Body (Editable):", value=draft['body'], height=350)

        # NEW: Resume PDF Upload
        pdf_file = st.file_uploader(
            "Attach Resume PDF File:", 
            type=['pdf'],
            help="Upload the PDF version of your resume to be attached to the email. This is mandatory for sending."
        )

        # Sender/Recipient Details
        st.markdown("**Recipient & Sender Details**")
        
        col_send_1, col_send_2 = st.columns(2)
        
        with col_send_1:
            sender_email = st.text_input("Sender Email (Your Address)", key="sender_email_input", type="default")
            sender_password = st.text_input("App Password (16-char code)", key="sender_password_input", type="password", help="REQUIRED for Gmail. Google 'Generate App Password' for instructions.")
        
        with col_send_2:
            recipient_name = st.text_input("Recipient Name", value="Hiring Manager")
            recipient_email = st.text_input("Recipient Email", value="recruiter@company.com")

        st.markdown("---")
        
        # Send Button Logic
        if st.button("📧 SEND FINAL APPLICATION EMAIL", type="secondary", use_container_width=True):
            if not st.session_state.final_subject or not st.session_state.final_body:
                st.error("Email subject or body cannot be empty.")
            elif not sender_email or not sender_password:
                st.error("Please enter your Sender Email and App Password.")
            elif not recipient_email:
                st.error("Please enter the Recipient Email address.")
            elif not pdf_file: # NEW: Check for file attachment
                st.error("Please upload your resume as a PDF file to attach.")
            else:
                # Read the file data and filename from the uploaded object
                pdf_attachment_data = pdf_file.read()
                pdf_filename = pdf_file.name
                
                send_generated_email(
                    sender_email, 
                    sender_password, 
                    recipient_email, 
                    recipient_name,
                    st.session_state.final_subject,
                    st.session_state.final_body,
                    pdf_attachment_data, # NEW: Pass data
                    pdf_filename         # NEW: Pass filename
                )

    else:
        st.info("👈 Enter the Job Description and Resume in Step 1 and click 'Generate' to create the draft.")


if __name__ == "__main__":
    # Instantiate core components
    # The Chain class is assumed to load the GROQ_API_KEY from the environment
    chain = Chain()
    
    # Streamlit configuration
    st.set_page_config(layout="wide", page_title="AI Email Automator", page_icon="📧")
    
    # Run the application, passing only the chain and the utility function

    create_streamlit_app(chain, clean_text)
