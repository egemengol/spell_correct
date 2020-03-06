# -*- coding: utf-8 -*-


from typing import NamedTuple
import io
import subprocess

"""

def case_generator():
	with open("test-words-misspelled.txt", "r") as m:
		with open("test-words-correct.txt", "r") as c:
			while True:
				case = (m.readline().rstrip(), c.readline().rstrip())
				if case[0] == "" and case[1] == "":
					break
				if case[0] == "" or case[1] == "":
					raise sys.SystemExit("Mismatching input lengths")
				yield case


class Miscorrection(NamedTuple):
	input: str
	correction: str
	supposed: str

	def __str__(self):
		return f"{self.input:<16} ❌ {self.correction:<16} ✔ {self.supposed}"


def test(corr_f):
	total = 0
	miscorrection = 0
	for miss, corr in case_generator():
		total += 1
		out = corr_f(miss)
		if out != corr:
			miscorrection += 1
			# print(Miscorrection(miss, out, corr))
	print(f"{miscorrection} errors, {(1-float(miscorrection)/total)}%\n")


test(correction)

"""

class Miscorrection(NamedTuple):
	input: str
	correction: str
	supposed: str

	def __str__(self):
		return f"{self.input:<16} ❌ {self.correction:<16} ✔ {self.supposed}"


def case_generator(misspells="test-words-misspelled.txt", corrects="test-words-correct.txt"):
	with open("test-words-misspelled.txt", "r") as m:
		with open("test-words-correct.txt", "r") as c:
			while True:
				mis, cor = m.readline().rstrip(), c.readline().rstrip()
				if mis == "" or cor == "":
					break
				yield (mis, cor)


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

	for (input, supposed), corrected in zip(case_generator(), stdout_iter):
		misc = Miscorrection(
			input,
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
		f.write(str(Miscorrection(
			"INPUT",
			"MIS-CORRECTION",
			"CORRECT",
		)))
		f.write("\n")
		f.write(f"\n{len(miscs)} mis-corrections, {total} total.\n\n")

	
test("simple")
test("smooth")