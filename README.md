# Spell Correct

Spell Correct is a Python program for isolated spelling correction. Tries to correct words into the nearest 1-edit distance word. If no candidate is found, outputs an empty line.

Uses a corpus as well as a hand-corrected correction-list.

Two python executables are `main.py` and `measure.py`, both providing useful `--help` dialogs.  
`main.py` uses `stdin` and `stdout` for corrections.  
`measure.py` produces files into the `./measurements/` folder.

You can also read [the report](./pdfs/report.pdf).

[GitHub link](https://github.com/egemengol/spell_correct)

## Usage
The recommended way to use is using stdin and stdout. 

`simple` or `smooth` explicit choice is left to the user, `smooth` refers to 'Laplacian smoothing'.

This is how you can use the program:
```terminal
$ python3 main.py -corpus ./data/corpus.txt -spell-errors ./data/spell-errors.txt simple < ./data/test-words-misspelled.txt > output.txt
```
`-corpus` and `-spell-errors` can be skipped since they default to `./data/corpus.txt` and `./data/spell-errors.txt` files, respectively.

```terminal
$ python3 main.py smooth < ./data/test-words-misspelled.txt > output.txt
```

Inputs can be directly supplied as a file argument as follows:
```terminal
$ python3 main.py -corpus ./data/corpus.txt -spell-errors ./data/spell-errors.txt smooth ./data/test-words-misspelled.txt
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

### Taking Measurements
For measurements, `simple` and `smooth` probability functions are both calculated.

Confusion matrices are produced over the correctly corrected, edit-distance=1 words like:
```
For REPLACE x -> y ==> (x, y)
For TRANSPOSE xy -> yx ==> (x, y)
For INSERT x -> xy ==> (x, y)
For DELETE xy -> x ==> (x, y)

For INSERT and DELETE, gives '_' for x if start of the word.
```

Accuracy measures are calculated for both correct or incorrect suggestions,
and with which method they have been suggested.

First, run this for installing dependencies `numpy` and `pandas`:
```terminal
$ pip3 install -r requirements.txt
```

To take all the measurements, run:
```terminal
$ python3 measure.py all
```

For detailed usage, see the `--help` dialog.

## Acknowledgement
This project is based on the blog entry of Peter Norvig, [How to Write a Spelling Corrector](http://norvig.com/spell-correct.html).

The [requirements](pdfs/cmpe493-assignment1-specification.pdf) are set by [Arzucan Özgür](https://www.cmpe.boun.edu.tr/~ozgur/) intended for the first assignment of  
"CMPE 493 - Introduction to Information Retrieval"

## License
[MIT](https://choosealicense.com/licenses/mit/)
