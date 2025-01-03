import streamlit as st
import requests
import os
import random
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import pandas as pd
import language_tool_python

# Flask backend URL
FLASK_URL = 'http://localhost:5000/ask'

tool = language_tool_python.LanguageTool('en-US', remote_server='https://api.languagetool.org')

# Load the FAQ and Terms data just as in the Flask code
terms_file_path = os.path.join(os.getcwd(), "data/Terms.xlsx")
faqs_file_path = os.path.join(os.getcwd(), "data/FAQs.xlsx")

def load_data(file_path):
    try:
        xls = pd.ExcelFile(file_path)
        data = {}
        for sheet_name in xls.sheet_names:
            data[sheet_name] = xls.parse(sheet_name)
        return data
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
        return {}

terms_data = load_data(terms_file_path)
faqs_data = load_data(faqs_file_path)

# Initialize the semantic search model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Pre-compute embeddings for FAQ questions
faq_questions = []
faq_answers = []
faq_embeddings = []
for df in faqs_data.values():
    if 'question' in df.columns and 'answer' in df.columns:
        faq_questions.extend(df['question'].tolist())
        faq_answers.extend(df['answer'].tolist())
faq_embeddings = model.encode(faq_questions)

def correct_text(text):
    try:
        matches = tool.check(text)
        corrected_text = language_tool_python.utils.correct(text, matches)
        return corrected_text
    except Exception as e:
        print(f"Error correcting text: {e}")
        return text

def semantic_search(query, threshold=0.5):
    query_embedding = model.encode(query)
    similarities = cosine_similarity([query_embedding], faq_embeddings)[0]
    results = []
    related_searches = []

    for i, similarity in enumerate(similarities):
        if similarity > threshold:
            results.append((faq_questions[i], faq_answers[i], similarity))
            related_searches.append(faq_questions[i])

    results.sort(key=lambda x: x[2], reverse=True)  # Sort by similarity score
    top_answers = [result[1] for result in results[:3]]  # Return only the top 3 answers

    if not top_answers:
        random_related_searches = random.sample(faq_questions, min(3, len(faq_questions)))
        related_searches.extend(random_related_searches)

    return top_answers, related_searches[:3]

def search_important_terms(query):
    if not isinstance(query, str):
        query = str(query)

    is_imp_terms = 'underwriter' in terms_file_path.lower()

    for df_name, df in terms_data.items():
        if 'term' in df.columns and 'defination' in df.columns:
            for _, row in df.iterrows():
                if query.lower() == str(row['term']).lower():
                    return row['defination']

            if is_imp_terms:
                random_related_terms = random.sample(df['term'].tolist(), min(3, len(df)))
                return random_related_terms

    return None

# Streamlit frontend
st.title("FAQ and Query System")

user_query = st.text_input("Ask your question here:")

if user_query:
    # Call the Flask backend
    payload = {'query': user_query}
    response = requests.post(FLASK_URL, data=payload)
    if response.status_code == 200:
        data = response.json()
        answers = data['response']
        related_searches = data['related_searches']

        if answers:
            st.subheader("Top Answers")
            for ans in answers:
                st.write(ans)
        else:
            st.write("No direct answers found.")

        if related_searches:
            st.subheader("Related Search Results")
            for related in related_searches:
                st.write(f"- {related}")
    else:
        st.write("There was an error with the backend.")
