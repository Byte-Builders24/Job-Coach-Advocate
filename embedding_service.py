import os
import requests
import json
from datetime import datetime
from azure_blob_storage import AzureBlobStorage
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

def generate_embedding(text):
    """
    Generate an embedding for the given text using Azure OpenAI (text-embedding-3-small-march21).
    """
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    deployment_name = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")

    if not endpoint or not api_key or not deployment_name:
        raise ValueError("Azure OpenAI environment variables for embedding generation are not set correctly.")

    api_url = f"{endpoint}/openai/deployments/{deployment_name}/embeddings?api-version=2023-05-15"

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    payload = {
        "input": text
    }

    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["data"][0]["embedding"]
    else:
        raise Exception(f"Failed to generate embedding. Error: {response.status_code} - {response.text}")


def store_embedding(email, embedding, resume_url):
    """
    Store the embedding in Azure Blob Storage as a JSON file.
    """
    blob_storage = AzureBlobStorage()
    container_name = "embeddings"

    # Build the JSON data for storing
    embedding_data = {
        "email": email,
        "embedding": embedding,
        "resume_url": resume_url
    }

    # Create a timestamp-based filename to avoid overwriting
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{email.replace('@', '_').replace('.', '_')}_embedding_{timestamp_str}.json"

    try:
        blob_storage.upload_resume(container_name, file_name, json.dumps(embedding_data))
        print(f"Embedding stored successfully in Blob Storage: {container_name}/{file_name}")
    except Exception as e:
        raise Exception(f"Failed to store embedding in Blob Storage: {e}")


def download_all_embeddings():
    """
    Download all embedding JSON files from Azure Blob Storage.
    """
    blob_storage = AzureBlobStorage()
    container_name = "embeddings"

    container_client = blob_storage.blob_service_client.get_container_client(container_name)
    embeddings = []

    for blob in container_client.list_blobs():
        if blob.name.endswith("_embedding.json") or "_embedding_" in blob.name:
            blob_client = container_client.get_blob_client(blob.name)
            embedding_data = json.loads(blob_client.download_blob().readall())
            embeddings.append(embedding_data)

    return embeddings

