import streamlit as st
from streamlit_option_menu import option_menu
from utils.pdf_handler import extract_text_from_pdf
from utils.citation_extractor import CitationExtractor
import scholarly
from scholarly import scholarly
import openai
import os
from PyPDF2 import PdfReader
from utils.visualization import VisualizationManager
from utils.google_scholar_search import GoogleScholarSearch
from utils.research_paper_summarization import ResearchPaperSummarizer
from utils.chatbot import Chatbot
from db import Database
from auth import AuthService

db = Database()
db.initialize() 

auth_service = AuthService(db)

st.set_page_config(page_title="Citation Extractor", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user" not in st.session_state:
    st.session_state["user"] = {}

st.markdown(
    """
    <style>
        /* Centering auth section */
        /* Styling the authentication container */
        .st-emotion-cache-ocqkz7 {
            border-top: 5px solid #4da1a4; /* Left border with specified color */
            border-left: none;
            border-right: none;
            border-bottom: none;
            border-radius: 10px;
            padding: 80px;
            background-color: #f9f9f9;
            box-shadow: 2px 2px 10px rgba(77,161,164, 0.5); /* Shadow on other sides */
            gap: 0rem;
            height: 800px;
        }
        .st-emotion-cache-12fmjuu {
            display: none;
        }
        
        .st-emotion-cache-6awftf {
            display: none;
        }

        .st-emotion-cache-7n25ys {
            width: 800px;
        
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.get("logged_in", False):
    authcol1, authcol2 = st.columns([1, 1])  

    with authcol1:
        st.write("### Sentimet Analysis Tool")

        import os
        logo_path = os.path.join(os.path.dirname(__file__), "static/bann.png")
        st.image(logo_path, width=680 , caption="Your Secure Citation Tool", output_format="auto")


    with authcol2:
        tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

        with tab_login:
            st.subheader("🔑 Login")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login", key="login_button"):
                user = auth_service.authenticate_user(username, password)
                if user:
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = {
                        "id": user[0],  
                        "name": user[1],  
                        "username": user[2], 
                        "email": user[3], 
                    }
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

        with tab_register:
            st.subheader("📝 Register")
            full_name = st.text_input("Full Name *", key="register_full_name")
            username = st.text_input("Username *", key="register_username")
            email = st.text_input("Email *", key="register_email")
            password = st.text_input("Password *", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password *", type="password", key="register_confirm_password")

            if st.button("Register", key="register_button"):
                if password != confirm_password:
                    st.error("Passwords do not match!")
                elif not AuthService.is_valid_password(password):
                    st.error("Password must be at least 8 characters long and include letters, numbers, and special characters.")
                elif auth_service.check_username_exists(username):
                    st.error("Username already taken. Please choose another.")
                elif auth_service.check_email_exists(email):
                    st.error("Email already registered. Try logging in.")
                else:
                    try:
                        auth_service.register_user(full_name, username, email, password, "User")
                        st.success("Registration successful! You can now log in.")
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {e}")

    st.stop()  

st.sidebar.header(f"👋 Welcome, {st.session_state['user']['name']}")

st.markdown(
    """
    <style>
    .citation-box {
        border: 1px solid black;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
        background-color: #f9f9f9;
    }
    .citation-title {
        font-size: 16px;
        font-weight: bold;
    }
    .citation-reference {
        color: blue;
        text-decoration: underline;
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    selected = option_menu(
        "Main Menu",
        ["Citation Extractor", "Google Scholar Search", "Research Paper Summarization", "Chatbot", "About", "Contact", "Logout"],
        icons=["book", "search", "file-earmark-text", "robot", "info-circle", "envelope", "box-arrow-right"],
        menu_icon="cast",
        default_index=0,
    )

if selected == "Citation Extractor":
    st.title("📚 Citation Extractor")
    st.write(
        "Upload a PDF research paper to extract all citation sentences, their corresponding references, "
        "and analyze the sentiment."
    )

    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file:
        st.success("File uploaded successfully!")

        if "citation_metadata" not in st.session_state:
            st.session_state["citation_metadata"] = []

        if st.button("Extract Citations and References"):
            with st.spinner("Processing PDF..."):
                pdf_text = extract_text_from_pdf(uploaded_file)

            extractor = CitationExtractor()
            with st.spinner("Extracting citations and references..."):
                st.session_state["citation_metadata"] = extractor.extract_citations_with_metadata(pdf_text)

            tab1, tab2 = st.tabs(["📊 Visualizations", "📄 Citations"])

            with tab1:
                st.header("📊 Citation Analysis Visualizations")
            
                st.subheader("📂 Citation Sentiment Tree Chart")
                VisualizationManager.display_tree_chart(st.session_state["citation_metadata"])
            
                st.subheader("🌐 Citation Sentiment Network Graph")
                VisualizationManager.display_network_graph(st.session_state["citation_metadata"])
            
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("📊 Citation Sentiment Distribution")
                    VisualizationManager.display_pie_chart(st.session_state["citation_metadata"])
                with col2:
                    st.subheader("📉 Citation Sentiment Histogram")
                    VisualizationManager.display_histogram(st.session_state["citation_metadata"])
            
                st.subheader("📈 Citation Sentiment Trend Over Time")
                VisualizationManager.display_line_chart(st.session_state["citation_metadata"])
            
            with tab2:
                st.header("Extracted Citation Sentences")
                st.write(f"**Total Citations Extracted:** {len(st.session_state['citation_metadata'])}")
                
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    filter_sentiment = st.selectbox(
                        "Filter by Sentiment:",
                        ["All", "Positive", "Negative", "Neutral"],
                        index=0,
                    )
                
                with col2:
                    search_query = st.text_input("Search Citations:")
                
                filtered_citations = [
                    data
                    for data in st.session_state["citation_metadata"]
                    if (filter_sentiment == "All" or data["sentiment"] == filter_sentiment)
                    and (search_query.lower() in data["citation"].lower())
                ]
                
                for idx, data in enumerate(filtered_citations, start=1):
                    with st.expander(f"Citation {idx}: {data['citation']}"):
                        st.markdown(
                            f"""
                            <p><b>Reference:</b> 
                                <a href="{data['link']}" class="citation-reference" target="_blank">{data['reference']}</a>
                            </p>
                            <p><b>Sentiment:</b> 
                                <span style="color: {'green' if data['sentiment'] == 'Positive' else 'red' if data['sentiment'] == 'Negative' else 'gray'}; font-weight: bold;">{data['sentiment']}</span>
                            </p>
                            """,
                            unsafe_allow_html=True,
                        )

if selected == "Google Scholar Search":
    st.title("🔍 Google Scholar Search")
    query = st.text_input("Enter search keyword or author name:")
    
    if query:
        with st.spinner("Searching Google Scholar..."):
            results = GoogleScholarSearch.search(query)
        
        if results:
            st.success(f"Found {len(results)} articles.")
            for i, article in enumerate(results):
                st.write(f"**{i + 1}. {article['title']}**")
                st.write(f"   - Authors: {article.get('author', 'N/A')}")
                st.write(f"   - Abstract: {article.get('abstract', 'N/A')}")
                st.write(f"   - URL: {article.get('url', 'N/A')}")
                st.write("")
            
            article_index = st.number_input(
                "Select an article number for sentiment analysis", min_value=1, max_value=len(results), step=1)
            
            selected_article = results[article_index - 1]
            st.write(f"Selected Article: **{selected_article['title']}**")
            
            abstract = selected_article.get('abstract', '')
            if abstract:
                st.session_state.user_input = abstract
            else:
                st.warning("No abstract available for sentiment analysis.")


elif selected == "Research Paper Summarization":
    summarizer = ResearchPaperSummarizer()

    st.title("📄 Research Paper Summarization")

    uploaded_file = st.file_uploader("Upload a PDF research paper for summarization", type=["pdf"])

    if uploaded_file:
        st.success("File uploaded successfully!")

        with st.spinner("Extracting text from PDF..."):
            pdf_text = summarizer.extract_text_from_pdf(uploaded_file)

        st.text_area("Extracted Text", pdf_text[:2000], height=300) 

        if st.button("Summarize Paper"):
            with st.spinner("Generating summary..."):
                summary = summarizer.summarize_paper(pdf_text)
                if summary:
                    st.subheader("Paper Summary")
                    st.write(summary)

elif selected == "Chatbot":
    chatbot = Chatbot()
    chatbot.run()

elif selected == "Logout":
    st.session_state["logged_in"] = False
    st.session_state["user"] = {}
    st.rerun()