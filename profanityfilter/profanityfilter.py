import os
from itertools import chain
from math import floor

import spacy

try:
    import Levenshtein
    import regex
    from pyffs.automaton_management import generate_automaton_to_file
    from pyffs.fuzzy_search.algorithms import trie_automaton_intersection
    from pyffs.fuzzy_search.trie import Trie
    from pyffs.fuzzy_search.levenshtein_automaton import LevenshteinAutomaton
    from hunspell import HunSpell, HunSpellError
    DEEP_ANALYSIS_AVAILABLE = True
except ImportError:
    DEEP_ANALYSIS_AVAILABLE = False

try:
    import pymorphy2
    PYMORPHY2_AVAILABLE = True
except ImportError:
    PYMORPHY2_AVAILABLE = False


class ProfanityFilterError(Exception):
    pass


class ProfanityFilter:
    def __init__(self, **kwargs):
        global DEEP_ANALYSIS_AVAILABLE, PYMORPHY2_AVAILABLE

        # If defined, use this instead of _censor_list
        self._custom_censor_list = kwargs.get('custom_censor_list', [])

        # Words to be used in conjunction with _censor_list
        self._extra_censor_list = kwargs.get('extra_censor_list', [])

        # Language for tokenization and lemmatization
        self._languages = kwargs.get('languages', ['en'])

        # What to be censored -- should not be modified by user
        self._censor_list = []

        # Dict of censored words (mapping from profane word to censored word) that is generated after censoring
        self._censored_words = {}

        # Set of words with no profanity inside that is generated after censoring
        # (include words that are not in the dictionary)
        self._words_with_no_profanity_inside = set()

        # What to censor the words with
        self._censor_char = "*"

        # Max relative distance to profane words
        self._MIN_MAX_DISTANCE = 3
        self._max_distance = kwargs.get('max_distance', 0.34)

        # Where to find the censored words
        self._BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        self._DATA_DIR = os.path.join(self._BASE_DIR, 'data')
        for language in self._languages:
            self._words_file = os.path.join(self._DATA_DIR, language + '_badwords.txt')
            if os.path.exists(self._words_file):
                break
        languages_comma_separated = ', '.join(self._languages)
        if not os.path.exists(self._words_file):
            raise ProfanityFilterError("Couldn't load profane words for any of languages: " + languages_comma_separated)

        self._load_words()

        spacy_available = False
        for language in self._languages:
            try:
                self._nlp = spacy.load(language, disable=['parser', 'ner'])
                spacy_available = True
                break
            except OSError:
                pass
        if not spacy_available:
            raise ProfanityFilterError("Couldn't load Spacy model for any of languages: " + languages_comma_separated)

        if DEEP_ANALYSIS_AVAILABLE:
            DEEP_ANALYSIS_AVAILABLE = False
            for language in self._languages:
                try:
                    self._hunspell = HunSpell(
                        os.path.join(self._DATA_DIR, language + '.dic'),
                        os.path.join(self._DATA_DIR, language + '.aff'))
                    DEEP_ANALYSIS_AVAILABLE = True
                    break
                except HunSpellError:
                    pass

        if DEEP_ANALYSIS_AVAILABLE:
            self._alphabet = set()
            self._trie = None

        if PYMORPHY2_AVAILABLE:
            PYMORPHY2_AVAILABLE = False
            for language in self._languages:
                try:
                    self._morph = pymorphy2.MorphAnalyzer(lang=language)
                    PYMORPHY2_AVAILABLE = True
                    break
                except ValueError:
                    pass

    def _load_words(self):
        """ Loads the list of profane words from file. """
        with open(self._words_file, 'r') as f:
            self._censor_list = [line.strip() for line in f.readlines()]

    @staticmethod
    def _substrings(text):
        return ((text[i:i + length], i, i + length)
                for length in range(len(text), 0, -1) for i in range(len(text) - length + 1))

    def _drop_fully_censored_words(self, words):
        return ((word, start, finish)
                for word, start, finish in words if not all(char == self._censor_char for char in word))

    @staticmethod
    def _drop_substrings(words):
        drop_intervals = set()
        for word, start, finish in words:
            if all(start < drop_start or finish > drop_finish for drop_start, drop_finish in drop_intervals):
                result = (word, start, finish)
                drop = yield result
                drop_start, drop_finish = drop
                if drop_start is not None and drop_finish is not None:
                    drop_intervals.add((drop_start, drop_finish))

    def define_words(self, word_list):
        """ Define a custom list of profane words. """
        self._censored_words = {}
        self._words_with_no_profanity_inside = set()
        self._custom_censor_list = word_list

    def append_words(self, word_list):
        """ Extends the profane word list with word_list """
        self._censored_words = {}
        self._words_with_no_profanity_inside = set()
        self._extra_censor_list.extend(word_list)

    def set_censor(self, character):
        """ Replaces the original censor character '*' with character """
        # TODO: what if character isn't str()-able?
        if isinstance(character, int):
            character = str(character)
        self._censor_char = character

    def has_bad_word(self, text, deep_analysis=True):
        """ Returns True if text contains profanity, False otherwise """
        return self._censor(input_text=text, deep_analysis=deep_analysis, censor_whole_words=True, return_bool=True)

    def get_custom_censor_list(self):
        """ Returns the list of custom profane words """
        return self._custom_censor_list

    def get_extra_censor_list(self):
        """ Returns the list of custom, additional, profane words """
        return self._extra_censor_list

    def _get_max_distance(self, length):
        return min(self._MIN_MAX_DISTANCE, floor(self._max_distance * length))

    def get_profane_words(self):
        """ Gets all profane words """
        profane_words = []

        if self._custom_censor_list:
            profane_words = [w for w in self._custom_censor_list]  # Previous versions of Python don't have list.copy()
        else:
            profane_words = [w for w in self._censor_list]

        profane_words.extend(self._extra_censor_list)
        profane_words = list(set(profane_words))

        if DEEP_ANALYSIS_AVAILABLE:
            self._alphabet = set()
            self._trie = Trie(words=profane_words, alphabet=self._alphabet)
            for length in range(self._MIN_MAX_DISTANCE + 1):
                generate_automaton_to_file(length)

        return profane_words

    def restore_words(self):
        """ Clears all custom censor lists """
        self._custom_censor_list = []
        self._extra_censor_list = []
        self._censored_words = {}
        self._words_with_no_profanity_inside = set()
        #self._load_words()
        #print("Hey" in self.get_profane_words())

    def _generate_censored_word(self, word):
        return len(word) * self._censor_char

    def _censor_word_by_part(self, word, bad_word):
        def is_delete_or_insert(opcode):
            return opcode[0] in ('delete', 'insert')

        def find_word_part(word, word_part):
            word_to_word_part_opcodes = Levenshtein.opcodes(word, word_part)
            word_part_in_word_start = (
                word_to_word_part_opcodes[0][2] if is_delete_or_insert(word_to_word_part_opcodes[0]) else 0)
            word_part_in_word_finish = (
                word_to_word_part_opcodes[-1][1] if is_delete_or_insert(word_to_word_part_opcodes[-1]) else len(word))
            return word[word_part_in_word_start:word_part_in_word_finish]

        try:
            word = word.text
        except AttributeError:
            pass

        word_part_for_censoring = find_word_part(word.lower(), bad_word)
        return regex.sub(pattern=word_part_for_censoring,
                         repl=self._generate_censored_word(word_part_for_censoring),
                         string=word,
                         flags=regex.IGNORECASE)

    def _lemmas(self, word, deep_analysis=True):
        if not word:
            return set()
        try:
            spacy_lemma = word.lemma_
        except AttributeError:
            word = self._nlp(word)[:].merge()
            spacy_lemma = word.lemma_
        spacy_lemma = spacy_lemma if spacy_lemma != '-PRON-' else word.lower_
        result = {word.text, spacy_lemma}
        if deep_analysis and DEEP_ANALYSIS_AVAILABLE:
            hunspell_stems = self._hunspell.stem(word.text)
            result |= {hunspell_stem.decode('utf-8') for hunspell_stem in hunspell_stems}
        if PYMORPHY2_AVAILABLE:
            pymorphy_normal_form = self._morph.parse(word.text)[0].normal_form
            result.add(pymorphy_normal_form)
        return result

    def _keep_only_letters_or_dictionary_word(self, word):
        try:
            word = word.text
        except AttributeError:
            pass
        if DEEP_ANALYSIS_AVAILABLE and self._hunspell.spell(word):
            return word
        else:
            return ''.join(regex.findall(r'\p{letter}', word))

    def _has_no_profanity(self, words):
        return any(str(word) in word_with_no_profanity_inside
                   for word in words
                   for word_with_no_profanity_inside in self._words_with_no_profanity_inside)

    def _censor_word(self, word, bad_words, deep_analysis=True, censor_whole_word=True):
        """
        :return: Tuple of censored word and flag of no profanity inside
        """
        lemmas = self._lemmas(word=word, deep_analysis=deep_analysis)
        if deep_analysis and DEEP_ANALYSIS_AVAILABLE:
            lemmas_only_letters = {self._keep_only_letters_or_dictionary_word(lemma) for lemma in lemmas}
            if lemmas_only_letters != lemmas:
                lemmas = set(chain(*(self._lemmas(word=lemma, deep_analysis=deep_analysis)
                                     for lemma in lemmas_only_letters)))
        if self._has_no_profanity(lemmas):
            return word.text, True
        censored_words_key = (word.text, self._censor_char, censor_whole_word)
        if censored_words_key in self._censored_words:
            return self._censored_words[censored_words_key], False
        for lemma in lemmas:
            if lemma in bad_words:
                censored = self._censor_word_by_part(word=word, bad_word=lemma)
                self._censored_words[censored_words_key] = censored
                return censored, False
        if deep_analysis and DEEP_ANALYSIS_AVAILABLE:
            for lemma in lemmas:
                if self._hunspell.spell(lemma):
                    return word.text, True
            for lemma in lemmas:
                automaton = LevenshteinAutomaton(tolerance=self._get_max_distance(len(lemma)),
                                                 query_word=lemma,
                                                 alphabet=self._alphabet)
                matching_bad_words = trie_automaton_intersection(automaton=automaton,
                                                                 trie=self._trie,
                                                                 include_error=False)
                if matching_bad_words:
                    if censor_whole_word:
                        censored = self._generate_censored_word(word.text)
                    else:
                        bad_word = matching_bad_words[0]
                        censored = self._censor_word_by_part(word=word, bad_word=bad_word)
                    self._censored_words[censored_words_key] = censored
                    return censored, False
        return word.text, False

    def censor_word(self, word, bad_words=None, deep_analysis=True, censor_whole_word=True):
        """Returns censored word"""
        if bad_words is None:
            bad_words = self.get_profane_words()
        censored_prev = None
        censored = word.text
        while censored != censored_prev:
            censored_prev = censored
            substrings = self._drop_substrings(self._drop_fully_censored_words(self._substrings(censored_prev)))
            no_profanity_start, no_profanity_finish = None, None
            try:
                substring = next(substrings)
                censored_part, start, finish = substring
            except StopIteration:
                break
            while True:
                try:
                    censored_part = self._nlp(censored_part)[:].merge()
                    censored_censored_part, no_profanity_inside = self._censor_word(word=censored_part,
                                                                                    bad_words=bad_words,
                                                                                    deep_analysis=deep_analysis,
                                                                                    censor_whole_word=censor_whole_word)
                    if no_profanity_inside:
                        no_profanity_start, no_profanity_finish = start, finish
                    if censored_censored_part != censored_part.text:
                        if censor_whole_word:
                            censored = self._generate_censored_word(word.text)
                        else:
                            censored = censored_prev.replace(censored_part.text, censored_censored_part)
                    # Stop after first iteration (with word part equal word) when deep analysis is disabled or
                    # if word was partly censored
                    if not (deep_analysis and DEEP_ANALYSIS_AVAILABLE) or (censored != censored_prev):
                        break
                    censored_part, start, finish = substrings.send((no_profanity_start, no_profanity_finish))
                except StopIteration:
                    break
        if censored == word.text:
            if deep_analysis and DEEP_ANALYSIS_AVAILABLE and not self._hunspell.spell(word.text):
                self._words_with_no_profanity_inside.add(word.text)
                return word.text
        else:
            censored_words_key = (word.text, self._censor_char, censor_whole_word)
            self._censored_words[censored_words_key] = censored
        return censored

    def _censor(self, input_text, deep_analysis=True, censor_whole_words=True, return_bool=False):
        """Returns input_text with any profane words censored or
        bool (True - input_text has profane words, False otherwise) if return_bool=True"""
        bad_words = self.get_profane_words()
        res = input_text
        doc = self._nlp(input_text)
        for token in doc:
            censored_word = self.censor_word(word=token,
                                             bad_words=bad_words,
                                             deep_analysis=deep_analysis,
                                             censor_whole_word=censor_whole_words)
            if censored_word != token.text:
                if return_bool:
                    return True
                else:
                    res = res[:token.idx] + censored_word + res[token.idx + len(token.text):]
        if return_bool:
            return False
        else:
            return res

    def censor(self, input_text, deep_analysis=True, censor_whole_words=True):
        """ Returns input_text with any profane words censored """
        return self._censor(input_text=input_text,
                            deep_analysis=deep_analysis,
                            censor_whole_words=censor_whole_words,
                            return_bool=False)

    def is_clean(self, input_text, deep_analysis=True):
        """ Returns True if input_text doesn't contain any profane words, False otherwise. """
        return not self.has_bad_word(text=input_text, deep_analysis=deep_analysis)

    def is_profane(self, input_text, deep_analysis=True):
        """ Returns True if input_text contains any profane words, False otherwise. """
        return self.has_bad_word(text=input_text, deep_analysis=deep_analysis)
