from flask import Flask, request, jsonify
import pandas as pd
import os
from transformers import pipeline
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import language_tool_python

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

tool = language_tool_python.LanguageTool('en-US', remote_server='https://api.languagetool.org')

def correct_text(text):
    try:
        matches = tool.check(text)
        corrected_text = language_tool_python.utils.correct(text, matches)
        return corrected_text
    except Exception as e:
        print(f"Error correcting text: {e}")
        return text

def semantic_search(query, threshold=0.5):
    query_embedding = model.encode(query).reshape(1, -1)  # Reshape to (1, 384)
    similarities = cosine_similarity(query_embedding, faq_embeddings)[0]
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

    query_embedding = model.encode(query)
    similarities = cosine_similarity([query_embedding], faq_embeddings)[0]
    results = []
    related_searches = []

    for i, similarity in enumerate(similarities):
        if similarity > threshold:
            results.append((faq_questions[i], faq_answers[i], similarity))
            related_searches.append(faq_questions[i])

    results.sort(key=lambda x: x[2], reverse=True)
    top_answers = [result[1] for result in results[:3]]

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

@app.route('/ask', methods=['POST'])
def ask():
    try:
        user_query = request.form['query']

        if len(user_query.split()) > 1:
            corrected_query = correct_text(user_query)
        else:
            corrected_query = user_query

        term_definition = search_important_terms(corrected_query)
        if term_definition:
            return jsonify({'response': [term_definition], 'related_searches': []})

        faq_answers, related_searches = semantic_search(corrected_query)
        if faq_answers:
            return jsonify({'response': faq_answers[:3], 'related_searches': related_searches})

        faq_context = " ".join(faq_answers)
        qa_answer = "Sorry, I couldn't find an answer to your question."
        return jsonify({'response': [qa_answer], 'related_searches': []})

    except Exception as e:
        return jsonify({'response': [f'An error occurred: {str(e)}'], 'related_searches': []})

if __name__ == '__main__':
    app.run(debug=True)
