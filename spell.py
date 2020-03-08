import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Optional, Tuple, DefaultDict, Set
import random
from sys import stderr

random.seed(17)


class Spell:
    # Smoothing variable
    alpha = 1

    # Weighing the spell-errors and corpus.
    # Determined by hand regarding the test set.
    ERROR_COEFFICIENT = 30

    # Using the spell-errors corrections in the corpus
    # in a weighted manner.
    # ~8k words!
    SPELL_ERROR_TRUST = 3

    def __init__(self, corpus: Path, prob_type: str, spell_errors: Path):
        self.prepare_corpus(corpus, prob_type)
        
        self.prepare_spell_error_dict(spell_errors)

        self.f = self.P_simple if prob_type.lower() == "simple" else self.P_smooth

    def prepare_corpus(self, corpus: Path, prob_type: str):
        """Read the corpus file, count every token."""
        self.words = Counter(
            re.findall(r'\w+', open(corpus).read().lower()))
        # corpus size
        self.N = float(sum(self.words.values()))
        # used for size in smoothing
        self.Nplus = self.N + self.alpha * (len(self.words)+1)

        # for using the spell-errors corrections in the corpus.
        if hasattr(self, "errors"):
            for v_l in self.errors.values():
                for v in v_l:
                    self.words[v] += self.SPELL_ERROR_TRUST

    def prepare_spell_error_dict(self, path: Path):
        """Read the spell-error file,
        keep them in their counters for every misspelled word."""
        self.errors: DefaultDict[Counter] = defaultdict(Counter)
        self.N_error: float = 0

        with open(path, "r") as f:
            for line in f.readlines():
                target, s = line.split(": ", maxsplit=1)
                tokens = s.split(", ")
                for mis in tokens:
                    pair = mis.rstrip().split("*")
                    mis = pair[0]
                    weight = int(pair[1]) if len(pair) == 2 else 1
                    self.errors[mis][target] += weight
    
        count = 0
        for v_l in self.errors.values():
            for v in v_l:
                count += 1
                # for using the spell-errors corrections in the corpus.
                if hasattr(self, "words"):
                    self.words[v] += self.SPELL_ERROR_TRUST

        self.N_error = float(count)

    def P_simple(self, word): 
        """Probability of `word`."""
        return self.words[word] / self.N

    def P_smooth(self, word):
        """Smoothed probability of `word`"""
        return (self.words[word] + self.alpha) / self.Nplus

    def max_from_corpus(self, word) -> Optional[Tuple[str, float]]:
        """Best suggestion and its probability from corpus."""
        candids = self.candidates(word)
        if not candids:
            return "", 0
        maxes: Set[str] = set()
        cur_max_prob = 0
        for c in candids:
            cur_prob = self.f(c)
            if cur_prob > cur_max_prob:
                maxes = set([c])
                cur_max_prob = cur_prob
        return random.choice(list(maxes)), cur_max_prob

    def max_from_spell_errors(self, word) -> Optional[Tuple[str, float]]:
        """Best suggestion and its probability from spell-errors."""
        spelling_error_counter = self.errors[word]
        spelling_common = spelling_error_counter.most_common(1)
        if spelling_common:
            maxes = [(key, value) for key, value in spelling_error_counter.items() if value == spelling_common[0][1]]
            key, value = random.choice(maxes)
            value /= self.N_error
            value = value * self.ERROR_COEFFICIENT
        else:
            key, value = "", 0
        return key, value

    def correct(self, word): 
        """Most probable spelling correction for word."""

        is_word_known = word in self.words
        if is_word_known:
            return word

        best_word, prob = self.max_from_corpus(word)
        key, value = self.max_from_spell_errors(word)

        if prob > value:
            return best_word
        else:
            return key

    def candidates(self, word):
        """Generate possible spelling corrections for word."""
        return self.known([word]) or self.known(self.edits1(word))

    def known(self, words):
        """The subset of `words` that appear in the dictionary of WORDS."""
        return set(w for w in words if w in self.words)

    @staticmethod
    def edits1(word: str):
        """All edits that are one edit away from `word`."""
        letters    = 'abcdefghijklmnopqrstuvwxyz'
        splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
        deletes    = [L + R[1:]               for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
        inserts    = [L + c + R               for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)
