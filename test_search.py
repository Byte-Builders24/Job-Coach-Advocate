from search_service import search_candidates

# Test without embedding (retrieve all documents)
print("Testing without embedding:")
try:
    results = search_candidates(query_embedding=None, top_k=5)
    for result in results:
        print(result)
except Exception as e:
    print(f"Error during search: {e}")

# Test with a dummy embedding (replace with a real embedding for production)
print("\nTesting with embedding:")
try:
    dummy_embedding = [0.1] * 1536  # Replace with a real embedding vector
    results = search_candidates(query_embedding=dummy_embedding, top_k=5)
    for result in results:
        print(result)
except Exception as e:
    print(f"Error during vector search: {e}")