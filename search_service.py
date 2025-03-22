import os
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

def search_candidates(query_text=None, top_k=5):
    """
    Perform a text-based search in Azure Cognitive Search using the 'content' field.
    """
    endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    api_key = os.environ.get("AZURE_SEARCH_API_KEY")
    index_name = "resumesearch"  # Ensure this matches your index name

    # Initialize the SearchClient
    client = SearchClient(endpoint=endpoint, index_name=index_name, credential=AzureKeyCredential(api_key))

    try:
        # Perform text-based search
        results = client.search(
            search_text=query_text if query_text else "*",  # Use query_text or match all documents
            top=top_k,
            select=["id", "content", "@search.score"]  # Select relevant fields
        )

        # Parse and return the results
        return [
            {
                "id": result.get("id", "Unknown"),
                "content": result.get("content", "No content available"),
                "score": result.get("@search.score", 0)
            }
            for result in results
        ]
    except Exception as e:
        raise Exception(f"Failed to perform search: {e}")