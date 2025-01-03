from flask import Flask, request, jsonify, render_template
import pandas as pd
import os
from transformers import pipeline
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import language_tool_python

tool = language_tool_python.LanguageTool('en-US', remote_server='https://api.languagetool.org')

import random

app = Flask(__name__)

# Define file paths
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
        print(f"Error loading data from {file_path}: {e}")
        return {}

# Initialize data from both Excel files
terms_data = load_data(terms_file_path)
faqs_data = load_data(faqs_file_path)

# Initialize the question-answering pipeline with a specific model
qa_pipeline = pipeline('question-answering', model='distilbert-base-cased-distilled-squad')

# Initialize the language tool for grammar correction
tool = language_tool_python.LanguageTool('en-US')

# Initialize SentenceTransformer for semantic similarity
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
        # If no direct matches found, return random 3 related searches from the same FAQ sheet
        random_related_searches = random.sample(faq_questions, min(3, len(faq_questions)))
        related_searches.extend(random_related_searches)

    # Return both top answers and related searches
    return top_answers, related_searches[:3]

def get_qa_answer(question, context):
    try:
        result = qa_pipeline(question=question, context=context)
        return result['answer']
    except Exception as e:
        print(f"Error getting QA answer: {e}")
        return "Sorry, I couldn't find an answer to your question."

def search_important_terms(query):
    # Convert query to string if it's not already
    if not isinstance(query, str):
        query = str(query)

    # Check if the Excel file name contains "imp terms"
    is_imp_terms = 'underwriter' in terms_file_path.lower()

    # Assuming important terms data has 'term' and 'definition' columns
    for df_name, df in terms_data.items():
        if 'term' in df.columns and 'defination' in df.columns:
            for _, row in df.iterrows():
                # Convert row['term'] to string to avoid AttributeError
                if query.lower() == str(row['term']).lower():
                    return row['defination']

            # If no direct match found and it's 'imp terms', return random related terms
            if is_imp_terms:
                random_related_terms = random.sample(df['term'].tolist(), min(3, len(df)))
                return random_related_terms

    return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        user_query = request.form['query']

        # Apply grammar correction only if the query is a full sentence
        if len(user_query.split()) > 1:
            corrected_query = correct_text(user_query)
        else:
            corrected_query = user_query

        # Check if the query matches any important terms
        term_definition = search_important_terms(corrected_query)
        if term_definition:
            return jsonify({'response': [term_definition], 'related_searches': []})

        # If not an important term, search in FAQs
        faq_answers, related_searches = semantic_search(corrected_query)
        if faq_answers:
            # Return only the top 3 responses
            return jsonify({'response': faq_answers[:3], 'related_searches': related_searches})

        # If no relevant FAQs found, try QA pipeline
        # Assuming all FAQ answers are in one sheet, use it as context
        faq_context = " ".join(faq_answers)
        qa_answer = get_qa_answer(corrected_query, faq_context)
        return jsonify({'response': [qa_answer] if qa_answer else ["Sorry, I couldn't find an answer to your question."], 'related_searches': []})

    except Exception as e:
        print(f"Error in /ask route: {e}")
        return jsonify({'response': [f'An error occurred: {str(e)}'], 'related_searches': []})

if __name__ == '__main__':
    app.run(debug=True)
