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
> wget https://cgit.freedesktop.org/libreoffice/dictionaries/plain/en/en_US.dic
> wget https://cgit.freedesktop.org/libreoffice/dictionaries/plain/en/en_US.aff
> mv en_US.aff en.aff
> mv en_US.dic en.dic
```

Then use profanity filter as usual:
```
from profanityfilter import ProfanityFilter

pf = ProfanityFilter()

pf.censor("fuckfuck")
> "********"

pf.censor("oofucksoo")
> "oo*****oo"
```

## Pymorphy2
For Russian and Ukranian languages to achieve better results we suggest you to install `pymorphy2`. For Russian language do:
```
> pip install pymorphy2 pymorphy2-dicts-ru
```

# Console Executable

```
profanityfilter -h
> usage: profanityfilter-script.py [-h] [-t TEXT | -f PATH] [-o OUTPUT_FILE]
>                                  [--show]
>
> Profanity filter console utility
>
> optional arguments:
>   -h, --help            show this help message and exit
>   -t TEXT, --text TEXT  Test the given text for profanity
>   -f PATH, --file PATH  Test the given file for profanity
>   -o OUTPUT_FILE, --output OUTPUT_FILE
>                         Write the censored output to a file
>   --show                Print the censored text
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
