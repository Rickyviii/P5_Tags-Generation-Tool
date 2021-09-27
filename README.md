# P5_Tags-Generation-Tool

 This is the Code repository for Project 5 of Open Classroom 'Machine Learning' Path : 'Tag extraction'

The project consists in developing various 'tag generation' tools using classic text extraction and text selection technique methods: 
- bag of words, tf and tf idf representations, LDA and NMF algorithms... 
- classification models

As part of the project, an end point is provided, hosted on Heroku, using Flask framework and gunicorn web server.
Please note that the html and jquery/javascript code include the generation of background tasks, which are necessary when the text treatment tasks take more than 30s to compute. 
It uses Redis and RQ servers (compatible with heroku).

URL : 
      https://oc-p5-tags.herokuapp.com/

The PDF file is the powerpoint presentation used for the final project's oral defense.
