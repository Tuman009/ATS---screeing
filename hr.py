from dotenv import load_dotenv
import base64
import streamlit as st
import os
import io
from PIL import Image 
import pdf2image
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API with your API key from environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to generate response from Gemini AI
def get_gemini_response(input_text, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')  # Updated model
    response = model.generate_content([input_text, pdf_content[0], prompt])
    return response.text

# Function to process the uploaded PDF, convert it to images and return base64-encoded content
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        # Convert the PDF to image using pdf2image
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        
        # Get the first page
        first_page = images[0]

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        # Encode the image in base64 for passing to the model
        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Streamlit app setup
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")

# Input fields for job description and uploaded resume (PDF)
input_text = st.text_area("Job Description: ", key="input")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

# Button to trigger different analyses
submit1 = st.button("Tell Me About the Resume")
submit3 = st.button("Percentage Match")

# Prompts for Gemini AI
input_prompt1 = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description.
Please share your professional evaluation on whether the candidate's profile aligns with the role.
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality.
Your task is to evaluate the resume against the provided job description. Provide the percentage match if the resume matches
the job description. First, the output should be the percentage, followed by missing keywords, and lastly, final thoughts.
"""

# Handling form submission and responses
if submit1 or submit3:
    # Check if the job description is provided
    if input_text.strip() == "":
        st.write("Please enter a job description.")
    elif uploaded_file is not None:
        with st.spinner('Processing your request...'):
            # Convert PDF to content
            try:
                pdf_content = input_pdf_setup(uploaded_file)
            except FileNotFoundError:
                st.write("No file uploaded.")
                st.stop()

            # Choose the appropriate prompt and request the response from Gemini AI
            if submit1:
                response = get_gemini_response(input_text, pdf_content, input_prompt1)
                st.subheader("The Response is")
                st.write(response)
            elif submit3:
                response = get_gemini_response(input_text, pdf_content, input_prompt3)
                st.subheader("The Response is")
                st.write(response)
    else:
        st.write("Please upload the resume (PDF).")
