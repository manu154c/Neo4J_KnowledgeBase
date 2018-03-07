""" 

@auther : MANU C
Created : 27/01/18
Last Updated : 2/03/18

"""


from django.shortcuts import render
from nltk.tokenize import word_tokenize
import string
from numpy import *

from py2neo import Graph, Node, Relationship, NodeSelector


# for testing purpose
import pdb
from py2neo import watch

# Main context Predictor Function
def predict_context(request):
    if request.method == "POST":
        #print(request)
        word1 = request.POST['word1']
        word2 = request.POST['word2']
        up_know = request.POST['knowledge']
        input_data = "Cat climbed the tree. Dog Climbed the other tree."
        #file = open("/home/manu154c/Downloads/phd-datasets/datasets/webkb-test-stemmed1.txt","r")
        #input_data = file.read()
        cleaned_tocken = text_cleaning(input_data)
        cleaned_tocken_len = len(cleaned_tocken)
        #print(cleaned_tocken)
        dictinary_from_tokens = create_dictionary(cleaned_tocken)
        count_bigram_relatedness(cleaned_tocken)
        update_word_count_from_dictionary(dictinary_from_tokens)
        liklihood_ratio = calculate_likelihood_ratio(word1, word2, cleaned_tocken_len)
        output = liklihood_ratio
        #output = request
        return render(request, 'Predict/post_list.html', {'output' : output})
    else:
        return render(request, 'Predict/get_request.html')


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

# this function is not used at the moment. direct list is used for node creation
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


def factorial(n): 

    if n < 2: return 1
    return reduce(lambda x, y: x*y, xrange(2, int(n)+1))

def prob(k, n, x):

    k = float(k)
    n = float(n)
    x = float(x)

    #combinations = factorial(n)/(factorial(k)*factorial(n-k))
    binomial = x**k * (1-x)**(n-k)

    return binomial


def calculate_likelihood_ratio(word1, word2, cleaned_tocken_len):
    g = Graph('http://localhost:7474/db/data', user='neo4j', password='root')
    node1 = g.run("MATCH (a:Word) WHERE a.value={b} RETURN a", b=word1)
    list_node1 = list(node1)
    start_node = list_node1[0]['a']
    node2 = g.run("MATCH (a:Word) WHERE a.value={b} RETURN a", b=word2)
    list_node2 = list(node2)
    end_node = list_node2[0]['a']
    relation = g.match(start_node=start_node, rel_type="CO_OCCURENCED", end_node=end_node)
    existing_relation = list(relation)
    print(existing_relation)
    relation_count = existing_relation[0]['count']

    c1 = start_node['word_count']
    c2 = end_node['word_count']
    c12 = relation_count
    N = float(cleaned_tocken_len)

    p = float(c2)/float(N)
    p1 = float(c12)/float(c1)
    p2 = (float(c2)-float(c12))/(float(N)-float(c1))

    a11 = prob(c12, c1, p1)
    if a11 < 0:
        a11 = -a11
    a12 = log10(a11)

    prob_a = float(c2)-float(c12)
    prob_b = float(N)-float(c1)
    prob_c = p2

    b11 = prob(prob_a, prob_b, prob_c)
    if b11 < 0:
        b11 = -b11
    b12 = log10(b11)

    lh2 = float(a12) - float(b12)

    d11 = prob(c12, c1, p)
    if d11 < 0:
        d11 = -d11
    d12 = log10(d11)

    prob_a = float(c2)-float(c12)
    prob_b = float(N)-float(c1)
    prob_c = p

    e11 = prob(prob_a, prob_b, prob_c)
    if e11 < 0:
        e11 = -e11
    e12 = log10(e11)

    lh1 = d12 + e12 - float(lh2)

    #pdb.set_trace()
    

    return 2*lh1


# this function will update the count of each node (the words)
# input is a dictionary {'word' : 'word_count'}
def update_word_count_from_dictionary(dictinary_from_tokens):
    g = Graph('http://localhost:7474/db/data', user='neo4j', password='root')
    for key, value in dictinary_from_tokens.items():
        word = g.run("MATCH (a:Word) WHERE a.value={b} RETURN a", b=key)
        list_word = list(word)
        if len(list_word) > 0:
            node = list_word[0]['a'] # (f0a4f80:Word {value:"cat",word_count:1})
            present_count = node['word_count']
            new_count = present_count + value
            node["word_count"] = new_count # return the updated value
            node.push()

    
    return 1


# it will count the number of relation exist between 2 nodes
# from input-token-list pick adjecent nodes
# check both nodes are present 
# if not create a CO_OCCURENCE relation after adding the node
#   do nothing
# else
#   call check_for_relation for check for a CO_OCCURENCE relation
def count_bigram_relatedness(cleaned_tocken):
    list_position = len(cleaned_tocken)
    list_position = list_position-1
    print(cleaned_tocken)
    for i in range(list_position):
        node1 = cleaned_tocken[i]
        node2 = cleaned_tocken[i+1]
        check_for_relation(node1, node2)

    return 1


#   if CO_OCCURENCE 
#        increment the count
#   else 
#        create a new CO_OCCURENCE relation between those nodes
#        initialize the count to 1
def check_for_relation(node1, node2):
    g = Graph('http://localhost:7474/db/data', user='neo4j', password='root')

    d = g.run("MATCH (a:Word) WHERE a.value={b} RETURN a", b=node1)
    list_d = list(d)
    if len(list_d) > 0:
        d = list_d[0]['a'] # (f0a4f80:Word {value:"cat",word_count:1})
    else:
        neo4j_transaction = g.begin()
        d = Node("Word",value=node1, word_count=1)
        neo4j_transaction.create(d)
        neo4j_transaction.commit()

    e = g.run("MATCH (a:Word) WHERE a.value={b} RETURN a", b=node2)
    list_e = list(e)
    if len(list_e) > 0:
        e = list_e[0]['a'] # (f0a4f80:Word {value:"cat",word_count:1})
    else:
        neo4j_transaction = g.begin()
        e = Node("Word",value=node2, word_count=1)
        neo4j_transaction.create(e)
        neo4j_transaction.commit()


    relations = g.match(start_node=d, rel_type="CO_OCCURENCED", end_node=e)
    existing_relation = list(relations)
    
    if len(existing_relation) == 0:
        print("No Relationship exists")
        neo4j_transaction = g.begin()
        ab = Relationship(d, "CO_OCCURENCED", e, count=1, bidirectional=True)
        neo4j_transaction.create(ab)
        neo4j_transaction.commit()
    else:
        relation_update = existing_relation[0]
        #print(relation_update)
        present_count = relation_update['count']
        #print(present_count)
        new_count = int(present_count) + 1
        #print(new_count)
        #neo4j_transaction = g.begin() # No need of transaction before updating the count
        relation_update["count"] = new_count # return the updated value
        relation_update.push()
        #neo4j_transaction.commit()

    return 1