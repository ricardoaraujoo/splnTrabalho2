import json
import sys
from gensim.utils import tokenize
import nltk
from gensim.models import TfidfModel
from gensim.corpora import Dictionary
from gensim.similarities import SparseMatrixSimilarity
from fetchBD import query_by_ids
from transformers import pipeline, BertModel, BertTokenizer

#DATA BASE PATH
db_path = 'dataset/database111_DRE.sqlite'


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


def print_resuls_table(normalTable):

    if normalTable:
        print("Documents ordered by similarity:")
        for entrada in normalTable:
            print("---------------------------------------------")
            print(f"\nResult::\n {entrada}\n")
    else:
        print("No details found for ID")


def processa_query():
    print("Choose the number of documents you wish to see")
    while True:
        choiceNumberDocs = input("Enter your choice: ")
        if choiceNumberDocs.isdigit():  # Checks if the input is all digits
            choiceNumberDocs = int(choiceNumberDocs)  # Converts to integer
            query = input("Enter your query: ")
            results = search(query,choiceNumberDocs)
            ids = []
            for result in results:
                ids.append(result[0]['id'])
            return ids
        else:
            print("Invalid choice. Please enter a number.")


# Function to perform Question Answering with a specified model
def run_qa_pipeline(model_identifier, text_context, query):
    question_answering_pipeline = pipeline('question-answering', model=model_identifier)
    answer_result = question_answering_pipeline(question=query, context=text_context)
    return answer_result['answer']

# Function to test various models on a set of questions
def test_model_performance(text_context, query_list):
    models_list = [
        "lfcc/bert-portuguese-squad",
        "pierreguillou/bert-large-cased-squad-v1.1-portuguese"
    ]

    performance_results = {}
    for each_model in models_list:
        model_answers = [run_qa_pipeline(each_model, text_context, single_query) for single_query in query_list]
        performance_results[each_model] = model_answers

    return performance_results


def get_user_questions():
    questions = []
    print("Enter your questions (type 'exit' to finish):")
    while True:
        user_input = input()
        if user_input.lower() == "exit":
            break
        questions.append(user_input)
    return questions

def qa_logic(result):

    print("Performing Question Answering on the document...")
    print("Please select one of the options below:")
    print("1. Use the default questions")
    print("2. Enter your own questions")
    choiceQA = input("Enter your choice: ")
    questions = []
    if choiceQA == '1':

        questions = [
            "Qual é o tema do documento?",
            "Quem emitiu o documento?",
            "Qual é a data do documento?",
            "Que locais são referidos no documento?",
            "Qual é o tipo do documento?"
        ]
    elif choiceQA == '2':
        questions = get_user_questions()
    else:
        print("Invalid choice. Using default questions.")
        questions = [
            "Qual é o tema do documento?",
            "Quem emitiu o documento?",
            "Qual é a data do documento?",
            "Que locais são referidos no documento?",
            "Qual é o tipo do documento?"
        ]

    model_performance_results = test_model_performance(result, questions)

    # Display the comparison results
    for each_model, answers in model_performance_results.items():
        print(f"Performance for {each_model}:")
        for each_question, each_answer in zip(questions, answers):
            print(f"Question: {each_question}\nAnswer: {each_answer}\n")


def main():
    while True:
        print("\nMenu:")
        print("1. Perform a query")
        print("2. Quit")
        choice = input("Enter your choice: ")
        
        if choice == '1':
            ids = processa_query()
            print("Querying the database...")
            print(ids)
            results, resultadosTEXTO,flag  = query_by_ids(db_path, ids)
            print_resuls_table(results)
            stringQA = ""
            if flag: #text table
                data = resultadosTEXTO[2]
                info = resultadosTEXTO[4]
                stringQA = f"O documento foi emitido na data {data} e contém as seguintes informações: {info}"

            else: #table normal
                print("Document inteiro não encontrado, vamos executar com um resumo do documento")
                tipo_Doc = resultadosTEXTO[2]
                emitiou = resultadosTEXTO[4]
                fonte = resultadosTEXTO[5]
                data = resultadosTEXTO[9]
                info2 = resultadosTEXTO[10]
                stringQA = f"O documento é do tipo {tipo_Doc}, foi emitido por {emitiou}, na data {data} e contém as seguintes informações: {info2}. Fonte: {fonte}"

            qa_logic(stringQA)

        elif choice == '2':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()