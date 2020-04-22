# Disaster Response Pipeline Project


This project is web app to predict if the sentence is belong to any main categories. It is contain ETL and machine learning pipeline process. There are 3 main python script :

1. /app/run.py for running the web app.
2. /data/process_data.py for running the ETL.
3. /models/train_classifier.py for train the data.

### General flow :

1. Load and Clean data, save it into sqlite db.
2. Train the cleaned data (tokenization, TFIDF, Classify) and save it into pickle.
3. Run the webapp.

### Instructions:
1. Run the following commands in the project's root directory to set up your database and model.

    - To run ETL pipeline that cleans data and stores in database
        `python data/process_data.py data/disaster_messages.csv data/disaster_categories.csv data/DisasterResponse.db`
    - To run ML pipeline that trains classifier and saves
        `python models/train_classifier.py data/DisasterResponse.db models/classifier.pkl`

2. Run the following command in the app's directory to run your web app.
    `python run.py`

3. Go to http://0.0.0.0:3001/
