import os
from inflection import singularize


class ProfanityFilter:
    def __init__(self, **kwargs):

        # If defined, use this instead of _censor_list
        self._custom_censor_list = kwargs.get('custom_censor_list', [])

        # Words to be used in conjunction with _censor_list
        self._extra_censor_list = kwargs.get('extra_censor_words', [])

        # What to be censored -- should not be modified by user
        self._censor_list = []

        # What to censor the words with
        self._censor_char = "*"

        # Where to find the censored words
        self._BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        self._words_file = os.path.join(_BASE_DIR, 'data', 'badwords.txt')

        self._load_words()

    def _load_words(self):
        """ Loads the list of profane words from file. """
        with open(_words_file, 'r') as f:
            self._censor_list = set([line.strip() for line in f.readlines()])

    def define_words(self, word_list):
        """ Define a custom list of profane words. """
        self._custom_censor_list = word_list

    def append_words(self, word_list):
        """ Extends the profane word list with word_list """
        self._extra_censor_list.extend(word_list)

    def set_censor(character):
        """ Replaces the original censor character '*' with character """
        # TODO: what if character isn't str()-able?
        if isinstance(character, int):
            character = str(character)
        self._censor_char = character

    def has_bad_word(text):
        """ Returns True if text contains profanity, False otherwise """
        bad_words = self.get_profane_words()
        return any(word in text for word in bad_words)

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
            profane_words = self._custom_censor_list
        else:
            profane_words = self._censor_list

        profane_words.extend(self._extra_censor_list)

        return profane_words
 
    def restore_words(self):
        """ Clears all custom censor lists """
        self._custom_censor_list = []
        self._extra_censor_list = []


    def censor(input_text):
        """ Returns input_text with any profane words censored """
        bad_words = self.get_profane_words()

        spl = input_text.split(' ')

        for index, value in spl:
            word = singularize(value)
            if word in bad_words:
                spl[index] = '*' * len(value)

        return ' '.join(spl)


    def is_clean(input_text):
        """ Returns True if input_text doesn't contain any profane words, False otherwise. """
        return not self.has_bad_word(input_text)


    def is_profane(input_text):
        """ Returns True if input_text contains any profane words, False otherwise. """
        return self.has_bad_word(input_text)

