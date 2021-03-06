import sys
from sqlalchemy import create_engine
import pandas as pd
import nltk
nltk.download(['punkt', 'wordnet', 'averaged_perceptron_tagger'])

import re
import numpy as np
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

from sklearn.metrics import classification_report
# from sklearn.metrics import multilabel_confusion_matrix
from sklearn.model_selection import GridSearchCV
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from joblib import dump, load


def load_data(database_filepath):
    '''
    INPUT - database filepath 
    OUTPUT - X : text messages from dataframe, Y : categories names from the dataframe, category_names : cat 
    '''
    
    engine = create_engine('sqlite:///{}'.format(database_filepath))
    df = pd.read_sql_table(con=engine,table_name='raw_data')
    X = df['message']
    Y = df.drop(columns=['id','message','original','genre'])
    category_names = Y.columns
    return X,Y,category_names


def tokenize(text):
    '''
    INPUT - text
    OUTPUT - word tokens
    '''
    
    url_regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    detected_urls = re.findall(url_regex, text)
    for url in detected_urls:
        text = text.replace(url, "urlplaceholder")

    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()

    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)

    return clean_tokens


def build_model():
    '''
    Function to generate machine learning pipeline 
    OUTPUT - Pipeline
    '''
    pipeline = Pipeline([
        ('features', FeatureUnion([

            ('text_pipeline', Pipeline([
                ('vect', CountVectorizer(tokenizer=tokenize)),
                ('tfidf', TfidfTransformer())
            ]))
        ])),

        ('clf', MultiOutputClassifier(RandomForestClassifier()))
    ])
    
    parameters = {
    #     'features__text_pipeline__vect__ngram_range': ((1, 1), (1, 2)),
    #     'features__text_pipeline__vect__max_df': (0.5, 0.75, 1.0),
        'features__text_pipeline__vect__max_features': (None, 5000, 10000),
    #     'features__text_pipeline__tfidf__use_idf': (True, False),
        'features__transformer_weights': (
            {'text_pipeline': 1, 'starting_verb': 0.5},
    #         {'text_pipeline': 0.5, 'starting_verb': 1},
    #         {'text_pipeline': 0.8, 'starting_verb': 1},
        )
    }

    cv = GridSearchCV(pipeline, param_grid=parameters,n_jobs=2)
    return cv


def evaluate_model(model, X_test, Y_test, category_names):
    '''
    Generate classification report from the models for each category. 
    Iteration each column and print classification report
    
    INPUT - model : pipeline, X_test : text dataframe, Y_test : array of prediction result, category_names : category name
    '''
    y_pred = model.predict(X_test)
    
    for i in range(0,len(category_names)):
        print(category_names[i], classification_report(y_pred[:,i],Y_test[category_names[i]]))



def save_model(model, model_filepath):
    '''
    Save model into pickle file
    INPUT - model : pipeline, model_filepath : model filepath
    '''

    
    dump(model, model_filepath) 


def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y, category_names = load_data(database_filepath)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
        
        print('Building model...')
        model = build_model()
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test, category_names)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()