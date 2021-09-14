import os
from flask import Flask, render_template, url_for, request, jsonify
from flask_jsglue import JSGlue

import functions, mymodule

import pandas as pd
import time

from time import sleep
from rq import Queue
from rq.job import Job
from rq.registry import FailedJobRegistry
from rq.registry import StartedJobRegistry
from rq.registry import FinishedJobRegistry

app = Flask(__name__) #Flask application instance
jsGlue=JSGlue(app)

from worker import conn
q = Queue(connection=conn)
#if __name__ == '__main__':
#    app.run()

print()
print()

max_length_question = 150
#import of tag models & csv files
ModelDir, CSVDir = r"files/models", r"files/CSV files"

lda_tag_model, nmf_tag_model, stovf_tag_model, list_words, list_tags_nmf, list_tags_stovf, CVect, transformer, list_vocab = functions.import_files(ModelDir, CSVDir)

#main HTML page generation
@app.route('/', methods=['GET', 'POST']) #app.route transform the output of the function into an HTTP response when the URL is / (root of the web site)
def question():
    ERR = False
    return render_template('main_template.html', len_qu = max_length_question,
                                input_data = 'your question', output_data = "", input_model="", ERR = ERR)

@app.route('/createjob', methods=['POST'])
def create_job():
    form_data = request.form
    #question from the input_user (string)  + model selected by user
    input_user, tag_model_string = list(form_data.values())[0], list(form_data.values())[1]
    print(input_user, tag_model_string)
    tag_model, list_tags, unsup, errm, tfidf = functions.user_select(form_data, lda_tag_model, nmf_tag_model, stovf_tag_model,
                                                                list_tags_nmf, list_tags_stovf )
    job = q.enqueue(launch_task, input_user, tag_model, CVect, transformer, list_words, list_tags,
                                    list_vocab, unsup, tfidf, job_timeout='7m') #timeout fixed at 7 minutes.

    jobID = job.get_id()
    responseObject = {"status": "success",
                      "data": { "model": tag_model_string,
                                "job_ID": jobID
                              }
                     }
    print (jsonify(responseObject))
    print (responseObject)
    return(jsonify(responseObject))

@app.route('/job', methods=['GET'])
def checkstatus():
    jid= request.args.get('jid')
    print('job id: ' + jid)
    job = q.fetch_job(jid)
    # If such a job exists, return its info

    if (job):
        print('job found')
        jstat = job.get_status()
        print(jstat)
        if jstat == "finished":
            print(job.result)
            output_to_user = job.result
            responseObject = {
                "success": "OK",
                "data": {
                    "jobID": jid,
                    "jobStatus": jstat,
                    "list_tags_or_errmsg": output_to_user[0],
                    "te":  output_to_user[1],
                    "iserror" : output_to_user[2]
                }
            }
        else :
            #queued, started, deferred, finished, stopped, scheduled, canceled and failed
            responseObject = {"data": {"jobStatus": jstat}}
    else:
        responseObject = {"data": {"jobStatus": "no job found!"}}
    return responseObject

def launch_task(input_user, tag_model, CVect, transformer, list_words, list_tags, list_vocab, unsup, tfidf):
    # Start the tag creation as a background task in the Redis queue
    st=time.time()
    print('/////////////////////////////////////////////////','starting job at {0:.2f}'.format(st),'/////////////////////////////////////////////////////')
    list_tags_output_ = functions.create_tags(input_user, tag_model, CVect, transformer, list_words, list_tags, list_vocab, unsup, tfidf)

    print('FUNCTION create_tags _ FINISHED')

    if list_tags_output_[2] == True:  #ERROR
        ERR = list_tags_output_[0]
        ERR_MSG = list_tags_output_[1]
        if ERR=="ERR1":
            err_msg ="The question does not contain any word specific enough, or the vocabulary is unknown.\nPlease rephrase your question."
        elif ERR=="ERR2":
            err_msg ="Vocabulary unknown. Please enter a valid question."
        elif ERR=="ERR 3A":
            err_msg = "Error at step 3A: " + str(ERR_MSG) + "'_ Please try again."
        elif ERR=="ERR 3B":
            err_msg = "Error at step 3B: " + str(ERR_MSG) + "'_ Please try again."
        elif ERR=="ERR 4A":
            err_msg = "Error at step 4A: " + str(ERR_MSG) + "'_ Please try again."
        else:
            err_msg = "Unknown error: '" + str(ERR_MSG) + "'_ Please try again."
        output_to_user = [err_msg, '', True]

        print()
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$                       TAGS CREATION FINISHED _ OUTPUT ERROR:                       $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print(ERR, ERR_MSG)
        print(err_msg)
    else: #NO ERROR
        output_to_user1 = "    " + "    ".join(['<'+c+'>' for c in list_tags_output_[0]]) #list of tags

        output_to_user2 = "{0:.2f} min.".format(list_tags_output_[1])                     #time elapsed
        if list_tags_output_[1]<1:
            output_to_user2 = "{0:.1f}s".format(60*list_tags_output_[1])


        output_to_user  = [output_to_user1, output_to_user2, False]
        print()
        print('TAGS CREATION _ SUCCESS. FINAL OUTPUT = {0}'.format(output_to_user))
        print('//////////////////////////////////////////////////////////////////////////////////////////////////////')

    return output_to_user
