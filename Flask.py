import os
from urllib.request import Request,urlopen
from bs4 import BeautifulSoup
from flask import Flask, render_template, url_for, request, redirect, flash
from spacy.lang.en.stop_words import STOP_WORDS
from spacy.lang.en import English
from sklearn.base import TransformerMixin
import joblib
import string
import spacy
import requests

punctuations = string.punctuation

stop_words = spacy.lang.en.stop_words.STOP_WORDS

parser = English()

def spacy_tokenizer(sentence):
    # Creating our token object, which is used to create documents with linguistic annotations.
    mytokens = parser(sentence)

    # Lemmatizing each token and converting each token into lowercase
    mytokens = [ word.lemma_.lower().strip() if word.lemma_ != "-PRON-" else word.lower_ for word in mytokens ]

    # Removing stop words
    mytokens = [ word for word in mytokens if word not in stop_words and word not in punctuations ]

    # return a preprocessed list of tokens
    return mytokens

class predictors(TransformerMixin):
    def transform(self, X, **transform_params):
        # Cleaning Text
        return [clean_text(text) for text in X]
    def fit(self, X, y=None, **fit_params):
        return self
    def get_params(self, deep=True):
        return {}

def clean_text(text):
    # Removing spaces and converting text into lowercase
    return text.strip().lower()

class PageSentiment:
    def __init__(self, url, header, predict):
        self.url = url
        self.header = header

        # self.overall = predict[0]

        if predict[0]==1:

            self.overall='FAKE'
        else:

            self.overall='REAL'

        # self.most_polar_sentence = blob.sentences[0]
        # self.least_polar_sentence = blob.sentences[0]
        # self.most_objective_sentence = blob.sentences[0]
        # self.most_subjective_sentence = blob.sentences[0]

        # for sentence in blob.sentences[1:]:
        #     if self.most_polar_sentence.sentiment.polarity < sentence.sentiment.polarity:
        #         self.most_polar_sentence = sentence

        #     if self.least_polar_sentence.sentiment.polarity > sentence.sentiment.polarity:
        #         self.least_polar_sentence = sentence

        #     if self.most_objective_sentence.sentiment.subjectivity > sentence.sentiment.subjectivity:
        #         self.most_objective_sentence = sentence

        #     if self.most_subjective_sentence.sentiment.subjectivity < sentence.sentiment.subjectivity:
        #         self.most_subjective_sentence = sentence



from flask import Flask  , render_template ,url_for, request
app = Flask(__name__) 

    
app.config.update(SECRET_KEY='flaskisawesome')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/results', methods=('POST',))
def results():
    url = request.form.get('url')

    try:
        # fetch page associated with url using requests
        response = requests.get(url)

        if response.status_code != 200:
            raise RuntimeError()

    except:
        # Give error message that this was an invalid url
        flash('Invalid url. Please fix and resubmit.')
        return redirect(url_for('index'))


    # opening here the link

    html = urlopen(url).read()

    # making data scraping from url

    soup = BeautifulSoup(html, 'html.parser')

    # # parse results using BeautifulSoup
    # soup = BeautifulSoup(response.content, 'html.parser')

    if soup.find('h1'):
        header = soup.find('h1').get_text()
    else:
        header = soup.title.get_text()

    # create TextBlob instance
    text = str(soup.get_text())

    model = joblib.load(r'C:\Users\Ali Raza\python projects\FYPWebApp\fyp_model_predict')
    
    predict = model.predict([' '.join([s for s in text.splitlines() if s])])
    # blob = TextBlob(soup.get_text())

    # process TextBlob text analytics results
    page_results = PageSentiment(url, header, predict)

    return render_template('results.html', page_results=page_results)

if __name__ =='__main__':  

    app.run(debug = True)  
