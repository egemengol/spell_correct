import re
from collections import Counter
from pathlib import Path
import pickle
from typing import Optional
import random

random.seed(13)


def get_spell_error_dict(path: Path):
    pass
    # TODO


class Spell:
    alpha = 1
    def __init__(self, corpus: Path, prob_type: str, spell_errors: Path):
        self.words = Counter(
            re.findall(r'\w+', open(corpus).read().lower()))
        self.N = float(sum(self.words.values()))
        self.Nplus = self.N + self.alpha * (len(self.words)+1)

        self.f = self.P_simple if prob_type.lower() == "simple" else self.P_smooth

    def P_simple(self, word): 
        "Probability of `word`."
        return self.words[word] / self.N

    def P_smooth(self, word):
        return (self.words[word] + self.alpha) / self.Nplus

    def correct(self, word): 
        "Most probable spelling correction for word."
        candids = self.candidates(word)
        if not candids:
            return ""
        maxes = set()
        cur_max_prob = 0
        for c in candids:
            cur_prob = self.f(c)
            if cur_prob > cur_max_prob:
                maxes = set([c])
                cur_max_prob = cur_prob
        return random.choice(list(maxes))

    def candidates(self, word): 
        "Generate possible spelling corrections for word."
        return (self.known([word]) or self.known(self.edits1(word)))

    def known(self, words): 
        "The subset of `words` that appear in the dictionary of WORDS."
        return set(w for w in words if w in self.words)

    @staticmethod
    def edits1(word: str):
        "All edits that are one edit away from `word`."
        letters    = 'abcdefghijklmnopqrstuvwxyz'
        splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
        deletes    = [L + R[1:]               for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
        inserts    = [L + c + R               for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)
