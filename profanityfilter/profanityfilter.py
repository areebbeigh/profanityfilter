import os
import re
from collections import defaultdict
from itertools import chain
from math import floor

import spacy
from ordered_set import OrderedSet

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

try:
    import polyglot.detect
    POLYGLOT_AVAILABLE = True
except ImportError:
    POLYGLOT_AVAILABLE = False


class ProfanityFilterError(Exception):
    pass


class ProfanityFilter:
    def __init__(self, **kwargs):
        global DEEP_ANALYSIS_AVAILABLE, PYMORPHY2_AVAILABLE, POLYGLOT_AVAILABLE

        # If defined, use this instead of _censor_list
        self._custom_censor_list = defaultdict(lambda: [], **kwargs.get('custom_censor_list', {}))

        # Words to be used in conjunction with _censor_list
        self._extra_censor_list = defaultdict(lambda: [], **kwargs.get('extra_censor_list', {}))

        # Language for tokenization and lemmatization
        self._languages = OrderedSet(kwargs.get('languages', {'en'}))

        # What to be censored -- should not be modified by user
        self._censor_list = {}

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
        self._words_files = {}
        for language in self._languages:
            words_file = os.path.join(self._DATA_DIR, language + '_badwords.txt')
            if os.path.exists(words_file):
                self._words_files[language] = words_file
        languages_str = ', '.join(self._languages)
        if not self._words_files:
            raise ProfanityFilterError("Couldn't load profane words for any of languages: " + languages_str)

        self._load_words()

        if 'nlp' in kwargs:
            self._nlp = kwargs['nlp']
        else:
            self._nlp = {}
            for language in self._languages:
                try:
                    self._nlp[language] = spacy.load(language, disable=['parser', 'ner'])
                except OSError:
                    pass
            if not self._nlp:
                raise ProfanityFilterError("Couldn't load Spacy model for any of languages: " + languages_str)

        if DEEP_ANALYSIS_AVAILABLE:
            if 'spell' in kwargs:
                self._spell = kwargs['spell']
            else:
                self._spell = {}
                DEEP_ANALYSIS_AVAILABLE = False
                for language in self._languages:
                    try:
                        self._spell[language] = HunSpell(os.path.join(self._DATA_DIR, language + '.dic'),
                                                         os.path.join(self._DATA_DIR, language + '.aff'))
                        DEEP_ANALYSIS_AVAILABLE = True
                    except HunSpellError:
                        pass
            if DEEP_ANALYSIS_AVAILABLE:
                self._alphabet = set()
                self._trie = {}

        if PYMORPHY2_AVAILABLE:
            if 'morph' in kwargs:
                self._morph = kwargs['morph']
            else:
                self._morph = {}
                PYMORPHY2_AVAILABLE = False
                for language in self._languages:
                    try:
                        self._morph[language] = pymorphy2.MorphAnalyzer(lang=language)
                        PYMORPHY2_AVAILABLE = True
                    except ValueError:
                        pass

    def _load_words(self):
        """ Loads the list of profane words from file. """
        for language, words_file in self._words_files.items():
            with open(words_file) as f:
                self._censor_list[language] = [line.strip() for line in f.readlines()]

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

    def define_words(self, language, word_list):
        """ Define a custom list of profane words. """
        self._censored_words = {}
        self._words_with_no_profanity_inside = set()
        self._custom_censor_list[language] = word_list

    def append_words(self, language, word_list):
        """ Extends the profane word list with word_list """
        self._censored_words = {}
        self._words_with_no_profanity_inside = set()
        self._extra_censor_list[language].extend(word_list)

    def set_censor(self, character):
        """ Replaces the original censor character '*' with character """
        # TODO: what if character isn't str()-able?
        if isinstance(character, int):
            character = str(character)
        self._censor_char = character

    def has_bad_word(self, text, deep_analysis=True):
        """ Returns True if text contains profanity, False otherwise """
        return self._censor(input_text=text, deep_analysis=deep_analysis, censor_whole_words=True, return_bool=True)

    def get_custom_censor_list(self, language):
        """ Returns the list of custom profane words """
        return self._custom_censor_list[language]

    def get_extra_censor_list(self, language):
        """ Returns the list of custom, additional, profane words """
        return self._extra_censor_list[language]

    def _get_max_distance(self, length):
        return min(self._MIN_MAX_DISTANCE, floor(self._max_distance * length))

    @staticmethod
    def _copy_dict_of_lists(source):
        # Python 3.4 doesn't have copy module
        result = {}
        for key, l in source.items():
            result[key] = [x for x in l]
        return result

    def get_profane_words(self):
        """ Gets all profane words """
        if self._custom_censor_list:
            profane_words = self._copy_dict_of_lists(self._custom_censor_list)
        else:
            profane_words = self._copy_dict_of_lists(self._censor_list)

        for language in self._languages:
            profane_words[language].extend(self._extra_censor_list[language])
            profane_words[language] = list(set(profane_words[language]))

        if DEEP_ANALYSIS_AVAILABLE:
            for language in self._languages:
                self._trie[language] = Trie(words=profane_words[language], alphabet=self._alphabet)
            for length in range(self._MIN_MAX_DISTANCE + 1):
                generate_automaton_to_file(length)

        return profane_words

    def restore_words(self):
        """ Clears all custom censor lists """
        self._custom_censor_list = defaultdict(lambda: [])
        self._extra_censor_list = defaultdict(lambda: [])
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

    def _parse(self, language, text, merge):
        nlp = None
        languages = OrderedSet([language]) | self._languages
        for language in languages:
            try:
                nlp = self._nlp[language]
                break
            except KeyError:
                pass
        result = nlp(text)
        if merge:
            result = result[:].merge()
        return result

    def _get_spell(self, language):
        result = None
        if not DEEP_ANALYSIS_AVAILABLE:
            return result
        languages = OrderedSet([language]) | self._languages
        for language in languages:
            try:
                result = self._spell[language]
                break
            except KeyError:
                pass
        return result

    def _stems(self, language, word):
        spell = self._get_spell(language=language)
        if spell is None:
            return set()
        stems_bytes = spell.stem(word)
        return {stem_bytes.decode(spell.get_dic_encoding()) for stem_bytes in stems_bytes}

    def _normal_form(self, language, word):
        morph = None
        if not PYMORPHY2_AVAILABLE:
            return word
        languages = OrderedSet([language]) | self._languages
        for language in languages:
            try:
                morph = self._morph[language]
                break
            except KeyError:
                pass
        return morph.parse(word=word)[0].normal_form if morph is not None else word

    def _lemmas(self, word, language=None):
        result = set()
        if not word:
            return result
        try:
            spacy_lemma = word.lemma_
        except AttributeError:
            word = self._parse(language=language, text=word, merge=True)
            spacy_lemma = word.lemma_
        result.add(word.text)
        spacy_lemma = spacy_lemma if spacy_lemma != '-PRON-' else word.lower_
        result.add(spacy_lemma)
        result |= self._stems(language=language, word=word.text)
        result.add(self._normal_form(language=language, word=word.text))
        return result

    def _is_dictionary_word(self, language, word):
        spell = self._get_spell(language=language)
        return spell.spell(word) if spell is not None else False

    def _keep_only_letters_or_dictionary_word(self, word, language=None):
        try:
            word = word.text
        except AttributeError:
            pass
        if DEEP_ANALYSIS_AVAILABLE and language is not None and self._is_dictionary_word(language=language, word=word):
            return word
        else:
            return ''.join(regex.findall(r'\p{letter}', word))

    def _has_no_profanity(self, words):
        return any(str(word) in word_with_no_profanity_inside
                   for word in words
                   for word_with_no_profanity_inside in self._words_with_no_profanity_inside)

    def _get_trie(self, language):
        result = None
        languages = OrderedSet([language]) | self._languages
        for language in languages:
            try:
                result = self._trie[language]
                break
            except KeyError:
                pass
        return result

    def _get_bad_words(self, language, bad_words):
        result = []
        languages = OrderedSet([language]) | self._languages
        for language in languages:
            try:
                result = bad_words[language]
                break
            except KeyError:
                pass
        return result

    def _is_bad_word(self, language, bad_words, word):
        return word in self._get_bad_words(language=language, bad_words=bad_words)

    def _censor_word(self, word, bad_words, deep_analysis=True, censor_whole_word=True, language=None):
        """
        :return: Tuple of censored word and flag of no profanity inside
        """
        lemmas = self._lemmas(word=word, language=language)
        if deep_analysis and DEEP_ANALYSIS_AVAILABLE:
            lemmas_only_letters = {self._keep_only_letters_or_dictionary_word(lemma) for lemma in lemmas}
            if lemmas_only_letters != lemmas:
                lemmas = set(chain(*(self._lemmas(word=lemma, language=language) for lemma in lemmas_only_letters)))
        if self._has_no_profanity(lemmas):
            return word.text, True
        censored_words_key = (word.text, self._censor_char, censor_whole_word)
        if censored_words_key in self._censored_words:
            return self._censored_words[censored_words_key], False
        for lemma in lemmas:
            if self._is_bad_word(language=language, bad_words=bad_words, word=lemma):
                censored = self._censor_word_by_part(word=word, bad_word=lemma)
                self._censored_words[censored_words_key] = censored
                return censored, False
        if deep_analysis and DEEP_ANALYSIS_AVAILABLE:
            for lemma in lemmas:
                if self._is_dictionary_word(language=language, word=lemma):
                    return word.text, True
            for lemma in lemmas:
                automaton = LevenshteinAutomaton(tolerance=self._get_max_distance(len(lemma)),
                                                 query_word=lemma,
                                                 alphabet=self._alphabet)
                matching_bad_words = trie_automaton_intersection(automaton=automaton,
                                                                 trie=self._get_trie(language=language),
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

    def censor_word(self, word, bad_words=None, deep_analysis=True, censor_whole_word=True, language=None):
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
                    censored_part = self._parse(language=language, text=censored_part, merge=True)
                    censored_censored_part, no_profanity_inside = self._censor_word(word=censored_part,
                                                                                    bad_words=bad_words,
                                                                                    deep_analysis=deep_analysis,
                                                                                    censor_whole_word=censor_whole_word,
                                                                                    language=language)
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
            if deep_analysis and DEEP_ANALYSIS_AVAILABLE and not self._is_dictionary_word(language, word.text):
                self._words_with_no_profanity_inside.add(word.text)
                return word.text
        else:
            censored_words_key = (word.text, self._censor_char, censor_whole_word)
            self._censored_words[censored_words_key] = censored
        return censored

    @staticmethod
    def _detect_languages(text, fallback_language):
        if not POLYGLOT_AVAILABLE:
            result = [fallback_language]
        else:
            polyglot_output = polyglot.detect.Detector(text, quiet=True)
            result = [language.code for language in polyglot_output.languages if language.code != 'un']
            if not result:
                result = [fallback_language]
        return result

    @staticmethod
    def _merge_by_language(parts):
        result = []
        language = parts[0][0]
        merged = parts[0][1]
        i = 1
        while i < len(parts):
            if parts[i][0] != language:
                result.append((language, merged))
                language = parts[i][0]
                merged = parts[i][1]
            else:
                merged += parts[i][1]
            i += 1
        result.append((language, merged))
        return result

    @staticmethod
    def _split_by_language(text, fallback_language):
        languages = ProfanityFilter._detect_languages(text=text, fallback_language=fallback_language)
        tokens = re.split(r'(\W)', text)
        if len(languages) == 0:
            return [(None, text)]
        elif len(languages) == 1 or len(tokens) <= 1:
            return [(languages[0], text)]
        else:
            middle_index = len(tokens) // 2
            left_text, right_text, = ''.join(tokens[:middle_index]), ''.join(tokens[middle_index:])
            left = ProfanityFilter._split_by_language(text=left_text, fallback_language=fallback_language)
            right = ProfanityFilter._split_by_language(text=right_text, fallback_language=fallback_language)
            return ProfanityFilter._merge_by_language(left + right)

    @staticmethod
    def _replace_token(text, old, new):
        return text[:old.idx] + new + text[old.idx + len(old.text):]

    def _censor(self, input_text, deep_analysis=True, censor_whole_words=True, return_bool=False):
        """Returns input_text with any profane words censored or
        bool (True - input_text has profane words, False otherwise) if return_bool=True"""
        bad_words = self.get_profane_words()
        result = ''
        text_parts = self._split_by_language(text=input_text, fallback_language=self._languages[0])
        for language, text_part in text_parts:
            result_part = text_part
            doc = self._parse(language=language, text=text_part, merge=False)
            for token in doc:
                censored_word = self.censor_word(word=token,
                                                 bad_words=bad_words,
                                                 deep_analysis=deep_analysis,
                                                 censor_whole_word=censor_whole_words,
                                                 language=language)
                if censored_word != token.text:
                    if return_bool:
                        return True
                    else:
                        result_part = self._replace_token(text=result_part, old=token, new=censored_word)
            result += result_part
        if return_bool:
            return False
        else:
            return result

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
