# coding=utf-8
from __future__ import absolute_import, division, unicode_literals
from unittest import TestCase
from segtok.segmenter import split_single, split_multi, MAY_CROSS_ONE_LINE, \
    split_newline, rewrite_line_separators, ABBREVIATIONS, CONTINUATIONS, \
    NON_UNIX_LINEBREAK, to_unix_linebreaks


OSPL = """One sentence per line.
And another sentence on the same line.
(How about a sentence in parenthesis?)
Or a sentence with "a quote!"
'How about those pesky single quotes?'
[And not to forget about square brackets.]
And, brackets before the terminal [2].
You know Mr. Abbreviation I told you so.
What about the med. staff here?
But the undef.
abbreviation not.
And this f.e. is tricky stuff.
I.e. a little easier here.
However, e.g., should be really easy.
Three is one btw., is clear.
Their presence was detected by transformation into S. lividans.
Three subjects diagnosed as having something.
What the heck??!?!
(A) First things here.
(1) No, they go here.
[z] Last, but not least.
(vii) And the Romans, too.
Let's meet at 14.10 in N.Y..
This happened in the U.S. last week.
Brexit: The E.U. and the U.K. are separating.
Refugees are welcome in the E.U..
But they are thrown out of the U.K..
And they never get to the U.S..
The U.S. Air Force was called in.
What about the E.U. High Court?
And then there is the U.K. House of Commons.
Now only this splits: the EU.
A sentence ending in U.S. Another that won't split.
12 monkeys ran into here.
Nested (Parenthesis.
(With words inside! (Right)) (More stuff. Uff, this is it!))
In the Big City.
How we got an A.
Mathematics . dot times.
An abbreviation at the end..
This is a sentence terminal ellipsis...
This is another sentence terminal ellipsis....
An easy to handle G. species mention.
Am 13. Jän. 2006 war es regnerisch.
The administrative basis for Lester B. Pearson's foreign policy was developed later.
This model was introduced by Dr. Edgar F. Codd after initial criticisms.
This quote "He said it." is actually inside.
A. The first assumption.
B. The second bullet.
C. The last case.
1. This is one.
2. And that is two.
3. Finally, three, too.
Always last, clear closing example."""

SENTENCES = OSPL.split('\n')
TEXT = ' '.join(SENTENCES)


class TestToUnixLinebreak(TestCase):

    def test_function(self):
        result = to_unix_linebreaks("This\r\none.")
        self.assertEqual("This\none.", result)

class TestSentenceSegmenter(TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_ABBREVIATIONS_abbrevs(self):
        for example in ('Of approx', '12 vs'):
            self.assertTrue(ABBREVIATIONS.search(example) is not None, example)

    def test_ABBREVIATIONS_single_char(self):
        for example in ('A', 'Z', 'a', '1', '0', '.', '*', '$'):
            self.assertTrue(ABBREVIATIONS.search(example) is not None, example)

    def test_ABBREVIATIONS_name_or_bracket(self):
        for example in (  # 'by A',
            'Mister X', 'Xen, B', 'Xen and C', 'Xen, and C', 'this [G',
                        'that (Z'):
            self.assertTrue(ABBREVIATIONS.search(example) is not None, example)

    def test_ABBREVIATIONS_ignore(self):
        for example in ('not NOV', 'USA', 'Upper', 'Ab', 'some A', 'lower',
                        'some Upper', 'in A, B', 'in A and B', 'A, B, and C'):
            self.assertTrue(ABBREVIATIONS.search(example) is None, example)

    def test_CONTINUATIONS_detected(self):
        for example in ('and this', 'are those'):
            self.assertTrue(CONTINUATIONS.search(example) is not None, example)

    def test_CONTINUATIONS_ignored(self):
        for example in ('to be', 'Are those', 'not and'):
            self.assertTrue(CONTINUATIONS.search(example) is None, example)

    def test_NON_UNIX_LINEBREAK_search(self):
        for example in ('\r', '\r\n', '\u2028'):
            self.assertTrue(NON_UNIX_LINEBREAK.search(example) is not None, repr(example))

    def test_NON_UNIX_LINEBREAK_misses(self):
        for example in ('\n', ' ', '\t'):
            self.assertTrue(NON_UNIX_LINEBREAK.search(example) is None, repr(example))

    def test_simple_case(self):
        self.assertEqual(['This is a test.'], list(split_single("This is a test.")))

    def test_regex(self):
        self.assertSequenceEqual(SENTENCES, list(split_single(TEXT)))

    def test_names(self):
        sentences = ["Written by A. McArthur, K. Elvin, and D. Eden.",
                     "This is Mr. A. Starr over there.",
                     "B. Boyden is over there."]
        self.assertSequenceEqual(sentences, list(split_single(' '.join(sentences))))

    def test_alpha_items(self):
        sentences = ["This is figure A, B, and C.", "This is table A and B.", "That is item A, B."]
        self.assertSequenceEqual(sentences, list(split_single(' '.join(sentences))))

    def test_author_list(self):
        sentences = ["R. S. Kauffman, R. Ahmed, and B. N. Fields show stuff in their paper."]
        self.assertSequenceEqual(sentences, list(split_single(' '.join(sentences))))

    def test_long_bracket_abbervation(self):
        sentences = ["This is expected, on the basis of (Olmsted, M. C., C. F. Anderson, "
                     "and M. T. Record, Jr. 1989. Proc. Natl. Acad. Sci. USA. 100:100), "
                     "to decrease sharply."]
        self.assertSequenceEqual(sentences, list(split_single(' '.join(sentences))))

    def test_continuations(self):
        sentences = ["colonic colonization inhibits development of inflammatory lesions.",
                     "to investigate whether an inf. of the pancreas was the case...",
                     "though we hate to use capital lett. that usually separate sentences."]
        self.assertSequenceEqual(sentences, list(split_single(' '.join(sentences))))

    def test_inner_names(self):
        sentences = ["Bla bla [Sim et al. (1981) Biochem. J. 193, 129-141].",
                     "The adjusted (ml. min-1. 1.73 m-2) rate."]
        self.assertSequenceEqual(sentences, list(split_single(' '.join(sentences))))

    def test_species_names(self):
        sentences = ["Their presence was detected by transformation into S. lividans.",
                     "Three subjects diagnosed as having something."]
        self.assertSequenceEqual(sentences, list(split_single(' '.join(sentences))))

    def test_species_names_tough(self):
        sentences = ["The level of the genus Allomonas gen. nov. with so "
                     "far the only species A. enterica known."]
        self.assertSequenceEqual(sentences, list(split_single(' '.join(sentences))))

    def test_european_dates(self):
        sentences = ["Der Unfall am 24. Dezember 2016.",
                     "Am 13. Jän. 2006 war es regnerisch.",
                     "Am 13. 1. 2006 war es regnerisch."]
        self.assertSequenceEqual(sentences, list(split_single(' '.join(sentences))))

    def test_middle_name_initials(self):
        sentences = ["The administrative basis for Lester B. Pearson's foreign policy was developed later.",
                     "This model was introduced by Dr. Edgar F. Codd after initial criticisms."]
        self.assertSequenceEqual(sentences, list(split_single(' '.join(sentences))))

    def test_multiline(self):
        text = "This is a\nmultiline sentence. And this is Mr.\nAbbrevation."
        ml_sentences = ["This is a\nmultiline sentence.", "And this is Mr.\nAbbrevation."]
        self.assertSequenceEqual(ml_sentences, list(split_multi(text)))

    def test_parenthesis(self):
        sentences = ["Nested ((Parenthesis. (With words right (inside))) (More stuff. "
                     "Uff, this is it!))", "In the Big City."]
        self.assertSequenceEqual(sentences, list(split_single(' '.join(sentences))))

    def test_parenthesis_with_sentences(self):
        sentences = ["The segmenter segments on single lines or to consecutive lines.",
                     "(If you want to extract sentences that cross newlines, remove those line-breaks.",
                     "Segtok assumes your content has some minimal semantical meaning.)",
                     "It gracefully handles this and similar issues."]
        self.assertSequenceEqual(sentences, list(split_single(' '.join(sentences))))

    def test_unclosed_brackets(self):
        sentences = ["The medial preoptic area (MPOA), and 2) did not decrease Fos-lir.",
                     "However, olfactory desensitizations did decrease Fos-lir."]
        self.assertSequenceEqual(sentences, list(split_single(' '.join(sentences))))

    def test_linebreak(self):
        text = "This is a\nmultiline sentence."
        self.assertSequenceEqual(text.split('\n'), list(split_single(text)))

    def test_linebreak2(self):
        text = "Folding Beijing\nby Hao Jingfang"
        self.assertSequenceEqual(text.split('\n'), list(split_single(text)))

    def test_newline(self):
        self.assertSequenceEqual(SENTENCES, list(split_newline(OSPL)))

    def test_rewrite(self):
        # noinspection PyTypeChecker
        a_text = OSPL.replace('\n', '\u2028').replace(' ', '\n')
        result = rewrite_line_separators(a_text, MAY_CROSS_ONE_LINE)
        self.assertSequenceEqual(OSPL, ''.join(result))
