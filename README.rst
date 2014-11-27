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
While other Indo-European languages could work, it has only been designed with languages such as Spanish, English, German, Italian, or French in mind.
Extending the provided functionality to more foreign languages (e.g., CJK) might be even trickier.

Usage
=====

For details, please refer to the respective documentation; This README only provides an overview of the provided functionality.

A command-line
--------------

After installing the package, two command-line tools will be available, ``segmenter`` and ``tokenizer``.
Each can take UTF-8 encoded plain-text and transforms it into newline-separated sentences or tokens, respectively.
The latter assumes that each line contains (at most) one single sentence, as output by the former.
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
Tokens that match these patterns can then be split using the ``split_possessive_marker`` and ``split_contraction`` functions, respectively.
