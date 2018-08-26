# profanityfilter
[![Build Status](https://travis-ci.org/areebbeigh/profanityfilter.svg?branch=master)](https://travis-ci.org/areebbeigh/profanityfilter)

A universal Python library for detecting and/or filtering profane words.

<img src="https://pixabay.com/static/uploads/photo/2014/03/24/13/47/swearing-294391_960_720.png" height="300px" width="250px">

<b>PyPI:</b> https://pypi.python.org/pypi/profanityfilter<br>
<b>Doc:</b> https://areebbeigh.github.io/profanityfilter/

# Installation
For English:
```
> pip install profanityfilter
> python -m spacy download en  # Download Spacy model for tokenization and lemmatization
```

For more info about Spacy models read: https://spacy.io/usage/models/.

# Usage

```
from profanityfilter import ProfanityFilter

pf = ProfanityFilter()

pf.censor("That's bullshit!")
> "That's ********!"
pf.set_censor("@")
pf.censor("That's bullshit!")
> "That's @@@@@@@@!"
pf.define_words(["icecream", "choco"])
pf.censor("I love icecream and choco!")
> "I love ******** and *****"
pf.is_clean("That's awesome!")
> True
pf.is_clean("That's bullshit!")
> False
pf.is_profane("Profane shit is not good")
> True

pf_custom = ProfanityFilter(custom_censor_list=["chocolate", "orange"])
pf_custom.censor("Fuck orange chocolates")
> "Fuck ****** **********"

pf_extended = ProfanityFilter(extra_censor_list=["chocolate", "orange"])
pf_extended.censor("Fuck orange chocolates")
> "**** ****** **********"
```

## Deep analysis
Deep analysis detects profane words that are inflected from profane words in profane word dictionary.

To get deep analysis functionality install additional packages and dictionary for your language (English by default).

Firstly, install `hunspell` and `hunspell-devel` packages with your system package manager. Then run:
```
> pip install hunspell python-Levenshtein https://github.com/rominf/pyffs/archive/master.zip
> cd profanityfilter/data
> wget https://cgit.freedesktop.org/libreoffice/dictionaries/plain/en/en_US.aff
> wget https://cgit.freedesktop.org/libreoffice/dictionaries/plain/en/en_US.dic
> mv en_US.aff en.aff
> mv en_US.dic en.dic
```

Then use profanity filter as usual:
```
from profanityfilter import ProfanityFilter

pf = ProfanityFilter()

pf.censor("fuckfuck")
> "********"

pf.censor("oofucksoo", censor_whole_words=False)
> "oo*****oo"
```

## Multilingual support
This library comes with multilingual support, which is enabled automatically after installing `polyglot` package and 
it's requirements for language detection, see https://polyglot.readthedocs.io/en/latest/Installation.html and
https://polyglot.readthedocs.io/en/latest/Detection.html for instructions.

### Add language
Let's take Russian language for example, to show how to add language support.

#### Russian language support
Firstly, we need to provide file `profanityfilter/data/ru_badwords.txt` which contains newline separated list of profane
words. For Russian language it's already present, so we skip file generation.

Next, we need to download appropriate Spacy model. Unfortunately, Spacy model for Russian is not yet ready, 
so we will use English model for tokenization and `hunspell` and `pymorphy2` for lemmatization.

Next, we download dictionaries for deep analysis:
```
> cd profanityfilter/data
> wget https://cgit.freedesktop.org/libreoffice/dictionaries/plain/ru_RU/ru_RU.aff
> wget https://cgit.freedesktop.org/libreoffice/dictionaries/plain/ru_RU/ru_RU.dic
> mv ru_RU.aff ru.aff
> mv ru_RU.dic ru.dic
```

##### Pymorphy2
For Russian and Ukrainian languages to achieve better results we suggest you to install `pymorphy2`.
Let's install `pymorphy2` with Russian dictionary:
```
> pip install pymorphy2 pymorphy2-dicts-ru
```

### Usage
Let's create `ProfanityFilter` to filter Russian and English profanity. 
```
from profanityfilter import ProfanityFilter

pf = ProfanityFilter(languages=['ru', 'en'])

pf.censor("Да бля, это просто shit какой-то!")
> "Да ***, это просто **** какой-то!"
```

Note, that order of languages in `languages` argument does matter. If a tool (profane words list, Spacy model, HunSpell 
dictionary or pymorphy2 dictionary) is not found for a language that was detected for part of text, `profanityfilter` 
library automatically fallbacks to the first suitable language in `languages`.

As a consequence, if you want to filter just Russian profanity, you still need to specify some other language in 
`languages` argument to fallback on for loading Spacy model to perform tokenization, because, as noted before, there is 
no Spacy model for Russian.

# Console Executable

```
profanityfilter -h
usage: profanityfilter-script.py [-h] [-t TEXT | -f PATH] [-l LANGUAGES] [-o OUTPUT_FILE] [--show]

Profanity filter console utility

optional arguments:
  -h, --help            show this help message and exit
  -t TEXT, --text TEXT  Test the given text for profanity
  -f PATH, --file PATH  Test the given file for profanity
  -l LANGUAGES, --languages LANGUAGES
                        Test for profanity using specified languages (comma
                        separated)
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        Write the censored output to a file
  --show                Print the censored text
```

# Contributing

- Fork
- Add changes
- Add unit tests
- Make a pull request :)

I encourage you to fork this repo and expand it in anyway you like. Pull requests are welcomed!

# Additional Info
Developer: Areeb Beigh <areebbeigh@gmail.com><br>
GitHub Repo: https://github.com/areebbeigh/profanityfilter/
