from azure.storage.blob import BlobServiceClient
import os
class AzureBlobStorage:
    def __init__(self):
        connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            raise ValueError("Azure Storage connection string is not set in environment variables.")
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    def upload_resume(self, container_name, file_name, content):
        """
        Existing method to upload a JSON or text file to Azure Blob Storage.
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()

        blob_client = container_client.get_blob_client(file_name)
        blob_client.upload_blob(content, overwrite=True)
        return f"File stored successfully: {container_name}/{file_name}"

    def download_resume(self, container_name, file_name):
        """
        Existing method to download a file from Azure Blob Storage.
        """
        blob_client = self.blob_service_client.get_blob_client(container_name, file_name)
        if not blob_client.exists():
            raise FileNotFoundError(f"The file {file_name} does not exist in container {container_name}.")
        return blob_client.download_blob().readall()

    def store_resume(self, email, resume_text):
        """
        New method: store the plain text resume separately from embeddings.
        """
        container_name = "resumes"  # Use any container name you prefer
        container_client = self.blob_service_client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()

        file_name = f"{email.replace('@', '_').replace('.', '_')}_resume.txt"
        blob_client = container_client.get_blob_client(file_name)
        blob_client.upload_blob(resume_text, overwrite=True)
        return f"Resume stored successfully: {container_name}/{file_name}"
    
    