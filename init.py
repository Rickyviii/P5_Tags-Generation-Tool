import os
from flask import Flask, render_template, url_for, request
import pickle
import functions
import pandas as pd



app = Flask(__name__) #Flask application instance

max_length_question = 150


#import of various tag models
ThisDir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(ThisDir, r"files\models\stovf_model.pkl") ,"rb") as f:
    stovf_tag_model = pickle.load(f)

with open(os.path.join(ThisDir, r"files\models\nmf_model.pkl"),   "rb") as f:
    nmf_tag_model   = pickle.load(f)

#import of list of words used to train the models
list_words      = pd.read_csv(r'files\CSV files\words.csv', keep_default_na=False).word.tolist()
#import of list of tags corresponding to each tag models
list_tags_nmf   = pd.read_csv(r'files\CSV files\NMF0_Tag_list.csv', keep_default_na=False).Tags.tolist()
list_tags_stovf = pd.read_csv(r'files\CSV files\St_OVF_Tag_list.csv', keep_default_na=False).Tags.tolist()

#main HTML page generation
@app.route('/', methods=['POST', 'GET']) #app.route transform the output of the function into an HTTP response when the URL is / (root of the web site)
def question():
    if request.method == 'POST':
        form_data = request.form
        input_user = list(form_data.values())[0] #question from the input_user (string)
        #computation and output
        list_tags_output_ = functions.create_tags(input_user, stovf_tag_model, list_words, list_tags_stovf)

        output_to_user1 = list_tags_output_[0]
        output_to_user2 = "{0:.2f} min.".format(list_tags_output_[1])
        output_to_user = [output_to_user1, output_to_user2]
        return render_template('main_template.html', len_qu = max_length_question, input_data = input_user, output_data = output_to_user)
    else:
        return render_template('main_template.html', len_qu = max_length_question, input_data = 'your question', output_data = "")
