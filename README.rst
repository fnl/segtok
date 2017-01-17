======
segtok
======

.. image:: https://img.shields.io/pypi/v/segtok.svg
    :target: https://pypi.python.org/pypi/segtok

.. image:: https://img.shields.io/pypi/l/segtok.svg

.. image:: https://travis-ci.org/fnl/segtok.svg?branch=master
    :target: https://travis-ci.org/fnl/segtok

-------------------------------------------
Sentence segmentation and word tokenization
-------------------------------------------

The segtok package provides two modules, ``segtok.segmenter`` and ``segtok.tokenizer``.
The segmenter provides functionality for splitting (Indo-European) text into sentences.
The tokenizer provides functionality for splitting (Indo-European) sentences into words and symbols (collectively called *tokens*).
Both modules can also be used from the command-line.
While other Indo-European languages could work, it has only been designed with languages such as Spanish, English, and German in mind.
For a more informed introduction to this tool, please read the article on my blog_.

Install
=======

To use this package, you minimally should have the latest version of Python 2.7 or any 3.3+ branch installed.
The package is expected to work with both Python 2.7 and 3.3+, tested against those latest Python branches, as well as Python 3.3.
The easiest way to get ``segtok`` installed is using ``pip`` or any other package manager that works with PyPI::

    pip3 install segtok

*Important*: If you are on a Linux machine and have problems installing the ``regex`` dependency of ``segtok``, make sure you have the ``python-dev`` and/or ``python3-dev`` packages installed to get the necessary headers to compile the package.

Then try the command line tools on some plain-text files (e.g., this README) to see if ``segtok`` meets your needs::

    segmenter README.rst | tokenizer

Test Suite
==========

The testing environment works with ``pytest``, ``tox`` and ``pyenv``.
You first need to install pyenv_ (on OSX with Homebrew: ``brew install pyenv``), and ``tox`` with ``pytest`` (``pip3 install tox pytest``).
Configuring ``pyenv`` depends on the Python versions you have installed.
Here, we assume you have the latest 2.7 and 3 versions installed and only need to provide an environment for testing ``segtok`` against the 3.3 branch::

    pyenv install 3.3.6
    pyenv global system 3.3.6

The second command is essential and indicates that your preferred Python binary is the system version and then the 3.3.6 branch.
If you forget the second command, you will see errors like ``ERROR: InvocationError: Failed to get version_info for python3.3: pyenv: python3.3: command not found`` when running ``tox``.
If you only have one Python version installed (say, 2.7), to fully run the tests, you must also install and globally configure the other version (e.g., the latest 3.x) with ``pyenv``, too.

Finally, to run all of ``segtok``'s unit-test suite, just run ``tox``::

    tox


Usage
=====

For details, please refer to the respective documentation; This README only provides an overview of the provided functionality.

A command-line
--------------

After installing the package, two command-line tools will be available, ``segmenter`` and ``tokenizer``.
Each can take UTF-8 encoded plain-text and transforms it into newline-separated sentences or tokens, respectively.
You can use other encoding in Python3 simply by reconfiguring your environment encoding or in any version of Python by forcing a particular encoding with the ``--encoding`` parameters.
The tokenizer assumes that each line contains (at most) one single sentence, which is the output format of the segmenter.
To learn more about each tool, please invoke them with their help option (``-h`` or ``--help``).

B ``segtok.segmenter``
----------------------

This module provides several ``split_...`` functions to segment texts into lists of sentences.
In addition, ``to_unix_linebreaks`` *normalizes* linebreaks (including the Unicode linebreak) to newline control characters (``\\n``).
The function ``rewrite_line_separators`` can be used to move (rewrite) the newline separators in the input text so that they are placed at the sentence segmentation locations.

C ``segtok.tokenizer``
----------------------

This module provides several ``..._tokenizer`` functions to tokenize input sentences into words and symbols.
To get the full functionality, use the ``web_tokenizer``, which will split everything "semantically correctly" except for URLs and e-mail addresses.
In addition, it provides convenience functionality for English texts:
Two compiled patterns (``IS_...``) can be used to detect if a word token contains a possessive-s marker ("Frank's") or is an apostrophe-based contraction ("didn't").
Tokens that match these patterns can then be split using the ``split_possessive_markers`` and ``split_contractions`` functions, respectively.

Legal
=====

License: `MIT <http://opensource.org/licenses/MIT>`_

Copyright (c) 2014-2017, Florian Leitner. All rights reserved.

Contributors (kudos):

- Mikhail Korobov (@kmike; port to Python2.7 and Travis CI integration)

History
=======

- **1.5.2** fixed a tokenizer bug when parsing URLs ending with root paths (``/``), prevented sentence splitting after U.K., U.S. and E.U. if followed by upper-case ("U.S. Air Force"), added missing Unicode hyphens and apostrophes, and added test suite setup instructions
- **1.5.1** removed ``count_continuations.py`` discussion from README (was only confusing); the segmenter now can preserve tab-separated text IDs before the text itself when reading from STDIN and then inserts a (tab-separated) sentence ID column for each sentence printed to STDOUT: see ``segmenter`` option ``--with-ids``
- **1.5.0** continuation words have been statistically evaluated and some poor choices removed (leading to more [precise] sentence splitting; see issue #9 by @Klim314 on GitHub)
- **1.4.0** the ``word_tokenizer`` no longer splits on colons between digits (time, references, ...)
- **1.3.1** fixed multiple dangling commas and colons (reported by Jim Geovedi)
- **1.3.0** added Python2.7 support and Travis CI test integration (BIG thanks to Mikhail!)
- **1.2.2** made segtok.tokenizer.match protected (renamed to "_match") and fixed UNIX linebreak normalization
- **1.2.1** the length of sentences inside brackets is now parametrized
- **1.2.0** wrote blog_ "documentation" and added chemical formula sub/super-script functionality
- **1.1.2** fixed Unicode list of valid sentence terminals (was missing U+2048)
- **1.1.1** fixed PyPI setup (missing MANIFEST.in for README.rst and "packages" in setup.py)
- **1.1.0** added possessive-s marker and apostrophe contraction splitting of tokens
- **1.0.0** initial release

.. _blog: http://fnl.es/segtok-a-segmentation-and-tokenization-library.html
.. _pyenv: https://github.com/yyuu/pyenv