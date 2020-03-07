#!/usr/bin/env python3

from spell import Spell
from pathlib import Path
import fileinput
from argparse import ArgumentParser
from typing import List

def main(
    corpus: Path = Path("corpus.txt"),
    prob_type: str = "smooth",
    files: List[str] = [],
    spell_errors: Path = Path("spell-errors.txt"),
):
    speller = Spell(
        corpus=corpus,
        prob_type=prob_type,
        spell_errors=spell_errors)

    for line in fileinput.input(files):
        print(speller.correct(line.rstrip()))


if __name__ == "__main__":
    choices = ["simple", "smooth"]

    parser = ArgumentParser()
    parser.add_argument(
        "prob_type",
        type=str,
        choices=choices,
        help="Choose one of the probabilistic methods.",
    )
    parser.add_argument(
        "files",
        metavar='FILE',
        nargs='*',
        help="Files to read. If empty, stdin is used."
    )
    parser.add_argument(
        "-corpus",
        type=Path,
        default="corpus.txt",
        help="When you want to change the corpus.",
    )
    parser.add_argument(
        "-spell-errors",
        type=Path,
        default="spell-errors.txt",
        help="When you want to change the spell-errors.txt.",
    )
    args = parser.parse_args()

    main(
        corpus=args.corpus,
        prob_type=args.prob_type,
        files=args.files,
        spell_errors=args.spell_errors,
    )