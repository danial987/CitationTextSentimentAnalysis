import openai
import re
from textblob import TextBlob
from utils.helpers import split_text_into_chunks
from difflib import SequenceMatcher


class CitationExtractor:
    def __init__(self):
        openai.api_key = st.secrets["openai"]["api_key"]

    def extract_citations_with_metadata(self, text):
        """
        Extract citations, their associated references, and sentiment analysis.
        """
        references = self.extract_references(text)
        citations = self.get_citations(text)

        # Debugging: Print extracted references and citations
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

        return list(dict.fromkeys(citations))  # Remove duplicates

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
            references = references_raw.split("\n")  # Split references into individual items
            return [ref.strip() for ref in references if ref.strip()]
        except Exception as e:
            print(f"Error during reference extraction: {e}")
            return []

    def match_reference(self, citation, references, idx):
        """
        Match a citation to its most likely reference.
        """
        if len(references) > idx:
            # First try to match by index (assumes order alignment)
            return references[idx]

        # If no match by index, try similarity scoring
        best_match = None
        highest_similarity = 0

        for reference in references:
            # Use SequenceMatcher to calculate similarity
            similarity = SequenceMatcher(None, citation.lower(), reference.lower()).ratio()
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = reference

        # Threshold for acceptable similarity
        if highest_similarity > 0.4:  # Adjust threshold as needed
            return best_match

        return "No matching reference found"

    def generate_google_scholar_link(self, reference):
        """
        Generate a Google Scholar search link for the given reference.
        """
        if reference == "No matching reference found":
            return "https://scholar.google.com"

        # Replace spaces with "+" for Google Scholar search format
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