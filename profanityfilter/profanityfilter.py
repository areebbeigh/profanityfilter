import os
import re

_words = None
_censor_char = "*"
_BASE_DIR = os.path.abspath(os.path.dirname(__file__))
_words_file = os.path.join(_BASE_DIR, 'data', 'badwords.txt')


def _load_words(word_list=None, include_original=True):
    """ Loads the list of profane words. """
    global _words
    if word_list:
        _words = word_list
        if not include_original:
            return
    with open(_words_file, 'r') as f:
        lines = f.readlines()
        _words = [line.strip() for line in lines]


def define_words(word_list):
    """ Define a custom list of profane words. """
    _load_words(word_list, False)


def append_words(word_list):
    """ Extends the profane word list with word_list """
    get_bad_words()
    _words.extend(word_list)


def restore_words():
    """ Restores the original list of bad words """
    _load_words()


def set_censor(character):
    """ Replaces the original censor character '*' with character """
    global _censor_char
    if isinstance(character, int):
        character = str(character)
    _censor_char = character


def get_bad_words():
    """ Returns the list of profane words """
    if not _words:
        _load_words(None)
        return _words
    return _words


def censor(input_text):
    """ Returns input_text with any profane words censored """
    bad_words = get_bad_words()
    res = input_text
    for word in bad_words:
        word = r'\b%s\b' % word  # Apply word boundaries to the bad word
        regex = re.compile(word, re.IGNORECASE)
        res = regex.sub(_censor_char * (len(word) - 4), res)
    return res


def is_clean(input_text):
    """ Returns True if input_text doesn't contain any profane words, False otherwise. """
    return input_text == censor(input_text)


def is_profane(input_text):
    """ Returns True if input_text contains any profane words, False otherwise. """
    return input_text != censor(input_text)
