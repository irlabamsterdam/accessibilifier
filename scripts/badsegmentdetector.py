import numpy as np
from tqdm import tqdm
from typing import List
from preprocessing import *
from nltk.tokenize import word_tokenize

class BadSegmentDetector:
    def __init__(self, word_list_path: str = '../data/wordlist.txt'):
        # Read in the word list
        with open(word_list_path, 'r') as f:
            all_dutch_words = set([item.strip().lower() for item in f.readlines()])
        # remove any numbers from the word list, as we have also remove them from the page tokens.
        self.word_list = set([item for item in all_dutch_words if not any(char.isdigit() for char in item)])

    def wordlist_membership(self, list_of_tokens: List[str]) -> List[bool]:
        # simply check whether a token appears in the word list or not
        return np.array([token in self.word_list for token in list_of_tokens])

    @staticmethod
    def preprocess(input_string: str, clean_input: bool = True) -> List[str]:
        """
        :param input_string: string containing the text to be preprocessed
        :param clean_input: boolean specifying whether to clean the input,
        if this is Fale then only tokenization is performed.
        Function that handles the preprocessing of input text performs two steps
        1. Normalization by removing non-unicode characters and normalizing whitespace
        2. Tokenization using nltk
        :returns: A list of tokens
        """
        # perform normalization and tokenization
        if clean_input:
            input_string = clean_func(input_string)
        tokenized_text = word_tokenize(input_string)
        return tokenized_text

    def detect_bad_segments(self, input_text: str, tolerance=3, clean_input: bool = True) -> np.ndarray:
        """
        Function that detects bad segment in a list of input tokens based on the
        word list.
        :param inpuput_text: string that contains the input text for which we
        calculate the bad segments
        :param tolerance: integer specifying the tolerance of good words within a
        pad segment
        :param clean_input: boolean specifying whether to clean the input,
        if this is False then only tokenization is performed.
        :returns: numpy array with a boolean vector for each token indication whether it is
        part of a bad segment or not.
        """
        # Get the input tokens from the text
        tokenized_sample = self.preprocess(input_text, clean_input=clean_input)
        # Get a boolean vector for each word in the in text indicating whether
        # it is in the wordlist or not.
        word_list_array = self.wordlist_membership(tokenized_sample)
        # Get the words that are in the wordlist
        wordlist_members = word_list_array.nonzero()[0]
        # Get the start of good segment
        good_prefixes = np.diff(wordlist_members, prepend=-2)
        good_prefixes = wordlist_members[good_prefixes > 1]

        # Check whether a good segment is within the tolerance
        # if it is its part of a bad segment, otherwise it is ok.
        for item in good_prefixes:
            sequence = word_list_array[item: item + tolerance]
            if not np.all(sequence):
                word_list_array[item:item + tolerance - 1] = False

        return np.logical_not(word_list_array)


def run_bad_segment_detection(input_dataframe: list, tolerance: int, clean_input: bool = False):
    """
    Function that runs that bad segment detection on a dataframe and returns
    general statistics on the bad segments in the text.
    """
    det = BadSegmentDetector()
    all_bad_segment_lengths = []
    all_segment_indices = []
    results = dict()
    for document_id, document in tqdm(input_dataframe.to_dict().items()):
        bad_segments = det.detect_bad_segments(document, tolerance=tolerance, clean_input=clean_input)
        # skips empty pages
        if True in bad_segments:
            bad_segment_length = np.diff(np.where(np.concatenate(([bad_segments[0]],
                                                                  bad_segments[:-1] != bad_segments[1:],
                                                                  [True])))[0])[::2]
            num_bad_segments = len(bad_segment_length)
            all_bad_segment_lengths.extend(bad_segment_length)
        else:
            num_bad_segments = 0
            bad_segment_length = np.array([0])

        mean_bad_segment_length = bad_segment_length.mean()
        num_bad_tokens = bad_segments.sum().astype(int)
        shortest_bad_segment, longest_bad_segment = bad_segment_length.min().astype(
            int), bad_segment_length.max().astype(int)
        results[document_id] = {'Number of bad Segments': num_bad_segments,
                                'Mean Bad Segment Length': mean_bad_segment_length,
                                'Max Bad Segment Length': longest_bad_segment,
                                'Min Bad Segment Length': shortest_bad_segment,
                                'Number of bad Tokens': num_bad_tokens,
                                'Bad Ratio': bad_segments.mean(),
                                'Num Tokens': len(bad_segments)}

    return pd.DataFrame.from_dict(results, orient='index'), all_bad_segment_lengths