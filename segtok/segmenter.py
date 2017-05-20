#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A pattern-based sentence segmentation strategy; Known limitations:

1. The sentence must use a known sentence terminal followed by space(s),
   skipping one optional, intervening quote and/or bracket.
2. The next sentence must start with an upper-case letter or a number,
   ignoring one optional quote and/or bracket before it.
   Alternatively, it may start with a camel-cased word, like "gene-A".
3. If the sentence ends with a single upper-case letter followed by a dot,
   a split is made (splits names like "A. Dent"), unless there is an easy
   to deduce reason that it is a human name.

The decision for requiring an "syntactically correct" terminal sequence with upper-case letters or
numbers as start symbol is based on the preference to under-split rather than over-split sentences.

Special care is taken not to split at common abbreviations like "i.e." or "etc.",
to not split at first or middle name initials "... F. M. Last ...",
to not split before a comma, colon, or semi-colon,
and to avoid single letters or digits as sentences ("A. This sentence...").

Sentence splits will always be enforced at [consecutive] line separators.

Important: Windows text files use ``\\r\\n`` as linebreaks and Mac files use ``\\r``;
Convert the text to Unix linebreaks if the case.
"""
from __future__ import absolute_import, unicode_literals
import codecs
from regex import compile, DOTALL, UNICODE, VERBOSE


__author__ = 'Florian Leitner <florian.leitner@gmail.com>'

SENTENCE_TERMINALS = '.!?\u203C\u203D\u2047\u2048\u2049\u3002' \
                     '\uFE52\uFE57\uFF01\uFF0E\uFF1F\uFF61'
"The list of valid Unicode sentence terminal characters."

# Note that Unicode the category Pd is NOT a good set for valid word-breaking hyphens,
# because it contains many dashes that should not be considered part of a word.
HYPHENS = '\u00AD\u058A\u05BE\u0F0C\u1400\u1806\u2010-\u2012\u2e17\u30A0-'
"Any valid word-breaking hyphen, including ASCII hyphen minus."

# Use upper-case for abbreviations that always are capitalized:
# Lower-case abbreviations may occur capitalized or not.
# Only abbreviations that should never occur at the end of a sentence
# (such as "etc.")
ABBREVIATIONS = """
approx Capt cf Col Dr f\.?e figs? Gen e\.?g i\.?e i\.?v
Mag med Mr Mrs Mt nat No nr p\.e phil prof rer
sci Sgt Sr Sra Srta St univ vol vs z\.B
Jän Jan Ene Feb Mär Mar Apr Abr May Jun Jul Aug Sep Sept Oct Okt Nov Dic Dez Dec
E\.U U\.K U\.S
""".split()
ABBREVIATIONS.extend(a.capitalize() for a in ABBREVIATIONS if a[0].islower())
ABBREVIATIONS = '|'.join(sorted(ABBREVIATIONS))
ABBREVIATIONS = compile(r"""
(?: \b(?:%s) # 1. known abbreviations,
|   ^\S      # 2. a single, non-space character "sentence" (only),
|   ^\d+     # 3. a series of digits "sentence" (only), or
|   (?: \b   # 4. terminal letters A.-A, A.A, or A, if prefixed with:
    # 4.a. something that makes them most likely a human first name initial
        (?: [Bb]y
        |   [Cc](?:aptain|ommander)
        |   [Dd]o[ck]tor
        |   [Gg]eneral
        |   [Mm](?:ag)?is(?:ter|s)
        |   [Pp]rofessor
        |   [Ss]e\u00F1or(?:it)?a?
        ) \s
    # 4.b. if they are most likely part of an author list: (avoiding "...A and B")
    |   (?: (?<! \b\p{Lu}\p{Lm}? ) , (?: \s and )?
        |   (?<! \b[\p{Lu},]\p{Lm}? ) \s and
        ) \s
    # 4.c. a bracket opened just before the letters
    |   [\[\(]
    ) (?: # finally, the letter sequence A.-A, A.A, or A:
        [\p{Lu}\p{Lt}] \p{Lm}? \. # optional A.
        [%s]?                     # optional hyphen
    )? [\p{Lu}\p{Lt}] \p{Lm}?     # required A
) $""" % (ABBREVIATIONS, HYPHENS), UNICODE | VERBOSE)
"""
Common abbreviations at the candidate sentence end that normally don't terminate a sentence.
Note that a check is required to ensure the potential abbreviation is actually followed by a dot
and not some other sentence segmentation marker.
"""

# PMC OA corpus statistics
# SSs: sentence starters
# abbrevs: abbreviations
#
# Words likely used as SSs (poor continuations, >10%):
# after, though, upon, while, yet
#
# Words hardly used after abbrevs vs. SSs (poor continuations, <2%):
# [after], as, at, but, during, for, in, nor, on, to, [though], [upon],
# whereas, [while], within, [yet]
#
# Words hardly ever used as SSs (excellent continuations, <2%):
# and, are, between, by, from, has, into, is, of, or, that, than, through,
# via, was, were, with
#
# Words frequently used after abbrevs (excellent continuations, >10%):
# [and, are, has, into, is, of, or, than, via, was, were]
#
# Grey zone: undecidable words -> leave in to bias towards under-splitting
# whether

ENDS_IN_DATE_DIGITS = compile(r"\b[0123]?[0-9]$")
MONTH = compile(r"(J[äa]n|Ene|Feb|M[äa]r|A[pb]r|May|Jun|Jul|Aug|Sep|O[ck]t|Nov|D[ei][cz]|0?[1-9]|1[012])")
"""
Special facilities to detect European-style dates.
"""

CONTINUATIONS = compile(r""" ^ # at string start only
(?: a(?: nd|re )
|   b(?: etween|y )
|   from
|   has
|   i(?: nto|s )
|   o[fr]
|   t(?: han|hat|hrough )
|   via
|   w(?: as|ere|hether|ith )
)\b""", UNICODE | VERBOSE)
"Lower-case words that in the given form usually don't start a sentence."

BEFORE_LOWER = compile(r""" .*?
(?: [%s]"[\)\]]*           # ."]) .") ."
|   [%s] [\)\]]+           # .]) .)
|   \b spp \.              # spp.  (species pluralis)
|   \b \p{L} \p{Ll}? \.    # Ll. L.
) \s+ $""" % (SENTENCE_TERMINALS, SENTENCE_TERMINALS), DOTALL | UNICODE | VERBOSE
)
"""
Endings that, if followed by a lower-case word, are not sentence terminals:
- Quotations and brackets ("Hello!" said the man.)
- dotted abbreviations (U.S.A. was)
- genus-species-like (m. musculus)
"""
LOWER_WORD = compile(r'^\p{Ll}+[%s]?\p{Ll}*\b' % HYPHENS, UNICODE)
"Lower-case words are not sentence starters (after an abbreviation)."

MIDDLE_INITIAL_END = compile(r'\b\p{Lu}\p{Ll}+\W+\p{Lu}$', UNICODE)
"Upper-case initial after upper-case word at the end of a string."

UPPER_WORD_START = compile(r'^\p{Lu}\p{Ll}+\b', UNICODE)
"Upper-case word at the beginning of a string."

LONE_WORD = compile(r'^\p{Ll}+[\p{Ll}\p{Nd}%s]*$' % HYPHENS, UNICODE)
"Any 'lone' lower-case word [with hyphens or digits inside] is a continuation."

UPPER_CASE_END = compile(r'\b[\p{Lu}\p{Lt}]\p{L}*\.\s+$', UNICODE)
"Inside brackets, 'Words' that can be part of a proper noun abbreviation, like a journal name."
UPPER_CASE_START = compile(r'^(?:(?:\(\d{4}\)\s)?[\p{Lu}\p{Lt}]\p{L}*|\d+)[\.,:]\s+', UNICODE)
"Inside brackets, 'Words' that can be part of a large abbreviation, like a journal name."

SHORT_SENTENCE_LENGTH = 55
"Length of either sentence fragment inside brackets to assume the fragment is not its own sentence."
# This can be increased/decreased to heighten/lower the likelihood of splits inside brackets.

NON_UNIX_LINEBREAK = compile(r'(?:\r\n|\r|\u2028)', UNICODE)
"All linebreak sequence variants except the Unix newline (only)."

SEGMENTER_REGEX = r"""
(                       # A sentence ends at one of two sequences:
    [%s]                # Either, a sequence starting with a sentence terminal,
    [\'\u2019\"\u201D]? # an optional right quote,
    [\]\)]*             # optional closing brackets and
    \s+                 # a sequence of required spaces.
|                       # Otherwise,
    \n{{{},}}           # a sentence also terminates at [consecutive] newlines.
)""" % SENTENCE_TERMINALS
"""
Sentence end a sentence terminal, followed by spaces.
Optionally, a right quote and any number of closing brackets may succeed the terminal marker.
Alternatively, an yet undefined number of line-breaks also may terminate sentences.
"""

_compile = lambda count: compile(SEGMENTER_REGEX.format(count), UNICODE | VERBOSE)

# Define that one or more line-breaks split sentences:
DO_NOT_CROSS_LINES = _compile(1)
"A segmentation pattern where any newline char also terminates a sentence."

# Define that two or more line-breaks split sentences:
MAY_CROSS_ONE_LINE = _compile(2)
"A segmentation pattern where two or more newline chars also terminate sentences."


def split_single(text, join_on_lowercase=False, short_sentence_length=SHORT_SENTENCE_LENGTH):
    """
    Default: split `text` at sentence terminals and at newline chars.
    """
    sentences = _sentences(DO_NOT_CROSS_LINES.split(text), join_on_lowercase, short_sentence_length)
    return [s for ss in sentences  for s in ss.split('\n')]


def split_multi(text, join_on_lowercase=False, short_sentence_length=SHORT_SENTENCE_LENGTH):
    """
    Sentences may contain non-consecutive (single) newline chars, while consecutive newline chars
    ("paragraph separators") always split sentences.
    """
    return _sentences(MAY_CROSS_ONE_LINE.split(text), join_on_lowercase, short_sentence_length)


def split_newline(text):
    """
    Split the `text` at newlines (``\\n'') and strip the lines,
    but only return lines with content.
    """
    for line in text.split('\n'):
        line = line.strip()

        if line:
            yield line


def rewrite_line_separators(text, pattern, join_on_lowercase=False,
                            short_sentence_length=SHORT_SENTENCE_LENGTH):
    """
    Remove line separator chars inside sentences and ensure there is a ``\\n`` at their end.

    :param text: input plain-text
    :param pattern: for the initial sentence splitting
    :param join_on_lowercase: always join sentences that start with lower-case
    :param short_sentence_length: the upper boundary for text spans that are not split
                                  into sentences inside brackets
    :return: a generator yielding the spans of text
    """
    offset = 0

    for sentence in _sentences(pattern.split(text), join_on_lowercase, short_sentence_length):
        start = text.index(sentence, offset)
        intervening = text[offset:start]

        if offset != 0 and '\n' not in intervening:
            yield '\n'
            intervening = intervening[1:]

        yield intervening
        yield sentence.replace('\n', ' ')
        offset = start + len(sentence)

    if offset < len(text):
        yield text[offset:]


def to_unix_linebreaks(text):
    """Replace non-Unix linebreak sequences (Windows, Mac, Unicode) with newlines (\\n)."""
    return NON_UNIX_LINEBREAK.sub('\n', text)


def _sentences(spans, join_on_lowercase, short_sentence_length):
    """Join spans back together into sentences as necessary."""
    last = None
    shorterThanATypicalSentence = lambda c, l: c < short_sentence_length or l < short_sentence_length

    for current in _abbreviation_joiner(spans):
        if last is not None:
            if (join_on_lowercase or BEFORE_LOWER.match(last)) and LOWER_WORD.match(current):
                last = '%s%s' % (last, current)
            elif shorterThanATypicalSentence(len(current), len(last)) and _is_open(last) and (
                _is_not_opened(current) or last.endswith(' et al. ') or (
                    UPPER_CASE_END.search(last) and UPPER_CASE_START.match(current)
                )
            ):
                last = '%s%s' % (last, current)
            elif shorterThanATypicalSentence(len(current), len(last)) and _is_open(last, '[]') and (
                _is_not_opened(current, '[]') or last.endswith(' et al. ') or (
                    UPPER_CASE_END.search(last) and UPPER_CASE_START.match(current)
                )
            ):
                last = '%s%s' % (last, current)
            elif CONTINUATIONS.match(current):
                last = '%s%s' % (last, current)
            else:
                yield last.strip()
                last = current
        else:
            last = current

    if last is not None:
        yield last.strip()


def _abbreviation_joiner(spans):
    """Join spans that match the ABBREVIATIONS pattern."""
    segment = None
    makeSentence = lambda start, end: ''.join(spans[start:end])
    total = len(spans)

    for pos in range(total):
        if pos and pos % 2:  # even => segment, uneven => (potential) terminal
            prev_s = spans[pos - 1]
            marker = spans[pos]
            next_s = spans[pos+1] if pos + 1 < total else None

            if prev_s[-1:].isspace():
                pass # join
            elif marker[0] == '.' and ABBREVIATIONS.search(prev_s):
                pass # join
            elif marker[0] == '.' and next_s and (
                    LONE_WORD.match(next_s) or
                    (ENDS_IN_DATE_DIGITS.search(prev_s) and MONTH.match(next_s)) or
                    (MIDDLE_INITIAL_END.search(prev_s) and UPPER_WORD_START.match(next_s))
                    ):
                pass # join
            else:
                yield makeSentence(segment, pos + 1)
                segment = None
        elif segment is None:
            segment = pos

    if segment is not None:
        yield makeSentence(segment, total)


def _is_open(span_str, brackets='()'):
    """Check if the span ends with an unclosed `bracket`."""
    offset = span_str.find(brackets[0])
    nesting = 0 if offset == -1 else 1

    while offset != -1:
        opener = span_str.find(brackets[0], offset + 1)
        closer = span_str.find(brackets[1], offset + 1)

        if opener == -1:
            if closer == -1:
                offset = -1
            else:
                offset = closer
                nesting -= 1
        elif closer == -1:
            offset = opener
            nesting += 1
        elif opener < closer:
            offset = opener
            nesting += 1
        elif closer < opener:
            offset = closer
            nesting -= 1
        else:
            msg = 'at offset={}: closer={}, opener={}'
            raise RuntimeError(msg.format(offset, closer, opener))

    return nesting > 0


def _is_not_opened(span_str, brackets='()'):
    """Check if the span starts with an unopened `bracket`."""
    offset = span_str.rfind(brackets[1])
    nesting = 0 if offset == -1 else 1

    while offset != -1:
        opener = span_str.rfind(brackets[0], 0, offset)
        closer = span_str.rfind(brackets[1], 0, offset)

        if opener == -1:
            if closer == -1:
                offset = -1
            else:
                offset = closer
                nesting += 1
        elif closer == -1:
            offset = opener
            nesting -= 1
        elif closer < opener:
            offset = opener
            nesting -= 1
        elif opener < closer:
            offset = closer
            nesting += 1
        else:
            msg = 'at offset={}: closer={}, opener={}'
            raise RuntimeError(msg.format(offset, closer, opener))

    return nesting > 0


def main():
    # print one sentence per line
    from argparse import ArgumentParser
    from sys import argv, stdout, stdin, stderr, getdefaultencoding, version_info
    from os import path, linesep

    single, multi = 0, 1

    parser = ArgumentParser(usage='%(prog)s [--mode] [FILE ...]',
                            description=__doc__, prog=path.basename(argv[0]),
                            epilog='default encoding: ' + getdefaultencoding())
    parser.add_argument('files', metavar='FILE', nargs='*',
                        help='UTF-8 plain-text file(s); if absent, read from STDIN')
    parser.add_argument('--with-ids', action='store_true',
                        help='STDIN (only!) input is ID-tab-TEXT; the ID is '
                             'preserved in the output as ID-tab-N-tab-SENTENCE '
                             'where N is the incremental sentence number for that '
                             'text ID')
    parser.add_argument('--normal-breaks', '-n', action='store_true',
                        help=to_unix_linebreaks.__doc__)
    parser.add_argument('--bracket-spans', '-b', metavar="INT", type=int,
                        default=SHORT_SENTENCE_LENGTH,
                        help="upper boundary for text spans that are not split "
                             "into sentences inside brackets [%(default)d]")
    parser.add_argument('--encoding', '-e', help='force another encoding to use')
    mode = parser.add_mutually_exclusive_group()
    parser.set_defaults(mode=single)
    mode.add_argument('--single', '-s', action='store_const', dest='mode', const=single,
                      help=split_single.__doc__)
    mode.add_argument('--multi', '-m', action='store_const', dest='mode', const=multi,
                      help=split_multi.__doc__)

    args = parser.parse_args()
    pattern = [DO_NOT_CROSS_LINES, MAY_CROSS_ONE_LINE, ][args.mode]
    normal = to_unix_linebreaks if args.normal_breaks else lambda t: t

    # fix broken Unicode handling in Python 2.x
    # see http://www.macfreek.nl/memory/Encoding_of_Python_stdout
    if args.encoding or version_info < (3, 0):
        if version_info >= (3, 0):
            stdout = stdout.buffer
            stdin = stdin.buffer

        stdout = codecs.getwriter(
            args.encoding or 'utf-8'
        )(stdout, 'xmlcharrefreplace')

        stdin = codecs.getreader(
            args.encoding or 'utf-8'
        )(stdin, 'xmlcharrefreplace')

        if not args.encoding:
            stderr.write('wrapped segmenter stdio with UTF-8 de/encoders')
            stderr.write(linesep)

    if not args.files and args.mode != single:
        parser.error('only single line splitting mode allowed '
                     'when reading from STDIN')

    def segment(text):
        if not args.files and args.with_ids:
            tid, text = text.split('\t', 1)
        else:
            tid = None

        if args.mode == single:
            sentences = split_single(normal(text), short_sentence_length=args.bracket_spans)
            text_spans = [i for s in sentences for i in (s, '\n')]
        else:
            text_spans = rewrite_line_separators(
                normal(text), pattern, short_sentence_length=args.bracket_spans
            )

        if tid is not None:
            def write_ids(tid, sid):
                stdout.write(tid)
                stdout.write('\t')
                stdout.write(str(sid))
                stdout.write('\t')

            last = '\n'
            sid = 1

            for span in text_spans:
                if last == '\n' and span not in ('', '\n'):
                    write_ids(tid, sid)
                    sid += 1

                stdout.write(span)

                if span:
                    last = span
        else:
            for span in text_spans:
                stdout.write(span)

    if args.files:
        for txt_file_path in args.files:
            with codecs.open(
                txt_file_path, 'r', encoding=(args.encoding or 'utf-8')
            ) as fp:
                segment(fp.read())
    else:
        for line in stdin:
            segment(line)


if __name__ == '__main__':
    main()
