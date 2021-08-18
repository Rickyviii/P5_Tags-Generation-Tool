from flask import Flask, render_template, url_for

app = Flask(__name__) #Flask application instance

@app.route('/') #app.route transform the output of the function into an HTTP response when the URL is / (root of the web site)
def question():
    return render_template('main_template.html')
