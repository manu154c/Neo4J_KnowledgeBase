from django.shortcuts import render
from nltk.tokenize import word_tokenize
import string

from py2neo import Graph
from py2neo import Node, Relationship

# for testing purpose
import pdb

# Main context Predictor Function
def predict_context(request):
    input_data = "Cat climbed the tree. Dog Climbed the tree."
    cleaned_tocken = text_cleaning(input_data)
    dictinary_from_tokens = create_dictionary(cleaned_tocken)
    insert_into_graph_db(dictinary_from_tokens)
    #output = "Cat climbed the tree. Dog Climbed the tree."
    output = dictinary_from_tokens
    return render(request, 'Predict/post_list.html', {'output' : output})

# Word embedding require minimal document cleaning
# No need of stemming, stop words removal etc...
def text_cleaning(input_doc):
    tokens = word_tokenize(input_doc)
    # convert to lower case
    tokens_lower = [w.lower() for w in tokens]
    # remove punctuation from each word
    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table) for w in tokens_lower]
    
    return stripped

# Creates a dictionary from the input document.
def create_dictionary(input_token):
    # unique_values_list = list(set(input_token))
    output = {}
    # pdb.set_trace()
    for item in input_token:
        if item in output:
            output[item] = int(output[item]) + 1
        else:
            output[item] = 1
            
    # pdb.set_trace()

    return output


def insert_into_graph_db(dictionary_in):
    graph = Graph('http://localhost:7474/db/data', user='neo4j', password='root')
    cypher = graph.cypher
    for key, value in dictionary_in.items():
        cypher.execute("CREATE ({a}:Word { value: {a}, count: {b} }), a="+key+", b="+value+"")
        
    return 1

