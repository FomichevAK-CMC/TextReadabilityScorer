# -*- coding: utf8 -*-

from typing import Callable
from copy import deepcopy  # на случай если будет кешироваться, возвращаемый методом, изменяемый тип данных.
from tscanner import *

WSEP = TModel('SEP', 'WORD', r'\s+')  # word separators (whitespaces)
SSEP = TModel('SEP', 'SENT', r'([?!.]+["»]?)(?=(\s+(([-—] )?["«]?[А-ЯЁ]))|\s*$)')  # sentence separators
WORD_RU = TModel('WORD', 'RU', r'([а-яА-ЯёЁ]+[./-]?)*[а-яА-ЯёЁ]+(?!\w)')      # russian words
WORD_LAT = TModel('WORD', 'LAT', r"([a-zA-Z]+['`’./-]?)*[a-zA-Z']+(?!\w)")    # latin words
NUM = TModel('NUM', '', r'[-+]?\d+(?!\d)')   # numbers
WORD = TModel('WORD', '', r"[-\w_`’']+")    # any word-like structure
PUNC = TModel('PUNC', '', r'[.,;:!?"»«\']')  # punctuation marks


ru_vowels = 'аоуэыяёюеи'
ru_alphabet = 'абвгдеёжзийклмнопрстуфхцчшщьыъэюя'
digits = '0123456789'


def ru_syl_count(word: Token) -> int:
    """Counts the number of syllables in a russian word."""
    w = word.body.lower()
    count = 0
    for t in w:
        if t in ru_vowels:
            count += 1
    return count


class RUAnalyzer:
    """Class for russian text analysis. Functionality could be expanded infinitely :)"""
    _rules = [WSEP, SSEP, WORD_RU, NUM, WORD, PUNC]
    _stop_list = [WSEP]

    def __init__(self, file_or_text: TextIO | str | TList):
        self._stats = {}
        if isinstance(file_or_text, TList):
            self._tlist = deepcopy(file_or_text)
        elif isinstance(file_or_text, str):
            self._tlist = scan_text(file_or_text, self._rules, stop=self._stop_list)
        else:
            self._tlist = scan_file(file_or_text, self._rules, stop=self._stop_list)

    def _cache(func: Callable):
        """Caches calculated values for various stats.
        Properties marked with @_cache decorator are only calculated once per instance of the RUAnalyzer.
        """
        def wrapper(self):
            if func.__name__ in self._stats:
                return deepcopy(self._stats[func.__name__])
            val = func(self)
            self._stats[func.__name__] = deepcopy(val)
            return val
        return wrapper

    def sentences(self) -> List[TList]:
        """Splits token list by SSEP token type into sentences."""
        return self._tlist.split([SSEP])

    def ru_words(self) -> TList:
        """Gets the TList of all russian words."""
        return self._tlist.filter([WORD_RU], remove=False)

    def numbers(self) -> TList:
        """Gets the TList of all numbers."""
        return self._tlist.filter([NUM], remove=False)

    @_cache
    def sent_count(self) -> int:
        """Counts number of sentences."""
        return len(self.sentences())

    @_cache
    def avr_word_per_sent(self) -> float:
        """Counts average sentence length in words."""
        return self.ru_word_count() / self.sent_count()

    @_cache
    def avr_let_per_word(self) -> float:
        return self.ru_let_count() / self.ru_word_count()

    @_cache
    def avr_syl_per_word(self) -> float:
        return self.ru_syl_count() / self.ru_word_count()

    @_cache
    def ru_word_count(self) -> int:
        """Counts the number of russian words."""
        return self._tlist.count(WORD_RU)

    @_cache
    def ru_syl_count(self) -> int:
        """Counts the number of syllables of all russian words."""
        return sum(map(ru_syl_count, self.ru_words()))

    @_cache
    def ru_let_count(self) -> int:
        """Counts the number of russian letters."""
        count = 0
        for n in self.ru_words():
            for c in n.body.lower():
                if c in ru_alphabet:
                    count += 1
        return count

    @_cache
    def dig_count(self):
        """Counts the number of digits."""
        count = 0
        for n in self.numbers():
            for c in n.body:
                if c in digits:
                    count += 1
        return count

    def ARI(self):
        """Automated readability index"""
        C = self.ru_let_count() + self.dig_count()
        W = self.ru_word_count()
        S = self.sent_count()
        return 6.26 * C / W + 0.2805 * W / S - 31.04

    def FRES(self):
        """Flesch reading-ease score"""
        ASL = self.avr_word_per_sent()
        ASW = self.avr_syl_per_word()
        return 206.835 - 1.3 * ASL - 60.1 * ASW

    def FKGL(self):
        """Flesch–Kincaid grade level"""
        ASL = self.avr_word_per_sent()
        ASW = self.avr_syl_per_word()
        return 0.5 * ASL + 8.4 * ASW - 15.59

    def CLI(self):
        """Coleman — Liau index"""
        L = self.avr_let_per_word() * 100
        S = 100 / self.avr_word_per_sent()
        return 0.055 * L - 0.35 * S - 20.33

    def longest_sent(self) -> TList:
        return deepcopy(max(self.sentences(), key=len))




def interp(index: str, val: float):
    """Returns explanation message for given index value."""
    match index:
        case 'FRES':
            if val > 100:
                return "Extremely high readability (<5th grade)."
            if 90 < val <= 100:
                return "Very high readability (5th grade)."
            if 80 < val <= 90:
                return "High readability (6th grade)."
            if 70 < val <= 80:
                return "Above average readability (7th grade)."
            if 60 < val <= 70:
                return "Average readability (8-9th grade)."
            if 50 < val <= 60:
                return "Below average readability (10-12th grade)."
            if 30 < val <= 50:
                return "Low readability (University student)."
            if 0 < val <= 30:
                return "Very low readability (Graduate)."
            if val <= 0:
                return "Extremely low readability (Above graduate)."

        case 'ARI' | 'CLI' | 'FKGL':
            v = round(val)
            if v < 1:
                return "Readability age: <6 (Kindergarten)."
            if v > 12:
                return "Readability age: >18 (University student and above)."
            return f"Readability age: {v+5}-{v+6} (Grade: {v})."