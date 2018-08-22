import os

import spacy


class ProfanityFilter:
    def __init__(self, **kwargs):

        # If defined, use this instead of _censor_list
        self._custom_censor_list = kwargs.get('custom_censor_list', [])

        # Words to be used in conjunction with _censor_list
        self._extra_censor_list = kwargs.get('extra_censor_list', [])

        # Language for tokenization and lemmatization
        self._language = kwargs.get('language', 'en')

        # What to be censored -- should not be modified by user
        self._censor_list = []

        # What to censor the words with
        self._censor_char = "*"

        # Where to find the censored words
        self._BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        self._words_file = os.path.join(self._BASE_DIR, 'data', 'badwords.txt')

        self._load_words()

        self._nlp = spacy.load(self._language)

    def _load_words(self):
        """ Loads the list of profane words from file. """
        with open(self._words_file, 'r') as f:
            self._censor_list = [line.strip() for line in f.readlines()]

    def define_words(self, word_list):
        """ Define a custom list of profane words. """
        self._custom_censor_list = word_list

    def append_words(self, word_list):
        """ Extends the profane word list with word_list """
        self._extra_censor_list.extend(word_list)

    def set_censor(self, character):
        """ Replaces the original censor character '*' with character """
        # TODO: what if character isn't str()-able?
        if isinstance(character, int):
            character = str(character)
        self._censor_char = character

    def has_bad_word(self, text):
        """ Returns True if text contains profanity, False otherwise """
        return self.censor(text) != text

    def get_custom_censor_list(self):
        """ Returns the list of custom profane words """
        return self._custom_censor_list

    def get_extra_censor_list(self):
        """ Returns the list of custom, additional, profane words """
        return self._extra_censor_list

    def get_profane_words(self):
        """ Gets all profane words """
        profane_words = []

        if self._custom_censor_list:
            profane_words = [w for w in self._custom_censor_list]  # Previous versions of Python don't have list.copy()
        else:
            profane_words = [w for w in self._censor_list]

        profane_words.extend(self._extra_censor_list)
        profane_words = list(set(profane_words))

        return profane_words

    def restore_words(self):
        """ Clears all custom censor lists """
        self._custom_censor_list = []
        self._extra_censor_list = []
        #self._load_words()
        #print("Hey" in self.get_profane_words())

    def censor(self, input_text):
        """ Returns input_text with any profane words censored """
        bad_words = self.get_profane_words()
        res = input_text
        doc = self._nlp(input_text)
        for token in doc:
            if token.lemma_ in bad_words:
                res = res[:token.idx] + len(token.text) * self._censor_char + res[token.idx + len(token.text):]
        return res

    def is_clean(self, input_text):
        """ Returns True if input_text doesn't contain any profane words, False otherwise. """
        return not self.has_bad_word(input_text)

    def is_profane(self, input_text):
        """ Returns True if input_text contains any profane words, False otherwise. """
        return self.has_bad_word(input_text)
