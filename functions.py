from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer
import nltk
nltk.download('stopwords')
nltk.download('wordnet')

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

################################# ----------- CountVectorizer Functions -------------- ############################

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
###################################### --------------------- Tokenize main function ------------------ #################################"""

def tokenize_question(input_string):
    #Vectorization
    CVect = CountVectorizer(preprocessor = my_preprocessor, tokenizer = my_tokenizer, stop_words = None, token_pattern = None)
    CVect.fit_transform(input_string)
    #output as a list of cleaned stemmed words
    return CVect.get_feature_names()
