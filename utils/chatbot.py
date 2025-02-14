import os
import openai
import streamlit as st
from PyPDF2 import PdfReader
import uuid

class Chatbot:
    def __init__(self):
        self.initialize_session()
        self.load_openai_api_key()

    def initialize_session(self):
        """Initialize session state for chatbot."""
        if 'session_id' not in st.session_state:
            st.session_state['session_id'] = str(uuid.uuid4())
        if 'chat_history' not in st.session_state:
            st.session_state['chat_history'] = []
        if 'pdf_text' not in st.session_state:
            st.session_state['pdf_text'] = ""

    def load_openai_api_key(self):
        """Load OpenAI API Key from Streamlit Secrets or Environment Variables."""
        try:
            self.OPENAI_API_KEY = st.secrets["openai"]["api_key"]
        except KeyError:
            self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

        if not self.OPENAI_API_KEY:
            st.error("OpenAI API key not found! Please set it in Streamlit Secrets or as an environment variable.")
            st.stop()
        else:
            openai.api_key = self.OPENAI_API_KEY  


    def extract_text_from_pdf(self, uploaded_file):
        """Extract text from a PDF file."""
        reader = PdfReader(uploaded_file)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text

    def call_openai(self, prompt):
        """Call OpenAI API to generate chatbot responses."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI that answers research-related queries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            return f"Error calling OpenAI API: {str(e)}"

    def run(self):
        """Run the chatbot UI."""
        st.header("💬 AI Research Q&A Chatbot 🤖")

        uploaded_file = st.file_uploader("Upload a research paper (PDF)", type=["pdf"])
        if uploaded_file:
            with st.spinner("Extracting text from PDF..."):
                pdf_text = self.extract_text_from_pdf(uploaded_file)
                st.session_state['pdf_text'] = pdf_text
            st.text_area("Extracted Text (Preview)", pdf_text[:2000], height=300)

        for chat in st.session_state['chat_history']:
            st.chat_message(chat['role']).write(chat['message'])

        user_input = st.chat_input("Ask a research-related question!")
        if user_input:
            prompt = f"Based on the following research paper, answer this question:\n\n{st.session_state['pdf_text'][:5000]}\n\nQuestion: {user_input}"
            self.append_chat_history('user', user_input)
            response = self.call_openai(prompt)
            self.append_chat_history('assistant', response)

        self.export_chat_history()

    def append_chat_history(self, role, message):
        """Append chat history and display messages."""
        st.session_state['chat_history'].append({'role': role, 'message': message})
        st.chat_message(role).write(message)

    def export_chat_history(self):
        """Export chat history as a downloadable text file."""
        if st.session_state.get('chat_history'):
            chat_history_text = self.format_chat_history()
            st.download_button(
                label="Download Chat History",
                data=chat_history_text,
                file_name="chat_history.txt",
                mime="text/plain"
            )

    def format_chat_history(self):
        """Format chat history for export."""
        formatted_history = []
        for chat in st.session_state['chat_history']:
            role = "User" if chat['role'] == 'user' else "Assistant"
            formatted_history.append(f"{role}: {chat['message']}\n")
        return "".join(formatted_history)
