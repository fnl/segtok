======
segtok
======
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

To install this package, you need to have the latest official version of Python installed.
The easiest way to get it installed is using ``pip`` or any other package manager that works with PyPI::

    pip install segtok

Then try the command line tools on some plain-text files (e.g., this README) to see if segtok meets your needs::

    segmenter README.rst | tokenizer

Usage
=====

For details, please refer to the respective documentation; This README only provides an overview of the provided functionality.

A command-line
--------------

After installing the package, two command-line tools will be available, ``segmenter`` and ``tokenizer``.
Each can take UTF-8 encoded plain-text and transforms it into newline-separated sentences or tokens, respectively.
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
In addition, it provides convenience functionality for English texts:
Two compiled patterns (``IS_...``) can be used to detect if a word token contains a possessive-s marker ("Frank's") or is an apostrophe-based contraction ("didn't").
Tokens that match these patterns can then be split using the ``split_possessive_markers`` and ``split_contractions`` functions, respectively.

Legal
=====

License: `MIT <http://opensource.org/licenses/MIT>`_

Copyright (c) 2014, Florian Leitner. All rights reserved.

History
=======

- **1.2.2** made segtok.tokenizer.match protected (renamed to "_match") and fixed UNIX linebreak normalization
- **1.2.1** the length of sentences inside brackets is now parametrized
- **1.2.0** wrote blog_ "documentation" and added chemical formula sub/super-script functionality
- **1.1.2** fixed Unicode list of valid sentence terminals (was missing U+2048)
- **1.1.1** fixed PyPI setup (missing MANIFEST.in for README.rst and "packages" in setup.py)
- **1.1.0** added possessive-s marker and apostrophe contraction splitting of tokens
- **1.0.0** initial release

.. _blog: http://fnl.es/segtok-a-segmentation-and-tokenization-library.html
