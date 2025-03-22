import streamlit as st
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import os

# Streamlit Resume Retrieval Page
st.title("Resume Retrieval")
st.subheader("View all resumes stored in the system")

# Add a search box for semantic sorting
query_text = st.text_input("Search Resumes (optional):", placeholder="Enter a query to sort resumes semantically")

try:
    with st.spinner("Loading resumes..."):
        # Fetch resumes with semantic sorting
        results = search_candidates(query_text=query_text, top_k=100)

    # Display results
    if results:
        st.write("### Resumes")
        for result in results:
            st.write(f"**ID**: {result['id']}")
            st.write(f"**Resume Content**: {result['content'][:500]}...")  # Display first 500 characters
            st.write("---")
    else:
        st.info("No resumes found.")
except Exception as e:
    st.error(f"Failed to load resumes: {e}")

def search_candidates(query_text=None, top_k=100):
    """
    Perform a text-based search in Azure Cognitive Search using the 'content' field.
    If no query_text is provided, return all resumes.
    """
    endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    api_key = os.environ.get("AZURE_SEARCH_API_KEY")
    index_name = "resumesearch"  # Ensure this matches your index name

 
    try:
        # Perform semantic search
        results = client.search(
            search_text=query_text if query_text else "*",  # Match all documents if no query_text
            top=top_k,
            query_type="semantic",  # Enable semantic search
            semantic_configuration_name="semantic-config",  # Use the semantic configuration you created
            select=["id", "content"]  # Only fetch the ID and content fields
        )

        # Parse and return the results
        return [
            {
                "id": result.get("id", "Unknown"),
                "content": result.get("content", "No content available")
            }
            for result in results
        ]
    except Exception as e:
        raise Exception(f"Failed to perform search: {e}")

# Streamlit Resume Retrieval Page
st.title("Resume Retrieval")
st.subheader("View all resumes stored in the system")

try:
    with st.spinner("Loading resumes..."):
        # Fetch all resumes
        results = search_candidates(top_k=100)

    # Display results
    if results:
        st.write("### Resumes")
        for result in results:
            st.write(f"**ID**: {result['id']}")
            st.write(f"**Resume Content**: {result['content'][:500]}...")  # Display first 500 characters
            st.write("---")
    else:
        st.info("No resumes found.")
except Exception as e:
    st.error(f"Failed to load resumes: {e}")
