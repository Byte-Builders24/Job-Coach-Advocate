import os
import requests
from embedding_service import generate_embedding
from search_service import search_candidates

def generate_resume(input_text, email="", phone=""):
    """
    Generate a resume using Azure OpenAI (gpt-35-turbo).
    """
    # Append additional information to the input text
    additional_info = f"""
    Candidate Contact Information:
    - Email: {email}
    - Phone: {phone}
    """
    input_text += "\n\n" + additional_info

    # Azure OpenAI API endpoint, key, and deployment name
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    deployment_name = os.environ.get("AZURE_OPENAI_RESUME_DEPLOYMENT_NAME")  # Deployment name

    # Validate environment variables
    if not endpoint or not api_key or not deployment_name:
        raise ValueError("Azure OpenAI environment variables are not set correctly.")

    # Define the prompt for generating a resume
    prompt = f"""
    You are a professional resume writer and Job Coach. Based on the following input, create a structured resume in plain text format, and note that later, your resumes will be embedded for vector search with 'growth potential', hidden_skills, skills, resume_url, email, and phone as the things to look for:
    
    Input: {input_text}
    
    Resume Format:
    - Name:
    - Professional Summary:
    - Key Skills:
    - Work Experience:
    - Education:
    - Certifications:
    - Technical Skills:
    """

    # Azure OpenAI API request
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    payload = {
        "messages": [
            {"role": "system", "content": "You are a professional resume writer."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    # Construct the full API URL
    api_url = f"{endpoint}openai/deployments/{deployment_name}/chat/completions?api-version=2025-01-01-preview"

    response = requests.post(
        api_url,
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        # Extract the generated resume
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Failed to generate resume. Error: {response.status_code} - {response.text}")