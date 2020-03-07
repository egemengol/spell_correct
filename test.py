#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import NamedTuple
import subprocess


class MisCorrection(NamedTuple):
	input: str
	correction: str
	supposed: str

	def __str__(self):
		return f"{self.input:<16} ❌ {self.correction:<16} ✔ {self.supposed}"


def case_generator(misspells="test-words-misspelled.txt", corrects="test-words-correct.txt"):
	with open(misspells, "r") as m:
		with open(corrects, "r") as c:
			while True:
				mis = m.readline().rstrip()
				cor = c.readline().rstrip()
				if mis == "" or cor == "":
					break
				yield mis, cor


def test(simple_or_smooth):
	spell_corrector = subprocess.run([
		"python",
		"main.py",
		simple_or_smooth,
		"test-words-misspelled.txt",
	],
		capture_output=True,
		check=True,
	)

	stdout_iter = iter(spell_corrector.stdout.decode('utf-8').splitlines())

	total = 0
	miscs = list()

	for (user_input, supposed), corrected in zip(case_generator(), stdout_iter):
		misc = MisCorrection(
			user_input,
			corrected,
			supposed,
		)
		if misc.supposed != misc.correction:
			miscs.append(misc)
		if misc.input == "" or misc.supposed == "":
			break
		total += 1

	with open(simple_or_smooth+".txt", "w") as f:
		f.writelines((str(m)+"\n" for m in miscs))
		f.write("\n")
		f.write(str(MisCorrection(
			"INPUT",
			"MIS-CORRECTION",
			"CORRECT",
		)))
		f.write("\n")
		f.write(f"\n{len(miscs)} mis-corrections, {total} total.\n\n")

	
test("simple")
test("smooth")
