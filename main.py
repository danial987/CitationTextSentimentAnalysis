import streamlit as st
from streamlit_option_menu import option_menu
from utils.pdf_handler import extract_text_from_pdf
from utils.citation_extractor import CitationExtractor

# Set up Streamlit page
st.set_page_config(page_title="Citation Extractor", layout="wide")

# Inject custom CSS for consistent styling
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

# Sidebar menu
with st.sidebar:
    selected = option_menu(
        "Main Menu",
        ["Home", "About", "Contact"],
        icons=["house", "info-circle", "envelope"],
        menu_icon="cast",
        default_index=0,
    )

# Home Page
if selected == "Home":
    st.title("Citation Extractor")
    st.write(
        "Upload a PDF research paper to extract all citation sentences, their corresponding references, "
        "and analyze the sentiment."
    )

    # File uploader
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file:
        st.success("File uploaded successfully!")

    # Initialize session state for storing extracted citations
    if "citation_metadata" not in st.session_state:
        st.session_state["citation_metadata"] = []

    # Process button
    if st.button("Extract Citations and References"):
        if not uploaded_file:
            st.error("Please upload a PDF file first.")
        else:
            with st.spinner("Processing PDF..."):
                pdf_text = extract_text_from_pdf(uploaded_file)

            extractor = CitationExtractor()
            with st.spinner("Extracting citations and references..."):
                st.session_state["citation_metadata"] = extractor.extract_citations_with_metadata(pdf_text)

    # Display extracted citations
    if st.session_state["citation_metadata"]:
        st.header("Extracted Citation Sentences")
        st.write(f"**Total Citations Extracted:** {len(st.session_state['citation_metadata'])}")

        # Filter and Search Bar
        col1, col2 = st.columns([1, 3])

        # Dropdown filter for sentiment
        with col1:
            filter_sentiment = st.selectbox(
                "Filter by Sentiment:",
                ["All", "Positive", "Negative", "Neutral"],
                index=0,
            )

        # Search bar for citations
        with col2:
            search_query = st.text_input("Search Citations:")

        # Apply filter and search
        filtered_citations = [
            data
            for data in st.session_state["citation_metadata"]
            if (filter_sentiment == "All" or data["sentiment"] == filter_sentiment)
            and (search_query.lower() in data["citation"].lower())
        ]

        # Display all filtered and searched citations
        for idx, data in enumerate(filtered_citations, start=1):
            with st.expander(f"Citation {idx}: {data['citation']}"):
                st.markdown(
                    f"""
                    <p><b>Reference:</b> 
                        <a href="{data['link']}" class="citation-reference" target="_blank">{data['reference']}</a>
                    </p>
                    <p><b>Sentiment:</b> 
                        <span style="color: {'green' if data['sentiment'] == 'Positive' else 'red' if data['sentiment'] == 'Negative' else '#FFD700'}; font-weight: bold;">{data['sentiment']}</span>
                    </p>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.warning("No citations extracted yet. Please upload a file and click 'Extract Citations and References'.")

# About Page
elif selected == "About":
    st.title("About This App")
    st.write(
        "**Citation Extractor** is a cutting-edge tool designed to empower researchers, academics, and professionals "
        "by simplifying the process of analyzing research papers. This app automatically extracts citation sentences, "
        "intelligently matches them with their respective references, and performs sentiment analysis to provide deeper insights into the context of each citation.\n\n"
        "With its user-friendly interface and advanced algorithms, Citation Extractor helps you:\n\n"
        "- **Quickly Extract Citations**: Identify key citation sentences from any uploaded PDF.\n"
        "- **Effortlessly Match References**: Link citations to their corresponding references with high accuracy.\n"
        "- **Analyze Sentiments**: Understand the tone and context of citations—positive, neutral, or negative.\n"
        "- **Save Time and Boost Productivity**: Focus on your research while the app handles the heavy lifting.\n\n"
        "Built using the powerful **Streamlit** framework and AI-driven technologies, this app is your reliable assistant for citation analysis and reference management."
    )

# Contact Page
elif selected == "Contact":
    st.title("Contact Us")
    st.write(
        "For inquiries or support, reach out to us:\n\n"
        "- **Name**: Umer Qureshi\n"
        "- **Email**: [umerqureshi@gmail.com](mailto:umerqureshi@gmail.com)\n"
        "- **Phone**: +92-331-5429908\n"
        "- **Website**: [CitationExtractor.com](https://citationextractor.com)"
    )
