# coding=utf-8
from __future__ import absolute_import, division, unicode_literals
from unittest import TestCase
from segtok.tokenizer import space_tokenizer, symbol_tokenizer, word_tokenizer, web_tokenizer, IS_POSSESSIVE, \
    split_possessive_markers, IS_CONTRACTION, split_contractions

__author__ = 'Florian Leitner <florian.leitner@gmail.com>'


class TestPossessiveMarker(TestCase):

    def test_misses(self):
        self.assertIsNone(IS_POSSESSIVE.match("Frank'd"))
        self.assertIsNone(IS_POSSESSIVE.match("s'"))

    def test_matches(self):
        self.assertIsNotNone(IS_POSSESSIVE.match("Frank's"))
        self.assertIsNotNone(IS_POSSESSIVE.match("Charles'"))

    def test_unicode(self):
        self.assertIsNotNone(IS_POSSESSIVE.match("Frank\u02BCs"))
        self.assertIsNotNone(IS_POSSESSIVE.match("Charles\u2019"))
        self.assertIsNotNone(IS_POSSESSIVE.match("home-less\u2032"))

    def test_split_with_s(self):
        result = split_possessive_markers(["Fred's", 'is', "Frank's", 'bar', '.'])
        self.assertEqual(7, len(result), str(result))
        self.assertEqual(result[0], "Fred", str(result))
        self.assertEqual(result[1], "'s", str(result))
        self.assertEqual(result[3], "Frank", str(result))
        self.assertEqual(result[4], "'s", str(result))

    def test_split_without_s(self):
        stem, marker = split_possessive_markers(["CHARLES'"])
        self.assertEqual(stem, "CHARLES")
        self.assertEqual(marker, "'")

    def test_split_unicode(self):
        stem, marker = split_possessive_markers(["a\u2032s"])
        self.assertEqual(stem, 'a')
        self.assertEqual(marker, "\u2032s")


class TestContractions(TestCase):

    def test_misses(self):
        self.assertIsNone(IS_CONTRACTION.match("don'r"))
        self.assertIsNone(IS_CONTRACTION.match("'ve"))

    def test_matches(self):
        self.assertIsNotNone(IS_CONTRACTION.match("I've"))
        self.assertIsNotNone(IS_CONTRACTION.match("don't"))

    def test_unicode(self):
        self.assertIsNotNone(IS_CONTRACTION.match("Frank\u02BCs"))
        self.assertIsNotNone(IS_POSSESSIVE.match("Charles\u2019"))
        self.assertIsNotNone(IS_POSSESSIVE.match("home-less\u2032"))

    def test_split_regular(self):
        result = split_contractions(["We'll", 'see', "her's", 'too', '!'])
        self.assertEqual(7, len(result), str(result))
        self.assertEqual(result[0], 'We', str(result))
        self.assertEqual(result[1], "'ll", str(result))
        self.assertEqual(result[3], 'her', str(result))
        self.assertEqual(result[4], "'s", str(result))

    def test_split_not(self):
        stem, contraction = split_contractions(["don't"])
        self.assertEqual(stem, 'do')
        self.assertEqual(contraction, "n't")

    def test_split_unicode(self):
        stem, contraction = split_contractions(["a\u2032d"])
        self.assertEqual(stem, 'a')
        self.assertEqual(contraction, "\u2032d")


class TestSpaceTokenizer(TestCase):

    def setUp(self):
        self.tokenizer = space_tokenizer

    def test_split(self):
        sentence = u" 1\n2\t3  4\t\n 5 "
        self.assertEqual([u'1', u'2', u'3', u'4', u'5'], self.tokenizer(sentence))

    def test_unicode(self):
        sentence = u"1\u00A02\u2007 3  \u2007  "
        self.assertSequenceEqual([u'1', u'2', u'3'], self.tokenizer(sentence))


class TestSymbolTokenizer(TestCase):

    def setUp(self):
        self.tokenizer = symbol_tokenizer

    def test_split(self):
        sentence = u"  1a. --  http://www.ex_ample.com  "
        tokens = [u'1a', u'.', u'--', u'http', u'://', u'www', u'.', u'ex', '_', u'ample', u'.',
                  u'com']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_unicode(self):

        sentence = u"\u0532A\u01CB\u0632:\u2580%"
        tokens = [u'\u0532A\u01CB', u'\u0632:\u2580%']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_unicode_hyphens(self):
        sentence = u"123-ABC\u2011DEF\u2015XYZ"
        tokens = [u'123', u'-', u'ABC', u'\u2011', u'DEF', u'\u2015', u'XYZ']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_slashes(self):
        sentence = u"kg/meter"
        tokens = [u'kg', u'/', u'meter']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_superscript_numbers(self):
        sentence = u"per m\u00B3 earth"  # (superscript three)
        tokens = [u'per', u'm', u'\u00B3', u'earth']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))


class TestWordTokenizer(TestCase):

    def setUp(self):
        self.tokenizer = word_tokenizer

    def assert_inner(self, sep):
        sentence = u" 123%s456 abc%sdef " % (sep, sep)
        tokens = [u'123%s456' % sep, u'abc%sdef' % sep]
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_hyphen_inner(self):
        self.assert_inner(u'-')

    def test_comma_inner(self):
        self.assert_inner(u',')

    def test_dot_inner(self):
        self.assert_inner(u'.')

    def test_colon_inner(self):
        sentence = u"12:6 12:50"
        tokens = [u'12:6', u'12:50']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))
        sentence = u"abc:def 12:34:abc abc:12:34"
        tokens = [u'abc', u':', u'def', u'12:34', u':', u'abc', u'abc', u':', u'12:34']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def assert_dangling(self, sep):
        sentence = u"that %sbut not%s this" % (sep, sep)
        tokens = [u'that', sep, u'but', u'not', sep, u'this']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_hyphen_dangling(self):
        self.assert_dangling(u'-')

    def test_comma_dangling(self):
        self.assert_dangling(u',')

    def test_colon_dangling(self):
        self.assert_dangling(u':')

    def test_semicolon_dangling(self):
        self.assert_dangling(u';')

    def test_comma_dangling_twice(self):
        sentence = u'token (, hi), issue'
        tokens = [u'token', '(', ',', 'hi', ')', ',', 'issue']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_comma_dangling_double(self):
        sentence = u'token (,; hi), issue'
        tokens = [u'token', '(', ',', ';', 'hi', ')', ',', 'issue']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def assert_terminal(self, sep):
        sentence = u"A%s" % sep
        tokens = [u'A', sep]
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_hyphen_terminal(self):
        self.assert_terminal(u'-')

    def test_comma_terminal(self):
        self.assert_terminal(u',')

    def test_colon_terminal(self):
        self.assert_terminal(u':')

    def test_semicolon_terminal(self):
        self.assert_terminal(u';')

    def test_hyphen_repeat(self):
        sentence = u"A--B"
        tokens = [u'A', u'--', u'B']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_comma_repeat(self):
        sentence = u"A,,B"
        tokens = [u'A', u',', u',', u'B']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_hyphen_unicode(self):
        sentence = u"\u00A0ABC\u2011DEF\u2015XYZ\u00A0"
        tokens = [u'ABC\u2011DEF', u'\u2015', u'XYZ']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_hyphen_mixed(self):
        sentence = u"123-Abc-xyZ-123"
        tokens = [u'123-Abc-xyZ-123']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_hyphen_linebreak(self):
        sentence = u"A-B A-\rB A-\nB A-  \r\n\tB"
        tokens = [u'A-B', u'A-B', u'A-B', u'A-B', ]
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_dots(self):
        sentence = u"\t1.2.3, f.e., is Mr. .Abbreviation.\n"
        tokens = [u'1.2.3', u',', u'f.e.', u',', u'is', u'Mr.', u'.', u'Abbreviation', u'.']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_splice_sentence_terminal_start(self):
        sentence = u"This is a ?sentence,"
        tokens = [u'This', u'is', u'a', u'?', u'sentence', u',']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_splice_sentence_terminal_end(self):
        sentence = u"This is a sentence?,"
        tokens = [u'This', u'is', u'a', u'sentence', u'?', u',']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_final_abbreviation(self):
        sentence = u"This is another abbrev..\n"
        tokens = [u'This', u'is', u'another', u'abbrev.', u'.']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_final_ellipsis(self):
        sentence = u"Please no more..."
        tokens = [u'Please', u'no', u'more', u'...']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_abbreviated_ellipsis(self):
        sentence = u"abbrev... final...."
        tokens = [u'abbrev', u'...', u'final', u'...', u'.']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_double_dot(self):
        sentence = u"a.. b.."
        tokens = [u'a.', u'.', u'b.', u'.']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_dot_apo_single_quote(self):
        sentence = u"He said, 'this.'"
        tokens = [u'He', u'said', u",", u"'", u'this', u'.', u"'"]
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_ellipsis_inner(self):
        sentence = u"and...or"
        tokens = [u'and', u'...', u'or']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_apostrophe_simple(self):
        # NB: ASCII single quote "apostrophe" (ab-) use is to unsafe to maintain attached...
        sentence = u"That's 'tis less' O'Don'Ovan's"
        tokens = [u"That's", u"'", u"tis", u"less'", u"O'Don'Ovan's"]
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_possesive_s_ascii_apostrophe(self):
        # NB: ...except for the clear case of "...s'"
        sentence = u"Words' end."
        tokens = [u"Words'", u'end', u'.']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_apostrophe_unicode(self):
        sentence = u"\u2019tis less\u02BC O\u2019Neil\u02BCs"
        tokens = [u'\u2019tis', u'less\u02BC', u'O\u2019Neil\u02BCs']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_hyphen_dot_apostrophe(self):
        sentence = u" O.h'Ne.l- \n l's "
        tokens = [u"O.h'Ne.l-l's"]
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_numbers(self):
        sentence = u"$123,456.99 45.67+/-1.23%"
        tokens = [u'$', u'123,456.99', u'45.67', u'+/-', u'1.23', u'%']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_chemicals_and_DNA(self):
        sentence = u"1,r-4-cyclo.hexene 5\u2032-ATGCAAAT-3\u2032 5'-ACGT-3'"
        tokens = [u'1,r-4-cyclo.hexene',
                  u'5\u2032-ATGCAAAT-3\u2032',
                  u'5', u"'-", u'ACGT-3', u"'"]  # this one is too ambiguous
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_physical_units(self):
        sentence = u"10 V\u00B7m\u207B\u00B9 msec\u00B2"
        tokens = [u'10', u'V', u'\u00B7', u'm\u207B\u00B9', u'msec\u00B2']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_chemical_formula(self):
        sentence = u"O\u2082 H\u2081\u2082Si\u2085O\u2082 " \
                   u"Al\u2082(SO\u2084)\u2083 [NO\u2084]\u207B Not\u2081"
        tokens = [u"O\u2082", u"H\u2081\u2082Si\u2085O\u2082",
                  u"Al\u2082", u"(", u"SO\u2084", u")\u2083",
                  u"[", u"NO\u2084", u"]\u207B",
                  u"Not", u'\u2081']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))

    def test_URLs(self):
        sentence = u"http://www.example.com/path/to.file?kwd=1&arg"
        tokens = [u'http', u'://', u'www.example.com', u'/', u'path',
                  u'/', u'to.file', u'?', u'kwd', u'=', u'1', u'&', u'arg']
        self.assertSequenceEqual(tokens, self.tokenizer(sentence))


class TestWebTokenizer(TestCase):

    def setUp(self):
        self.tokenizer = web_tokenizer

    def test_URL(self):
        sentence = u"test ftps://user:pass@file.server.com:1234/get/me.this?what=that#part test"
        tokens = sentence.split()
        self.assertEqual(tokens, self.tokenizer(sentence))

    def test_URL_at_string_end(self):
        sentence = u"test this works https://file.server.com:8080/"
        tokens = sentence.split()
        self.assertEqual(tokens, self.tokenizer(sentence))

    def test_URL_with_root_path(self):
        sentence = u"test this https://file.server.com:8080/ as well"
        tokens = sentence.split()
        self.assertEqual(tokens, self.tokenizer(sentence))

    def test_link(self):
        sentence = u'<a href="http://here.to/me">hi'
        tokens = [u'<', u'a', u'href', u'="', u'http://here.to/me', u'">', u'hi']
        self.assertEqual(tokens, self.tokenizer(sentence))

    def test_email(self):
        sentence = u"test here+there#this&that@mo.re_serious-now.com test"
        tokens = sentence.split()
        self.assertEqual(tokens, self.tokenizer(sentence))

    def test_named(self):
        sentence = u'"Florian Leitner <florian.leitner@gmail.com>"'
        tokens = [u'"', u'Florian', u'Leitner', u'<', u'florian.leitner@gmail.com', u'>"']
        self.assertEqual(tokens, self.tokenizer(sentence))

    def test_bad_email(self):
        sentence = u"test hidden@mail.com~"
        tokens = [u'test', u'hidden', u'@', u'mail.com', u'~']
        self.assertEqual(tokens, self.tokenizer(sentence))

    def test_sentence(self):
        sentence = u"""
            Independent of current body composition, IGF-I levels at 5 yr were significantly
            associated with rate of weight gain between 0-2 yr (beta=0.19; P&lt;0.0005);
            and children who showed postnatal catch-\nup growth (i.e. those who showed gains in
            weight or length between 0-2 yr by >0.67 SD score) had higher IGF-I levels than other
            children (P=0.02; http://univ.edu.es/study.html) [20-22].
        """
        tokens = u"""
            Independent of current body composition , IGF-I levels at 5 yr were significantly
            associated with rate of weight gain between 0-2 yr ( beta = 0.19 ; P < 0.0005 ) ;
            and children who showed postnatal catch-up growth ( i.e. those who showed gains in
            weight or length between 0-2 yr by > 0.67 SD score ) had higher IGF-I levels than other
            children ( P = 0.02 ; http://univ.edu.es/study.html ) [ 20-22 ] .
        """.split()
        self.assertEqual(tokens, self.tokenizer(sentence))
