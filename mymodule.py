import nltk, re

#functions

RegExp = r'[\da-zA-Z\+#\&]+'
tokenizer0 = nltk.RegexpTokenizer(RegExp)

#list of stop words in English that we want to remove
st_w=nltk.corpus.stopwords.words('english')
st_w.remove('o')
st_w.remove('d')

#remove stop words within a list
def remove_stop_word(list_, stopwords):
    return [c for c in list_ if not c in stopwords]

#lemmatization
Lemm = nltk.stem.WordNetLemmatizer()
def lemmatize_list(List_):
    d=[]
    for c in List_:
        if c[-2:]!='ss':
            d = d + [Lemm.lemmatize(c)]
        else:
            d = d + [c]
    return d

#remove hexa, non digits + strip
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

#stemming function
PS = nltk.stem.PorterStemmer()
def stemming_list(List_):
    return [PS.stem(c) for c in List_]

#stopwords bis
st2 = ['use', 'get', 'way', 'differ', 'creat', 'valu', 'make', 'data', 'chang', 'best', 'work', 'run', 'possibl',
       'variabl', 'without', 'one', 'find', 'check', 'line', 'name', 'number', 'text', 'multipl', 'call', 'convert',
       'element', 'implement', 'return', 'two', 'user', 'mean', 'remov', 'page', 'good', 'project', 'view', 'write',
       'new', 'like', 'size', 'column', 'control', 'default']



#preprocessing of the document includes just lowerization
def my_preprocessor(doc):
    return(doc.lower().replace('_', '-'))

def my_tokenizer(s):
    Step1 = tokenizer0.tokenize(s)
    Step2 = remove_stop_word(Step1, st_w)
    Step3 = lemmatize_list(Step2)
    Step4 = remove_digits_and_non_alphachar(remove_hex(single_(Step3)))  #postprocessing
    Step5 = stemming_list(Step4)
    Step6 = remove_stop_word(Step5, st2)
    return Step6
