import os
from flask import Flask, render_template, url_for, request
#from flask_executor import Executor
import joblib
import functions
import pandas as pd
from time import sleep
from rq import Queue
from worker import conn2

app = Flask(__name__) #Flask application instance

#if __name__ == '__main__':
#    app.run()

print(__name__)
q = Queue(connection=conn2)
def test_task():
    print('long task terminated')
    x = 5
    print(x)
    return x


#main HTML page generation
@app.route('/', methods=['POST', 'GET']) #app.route transform the output of the function into an HTTP response when the URL is / (root of the web site)
def question():
    ERR = False
    print('test_model, about to ask for connection from __main__')
    task = q.enqueue(test_task, job_timeout=300)

    print('task id: {0}'.format(task.id))
    print('task status: {0}'.format(task.get_status(refresh=True)))
    sleep(10)
    print('task status: {0}'.format(task.get_status(refresh=True)))
    #if task.get_status(refresh=True)=='queued':
    #    task = q.reenqueue(test_task, job_timeout=300)
    print('task result: {0}'.format(task.result))
    return render_template('main_template.html', len_qu = 150,
                    input_data = 'your question', output_data = "blabla", input_model="LDA", ERR = ERR)
