import sys
import pandas as pd
from sqlalchemy import create_engine


def load_data(messages_filepath, categories_filepath):
    '''
    INPUT - messages_filepath : messages filepath, categories_filepath : categories filepath  
    OUTPUT - df : dataframe combination of messages and categories
    '''
    
    
    messages = pd.read_csv(messages_filepath)
    # load categories dataset
    categories = pd.read_csv(categories_filepath)
    categories_id = categories.id
    categories_headers = [x.split('-')[0] for x in categories.categories[0].split(';')]

    # create a dataframe of the 36 individual category columns
    categories = categories.categories.str.split(';',expand=True)
    categories.columns = categories_headers

    for column in categories:
        # set each value to be the last character of the string
        categories[column] = [x[-1:] for x in categories[column]]

        # convert column from string to numeric
        categories[column] = categories[column].astype(int)

    categories = categories.join(categories_id)


    # concatenate the original dataframe with the new `categories` dataframe
    df = pd.merge(messages,categories)
    return df


def clean_data(df):
    '''
    Return dataframe with clean and no duplicates dataset
    
    INPUT - df : input dataframe
    OUTPUT - df : cleaned dataframe
    '''
    
    df['message'] = df['message'].str.lower()
    df = df.drop_duplicates()
    return df


def save_data(df, database_filename):
    '''
    This function save dataframe into sqlite db
    
    INPUT - df : input dataframe, database_filename : db filename
    '''
    
    engine = create_engine('sqlite:///{}'.format(database_filename))
    df.to_sql('raw_data', engine, index=False, if_exists='replace')  


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()