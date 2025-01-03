import streamlit as st
import pandas as pd
import os
from transformers import pipeline
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import language_tool_python
import random

# Initialize the language tool for grammar correction
tool = language_tool_python.LanguageTool('en-US', remote_server='https://api.languagetool.org')


# Initialize SentenceTransformer for semantic similarity
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Initialize the question-answering pipeline with a specific model
qa_pipeline = pipeline('question-answering', model='distilbert-base-cased-distilled-squad')

# Define file paths (use the Streamlit Cloud path for deployment)
terms_file_path = os.path.join(os.getcwd(), "data/Terms.xlsx")
faqs_file_path = os.path.join(os.getcwd(), "data/FAQs.xlsx")

# Load data from all sheets in the Excel file
def load_data(file_path):
    try:
        xls = pd.ExcelFile(file_path)
        data = {}
        for sheet_name in xls.sheet_names:
            data[sheet_name] = xls.parse(sheet_name)
        return data
    except Exception as e:
        st.error(f"Error loading data from {file_path}: {e}")
        return {}

# Initialize data from both Excel files
terms_data = load_data(terms_file_path)
faqs_data = load_data(faqs_file_path)

# Pre-compute embeddings for FAQ questions
faq_questions = []
faq_answers = []
faq_embeddings = []
for df in faqs_data.values():
    if 'question' in df.columns and 'answer' in df.columns:
        faq_questions.extend(df['question'].tolist())
        faq_answers.extend(df['answer'].tolist())
faq_embeddings = model.encode(faq_questions)

# Function to correct text using LanguageTool
def correct_text(text):
    try:
        matches = tool.check(text)
        corrected_text = language_tool_python.utils.correct(text, matches)
        return corrected_text
    except Exception as e:
        st.error(f"Error correcting text: {e}")
        return text

# Function for semantic search (FAQ matching)
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
        # If no direct matches found, return random 3 related searches from the same FAQ sheet
        random_related_searches = random.sample(faq_questions, min(3, len(faq_questions)))
        related_searches.extend(random_related_searches)

    return top_answers, related_searches[:3]

# Function to search important terms
def search_important_terms(query):
    if not isinstance(query, str):
        query = str(query)

    # Check if the Excel file name contains "imp terms"
    is_imp_terms = 'underwriter' in terms_file_path.lower()

    for df_name, df in terms_data.items():
        if 'term' in df.columns and 'defination' in df.columns:
            for _, row in df.iterrows():
                if query.lower() == str(row['term']).lower():
                    return row['defination']

            # If no match and it's 'imp terms', return random terms
            if is_imp_terms:
                random_related_terms = random.sample(df['term'].tolist(), min(3, len(df)))
                return random_related_terms

    return None

# Streamlit User Interface
st.title("Insurance Query Answering System")

# User input for query
user_query = st.text_input("Ask your question:")

if user_query:
    # Apply grammar correction if the query is more than a single word
    corrected_query = correct_text(user_query) if len(user_query.split()) > 1 else user_query

    # Check if the query matches any important terms
    term_definition = search_important_terms(corrected_query)
    if term_definition:
        st.write("Term Definition:", term_definition)
    else:
        # Perform semantic search if no important term is found
        faq_answers, related_searches = semantic_search(corrected_query)
        if faq_answers:
            st.write("Top Answers:")
            for answer in faq_answers:
                st.write(f"- {answer}")

        # If no FAQ answers, try QA pipeline
        if not faq_answers:
            faq_context = " ".join(faq_answers)
            qa_answer = qa_pipeline(question=corrected_query, context=faq_context)
            st.write(f"QA Answer: {qa_answer['answer']}")

        # Display related searches
        if related_searches:
            st.write("Related Searches:")
            for related in related_searches:
                st.write(f"- {related}")
