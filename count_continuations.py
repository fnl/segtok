#!/usr/bin/env python3
"""Count the relative frequency of continuations in a corpus (from STDIN)."""
# The MIT License (MIT)
#
# Copyright (c) 2014 Florian Leitner <florian.leitner@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# This command-line tool takes a list of words, namely "continuations".
# Then, it counts how often each word is found in an input text coming from
# STDIN.
#
# Particularly, it counts:
# 1. capitalized occurrences after a dot or as the first word in a section,
# 2. in the input case after a dot, and
# 3. in the input case anywhere in the text (including after a dot in input
#    case).
#
# Finally, these counts and a few percentages are reported on STDOUT.
# This makes it possible to measure the frequency of each word as a sentence
# starter and after the abbreviation marker versus its general corpus
# frequency in default cases.

import logging
import os
import sys
from argparse import ArgumentParser
import re


__author__ = 'Florian Leitner <florian.leitner@gmail.com>'
__version__ = 1

# parser and arguments
epilog = "(C) 2015 {}. All rights reserved. License: MIT".format(__author__)
parser = ArgumentParser(usage='%(prog)s [options] TOKEN ...',
                        description=__doc__, epilog=epilog,
                        prog=os.path.basename(sys.argv[0]))
parser.add_argument('continuations', metavar='TOKEN', nargs='+',
                    help = 'lower-case continuation token(s)')

# logging/info options
parser.add_argument('--version', action='version',
                    version='v%s' % __version__)
parser.add_argument('--verbose', '-v', action='count', default=0,
                    help='increase log level [WARN]')
parser.add_argument('--quiet', '-q', action='count', default=0,
                    help='decrease log level [WARN]')
parser.add_argument('--abbreviations', action='store_true',
                    help='only count abbreviation-to-sentence-start usage')
args = parser.parse_args()

# logging setup
log_adjust = max(min(args.quiet - args.verbose, 2), -2) * 10
log_format = '%(levelname)-8s %(module) 10s: %(funcName)s %(message)s'
logging.basicConfig(level=logging.WARNING + log_adjust,
                    format=log_format)
logging.info('verbosity increased')
logging.debug('verbosity increased')

def sentence_start_pattern(continuation):
    capitalized_continuation = continuation.capitalize()
    pattern = r'(?:^|>|\t|\.\s)\s*{}\b'
    return re.compile(pattern.format(capitalized_continuation))

def abbreviation_pattern(continuation):
    pattern = r'\.\s+{}\b'
    return re.compile(pattern.format(continuation))

inside_sentence = {}
sentence_start = {}
after_abbreviation = {}

for c in args.continuations:
    inside_sentence[c] = [re.compile(r'\b{}\b'.format(c)), 0]
    sentence_start[c] = [sentence_start_pattern(c), 0]
    after_abbreviation[c] = [abbreviation_pattern(c), 0]

cases = (sentence_start, after_abbreviation) if args.abbreviations else \
    (inside_sentence, sentence_start, after_abbreviation)

for line in sys.stdin:
    for continuation in args.continuations:
        for target in cases:
            pattern_count = target[continuation]
            pattern_count[1] += len(pattern_count[0].findall(line))

if not args.abbreviations:
    print("Freq.SS | Likelih. | N.abbrev. | N.starters | N.inside | Word")
else:
    print("Likelih. | N.abbrev. | N.starters | Word")

for continuation in inside_sentence:
    starter_count = sentence_start[continuation][1]
    inside_count = inside_sentence[continuation][1]
    abbrev_count = after_abbreviation[continuation][1]
    total = starter_count + inside_count
    after_dot = starter_count + abbrev_count
    ss_fraction = (starter_count / float(total)) if total > 0 else 0.0
    likelihood = (abbrev_count / after_dot) if after_dot > 0 else 0.0

    if not args.abbreviations:
        print('%.3f' % ss_fraction, end=' | ')

    print('%.3f' % likelihood, abbrev_count, starter_count,
          sep=' | ', end=' | ')

    if not args.abbreviations:
        print(inside_count, end=' | ')

    print(continuation)