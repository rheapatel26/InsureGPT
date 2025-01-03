# streamlit.py (Streamlit UI)
import streamlit as st
import requests

# Streamlit UI setup
st.title("Insurance Query Answering System")
st.subheader("Ask your question:")

# User input
user_query = st.text_input("Enter your question:")

if user_query:
    try:
        # Make a POST request to Flask API
        response = requests.post("http://localhost:5000/ask", data={"query": user_query})

        # Check if the response is valid
        if response.status_code == 200:
            data = response.json()
            st.write("Top Answers:")
            for idx, answer in enumerate(data['response']):
                st.write(f"{idx + 1}. {answer}")

            st.write("Related Searches:")
            for search in data['related_searches']:
                st.write(f"- {search}")
        else:
            st.write("Error occurred while fetching the answer.")
    
    except Exception as e:
        st.write(f"An error occurred: {e}")
