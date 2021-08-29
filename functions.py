from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
import re
import time
import pandas as pd

import nltk
#nltk.download('stopwords')
#nltk.download('wordnet')

############################ ----------- Functions for document processing
# ----------- (preprocessing, tokenizing, lemming, stemming, postprocessing...) ----------- ############################

#remove stop words within a list
def remove_stop_word(list_, stopwords):
    return [c for c in list_ if not c in stopwords]

#lemmatization
def lemmatize_list(List_, Lemmatizer):
    d=[]
    for c in List_:
        if c[-2:]!='ss':
            d = d + [Lemmatizer.lemmatize(c)]
        else:
            d = d + [c]
    return d

#post processing functions
def single_(x):
    y=x
    if x!=[]:
        y = [c.rstrip('.-/') for c in x]
        y = [c.lstrip('!$*-&#+0123456789') for c in y]
        y = [c for c in y if len(c)>1 or c in ['c', 'd', 'r', 'o']]

    if len(y)==0: y=[]
    return y

def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

def remove_hex(x): #removes decimal or hexadecimal or digit from list
    y=x
    if x!=[]:
        y = [c for c in y if c in ['c', 'd', 'r', 'o'] or not is_hex(c) or re.fullmatch(r'[a-z]+', c)]
    return y

def remove_digits_and_non_alphachar(x):
    y=x
    if x!=[]:
        y = [c for c in y if not (re.fullmatch(r'[\W\dx]+', c) or re.fullmatch(r'[a-z]+\++[a-z]', c))]
    return y

#stemming
def stemming_list(List_, stemmer):
    return [stemmer.stem(c) for c in List_]



############################ ----------- CountVectorizer Functions ----------- ############################

#preprocessing of the document includes just lowerization
def my_preprocessor(doc):
    return(doc.lower().replace('_', '-'))

#tokenization, stop words removing, lemmatization and stemming
def my_tokenizer(s):
    #tokenization
    tokenizer0 = nltk.RegexpTokenizer( r'[\da-zA-Z\+#\&]+') #words of 2 letters of more. Exclude single letters, and non letters characters
    Step1 = tokenizer0.tokenize(s)
    #Stop words
    st_w=nltk.corpus.stopwords.words('english') #list of stop words in English that we want to remove
    st_w.remove('o')
    st_w.remove('d')
    Step2 = remove_stop_word(Step1, st_w)
    #lemmatization
    Lemm = nltk.stem.WordNetLemmatizer()
    Step3 = lemmatize_list(Step2, Lemm)
    #postprocessing
    Step4 = remove_digits_and_non_alphachar(remove_hex(single_(Step3)))  #postprocessing
    #stemming
    PS = nltk.stem.PorterStemmer()
    Step5 = stemming_list(Step4, PS)
    #post processing stop words remove_digits_and_non_alphachar
    list_stop_words_2 = ['use', 'get', 'way', 'differ', 'creat', 'valu', 'make', 'data', 'chang', 'best', 'work', 'run', 'possibl',
       'variabl', 'without', 'one', 'find', 'check', 'line', 'name', 'number', 'text', 'multipl', 'call', 'convert',
       'element', 'implement', 'return', 'two', 'user', 'mean', 'remov', 'page', 'good', 'project', 'view', 'write',
       'new', 'like', 'size', 'column', 'control', 'default']
    Step6 = remove_stop_word(Step5, list_stop_words_2)
    return Step6

def tokenize_question(input_string):
    #Vectorization
    CVect = CountVectorizer(preprocessor = my_preprocessor, tokenizer = my_tokenizer, stop_words = None, token_pattern = None)

    try:
        CVect.fit_transform([input_string])
    except Exception as err:
        return str(err)
    else:
        #output as a list of cleaned stemmed words
        return CVect.get_feature_names()

def create_dummy_1R_matrix(input_list_tags, trained_list_words): #create input for models
    mlb0 = MultiLabelBinarizer()
    mlb0.fit([trained_list_words])
    df_input_for_model = pd.DataFrame(mlb0.transform([input_list_tags]))
    df_input_for_model.columns = trained_list_words
    return df_input_for_model

#function which returns the column name each time value is 1 in row (input list)
def get_column_name(list01, list_columns):
    list_indx = [i for i, e in enumerate(list01) if e == 1]
    return [list_columns[i] for i in  list_indx]

############################ ----------- unsupervised approach only ----------- ############################

#function which select best x topics for new user input, and then retrieve best words (tags) associated to the selected topics
def retrieve_tags_from_user_input(model, input_question_tokenized, trained_list_words, nb_topics = 1, nb_words = 3):

    Matrix_1row_question_topics = model.transform(input_question_tokenized) # 1 row doc-topics matrix
    df_userquestion_topics = pd.DataFrame(Matrix_1row_question_topics) #doc_topics matrix

    df_topic_words = pd.DataFrame(model.components_) #topic_words matrix
    print('topic words shape', df_topic_words.shape)
    print('doc topics shape', df_userquestion_topics.shape)
    #indices of best topics to consider for the document (question) index
    best_topics_ix = df_userquestion_topics.loc[0,:].argsort()[:-1-nb_topics:-1].values.tolist() #nb_topics top topics

    Tags_=[]
    for best_topic in best_topics_ix:
        print('****** LOOP ****** ')

        Tag_indices = df_topic_words.loc[best_topic,:].argsort()[:-1-nb_words:-1].values.tolist() #nb_words top words

        print ('best_topic:', best_topic, '_ tag_indices: ', Tag_indices,'__ type: ', type(Tag_indices) )
        Tags_ = Tags_ + [trained_list_words[tag] for tag in Tag_indices]

    return Tags_ #returns a list of best tags

############################ ----------- Create_tags final Function ----------- ############################

def create_tags(input_user, model, words_list_for_training, tag_list, unsupervised = False):
    #Step1 _ preprocessing, tokenizing, post processing
    st = time.time()
    input_tokenized = tokenize_question(input_user)
    if isinstance(input_tokenized, str):
        print('Error at step 1: ' + input_tokenized)
        return "ERR1", input_tokenized, True
    else:
        print('step1 completed _ tokenized input:', input_tokenized)

    #Step2 _ here, we create an entry which is actually a tf matrix for one question,
            # based on vocabulary list (words list) used for training
    input_dummy = create_dummy_1R_matrix(input_tokenized, words_list_for_training)
    try:
        print('step2 completed _ tokenized dummy input:\n', input_dummy[input_tokenized], '_ shape:', input_dummy.shape)
    except Exception as err:
        return "ERR2", str(err), True #True means error

    try:
        if unsupervised == False: #semi supervised or fully supervised model -> we use a classifier prediction
            #Step3a _ we use the model to make a prediction on the input computed at step 2
            output_dummy_Tags = model.predict(input_dummy)[0].tolist()
            print('step3 completed _ dummy tags output: size = 1 x', len(output_dummy_Tags))

            #Step4 _ we retrieve the tags from the model 1R vector output
            output_tags = get_column_name(output_dummy_Tags, tag_list)
            print('step4 completed _ output tags:', output_tags)
        else:
            #Step3b _ we use directly the dimension reduction algorithm to extract main words (tags)
            output_tags = retrieve_tags_from_user_input(model, input_dummy, words_list_for_training, nb_topics = 1, nb_words = 3)
            print('step3b completed _ output tags:', output_tags)

        te = (time.time() - st)/60
        print('time elapsed: {0:.2f} min.'.format(te))
        return output_tags, te, False #False means no error

    except Exception as err:
        return "UNKNOWN_ERROR", str(err), True #True means there is an error
