#!/usr/bin/env python
"""
Regex-based word tokenizers.

Note that small/full/half-width character variants are *not* covered.
If a text were to contains such characters, normalize it first.
"""
from __future__ import absolute_import, unicode_literals
import codecs
try:
    from html import unescape
except ImportError:
    # Python <= 3.3 doesn't have html.unescape
    try:
        from html.parser import HTMLParser
    except ImportError:
        # Python 2.x
        from HTMLParser import HTMLParser
    unescape = HTMLParser().unescape

from regex import compile, UNICODE, VERBOSE

try:
    from segtok.segmenter import SENTENCE_TERMINALS, HYPHENS
except ImportError:
    # if used as command-line tool
    # noinspection PyUnresolvedReferences
    from .segmenter import SENTENCE_TERMINALS, HYPHENS


__author__ = 'Florian Leitner <florian.leitner@gmail.com>'

APOSTROPHES = '\'\u00B4\u02B9\u02BC\u2019\u2032'
"""All apostrophe-like marks, including the ASCII "single quote"."""

APOSTROPHE = r"[\u00B4\u02B9\u02BC\u2019\u2032]"
"""Any apostrophe-like marks, including "prime" but not the ASCII "single quote"."""

LINEBREAK = r'(?:\r\n|\n|\r|\u2028)'
"""Any valid linebreak sequence (Windows, Unix, Mac, or U+2028)."""

LETTER = r'[\p{Ll}\p{Lm}\p{Lt}\p{Lu}]'
"""Any Unicode letter character that can form part of a word: Ll, Lm, Lt, Lu."""

NUMBER = r'[\p{Nd}\p{Nl}]'
"""Any Unicode number character: Nd or Nl."""

POWER = r'\u207B?[\u00B9\u00B2\u00B3]'
"""Superscript 1, 2, and 3, optionally prefixed with a minus sign."""

SUBDIGIT = r'[\u2080-\u2089]'
"""Subscript digits."""

ALNUM = LETTER[:-1] + NUMBER[1:]
"""Any alphanumeric Unicode character: letter or number."""

HYPHEN = r'[%s]' % HYPHENS

SPACE = r'[\p{Zs}\t]'
"""Any unicode space character plus the (horizontal) tab."""

APO_MATCHER = compile(APOSTROPHE, UNICODE)
"""Matcher for any apostrophe."""

HYPHENATED_LINEBREAK = compile(
    r'({alnum}{hyphen}){space}*?{linebreak}{space}*?({alnum})'.format(
        alnum=ALNUM, hyphen=HYPHEN, linebreak=LINEBREAK, space=SPACE
    ), UNICODE
)
"""
The pattern matches any alphanumeric Unicode character, followed by a hyphen,
a single line-break surrounded by optional (non-breaking) spaces,
and terminates with a alphanumeric character on this next line.
The opening char and hyphen as well as the terminating char are captured in two groups.
"""

IS_POSSESSIVE = compile(r"{alnum}+(?:{hyphen}{alnum}+)*(?:{apo}[sS]|[sS]{apo})$".format(
    alnum=ALNUM, hyphen=HYPHEN, apo="['" + APOSTROPHE[1:]
), UNICODE
)
"""A pattern that matches English words with a possessive s terminal form."""

IS_CONTRACTION = compile(r"{alnum}+(?:{hyphen}{alnum}+)*{apo}(?:d|ll|m|re|s|t|ve)$".format(
    alnum=ALNUM, hyphen=HYPHEN, apo="['" + APOSTROPHE[1:]
), UNICODE
)
"""A pattern that matches tokens with valid English contractions ``'(d|ll|m|re|s|t|ve)``."""


def split_possessive_markers(tokens):
    """
    A function to split possessive markers at the end of alphanumeric (and hyphenated) tokens.

    Takes the output of any of the tokenizer functions and produces and updated list.
    To use it, simply wrap the tokenizer function, for example::

    >>> my_sentence = "This is Fred's latest book."
    >>> split_possessive_markers(word_tokenizer(my_sentence))
    ['This', 'is', 'Fred', "'s", 'latest', 'book', '.']

    :param tokens: a list of tokens
    :returns: an updated list if a split was made or the original list otherwise
    """
    idx = -1

    for token in list(tokens):
        idx += 1

        if IS_POSSESSIVE.match(token) is not None:
            if token[-1].lower() == 's' and token[-2] in APOSTROPHES:
                tokens.insert(idx, token[:-2])
                idx += 1
                tokens[idx] = token[-2:]
            elif token[-2].lower() == 's' and token[-1] in APOSTROPHES:
                tokens.insert(idx, token[:-1])
                idx += 1
                tokens[idx] = token[-1:]

    return tokens


def split_contractions(tokens):
    """
    A function to split apostrophe contractions at the end of alphanumeric (and hyphenated) tokens.

    Takes the output of any of the tokenizer functions and produces and updated list.

    :param tokens: a list of tokens
    :returns: an updated list if a split was made or the original list otherwise
    """
    idx = -1

    for token in list(tokens):
        idx += 1

        if IS_CONTRACTION.match(token) is not None:
            length = len(token)

            if length > 1:
                for pos in range(length - 1, -1, -1):
                    if token[pos] in APOSTROPHES:
                        if 2 < length and pos + 2 == length and token[-1] == 't' and token[pos - 1] == 'n':
                            pos -= 1

                        tokens.insert(idx, token[:pos])
                        idx += 1
                        tokens[idx] = token[pos:]

    return tokens


def _matches(regex):
    """Regular expression compiling function decorator."""
    def match_decorator(fn):
        automaton = compile(regex, UNICODE | VERBOSE)
        fn.split = automaton.split
        fn.match = automaton.match
        return fn

    return match_decorator


@_matches(r'\s+')
def space_tokenizer(sentence):
    """
    For a given input `sentence`, return a list of its tokens.

    Split on Unicode spaces ``\\s+`` (i.e., any kind of **Unicode** space character).
    The separating space characters are not included in the resulting token list.
    """
    return [token for token in space_tokenizer.split(sentence) if token]


@_matches(r'(%s+)' % ALNUM)
def symbol_tokenizer(sentence):
    """
    The symbol tokenizer extends the :func:`space_tokenizer` by separating alphanumerics.

    Separates alphanumeric Unicode character sequences in already space-split tokens.
    """
    return [token for span in space_tokenizer(sentence) for
            token in symbol_tokenizer.split(span) if token]


@_matches(r"""((?:
    # Dots, except ellipsis
    {alnum} \. (?!\.\.)
    | # Comma, surrounded by digits (e.g., chemicals) or letters
    {alnum} , (?={alnum})
    | # Colon, surrounded by digits (e.g., time, references)
    {number} : (?={number})
    | # Hyphen, surrounded by digits (e.g., DNA endings: "5'-ACGT-3'") or letters
    {alnum} {apo}? {hyphen} (?={alnum})  # incl. optional apostrophe for DNA segments
    | # Apostophes, non-consecutive
    {apo} (?!{apo})
    | # ASCII single quote, surrounded by digits or letters (no dangling allowed)
    {alnum} ' (?={alnum})
    | # ASCII single quote after an s and at the token's end
    s ' $
    | # Terminal dimensions (superscript minus, 1, 2, and 3) attached to physical units
    #  size-prefix                 unit-acronym    dimension
    \b [yzafpn\u00B5mcdhkMGTPEZY]? {letter}{{1,3}} {power} $
    | # Atom counts (subscript numbers) and ionization states (optional superscript
    #   2 or 3 followed by a + or -) are attached to valid fragments of a chemical formula
    \b (?:[A-Z][a-z]?|[\)\]])+ {subdigit}+ (?:[\u00B2\u00B3]?[\u207A\u207B])?
    | # Any (Unicode) letter, digit, or the underscore
    {alnum}
    )+)""".format(alnum=ALNUM, apo=APOSTROPHE, power=POWER, subdigit=SUBDIGIT,
                  hyphen=HYPHEN, letter=LETTER, number=NUMBER))
def word_tokenizer(sentence):
    """
    This tokenizer extends the alphanumeric :func:`symbol_tokenizer` by splitting fewer cases:

    1. Dots appearing after a letter are maintained as part of the word, except for the last word
       in a sentence if that dot is the sentence terminal. Therefore, abbreviation marks (words
       containing or ending in a ``.``, like "i.e.") remain intact and URL or ID segments remain
       complete ("www.ex-ample.com", "EC1.2.3.4.5", etc.). The only dots that never are attached
       are triple dots (``...``; ellipsis).
    2. Commas surrounded by alphanumeric characters are maintained in the word, too, e.g. ``a,b``.
       Colons surrounded by digits are maintained, e.g., 'at 12:30pm' or 'Isaiah 12:3'.
       Commas, semi-colons, and colons dangling at the end of a token are always spliced off.
    3. Any two alphanumeric letters that are separated by a single hyphen are joined together;
       Those "inner" hyphens may optionally be followed by a linebreak surrounded by spaces;
       The spaces will be removed, however. For example, ``Hel- \\r\\n \t lo`` contains a (Windows)
       linebreak and will be returned as ``Hel-lo``.
    4. Apostrophes are always allowed in words as long as they are not repeated; The single quote
       ASCII letter ``'`` is only allowed as a terminal apostrophe after the letter ``s``,
       otherwise it must be surrounded by letters. To support DNA and chemicals, a apostrophe
       (prime) may be located before the hyphen, as in the single token "5'-ACGT-3'" (if any
       non-ASCII hyphens are used instead of the shown single quote).
    5. Superscript 1, 2, and 3, optionally prefixed with a superscript minus, are attached to a
       word if it is no longer than 3 letters (optionally 4 if the first letter is a power prefix
       in the range from yocto, y (10^-24) to yotta, Y (10^+24)).
    6. Subscript digits are attached if prefixed with letters that look like a chemical formula.
    """
    pruned = HYPHENATED_LINEBREAK.sub(r'\1\2', sentence)
    tokens = [token for span in space_tokenizer(pruned) for
              token in word_tokenizer.split(span) if token]

    # splice the sentence terminal off the last word/token if it has any at its borders
    # only look for the sentence terminal in the last three tokens
    for idx, word in enumerate(reversed(tokens[-3:]), 1):
        if (word_tokenizer.match(word) and not APO_MATCHER.match(word)) or \
                any(t in word for t in SENTENCE_TERMINALS):
            last = len(word) - 1

            if 0 == last or u'...' == word:
                # any case of "..." or any single char (last == 0)
                pass  # leave the token as it is
            elif any(word.rfind(t) == last for t in SENTENCE_TERMINALS):
                # "stuff."
                tokens[-idx] = word[:-1]
                tokens.insert(len(tokens) - idx + 1, word[-1])
            elif any(word.find(t) == 0 for t in SENTENCE_TERMINALS):
                # ".stuff"
                tokens[-idx] = word[0]
                tokens.insert(len(tokens) - idx + 1, word[1:])

            break

    # keep splicing off any dangling commas and (semi-) colons
    dirty = True
    while dirty:
        dirty = False

        for idx, word in enumerate(reversed(tokens), 1):
            while len(word) > 1 and word[-1] in u',;:':
                char = word[-1]  # the dangling comma/colon
                word = word[:-1]
                tokens[-idx] = word
                tokens.insert(len(tokens) - idx + 1, char)
                idx += 1
                dirty = True
            if dirty:
                break  # restart check to avoid index errors

    return tokens


@_matches(r"""
    (?<=^|[\s<"'(\[{])            # visual border

    (                             # RFC3986-like URIs:
        [A-z]+                    # required scheme
        ://                       # required hier-part
        (?:[^@]+@)?               # optional user
        (?:[\w-]+\.)+\w+          # required host
        (?::\d+)?                 # optional port
        (?:\/[^?\#\s'">)\]}]*)?   # optional path
        (?:\?[^\#\s'">)\]}]+)?    # optional query
        (?:\#[^\s'">)\]}]+)?      # optional fragment

    |                             # simplified e-Mail addresses:
        [\w.#$%&'*+/=!?^`{|}~-]+  # local part
        @                         # klammeraffe
        (?:[\w-]+\.)+             # (sub-)domain(s)
        \w+                       # TLD

    )(?=[\s>"')\]}]|$)            # visual border
    """)
def web_tokenizer(sentence):
    """
    The web tokenizer works like the :func:`word_tokenizer`, but does not split URIs or
    e-mail addresses. It also un-escapes all escape sequences (except in URIs or email addresses).
    """
    return [token for i, span in enumerate(web_tokenizer.split(sentence))
            for token in ((span,) if i % 2 else word_tokenizer(unescape(span)))]


def main():
    # tokenize one sentence per line input
    from argparse import ArgumentParser
    from sys import argv, stdout, stdin, stderr, getdefaultencoding, version_info
    from os import path, linesep

    def _tokenize(sentence, tokenizer):
        sep = None

        for token in tokenizer(sentence):
            if sep is not None:
                stdout.write(sep)

            stdout.write(token)
            sep = ' '

        stdout.write(linesep)

    NUM_TOKENIZERS = 4
    SPACE, ALNUM, TOKEN, WEB = list(range(NUM_TOKENIZERS))
    TOKENIZER = [None] * NUM_TOKENIZERS
    TOKENIZER[SPACE] = space_tokenizer
    TOKENIZER[ALNUM] = symbol_tokenizer
    TOKENIZER[TOKEN] = word_tokenizer
    TOKENIZER[WEB] = web_tokenizer

    parser = ArgumentParser(usage='%(prog)s [--mode] [FILE ...]',
                            description=__doc__, prog=path.basename(argv[0]),
                            epilog='default tokenizer: token; default encoding: ' +
                                   getdefaultencoding())
    parser.add_argument('files', metavar='FILE', nargs='*',
                        help='One-Sentence-Per-Line file; if absent, read from STDIN')
    parser.add_argument('--possessive-marker', '-p', action='store_true',  # TODO
                        help='split off the possessive marker from alphanumeric tokens')
    parser.add_argument('--split-contractions', '-c', action='store_true',  # TODO
                        help='split contractions like "don\'t" in alphanumeric tokens in two')
    parser.add_argument('--encoding', '-e', help='define encoding to use')
    mode = parser.add_mutually_exclusive_group()
    parser.set_defaults(mode=TOKEN)
    mode.add_argument('--space', '-s', action='store_const', dest='mode', const=SPACE,
                      help=space_tokenizer.__doc__)
    mode.add_argument('--alnum', '-a', action='store_const', dest='mode', const=ALNUM,
                      help=symbol_tokenizer.__doc__)
    mode.add_argument('--token', '-t', action='store_const', dest='mode', const=TOKEN,
                      help=word_tokenizer.__doc__)
    mode.add_argument('--web', '-w', action='store_const', dest='mode', const=WEB,
                      help=web_tokenizer.__doc__)

    args = parser.parse_args()
    tokenizer_func = TOKENIZER[args.mode]

    # fix broken Unicode handling in Python 2.x
    # see http://www.macfreek.nl/memory/Encoding_of_Python_stdout
    if args.encoding or version_info < (3, 0):
        if version_info >= (3, 0):
            stdout = stdout.buffer
            stdin = stdin.buffer

        stdout = codecs.getwriter(args.encoding or 'utf-8')(stdout, 'xmlcharrefreplace')
        stdin = codecs.getreader(args.encoding or 'utf-8')(stdin, 'xmlcharrefreplace')

        if not args.encoding:
            stderr.write('wrapped tokenizer stdio with UTF-8 de/encoders')
            stderr.write(linesep)

    if args.split_contractions:
        tokenizer = lambda sentence: split_contractions(tokenizer_func(sentence))
    elif args.possessive_marker:
        tokenizer = lambda sentence: split_possessive_markers(tokenizer_func(sentence))
    else:
        tokenizer = tokenizer_func

    if args.files:
        for txt_file_path in args.files:
            with codecs.open(txt_file_path, 'r', encoding=(args.encoding or 'utf-8')) as fp:
                for line in fp:
                    _tokenize(line, tokenizer)
    else:
        for line in stdin:
            _tokenize(line, tokenizer)


if __name__ == '__main__':
    main()
