import os
import openai
import streamlit as st
from PyPDF2 import PdfReader

class ResearchPaperSummarizer:
    def __init__(self):
        try:
            self.OPENAI_API_KEY = st.secrets["openai"]["api_key"]
        except KeyError:
            self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

        if not self.OPENAI_API_KEY:
            st.error("OpenAI API key not found! Please set it in Streamlit Secrets or as an environment variable.")
        else:
            openai.api_key = self.OPENAI_API_KEY  

    def extract_text_from_pdf(self, uploaded_file):
        """Extract text from a PDF file."""
        reader = PdfReader(uploaded_file)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text

    def summarize_paper(self, pdf_text):
        """Generate a summary of the research paper using OpenAI."""
        summary_prompt = "Summarize the following research paper concisely:\n\n" + pdf_text
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI that summarizes research papers in a detailed yet concise manner."},
                    {"role": "user", "content": summary_prompt}
                ],
                max_tokens=2000,
                temperature=0.6
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            st.error(f"Error calling OpenAI API: {str(e)}")
            return None
