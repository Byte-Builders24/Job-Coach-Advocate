import os
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

def search_candidates(query_text=None, top_k=5):
    """
    Perform a semantic search in Azure Cognitive Search, returning semantic captions and
    semantic answers if the query is question-like. The function demonstrates:
    1. query_type='semantic'
    2. semantic_configuration_name='my-semantic-config'
    3. returning captions (query_caption='extractive')
    4. returning semantic answers (query_answer='extractive')
    5. retrieving reranker scores, captions, answers, and standard fields
    """

    endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    api_key = os.environ.get("AZURE_SEARCH_API_KEY")
    index_name = "resumesearch"  # Replace with your index name

    if not endpoint or not api_key:
        raise ValueError("Azure Cognitive Search environment variables are not set correctly.")

    # Instantiate SearchClient
    client = SearchClient(endpoint=endpoint, index_name=index_name, credential=AzureKeyCredential(api_key))

    # Use wildcard "*" if no query_text is provided
    final_query = query_text if query_text else "*"

    try:
        # Perform the semantic search
        results = client.search(
            search_text=final_query,
            query_type="semantic",
            semantic_configuration_name="my-semantic-config",
            select=["id", "content"],
            top=top_k,
            query_caption="extractive",
            query_answer="extractive"
        )

        # 1) Retrieve semantic answers from the response
        semantic_answers = results.get_answers() or []

        # 2) Build a list of documents, including the reranker score & captions
        documents = []
        for result in results:
            # Retrieve the captions safely
            captions = result.get("@search.captions", None)
            first_caption = ""
            if captions is not None:
                if isinstance(captions, list):
                    if len(captions) > 0:
                        first_item = captions[0]
                        if isinstance(first_item, dict):
                            first_caption = first_item.get("highlights", "") or first_item.get("text", "")
                        else:
                            first_caption = getattr(first_item, "highlights", "") or getattr(first_item, "text", "")
                else:
                    # captions is not a list; assume it's a single object
                    first_caption = getattr(captions, "highlights", "") or getattr(captions, "text", "")
            
            documents.append({
                "id": result.get("id", "Unknown"),
                "content": result.get("content", "No content available"),
                "reranker_score": result.get("@search.rerankerScore", result.get("@search.reranker_score", 0)),
                "caption": first_caption
            })

        # 3) Return a dictionary with "semantic_answers" and "documents"
        return {
            "semantic_answers": [
                {
                    "text": ans.text,
                    "highlights": ans.highlights,
                    "score": ans.score
                }
                for ans in semantic_answers
            ],
            "documents": documents
        }

    except Exception as e:
        raise Exception(f"Failed to perform semantic search: {e}")