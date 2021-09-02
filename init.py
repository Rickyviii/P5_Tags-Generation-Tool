import os
from flask import Flask, render_template, url_for, request

import functions
import pandas as pd

app = Flask(__name__) #Flask application instance

max_length_question = 150

#import of various tag models & csv files
ModelDir, CSVDir = r"files/models", r"files/CSV files"
lda_tag_model, nmf_tag_model, stovf_tag_model, list_words, list_tags_nmf, list_tags_stovf = functions.import_files(ModelDir, CSVDir)

#main HTML page generation
@app.route('/', methods=['POST', 'GET']) #app.route transform the output of the function into an HTTP response when the URL is / (root of the web site)
def question():
    ERR = False
    if request.method == 'POST':
        form_data = request.form
        input_user, model = list(form_data.values())[0], list(form_data.values())[1] #question from the input_user (string) #model selected by user
        tag_model, list_tags, unsup, errm = functions.user_select(form_data, lda_tag_model, nmf_tag_model, stovf_tag_model)
        if not errm:
            #computation and output
            list_tags_output_ = functions.create_tags(input_user, tag_model, list_words, list_tags, unsup)
            print('***********************', list_tags_output_,'***********************')
            if list_tags_output_[2] == True:  #ERROR
                ERR = list_tags_output_[0]
                ERR_MSG = list_tags_output_[1]
                if ERR=="ERR1":
                    err_msg ="The question does not contain any word specific enough. Please rephrase your question."
                elif ERR=="ERR2":
                    err_msg ="Vocabulary unknown. Please enter a valid question."
                else:
                    err_msg = "Unknown error.: '" + ERR_MSG + "'_ Please try again."
                output_to_user = err_msg
                ERR = True
            else: #NO ERROR
                output_to_user1 = "    " + "    ".join(['<'+c+'>' for c in list_tags_output_[0]]) #list of tags
                output_to_user2 = "{0:.2f} min.".format(list_tags_output_[1]) #time elapsed
                output_to_user = [output_to_user1, output_to_user2]
        else:
            ERR = True
            output_to_user = "no_model"
        print(ERR)
        print('output', output_to_user)
        return render_template('main_template.html', len_qu = max_length_question,
                                input_data = input_user, output_data = output_to_user, input_model = model, ERR = ERR)

    else: #REQUEST == GET
        return render_template('main_template.html', len_qu = max_length_question,
                                input_data = 'your question', output_data = "", input_model="", ERR = ERR)
