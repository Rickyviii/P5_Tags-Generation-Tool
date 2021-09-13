#from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
#from sklearn.preprocessing import MultiLabelBinarizer

import time
import pandas as pd
import os, joblib
import warnings

#import nltk
#nltk.download('stopwords')
#nltk.download('wordnet')

#################### files import ###############################
def import_files(ModelDir, CSVDir):
    #import of various tag models
    with open(os.path.join(ModelDir, r"lda_unsupervised_model.pkl"), "rb")         as f: lda_tag_model   = joblib.load(f)
    with open(os.path.join(ModelDir, r"nmf_LSVC_semi_supervised_model.pkl"), "rb") as f: nmf_tag_model   = joblib.load(f)
    with open(os.path.join(ModelDir, r"stovf_LSVC_supervised_model.pkl"), "rb")    as f: stovf_tag_model = joblib.load(f)
    with open(os.path.join(ModelDir, r"transformer.pkl"), "rb")                    as f: transformer     = joblib.load(f)
    with open(os.path.join(ModelDir, r"CVect.pkl"), "rb")                          as f: CVect           = joblib.load(f)

    #import of list of words used to train the models
    list_words      = pd.read_csv(os.path.join(CSVDir, r'words.csv'),           keep_default_na=False).word.tolist()
    list_vocab      = pd.read_csv(os.path.join(CSVDir, r'vocab.csv'),           keep_default_na=False).Vocabulary.tolist()
    #import of list of tags corresponding to each tag models
    list_tags_nmf   = pd.read_csv(os.path.join(CSVDir, r'NMF0_Tag_list_2.csv'), keep_default_na=False).Tags.tolist()
    list_tags_stovf = pd.read_csv(os.path.join(CSVDir, r'St_OVF_Tag_list.csv'), keep_default_na=False).Tags.tolist()
    return lda_tag_model, nmf_tag_model, stovf_tag_model, list_words, list_tags_nmf, list_tags_stovf, CVect, transformer, list_vocab

##################### INPUT USER ###############################
def user_select(form_data, lda_tag_model, nmf_tag_model, stovf_tag_model, list_tags_nmf, list_tags_stovf):
    input_user, model = list(form_data.values())[0], list(form_data.values())[1]
    err = False
    tfidf = False
    if model in ['LDA', 'NMF', 'STOVF']:
        if model == "LDA":
            tag_model, list_tags, unsup = lda_tag_model, '', True
        elif model == "NMF":
            tag_model, list_tags, unsup, tfidf = nmf_tag_model, list_tags_nmf, False, True
        elif model == "STOVF":
            tag_model, list_tags, unsup = stovf_tag_model, list_tags_stovf, False
    else:
        tag_model, list_tags, unsup, err = None, [], False, True, False
    return tag_model, list_tags, unsup, err, tfidf

############################ ----------- Functions for document processing
# ----------- (preprocessing, tokenizing, lemming, stemming, postprocessing...) ----------- ############################

############################ ----------- CountVectorizer Functions ----------- ############################

#preprocessing of the document includes just lowerization

#function which uses CVect or transformer to transform a string into a tf or tfidf Matrix
#CVect, imported by joblib, uses my_preprocessor and my_tokenizer functions
def tokenize_question(input_string, CountVect_, Transformer_, tfidf = False):
    try:
        tf = CountVect_.transform([input_string])
        if tfidf!=True:
            return tf
        else:
            tfidf = Transformer_.transform(tf)
            return tfidf

    except Exception as err:
        return str(err)


#function which returns the column name each time value is 1 in row (input list)
def get_column_name(list01, list_columns):
    list_indx = [i for i, e in enumerate(list01) if e == 1]
    return [list_columns[i] for i in  list_indx]

#Reverse stemming
#Return the shortest word in a vocabulary list that matches the stem of the word
def find_word_in_vocab(list_of_stemmed_words, list_vocab):
    df_Vocab = pd.DataFrame()
    df_Vocab['Vocab'] = list_vocab
    Y = []

    for stem_word in list_of_stemmed_words:
        df_Vocab['Vocab_stemmed'] = df_Vocab['Vocab'].str[0:len(stem_word)]
        df_Vocab['len'] = df_Vocab['Vocab'].str.len()
        R = df_Vocab.query("Vocab_stemmed == '" + stem_word + "'")

        if R.shape[0]==0:
            Y = Y + [stem_word]
        else:
            Y = Y + [R.sort_values(by='len').iloc[0,0]]
    return Y

############################ ----------- unsupervised approach only ----------- ############################

#function which select best x topics for new user input, and then retrieve best words (tags) associated to the selected topics
def retrieve_tags_from_user_input(model, input_question_tokenized, trained_list_words, nb_topics, nb_words):
    print('STARTING STEP3B "retrieve_tags_from_user_input"')
    Matrix_1row_question_topics = model.transform(input_question_tokenized) # 1 row doc-topics matrix
    df_userquestion_topics      = pd.DataFrame(Matrix_1row_question_topics) #doc_topics matrix
    df_topic_words = pd.DataFrame(model.components_) #topic_words matrix
    print('topic words shape: ', df_topic_words.shape)
    print('doc topics shape: ', df_userquestion_topics.shape)
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

def create_tags(input_user, model,  CVect_, transformer_, words_list_for_training, tag_list,
                                                    Vocab = [], unsupervised = False, tfidf = False):
    #///////////////// Step 1 _ preprocessing, tokenizing, post processing
    st = time.time()
    tf_tfidf = tokenize_question(input_user, CVect_, transformer_, tfidf) #transform in tf or tfidf vector
    if isinstance(tf_tfidf, str):
        print('ERROR AT STEP 1: ' + tf_tfidf)
        return "ERR1", tf_tfidf, True
    else:
        M = pd.DataFrame(tf_tfidf.toarray().transpose(), columns=['data'])
        if M.query('data!=0').shape[0] >0:
            input_tokenized = [CVect_.get_feature_names()[c] for c in M.query('data!=0').index]
            print('STEP 1 COMPLETED _ tokenized input:', input_tokenized)
        else:
            print('ERROR AT STEP 1: tokenized input is empty')
            return "ERR1", "The vocabulary used in the question is unknown, or it is too common. Please rephrase your question.", True
    #///////////////// Step 2 _ here, we create an entry which is actually a tf matrix for one question,
            # based on vocabulary list (words list) used for training

    if unsupervised == False: #semi supervised or fully supervised model -> we use a classifier prediction
        #///////////////// Step 2A _ we use the model to make a prediction on the input computed at step 2
        try:
            output_dummy_Tags = model.predict(tf_tfidf)[0].tolist()
            print('STEP 2A COMPLETED _ dummy tags output: size = 1 x', len(output_dummy_Tags))
            #return output_dummy_Tags,"{0:.2f} s".format((time.time() - st)/60), False
        except Exception as err:
            print('ERROR AT STEP 2A: ' + str(err))
            return "ERR 2A", str(err), True #True means error

        #///////////////// Step 3a _ We retrieve the tags from the model 1R vector output
        try:
            output_tags = get_column_name(output_dummy_Tags, tag_list)
            print('STEP 3A COMPLETED _ output tags:', output_tags)
        except Exception as err:
            print('ERROR AT STEP 3A: ' + str(err))
            return "ERR 3A", str(err), True #True means error
    else: # Unsupervised case
        try:
            #///////////////// Step 2B _ we use directly the dimension reduction algorithm to extract main words (tags)
            output_tags = retrieve_tags_from_user_input(model, tf_tfidf, words_list_for_training, nb_topics = 1, nb_words = 3)
            #reverse stemming
            output_tags = find_word_in_vocab(output_tags, Vocab)
            print('STEP 2B COMPLETED _ output tags:', output_tags)
        except Exception as err:
            print('ERROR AT STEP 2B: ' + str(err))
            return "ERR 2B", str(err), True #True means error

    te = (time.time() - st)/60
    print('TIME ELAPSED: {0:.2f} min.'.format(te))
    return output_tags, te, False #False means no error
