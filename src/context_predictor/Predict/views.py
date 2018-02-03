from django.shortcuts import render
from nltk.tokenize import word_tokenize
import string

# Create your views here.
def predict_context(request):
    sentence = "Cat climbed the tree. Dog Climbed the tree."
    tokens = word_tokenize(sentence)
    # convert to lower case
    tokens_lower = [w.lower() for w in tokens]
    # remove punctuation from each word
    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table) for w in tokens_lower]
    
    output = stripped
    return render(request, 'Predict/post_list.html', {'output' : output})