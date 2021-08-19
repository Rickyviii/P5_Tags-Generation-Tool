from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer
import nltk
import os
nltk.download('stopwords')
nltk.download('wordnet')
from flask import Flask, render_template, url_for, request
import pickle
import functions

app = Flask(__name__) #Flask application instance

length_question = 150


#import of various tag models
ThisDir = os.path.dirname(os.path.abspath(__file__))

#f  = open(os.path.join(ThisDir, "models\stovf_model.pkl") ,"rb")
#f2 = open(os.path.join(ThisDir, "Files\nmf_model.pkl")   ,"rb")

#with open('D:\OC\P5\P5_Flask_Tags Creation\Files\stovf_model.pkl', 'rb') as f:
with open(os.path.join(ThisDir, r"models\stovf_model.pkl") ,"rb") as f:
    stovf_tag_model = pickle.load(f)

with open(os.path.join(ThisDir, r"models\nmf_model.pkl"), "rb") as f2:
    nmf_tag_model   = pickle.load(f2)


@app.route('/', methods=['POST', 'GET']) #app.route transform the output of the function into an HTTP response when the URL is / (root of the web site)
def question():
    if request.method == 'POST':
        form_data = request.form
        #print(form_data)
        input_user = list(form_data.values())[0] #question from the input_user (string)

        #ST_OVF output calculation

        input_tokenized = functions.tokenize_question(input_user)
        Tags_stovf = stovf_tag_model.predict(input_tokenized)


        return render_template('main_template.html', len_qu = length_question, output_data = input_user)
    else:
        return render_template('main_template.html', len_qu = length_question, output_data = "GET")
