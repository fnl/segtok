#!/usr/bin/env python
"""
Word tokenizing support.

Note that small/full/half-width character variants are *not* included.
If a text contains such characters, normalize it first.
"""
from HTMLParser import HTMLParser
from regex import compile, UNICODE, VERBOSE

try:
    from otplc.segmenter import SENTENCE_TERMINALS
except ImportError:
    # if used as command-line tool
    from segmenter import SENTENCE_TERMINALS


__author__ = 'Florian Leitner <florian.leitner@gmail.com>'

unescape = HTMLParser().unescape

# Note that Unicode the category Pd is NOT a good set for valid word-breaking hyphens,
# because it contains many dashes that should not be considered part of a word token.
HYPHEN = ur'[\u00AD\u058A\u05BE\u0F0C\u1400\u1806\u2010\u2011\u2e17\u30A0-]'
"""Any valid word-breaking hyphen, including ASCII "hyphen minus"."""

APOSTROPHE = ur"[\u02BC\u2019\u2032]"
"""Any apostrophe-like marks, including "prime" but not the ASCII "single quote"."""

LINEBREAK = ur'(?:\r\n|\n|\r|\u2028)'
"""Any valid linebreak sequence (Windows, Unix, Mac, or U+2028)."""

LETTER = ur'[\p{Ll}\p{Lm}\p{Lt}\p{Lu}]'
"""Any Unicode letter character that can form part of a word: Ll, Lm, Lt, Lu."""

NUMBER = ur'[\p{Nd}\p{Nl}]'
"""Any Unicode number character: Nd or Nl."""

DIMENSION = ur'\u207B?[\u00B9\u00B2\u00B3]'
"""Superscript 1, 2, and 3, optionally prefixed with a minus sign."""

ALNUM = ur'(?:%s|%s)' % (LETTER, NUMBER)
"""Any alphanumeric Unicode character: letter or number."""

SPACE = ur'[\p{Zs}\t]'
"""Any unicode space character plus the (horizontal) tab."""

APO_MATCHER = compile(APOSTROPHE, UNICODE)
"""Matcher for any apostrophe."""

HYPHENATED_LINEBREAK = compile(
    ur'({alnum}{hyphen}){space}*?{linebreak}{space}*?({alnum})'.format(
        alnum=ALNUM, hyphen=HYPHEN, linebreak=LINEBREAK, space=SPACE
    ), UNICODE
)
"""
The pattern matches any alphanumeric Unicode character, followed by a hyphen,
a single line-break surrounded by optional (non-breaking) spaces,
and terminates with a alphanumeric character on this next line.
The opening char and hyphen as well as the terminating char are captured in two groups.
"""


def matches(regex):
    """Regular expression compiling function decorator."""
    def match_decorator(fn):
        automaton = compile(regex, UNICODE | VERBOSE)
        fn.split = automaton.split
        fn.match = automaton.match
        return fn

    return match_decorator


@matches(ur'\s+')
def space_tokenizer(sentence):
    """
    For a given input `sentence`, list its tokens.

    Split on Unicode spaces ``\\s+`` (i.e., any kind of **Unicode** space character).
    Separating space characters are dropped.

    :type sentence: unicode
    :return: a unicode token list
    """
    return [token for token in space_tokenizer.split(sentence) if token]


@matches(ur'(%s+)' % ALNUM)
def symbol_tokenizer(sentence):
    """
    For a given input `sentence`, list its tokens.

    Extracts alphanumeric Unicode character sequences from already space-split tokens.

    :type sentence: unicode
    :return: a unicode token list
    """
    return [token for span in space_tokenizer(sentence) for
            token in symbol_tokenizer.split(span) if token]

#
@matches(ur"""((?:
    # Dots, except ellipsis
    {alnum} \. (?!\.\.)
    | # Comma, surrounded by digits (e.g., chemicals) or letters
    {alnum} , (?={alnum})
    | # Hyphen, surrounded by digits (e.g., DNA endings: "5'-ACGT-3'") or letters
    {alnum} {apo}? {hyphen} (?={alnum})  # incl. optional apostrophe for DNA segments
    | # Apostophes, non-consecutive
    {apo} (?!{apo})
    | # ASCII single quote, surrounded by digits or letters (no dangling allowed)
    {alnum} ' (?={alnum})
    | # ASCII single quote after an s and at the token's end
    s ' $
    | # Terminal dimensions (superscript minus, 1, 2, and 3) attached to physical units
    #  size-prefix           unit-acronym    dim-s #
    \b [yzafpn\u00B5mcdhkMGTPEZY]? {letter}{{1,3}} {dim} $
    | # Any (Unicode) letter, digit, or the underscore
    {alnum}
    )+)""".format(alnum=ALNUM, apo=APOSTROPHE, dim=DIMENSION,
                  hyphen=HYPHEN, letter=LETTER, number=NUMBER))
def word_tokenizer(sentence):
    """
    For a given input `sentence`, list its tokens.

    This tokenizer extends the :func:`symbol_tokenizer` by splitting fewer cases:

    * Dots appearing after a letter are maintained in the word, except for the last word in a
      sentence if that dot is the sentence terminal. Therefore, abbreviation marks (words
      containing or ending in a ``.``, like "i.e.") remain intact and URL or ID segments remain
      complete ("www.ex-ample.com", "EC1.2.3.4.5", etc.). The only dots that never are attached
      are triple dots (``...``; ellipsis).
    * Commas surrounded by alphanumeric characters are maintained in the word, too, e.g. ``a,b``.
      Commas, semi-colons, and colons "dangling" at the end of a token are always spliced off.
    * Any two alphanumeric letters that are separated by a single hyphen are joined together;
      Those "inner" hyphens may optionally be followed by a linebreak surrounded by spaces;
      The spaces will be removed, however. For example, ``Hel- \\r\\n \t lo`` contains a (Windows)
      linebreak and will be returned as ``Hel-lo``.
    * Apostrophes are always allowed in words as long as they are not repeated; The single quote
      ASCII letter ``'`` is only allowed as a terminal apostrophe after the letter ``s``,
      otherwise it must be surrounded by letters. To support DNA and chemicals, a apostrophe
      (prime) may be located before the hyphen, as in the single token "5'-ACGT-3'" (if any
      non-ASCII hyphens are used instead of the shown single quote).
    * Superscript 1, 2, and 3, optionally prefixed with a superscript minus, are attached to a
      word if it is no longer than 3 letters (optionally 4 if the first letter is a power prefix
      in the range from yocto, y (10^-24) to yotta, Y (10^+24)).

    :type sentence: unicode
    :return: a unicode token list
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
                tokens.insert(len(tokens) - idx, word[:-1])

            break

    # keep splicing off any dangling commas and (semi-) colons
    dirty = True
    while dirty:
        dirty = False
        count = len(tokens)

        for idx, word in enumerate(reversed(tokens), 1):
            if len(word) > 1 and word[-1] in u',;:':
                tokens[-idx] = word[:-1]
                tokens.insert(count - idx + 1, word[-1])
                dirty = True

    return tokens


@matches(ur"""
    (?<=^|[\s<"'(\[{])            # visual border

    (                             # RFC3986-like URIs:
        [A-z]+                    # required scheme
        ://                       # required hier-part
        (?:[^@]+@)?               # optional user
        (?:[\w-]+\.)+\w+          # required host
        (?::\d+)?                 # optional port
        (?:\/[^?\#\s'">)\]}]+)?   # optional path
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
    For a given input `sentence`, list its tokens.

    This tokenizer works like the :func:`word_tokenizer`, but does not split URIs or
    e-mail addresses. It also un-escapes all escape sequences (except in URIs or email addresses).

    :type sentence: unicode
    :return: a token generator
    """
    return [token for i, span in enumerate(web_tokenizer.split(sentence))
            for token in ((span,) if i % 2 else word_tokenizer(unescape(span)))]


def _tokenize(sentence, tokenizer):
    sep = None

    for token in tokenizer(sentence):
        if sep is not None:
            stdout.write(sep)

        stdout.write(token.encode('utf-8'))
        sep = u' '.encode('utf-8')

    stdout.write(linesep)


if __name__ == '__main__':
    # tokenize one sentence per line input
    from argparse import ArgumentParser
    from sys import argv, stdout, stdin
    from os import path, linesep


    SPACE, SYMBOL, WORD, WEB = 0, 1, 2, 3

    parser = ArgumentParser(usage=u'%(prog)s [--mode] [FILE ...]',
                            description=__doc__, prog=path.basename(argv[0]))
    parser.add_argument('files', metavar='FILE', nargs='*',
                        help=u'One-Sentence-Per-Line file; if absent, read from STDIN')
    mode = parser.add_mutually_exclusive_group()
    parser.set_defaults(mode=WORD)
    mode.add_argument('--space',  '-s', action='store_const', dest='mode', const=SPACE)
    mode.add_argument('--alnum',  '-a', action='store_const', dest='mode', const=SYMBOL)
    mode.add_argument('--token',  '-t', action='store_const', dest='mode', const=WORD)
    mode.add_argument('--web',    '-w', action='store_const', dest='mode', const=WEB)

    args = parser.parse_args()
    tokenizer = [space_tokenizer, symbol_tokenizer, word_tokenizer, web_tokenizer,][args.mode]

    if args.files:
        for txt_file_path in args.files:
            for line in open(txt_file_path, 'rU'):
                _tokenize(line.decode('UTF-8'), tokenizer)
    else:
        for line in stdin:
            _tokenize(line.decode('UTF-8'), tokenizer)