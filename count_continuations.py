#!/usr/bin/env python3
"""Count the relative freqeuncy of continuations in a corpus (STDIN)."""
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
args = parser.parse_args()

# logging setup
log_adjust = max(min(args.quiet - args.verbose, 2), -2) * 10
log_format = '%(levelname)-8s %(module) 10s: %(funcName)s %(message)s'
logging.basicConfig(level=logging.WARNING + log_adjust,
                    format=log_format)
logging.info('verbosity increased')
logging.debug('verbosity increased')

def sentence_start_pattern(continuation):
    upper_cont = '{}{}'.format(continuation[0].upper(), continuation[1:])
    return re.compile(r'(?:^|>|\t|\.\s)\s*{}\b'.format(upper_cont))

inside_sentence = {}
sentence_start = {}

for c in args.continuations:
    inside_sentence[c] = [re.compile(r'\b{}\b'.format(c)), 0]
    sentence_start[c] = [sentence_start_pattern(c), 0]

for line in sys.stdin:
    for continuation in inside_sentence:
        for coll in (inside_sentence, sentence_start):
            pat_count = coll[continuation]
            pat_count[1] += len(pat_count[0].findall(line))

for continuation in inside_sentence:
    starter_count = sentence_start[continuation][1]
    inside_count = inside_sentence[continuation][1]
    total = starter_count + inside_count
    fraction = (starter_count / float(total)) if total > 0 else 0.0
    print('%.3f' % fraction, "|", total, "|", continuation)