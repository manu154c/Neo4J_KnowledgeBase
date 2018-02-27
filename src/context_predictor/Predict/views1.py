""" 

@auther : MANU C
Created : 27/01/18
Last Updated : 09/02/18

"""


from django.shortcuts import render
from nltk.tokenize import word_tokenize
import string

from py2neo import Graph, Node, Relationship, NodeSelector

# neo4j python driver
# from neo4j.v1 import GraphDatabase, basic_auth


# for testing purpose
import pdb
from py2neo import watch

# Main context Predictor Function
def predict_context(request):
    input_data = "Cat climbed the tree. Dog Climbed the other tree."
    #file = open("/home/manu154c/Downloads/phd-datasets/datasets/webkb-test-stemmed.txt","r")
    #input_data = file.read()
    cleaned_tocken = text_cleaning(input_data)
    #print(cleaned_tocken)
    dictinary_from_tokens = create_dictionary(cleaned_tocken)
    #insert_into_graph_db(dictinary_from_tokens)
    count_bigram_relatedness(cleaned_tocken, dictinary_from_tokens)
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
    stripped = filter(None, stripped)
    stripped = list(stripped)
    #print(stripped)
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


# training phase function
# 1. insert_into_graph_db


def insert_into_graph_db(dictionary_in):
    graph = Graph('http://localhost:7474/db/data', user='neo4j', password='root')
    neo4j_transaction = graph.begin()
    #print(dictionary_in)
    for key, value in dictionary_in.items():
        #node = Node(key, name=key, count=value)
        #print(key)
        #print(value)
        #assert(False)
        neo4j_transaction.append("CREATE (word:Word {value:{a}, count:{b}}) RETURN word;", a=key, b=value)
        #pdb.set_trace()
        #watch("neo4j.http")
        #neo4j_transaction.create(node)
    neo4j_transaction.commit()
    return 1


"""
def insert_into_graph_db(dictionary_in):
    driver = GraphDatabase.driver("bolt://localhost", auth=basic_auth("neo4j", "root"))
    session = driver.session()
    insert_query = "CREATE (word:Word {value:{a}, count:{b}}) RETURN word;"
    data = [["Jim","Mike"],["Jim","Billy"],["Anna","Jim"], ["Anna","Mike"],["Sally","Anna"],["Joe","Sally"], ["Joe","Bob"],["Bob","Sally"]]

    session.run(insert_query, parameters={"pairs": data})
    return 1
"""

# it will count the number of relation exist between 2 nodes
# from input-token-list pick adjecent nodes
# check both nodes are present 
# if not create a CO_OCCURENCE relation after adding the node
#   do nothing
# else
#   call check_for_relation for check for a CO_OCCURENCE relation
def count_bigram_relatedness(cleaned_tocken, dictinary_from_tokens):
    list_position = len(cleaned_tocken)
    list_position = list_position-1
    print(cleaned_tocken)
    for i in range(list_position):
        node1 = cleaned_tocken[i]
        print(node1)
        node2 = cleaned_tocken[i+1]
        print(node2)
        check_for_relation(node1, node2)
        #list_position = list_position + 1

    return 1


#   if CO_OCCURENCE 
#        increment the count
#   else 
#        create a new CO_OCCURENCE relation between those nodes
#        initialize the count to 1
def check_for_relation(node1, node2):
    graph = Graph('http://localhost:7474/db/data', user='neo4j', password='root')
    #neo4j_transaction = graph.begin()

    #******************** TYPE ONE METHOD ***************************#
    #neo4j_transaction.append(" MATCH (n:Word)-[:CO_OCCURENCED]->(m:Word) RETURN n", n=node1, m=node2)

    #************************ TYPE TWO NEO$J ************************#
    selector = NodeSelector(graph)
    selected1 = selector.select("Word", value=node1)
    selected2 = selector.select("Word", value=node2)

    #********************* TYPE 3 NEO$j ****************************#
    #selected1 = Node("Word",value=node1)
    #selected2 = Node("Word",value=node2)
    #selected1 = graph.run("MATCH (a:Word) WHERE a.value={b} RETURN a.value", b=node1)
    #selected2 = graph.run("MATCH (a:Word) WHERE a.value={b} RETURN a.value", b=node2)
    print(selected1)
    print(selected2)
    #print(dir(selected1.values))
    #ab = Relationship(selected1, "CO_OCCURENCED", selected2, bidirectional=True)
    #print(ab)
    #neo4j_transaction.commit()
    #result = neo4j_transaction.commit()
    #result = graph.exists(ab)

    #******************* TYPE 4 **********************************#
    res = graph.match(start_node=selected1, end_node=selected2)
    print(res)

    #print(result)

    if not res:
        print("HAI")
        neo4j_transaction = graph.begin()

        #***************************** TYPE ONE INSERT **************#
        #neo4j_transaction.append(" CREATE (n:Word{value:{a}})-[r:CO_OCCURENCED]->(m:Word{value:{b}}) RETURN r", n=node1, m=node2, a=node1, b=node2)


        #***************************** TYPE 3 INSERT *****************#
        """selected1 = Node("Word",value=node1)
        selected2 = Node("Word",value=node2)
        ab = Relationship(selected1, "CO_OCCURENCED", selected2, bidirectional=True)
        neo4j_transaction.create(ab)
        neo4j_transaction.commit()
        result = graph.exists(ab)
        print(result)"""
        #result = neo4j_transaction.commit()

    return 1
