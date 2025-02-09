import openai
import re
from textblob import TextBlob
from utils.helpers import split_text_into_chunks
from difflib import SequenceMatcher
import streamlit as st

class CitationExtractor:
    def __init__(self):
        openai.api_key = st.secrets["openai"]["api_key"]

    def extract_citations_with_metadata(self, text):
        """
        Extract citations, their associated references, and sentiment analysis.
        """
        references = self.extract_references(text)
        citations = self.get_citations(text)

        print(f"Extracted References: {references}")
        print(f"Extracted Citations: {citations}")

        citation_metadata = []
        for idx, citation in enumerate(citations):
            sentiment = self.analyze_sentiment(citation)
            matched_reference = self.match_reference(citation, references, idx)
            link = self.generate_google_scholar_link(matched_reference)
            citation_metadata.append(
                {
                    "citation": citation,
                    "reference": matched_reference,
                    "link": link,
                    "sentiment": sentiment,
                }
            )

        return citation_metadata

    def get_citations(self, text):
        """
        Extract citation sentences from the text.
        """
        chunks = split_text_into_chunks(text, max_tokens=3000, overlap=50)
        citations = []

        for chunk in chunks:
            prompt = f"Extract all citation sentences from the following text:\n\n{chunk}"
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                    temperature=0.2,
                )
                sentences = response["choices"][0]["message"]["content"].strip().split("\n")
                citations.extend([sentence.strip() for sentence in sentences if sentence.strip()])
            except Exception as e:
                print(f"Error during citation extraction: {e}")

        return list(dict.fromkeys(citations))  

    def extract_references(self, text):
        """
        Extract the references section from the text and split them into individual references.
        """
        prompt = f"Extract the references section from the following text:\n\n{text}"
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.2,
            )
            references_raw = response["choices"][0]["message"]["content"].strip()
            references = references_raw.split("\n")  
            return [ref.strip() for ref in references if ref.strip()]
        except Exception as e:
            print(f"Error during reference extraction: {e}")
            return []

    def match_reference(self, citation, references, idx):
        """
        Match a citation to its most likely reference.
        """
        if len(references) > idx:
            return references[idx]

        best_match = None
        highest_similarity = 0

        for reference in references:
            similarity = SequenceMatcher(None, citation.lower(), reference.lower()).ratio()
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = reference

        if highest_similarity > 0.4:  
            return best_match

        return "No matching reference found"

    def generate_google_scholar_link(self, reference):
        """
        Generate a Google Scholar search link for the given reference.
        """
        if reference == "No matching reference found":
            return "https://scholar.google.com"

        search_query = "+".join(reference.split())
        return f"https://scholar.google.com/scholar?q={search_query}"

    def analyze_sentiment(self, text):
        """
        Perform sentiment analysis on a given citation sentence.
        """
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
        if polarity > 0:
            return "Positive"
        elif polarity < 0:
            return "Negative"
        else:
            return "Neutral"