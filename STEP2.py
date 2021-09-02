import os
from flask import Flask, render_template, url_for, request, jsonify
from flask_jsglue import JSGlue

#from flask_executor import Executor
import joblib
import functions
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
#if __name__ == '__main__':
#    app.run()

print()
print()

max_length_question = 150
#import of tag models & csv files
ModelDir, CSVDir = r"files/models", r"files/CSV files"
lda_tag_model, nmf_tag_model, stovf_tag_model, list_words, list_tags_nmf, list_tags_stovf = functions.import_files(ModelDir, CSVDir)

#main HTML page generation
@app.route('/', methods=['GET', 'POST']) #app.route transform the output of the function into an HTTP response when the URL is / (root of the web site)
def question():
    ERR = False
    return render_template('main_template2.html', len_qu = max_length_question,
                                input_data = 'your question', output_data = "", input_model="", ERR = ERR)

@app.route('/createjob', methods=['POST'])
def create_job():
    form_data = request.form
    #question from the input_user (string)  + model selected by user
    input_user, tag_model = list(form_data.values())[0], list(form_data.values())[1]
    print(input_user, tag_model)
    #job = q.enqueue(launch_task, input_user, tag_model, list_words, list_tags, unsup)
    #jobID = job.get_id()
    jobID = "ae88908j"
    responseObject = {"status": "success",
                      "data": { "model": tag_model,
                                "job_ID": jobID
                              }
                     }
    print (jsonify(responseObject))
    print (responseObject)
    return(jsonify(responseObject))

@app.route('/job', methods=['GET'])
def checkstatus():
    jid= request.args.get('jid')
    i= request.args.get('i')
    print(type(i))
    output_tags = [['list', 'of', 'tags'], 5.30, False]
    job=False
    #job = q.fetch_job(jid)
    # If such a job exists, return its info
    sleep(1)
    job=True
    job_finished=False
    jstat = 'ongoing'
    print(i)
    if (i=='3'):
        job_finished = True
        jstat = "finished" #job.get_status(),
    print(jstat)
    if (job==True): #if (job):
        if jstat == "finished":
            responseObject = {
                "success": "OK",
                "data": {
                    "jobID": jid,
                    "jobStatus": jstat,
                    "list_tags": output_tags[0],
                    "te":  output_tags[1],
                    "err0" : output_tags[2]
                }
            }
        else:
            responseObject = {
                "data": {
                    "jobStatus": jstat
                }
            }
    else:
        responseObject = {
            "data": {
                "jobStatus": "no job found!"
            }
        }
    return responseObject
