import streamlit as st
from search_service import search_candidates

st.title("Resume Retrieval")
st.subheader("View resumes stored in the system")

# Let the user enter a query
query_text = st.text_input("Enter a query (e.g., 'Who makes a good engineer?'):")

if st.button("Search"):
    try:
        with st.spinner("Searching..."):
            # Retrieve data from your semantic search function
            result_data = search_candidates(query_text=query_text, top_k=100)
        
        # Documents (our actual records)
        documents = result_data.get("documents", [])
        if documents:
            st.write("### Resumes")
            for doc in documents:
                st.write(f"**ID**: {doc.get('id', 'Unknown')}")
                st.write(f"**Score**: {doc.get('reranker_score', 0)}")
                
                # Safely handle strings for content
                content_text = doc.get('content', 'No content available')
                st.write(f"**Resume Content**: {content_text[:500]}...")  # Slice up to 500 chars
                
                # Display additional fields from your index (all are strings by default)
                roles = doc.get('roles', '')
                if roles:
                    st.write(f"**Roles**: {roles}")
                
                role_category = doc.get('role_category', '')
                if role_category:
                    st.write(f"**Role Category**: {role_category}")
                
                career = doc.get('career', '')
                if career:
                    st.write(f"**Career**: {career}")
                
                contact = doc.get('contact', '')
                if contact:
                    st.write(f"**Contact**: {contact}")

                personality = doc.get('personality', '')
                if personality:
                    st.write(f"**Personality**: {personality}")

                name = doc.get('name', '')
                if name:
                    st.write(f"**Name**: {name}")

                keywords = doc.get('keywords', '')
                if keywords:
                    st.write(f"**Keywords**: {keywords}")

                # If you have chunk, title, text_vector, or resume_url, display them similarly:
                chunk = doc.get('chunk', '')
                if chunk:
                    st.write(f"**Chunk**: {chunk}")
                
                title = doc.get('title', '')
                if title:
                    st.write(f"**Title**: {title}")
                
                resume_url = doc.get('resume_url', '')
                if resume_url:
                    st.write(f"**Resume URL**: {resume_url}")

                text_vector = doc.get('text_vector', '')
                if text_vector:
                    st.write(f"**Text Vector**: {text_vector}")

                st.write("---")
        else:
            st.info("No resumes found.")

        # Semantic answers (extractive answers from Azure Cognitive Search)
        semantic_answers = result_data.get("semantic_answers", [])
        if semantic_answers:
            st.write("### Semantic Answers")
            for ans in semantic_answers:
                highlights_or_text = ans.get('highlights') or ans.get('text') or ''
                st.write(f"**Answer** (score={ans.get('score', 0)}): {highlights_or_text}")

    except Exception as e:
        st.error(f"Failed to load resumes: {e}")