import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import NaiveBayesClassifier
from nltk.classify import apply_features

# Load data from Excel
df = pd.read_excel('data/Important_terms.xlsx')

# Preprocess data
faq_list = []
for index, row in df.iterrows():
    term = row['term']
    if isinstance(term, str):  # Check if term is a string
        term = term.strip()    # Remove leading/trailing whitespaces if necessary
        definition = row['defination']
        faq_list.append((term, definition))

# Tokenization and stop words removal
stop_words = set(stopwords.words('english'))
filtered_faq_list = []
for (term, definition) in faq_list:
    words = word_tokenize(term.lower())
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    filtered_faq_list.append((filtered_words, definition))

# Prepare features for the classifier
def extract_features(words):
    return dict([(word, True) for word in words])

# Format the features for training
featuresets = apply_features(extract_features, filtered_faq_list)

# Train a simple Naive Bayes classifier
classifier = NaiveBayesClassifier.train(featuresets)

# Example usage:
user_query = "rhea"
words = word_tokenize(user_query.lower())
filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
features = extract_features(filtered_words)
response = classifier.classify(features)

# Print both query and response
print(f"Query: {user_query}")
print(f"Response: {response}")
