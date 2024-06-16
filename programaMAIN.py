import json
import sys
from gensim.utils import tokenize
import nltk
from gensim.models import TfidfModel
from gensim.corpora import Dictionary
from gensim.similarities import SparseMatrixSimilarity

# Ensure you have the NLTK Portuguese stopwords
nltk.download('stopwords')
stopwords = nltk.corpus.stopwords.words('portuguese')

# Load JSON data
with open('drePEQUENINO.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract notes from the JSON data
notes = [entry['notes'] for entry in data]

def preprocess(text):
    text = text.lower()
    tokens = tokenize(text)
    tokens = [token for token in tokens if token not in stopwords]
    return list(tokens)

# Preprocess the text
sentences = [preprocess(note) for note in notes]

# Create a Dictionary and a Corpus
dictionary = Dictionary(sentences)
corpus_bow = [dictionary.doc2bow(sent) for sent in sentences]

# Create a TF-IDF model
tfidf_model = TfidfModel(corpus_bow, normalize=True)

# Create an index for similarity queries
index = SparseMatrixSimilarity(tfidf_model[corpus_bow], num_docs=len(corpus_bow), num_terms=len(dictionary))

def search(query, top_n=10):
    query_tokenized = preprocess(query)
    query_bow = dictionary.doc2bow(query_tokenized)
    tfidf_query = tfidf_model[query_bow]
    
    # Calculate similarities
    sims = index[tfidf_query]
    
    # Sort the results
    sims_ordered = sorted(enumerate(sims), key=lambda item: item[1], reverse=True)
    
    # Retrieve top N documents
    results = []
    for idx, sim in sims_ordered[:top_n]:
        results.append((data[idx], sim))
    return results

def main():
    while True:
        print("\nMenu:")
        print("1. Perform a query")
        print("2. Quit")
        choice = input("Enter your choice: ")
        
        if choice == '1':
            query = input("Enter your query: ")
            results = search(query)
            for result in results:
                print("----------------------------------------------------------------------\nResult:")
                print(f"Similarity: {result[1]}")
                print(f"Document ID: {result[0]['id']}")
                print(f"Date: {result[0]['date']}")
                print(f"Notes: {result[0]['notes']}")
                print("\n")
        elif choice == '2':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()