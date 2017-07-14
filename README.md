# profanityfilter
[![Build Status](https://travis-ci.org/areebbeigh/profanityfilter.svg?branch=master)](https://travis-ci.org/areebbeigh/profanityfilter)

A universal Python library for detecting and/or filtering profane words.

<img src="https://pixabay.com/static/uploads/photo/2014/03/24/13/47/swearing-294391_960_720.png" height="300px" width="250px">

<b>PyPI:</b> https://pypi.python.org/pypi/profanityfilter<br>
<b>Doc:</b> http://pythonhosted.org/profanityfilter

# Installation

`> pip install profanityfilter`

# Usage

```
from profanityfilter import ProfanityFilter

pf = Profanityfilter()

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
I encourage you to fork this repo and expand it in anyway you like. Pull requests are welcomed!

# Additional Info
Developer: Areeb Beigh <areebbeigh@gmail.com><br>
GitHub Repo: https://github.com/areebbeigh/profanityfilter/
