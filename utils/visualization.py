import plotly.express as px
import networkx as nx
from streamlit_agraph import agraph, Node, Edge, Config
import streamlit as st
import pandas as pd

class VisualizationManager:
    @staticmethod
    def generate_network_graph(citations):
        """Generate a NetworkX graph to visualize citation relationships."""
        G = nx.Graph()

        G.add_node("Uploaded Paper", size=30, color="blue")
        sentiment_colors = {"Positive": "green", "Negative": "red", "Neutral": "gray"}

        for sentiment in ["Positive", "Negative", "Neutral"]:
            G.add_node(sentiment, size=20, color=sentiment_colors[sentiment])
            G.add_edge("Uploaded Paper", sentiment)

            for data in citations:
                if data["sentiment"] == sentiment:
                    G.add_node(data["citation"], size=10, color=sentiment_colors[sentiment])
                    G.add_edge(sentiment, data["citation"])

        return G

    @staticmethod
    def display_tree_chart(citations):
        """Generate and display a treemap visualization for citations."""
        if citations:
            tree_data = [
                {
                    "Sentiment": data["sentiment"],
                    "Citation": data["citation"],
                    "Link": f'<a href="{data["link"]}" target="_blank" style="color: white; text-decoration: none;">{data["link"]}</a>',
                }
                for data in citations
            ]

            fig = px.treemap(
                tree_data,
                path=["Sentiment", "Citation", "Link"],
                color="Sentiment",
                color_discrete_map={"Positive": "green", "Negative": "red", "Neutral": "gray"},
            )
            st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def display_network_graph(citations):
        """Generate and display a full-width network graph for citations."""
        G = VisualizationManager.generate_network_graph(citations)

        nodes = [Node(id=n, label=n, size=G.nodes[n]["size"], color=G.nodes[n]["color"]) for n in G.nodes]
        edges = [Edge(source=e[0], target=e[1]) for e in G.edges]

        config = Config(width=1400, height=700, directed=False, physics=True)
        agraph(nodes=nodes, edges=edges, config=config)

    @staticmethod
    def display_pie_chart(citations):
        """Generate and display a Pie Chart of citation sentiment distribution."""
        if citations:
            df = pd.DataFrame(citations)
            fig = px.pie(
                df,
                names="sentiment",
                color="sentiment",
                color_discrete_map={"Positive": "green", "Negative": "red", "Neutral": "gray"},
            )
            st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def display_histogram(citations):
        """Generate and display a histogram of citation sentiment counts."""
        if citations:
            df = pd.DataFrame(citations)
            fig = px.histogram(
                df,
                x="sentiment",
                color="sentiment",
                color_discrete_map={"Positive": "green", "Negative": "red", "Neutral": "gray"},
            )
            st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def display_line_chart(citations):
        """Generate and display a line chart showing the trend of sentiment over time."""
        if citations:
            df = pd.DataFrame(citations)
            df["index"] = range(1, len(df) + 1)  
            fig = px.line(
                df,
                x="index",
                y="sentiment",
                markers=True,
                line_shape="linear",
            )
            st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def display_all_visualizations(citations):
        """Display all visualizations in a Streamlit layout."""
        if citations:
            st.header("📊 Citation Analysis Visualizations")
            
            VisualizationManager.display_network_graph(citations)

            col1, col2 = st.columns(2)
            with col1:
                VisualizationManager.display_pie_chart(citations)
            with col2:
                VisualizationManager.display_histogram(citations)

            VisualizationManager.display_line_chart(citations)

            VisualizationManager.display_tree_chart(citations)