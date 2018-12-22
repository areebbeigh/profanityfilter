.. profanityfilter documentation master file, created by
   sphinx-quickstart on Mon Dec  3 15:09:51 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ProfanityFilter Documentation
==============================

ProfanityFilter is a universal python library for detecting and filtering profanity in text.

Quick Start
===========

.. code-block:: python3

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

ProfanityFilter also comes with a simple command line utility. ``profanityfilter -h`` for more details.


Installing ProfanityFilter
==========================
You can install profanityfilter using pip.

``> pip install profanityfilter``


Using a Custom List
===================
You can use a custom list of bad words in profanityfilter the following two ways:

- During instantiation:

.. code-block:: python3

    from profanityfilter import ProfanityFilter

    with open("custom_words.txt", "r") as f:
        custom_list = [l.replace("\n", "") for l in f.readlines()]

    pf_custom = ProfanityFilter(custom_censor_list = custom_list)

- After instantiation:

.. code-block:: python3

    from profanityfilter import ProfanityFilter
    
    pf_custom = ProfanityFilter()

    with open("custom_words.txt", "r") as f:
        custom_list = [l.replace("\n", "") for l in f.readlines()]

    pf.define_words(custom_list)

.. note::
    Using a custom censor list means that profanityfilter will not use the default censor list.
    If you're looking for a way to add additional bad words to the list, see :ref:`Adding Bad Words`


Adding Bad Words
================
You can use an additional list of words in conjunction with the default words in profanityfilter.

- During instantiation:

.. code-block:: python3

    from profanityfilter import ProfanityFilter

    with open("more_words.txt", "r") as f:
        more_words = [l.replace("\n", "") for l in f.readlines()]

    pf = ProfanityFilter(extra_censor_list = more_words)

- After instantiation:

.. code-block:: python3

    from profanityfilter import ProfanityFilter
    
    pf = ProfanityFilter()

    with open("more_words.txt", "r") as f:
        more_words = [l.replace("\n", "") for l in f.readlines()]

    pf.append_words(more_words)


Words Boundaries
================
By default, profanityfilter applies word boundries to bad words during censoring. 
Therefore, the default behaviour of profanityfilter is to ignore bad words `inside` words.

`Example:`

.. code-block:: python3

    from profanityfilter import ProfanityFilter

    pf = ProfanityFilter()

    pf.censor("My username is fuckyouusername@bitch.com")
    > "My username is fuckyouusername@*****.com"

To avoid this behaviour you can pass a no_word_boundaries keyword to ProfanityFilter telling it
to detect bad words inside words.

.. code-block:: python3

    from profanityfilter import ProfanityFilter

    pf = ProfanityFilter(no_word_boundaries = True)

    pf.censor("My username is fuckyouusername")
    > "My username is ****youusername@*****.com"

.. note::

    Without word boundaries there's a risk of censoring non-harmful words. 
    For example `fun` is censored to `**n` when `fu` is in the censor list. 
    To avoid this behavior, you can either come up with custom censor lists or use different instances of profanityfilter accordingly.


API Reference
=============

.. automodule:: profanityfilter.profanityfilter
    :members:
    :undoc-members:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
