from scholarly import scholarly
import streamlit as st

class GoogleScholarSearch:
    @staticmethod
    def search(query, max_results=5):
        """
        Perform a Google Scholar search and return the top results.
        """
        search_query = scholarly.search_pubs(query)
        results = []
        
        for i, result in enumerate(search_query):
            if i >= max_results:
                break
            
            results.append({
                "title": result.get("bib", {}).get("title", "No title"),
                "author": result.get("bib", {}).get("author", "No author"),
                "abstract": result.get("bib", {}).get("abstract", "No abstract"),
                "url": result.get("pub_url", "No URL")
            })
        
        return results

