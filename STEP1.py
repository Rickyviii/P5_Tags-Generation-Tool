import os
from flask import Flask, render_template, url_for, request
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


from worker import conn

app = Flask(__name__) #Flask application instance
q = Queue(connection=conn)
#if __name__ == '__main__':
#    app.run()

print()
print()

max_length_question = 150
#import of tag models & csv files
ModelDir, CSVDir = r"files/models", r"files/CSV files"
lda_tag_model, nmf_tag_model, stovf_tag_model, list_words, list_tags_nmf, list_tags_stovf = functions.import_files(ModelDir, CSVDir)

def launch_task(input_user, tag_model, list_words, list_tags, unsup):
    # Start the tag creation as a background task in the Redis queue
    st=time.time()
    print('/////////////////////////////////////////////////','starting job at {0:.2f}'.format(st),'/////////////////////////////////////////////////////')
    list_tags_output_ = functions.create_tags(input_user, tag_model, list_words, list_tags, unsup)
    print('FUNCTION create_tags _ FINISHED')

    if list_tags_output_[2] == True:  #ERROR
        ERR = list_tags_output_[0]
        ERR_MSG = list_tags_output_[1]
        if ERR=="ERR1":
            err_msg ="The question does not contain any word specific enough. Please rephrase your question."
        elif ERR=="ERR2":
            err_msg ="Vocabulary unknown. Please enter a valid question."
        elif ERR=="ERR 3A":
            err_msg = "Error at step 3A"
        elif ERR=="ERR 3B":
            err_msg = "Error at step 3B"
        elif ERR=="ERR 4A":
            err_msg = "Error at step 4A"
        else:
            err_msg = "Unknown error.: '" + str(ERR_MSG) + "'_ Please try again."
        output_to_user = err_msg

        print()
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$                       TAGS CREATION FINISHED _ OUTPUT ERROR:                       $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print(ERR, ERR_MSG)
        print(err_msg)
        ERR = True
    else: #NO ERROR
        output_to_user1 = "    " + "    ".join(['<'+c+'>' for c in list_tags_output_[0]]) #list of tags
        output_to_user2 = "{0:.2f} min.".format(list_tags_output_[1]) #time elapsed
        output_to_user = [output_to_user1, output_to_user2]
        print()
        print('TAGS CREATION _ FINISHED. FINAL OUTPUT = {0}'.format(output_to_user))
        print('//////////////////////////////////////////////////////////////////////////////////////////////////////')
#        print_registries()

    return output_to_user

#main HTML page generation
@app.route('/', methods=['POST', 'GET']) #app.route transform the output of the function into an HTTP response when the URL is / (root of the web site)
def question():
    ERR = False
    print('*************************************************** CLEARING FAILED JOBS')
    clear_failed_jobs()
    #print_registries()
    if request.method == 'POST':
        form_data = request.form
        input_user, model = list(form_data.values())[0], list(form_data.values())[1] #question from the input_user (string) #model selected by user
        tag_model, list_tags, unsup, errm = functions.user_select(form_data, lda_tag_model, nmf_tag_model, stovf_tag_model,
                                                                    list_tags_nmf, list_tags_stovf )
        if not errm:
            print('*************************************************** JOB ENQUEUING')
            task = q.enqueue(launch_task, args=(input_user, tag_model, list_words, list_tags, unsup), job_timeout=300)
            print('*************************************************** JOB id: {0}'.format(task.id))
            print('*************************************************** JOB status 1: {0}'.format(task.get_status(refresh=True)))

#            print_registries()
        else: ERR = True

        return render_template('main_template.html', len_qu = max_length_question,
                            input_data = input_user, output_data = "blabla", input_model=model, ERR = ERR)
    else: #REQUEST == GET
        return render_template('main_template.html', len_qu = max_length_question,
                                input_data = 'your question', output_data = "", input_model="", ERR = ERR)

def clear_failed_jobs():
    FailedJobRegistry0 = FailedJobRegistry(queue=q)
    for jid in  FailedJobRegistry0.get_job_ids():
        j=Job.fetch(jid, connection=conn)
        j.delete()

def print_registries():
    print('x')
    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$            $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ REGISTRIES $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$            $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
    print('x')
    StartedJobRegistry0 = StartedJobRegistry(queue=q)
    FailedJobRegistry0 = FailedJobRegistry(queue=q)
    FinishedJobRegistry0 = FinishedJobRegistry(queue=q)
    print('IDs in started registry %s'  % StartedJobRegistry0.get_job_ids())
    print('IDs in failed registry %s'   % FailedJobRegistry0.get_job_ids())
    print('IDs in finished registry %s' % FinishedJobRegistry0.get_job_ids())
