#!/usr/bin/env python3
import json
import tempfile
from collections import defaultdict, Counter
from pathlib import Path
from typing import Tuple, List, Dict, Set
import subprocess
from enum import Enum
import numpy as np
import pandas as pd
from argparse import ArgumentParser


alphabet = '_abcdefghijklmnopqrstuvwxyz'


class Operation(Enum):
	INSERT = "insert"
	DELETE = "delete"
	TRANSPOSE = "transpose"
	REPLACE = "replace"
	TABLE = "table"
	NO_OP = "no_op"


def operation(user, system) -> Tuple[Operation, str, str]:
	"""
	For finding what transformation happened, also gives confusion parameters.

	For REPLACE x -> y ==> (x, y)
	For TRANSPOSE xy -> yx ==> (x, y)
	For INSERT x -> xy ==> (x, y)
	For DELETE xy -> x ==> (x, y)

	For INSERT and DELETE, gives '_' for x if start of the word.

	NO_OP refers to no change, already correct.
	TABLE refers to spell-errors lookup. Correction uses the table.
	"""
	if user == system:
		return Operation.NO_OP, "", ""

	len_user = len(user)
	len_sys = len(system)
	if len_user == len_sys:
		# REPLACE or TRANSPOSE ?
		for i in range(len_user):
			if user[i] != system[i]:
				# found
				us = user[i:i + 2]
				sy = system[i:i + 2]
				if len(us) == 2:
					if us[1] == sy[0] and us[0] == sy[1]:
						return Operation.TRANSPOSE, us[0], sy[0]
					elif us[1] == sy[1]:
						return Operation.REPLACE, us[0], sy[0]
					# TABLE.
					else:
						return Operation.TABLE, "", ""
				else:
					return Operation.REPLACE, us[0], sy[0]
	elif len_user + 1 == len_sys:
		# INSERT ?
		if user == system[1:]:
			return Operation.INSERT, "_", system[0]
		for i in range(len_user):
			if user[i + 1:] == system[i + 2:]:
				return Operation.INSERT, system[i], system[i + 1]
	elif len_sys + 1 == len_user:
		# DELETE ?
		if user[1:] == system:
			return Operation.DELETE, "_", user[0]
		for i in range(len_sys):
			if user[i + 2:] == system[i + 1:]:
				return Operation.DELETE, user[i], user[i + 1]
	# TABLE.
	return Operation.TABLE, "", ""


def confusions(corrections: List[Tuple[str, str]]) -> Dict[Operation, pd.DataFrame]:
	"""
	Emits four matrices containing confusion matrices.
	"""
	len_alph = len(alphabet)
	matrices = {
		Operation.INSERT: np.zeros((len_alph, len_alph), dtype=np.uint16),
		Operation.DELETE: np.zeros((len_alph, len_alph), dtype=np.uint16),
		Operation.TRANSPOSE: np.zeros((len_alph, len_alph), dtype=np.uint16),
		Operation.REPLACE: np.zeros((len_alph, len_alph), dtype=np.uint16),
	}

	for user, system in corrections:
		op, i_s, j_s = operation(user, system)

		if op not in [
			Operation.INSERT,
			Operation.DELETE,
			Operation.TRANSPOSE,
			Operation.REPLACE,
		]: continue

		i = alphabet.find(i_s)
		j = alphabet.find(j_s)
		matrices[op][i][j] += 1

	for op, arr in matrices.items():
		matrices[op] = pd.DataFrame(data=arr, index=list(alphabet), columns=list(alphabet))

	return matrices


def accuracy_set(corrections: List[Tuple[str, str, Set[str]]]):
	"""
	For accuracy parameters.
	"""
	counts = {
		True: {
			"edit": 0,
			"table": 0,
			"no_op": 0,
		},
		False: {
			"edit": 0,
			"table": 0,
			"no_op": 0,
		},
		None: 0,
	}

	for user, system, references in corrections:
		if system == "":
			counts[None] += 1
			continue
		op, _, _ = operation(user, system)
		d = counts[system in references]
		if op == Operation.TABLE:
			d["table"] += 1
		elif op == Operation.NO_OP:
			d["no_op"] += 1
		else:
			d["edit"] += 1

	return counts


def accuracy(corrections: List[Tuple[str, str, str]]) -> Dict[bool, Dict[str, int]]:
	"""
	For accuracy parameters.
	"""
	counts = {
		True: {
			"edit": 0,
			"table": 0,
			"no_op": 0,
		},
		False: {
			"edit": 0,
			"table": 0,
			"no_op": 0,
		},
		None: 0,
	}

	for user, system, ref in corrections:
		if system == "":
			counts[None] += 1
			continue
		op, _, _ = operation(user, system)
		d = counts[system == ref]
		if op == Operation.TABLE:
			d["table"] += 1
		elif op == Operation.NO_OP:
			d["no_op"] += 1
		else:
			d["edit"] += 1

	return counts


def get_user_references_from_spell_errors(spell_errors_path: Path) -> List[Tuple[str, Set[str]]]:
	"""
	Reads spell-errors.txt and creates [mistype -> {correction suggestion set}]
	Multiple suggestions are chosen because spell-errors document sometimes contradicts itself,
	if correction is in most-suggested set then it is counted correct.
	"""
	spell_errors = defaultdict(Counter)
	with open(spell_errors_path, "r") as f:
		for line in f.readlines():
			target, s = line.split(": ", maxsplit=1)
			tokens = s.split(", ")
			for mis in tokens:
				pair = mis.rstrip().split("*")
				mis = pair[0]
				weight = int(pair[1]) if len(pair) == 2 else 1
				spell_errors[mis][target] += weight

	user_references: List[Tuple[str, List[str]]] = list()

	for us, counter in spell_errors.items():
		max_count = counter.most_common(1)[0][1]
		best_refs = {key for (key, val) in counter.items() if val == max_count}
		user_references.append((us, best_refs))

	return user_references


def get_system_from_user(
		users: List[str],
		corpus_path:Path,
		spell_errors_path: Path,
		smooth_type: str
) -> List[str]:
	"""
	Runs the spelling error correction program.
	"""
	with tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8") as in_f:
		for user in users:
			in_f.write(user)
			in_f.write("\n")
		in_f.flush()

		spell_corrector = subprocess.run([
			"python",
			"main.py",
			"-corpus", corpus_path,
			"-spell-errors", spell_errors_path,
			smooth_type,
			in_f.name,
		],
			capture_output=True,
			check=True,
			encoding="utf-8",
		)

	return [line.rstrip() for line in spell_corrector.stdout.splitlines()]

def measure_spell_errors(
		spell_errors_path,
		corpus_path,
		out_dir_path: Path,
		smooth_type,
	):
	"""
	Measure how well the system performs over the corrections in the spell-errors document.
	Produces files.
	"""
	user_references = get_user_references_from_spell_errors(spell_errors_path)

	system = get_system_from_user(
		[u for (u, _) in user_references],
		corpus_path,
		spell_errors_path,
		smooth_type,
	)

	corrections = [(user, sy, refs) for ((user, refs), sy) in zip(user_references, system)]
	conversions = [(user, sy) for (user, sy, _) in corrections]

	matrices = confusions(conversions)
	for op, df in matrices.items():
		df.to_csv(out_dir_path / f"spellerrors_{smooth_type}_{op.value}.csv")

	with open(out_dir_path / f"spellerrors_{smooth_type}_accuracy.json", "w") as f:
		acc = accuracy_set(corrections)
		json.dump(acc, f, indent=2)


def get_user_refs_from_test_set(misspell_path: Path, correct_path: Path) -> List[Tuple[str, str]]:
	"""
	Reads the test set
	"""
	with open(misspell_path) as m:
		user = [ line.rstrip() for line in m.readlines()]
	with open(correct_path) as c:
		ref = [line.rstrip() for line in c.readlines()]
	return [t for t in zip(user, ref)]


def measure_test_set(
		misspell_path: Path,
		correct_path: Path,
		corpus_path: Path,
		smooth_type: str,
		spell_errors_path: Path,
		out_dir_path: Path,
	):
	"""
	Measures the performance of the program over the test set.
	"""
	user_ref = get_user_refs_from_test_set(misspell_path, correct_path)

	system = get_system_from_user(
		[u for (u, _) in user_ref],
		corpus_path,
		spell_errors_path,
		smooth_type,
	)

	corrections = [(user, sy, ref) for ((user, ref), sy) in zip(user_ref, system)]
	conversions = [(user, sy) for (user, sy, _) in corrections]

	matrices = confusions(conversions)
	for op, df in matrices.items():
		df.to_csv(out_dir_path / f"testset_{smooth_type}_{op.value}.csv")

	with open(out_dir_path / f"testset_{smooth_type}_accuracy.json", "w") as f:
		acc = accuracy(corrections)
		json.dump(acc, f, indent=2)


def measure(
		misspell_path: Path = Path("./data/test-words-misspelled.txt"),
		correct_path: Path = Path("./data/test-words-correct.txt"),
		spell_errors_path: Path = Path("./data/spell-errors.txt"),
		corpus_path: Path = Path("./data/corpus.txt"),
		out_dir_path: Path = Path("./measurements/"),
		what: str = "all",
	):
	for smooth in ["simple", "smooth"]:
		if what != "testset":
			measure_spell_errors(
				spell_errors_path=spell_errors_path,
				corpus_path=corpus_path,
				out_dir_path=out_dir_path,
				smooth_type=smooth,
			)
		if what != "spellerror":
			measure_test_set(
				spell_errors_path=spell_errors_path,
				misspell_path=misspell_path,
				correct_path=correct_path,
				corpus_path=corpus_path,
				smooth_type=smooth,
				out_dir_path=out_dir_path,
			)


if __name__ == "__main__":
	parser = ArgumentParser()
	parser.add_argument(
		"what",
		choices=["all", "testset", "spellerror"],
		default="all",
		help="Measurement selection."
	)
	parser.add_argument(
		"-corpus",
		type=Path,
		help="Specify the 'corpus.txt' path.",
		default=Path("./data/corpus.txt"),
	)
	parser.add_argument(
		"-spell_errors",
		type=Path,
		help="Specify the 'spell-errors.txt' path.",
		default=Path("./data/spell-errors.txt"),
	)
	parser.add_argument(
		"-test_correct",
		type=Path,
		help="Specify the 'test-words-correct.txt' path.",
		default=Path("./data/test-words-correct.txt"),
	)
	parser.add_argument(
		"-test_misspelled",
		type=Path,
		help="Specify the 'test-words-misspelled.txt' path.",
		default=Path("./data/test-words-misspelled.txt"),
	)
	parser.add_argument(
		"-out_dir",
		type=Path,
		help="Specify the 'measurements' path.",
		default=Path("./measurements/"),
	)

	args = parser.parse_args()

	measure(
		misspell_path=args.test_misspelled,
		correct_path=args.test_correct,
		spell_errors_path=args.spell_errors,
		corpus_path=args.corpus,
		out_dir_path=args.out_dir,
		what=args.what,
	)
