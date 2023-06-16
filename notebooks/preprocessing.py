# Function to create the updated word list which also contains all unique
# words from ParlaMint.

import os
import pandas as pd
from typing import List
from cleantext import clean
from nltk.tokenize import word_tokenize, sent_tokenize

clean_func = lambda x: clean(x,
    fix_unicode=True,              
    to_ascii=False,                
    lower=True,
    no_line_breaks=True,           
    no_urls=True,                 
    no_emails=True,              
    no_phone_numbers=True,         
    no_numbers=True,              
    no_digits=False,              
    no_currency_symbols=True,     
    no_punct=True,               
    replace_with_punct="",        
    replace_with_url="",
    replace_with_email="",
    replace_with_phone_number="",
    replace_with_number="",
    replace_with_currency_symbol="",
    lang="nl"
)

def update_word_list_with_parlamint(parlamint_dataframe_path: str, original_word_list_path: str, output_path: str):

	parlamint = pd.read_csv(parlamint_dataframe_path)
	parlamint['cleaned_text'].fillna(' ', inplace=True)
	# get unique words for each file, this takes a few mintues
	parlamint_words = parlamint['cleaned_text'].apply(lambda x: set(word_tokenize(x))).tolist()
	# build the complete set of all documents, make lowercase as well
	all_parlamint_words = set(word.strip().lower() for document in parlamint_words for word in document)
	# Load in the original word list
	with open(original_word_list_path, 'r') as f:
	    all_dutch_words = set([item.strip().lower() for item in f.readlines() if len(item.strip()) > 1])
	all_dutch_words_no_numbers = set([item for item in all_dutch_words if not any(char.isdigit() for char in item)])
	dutch_wordlist = set(all_dutch_words_no_numbers)
	parlamint_wordlist = set(item for item in all_unique_words if len(item) > 1 and not any(char.isdigit() for char in item))
	# Now merge the two word lists
	updated_wordlist = dutch_wordlist | parlamint_wordlist
	# Save it to a file
	with open(output_path, 'w') as f:
	    for item in updated_wordlist:
	        f.write(item+'\n')

def preprocess(input_string: str, clean_input: bool = True) -> List[str]:
    # perform normalization and tokenization
    if clean_input:
        input_string = clean_func(input_string)
    tokenized_text = word_tokenize(input_string)
    return tokenized_text

def merge_woogle_dumps_and_sanitize(dump_root_folder: str, output_dataframe_path: str):
	text = pd.read_csv(os.path.join(dump_root_folder, 'woo_bodytext.csv.gz')).set_index('foi_documentId')
	documents = pd.read_csv(os.path.join(dump_root_folder, 'woo_documents.csv.gz')).set_index('dc_identifier')
	dossiers = pd.read_csv(os.path.join(dump_root_folder, 'woo_dossiers.csv.gz')).set_index('dc_identifier')
	dossier_and_document_dataframe = documents.join(dossiers, on='foi_dossierId', rsuffix="_dossier")
	complete_dataframe = text.join(dossier_and_document_dataframe)
	experiment_dataframe = complete_dataframe[['foi_pageNumber', 'foi_bodyText', 'foi_bodyTextOCR',
	                                          'foi_hasOCR', 'foi_fileName', 'dc_type', 'dc_publisher', 'dc_date_year']]
	experiment_dataframe = experiment_dataframe.set_index(experiment_dataframe.index+'.'+experiment_dataframe['foi_pageNumber'].astype(str))
	experiment_dataframe = experiment_dataframe[experiment_dataframe.dc_type == 'besluit']
	experiment_dataframe['foi_bodyText'] = experiment_dataframe['foi_bodyText'].apply(clean_func)
	experiment_dataframe['foi_bodyTextOCR'] = experiment_dataframe['foi_bodyTextOCR'].apply(clean_func)
	experiment_dataframe.to_csv(output_dataframe_path, compression='gzip', index=True)