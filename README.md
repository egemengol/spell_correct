# Spell Correct

Spell Correct is a Python program for isolated spelling correction. Tries to correct words into the nearest 1-edit distance word. If no candidate is found, outputs an empty line.


## Usage
The recommended way to use is using stdin and stdout. 

`simple` or `smooth` explicit choice is left to the user, `smooth` refers to 'Laplacian smoothing'.

`-corpus` and `-spell-errors` can be skipped since they default to `corpus.txt` and `spell-errors.txt` files, respectively.
```terminal
$ python3 main.py -corpus corpus.txt -spell-errors spell-errors.txt smooth < test-words-misspelled.txt > output.txt
```

The help dialog:
```terminal
$ python3 main.py --help
usage: main.py [-h] [-corpus CORPUS] [-spell-errors SPELL_ERRORS]
               {simple,smooth} [FILE [FILE ...]]

positional arguments:
  {simple,smooth}       Choose one of the probabilistic methods.
  FILE                  Files to read and correct, line by line. If empty,
                        stdin is used.

optional arguments:
  -h, --help            show this help message and exit
  -corpus CORPUS        When you want to change the corpus.
  -spell-errors SPELL_ERRORS
                        When you want to change the spell-errors.txt.
```

This program can also be used like this:
```terminal
$ python3 main.py -corpus corpus.txt -spell-errors spell-errors.txt smooth test-words-misspelled.txt
ability
abroad
academic
accession
...
...
will
wonderful
worth
would
```

## Acknowledgement
This project is based on the blog entry of Peter Norvig, [How to Write a Spelling Corrector](http://norvig.com/spell-correct.html).

The [requirements](./cmpe493-assignment1-specification.pdf) are set by [Arzucan Özgür](https://www.cmpe.boun.edu.tr/~ozgur/) intended for the first assignment of  
"CMPE 493 - Introduction to Information Retrieval"

## License
[MIT](https://choosealicense.com/licenses/mit/)