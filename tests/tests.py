#!/usr/bin/env python
#-*- coding: utf-8 -*-


import unittest


from srcnip.languages import languages
from srcnip.storage import Snippet
from srcnip.parser import parse, simplify, ParseError, LexerError, SyntaxError


class LanguagesTestCase(unittest.TestCase):
    def testGetItemPython(self):
        py = languages['py']
        self.assertEquals(py.name, 'Python')
        self.assertEquals(py.code, 'python')
        
        self.assertTrue('python' in py.codes)
        self.assertTrue('py'     in py.codes)
        self.assertTrue('.py'    in py.codes)
        self.assertTrue('.pyw'   in py.codes)
        
    def testGetItemUnexisting(self):
        def do_get():
            return languages['unexisting']
            
        self.assertRaises(KeyError, do_get)
        
    def testContains(self):
        self.assertTrue('Python' in languages)
        self.assertTrue('python' in languages)
        self.assertTrue('py'     in languages)
        self.assertTrue('.py'    in languages)
        
        self.assertFalse('Foo' in languages)
        self.assertFalse(None  in languages)
    
    def testNames(self):
        names = languages.get_names()
        
        self.assertTrue('Python' in names)
        self.assertTrue('JavaScript' in names)
        
        self.assertFalse('python' in names)
        self.assertFalse('javascript' in names)
    
    def testNamesSort(self):
        names = languages.get_names()
        self.assertEquals(names, sorted(names))


class SnippetTestCase(unittest.TestCase):
    def testAttr(self):
        sn = Snippet('a = "żółw"', 'py var', 'py')
        
        self.assertEquals(sn.id,   None)
        self.assertEquals(sn.code, u'a = "żółw"')
        self.assertEquals(sn.tags, set([u'py', u'var']))
        self.assertEquals(sn.lang, u'python')
        
    def testTags(self):
        self.assertEquals(Snippet('', '',    'py').tags, set())
        self.assertEquals(Snippet('', u'',   'py').tags, set())
        self.assertEquals(Snippet('', (),    'py').tags, set())
        self.assertEquals(Snippet('', [],    'py').tags, set())
        self.assertEquals(Snippet('', set(), 'py').tags, set())
        
        self.assertEquals(Snippet('', 'py var',             'py').tags, set([u'py', u'var']))
        self.assertEquals(Snippet('', u'py var',            'py').tags, set([u'py', u'var']))
        
        self.assertEquals(Snippet('', ['py', 'var'],        'py').tags, set([u'py', u'var']))
        self.assertEquals(Snippet('', [u'py', u'var'],      'py').tags, set([u'py', u'var']))
        
        self.assertEquals(Snippet('', ('py', 'var'),        'py').tags, set([u'py', u'var']))
        self.assertEquals(Snippet('', (u'py', u'var'),      'py').tags, set([u'py', u'var']))
        
        self.assertEquals(Snippet('', set(['py', 'var']),   'py').tags, set([u'py', u'var']))
        self.assertEquals(Snippet('', set([u'py', u'var']), 'py').tags, set([u'py', u'var']))
        
    def testLang(self):
        self.assertEquals(Snippet('', '', 'Python').lang, 'python')
        self.assertEquals(Snippet('', '', 'python').lang, 'python')
        self.assertEquals(Snippet('', '', 'py'    ).lang, 'python')
        self.assertEquals(Snippet('', '', '.py'   ).lang, 'python')
        
        self.assertEquals(Snippet('', '', ''      ).lang, None)
        self.assertEquals(Snippet('', '', None    ).lang, None)


class ParserTestCase(unittest.TestCase):
    # TODO: more test: exceptions, more complex expresons
    def testAtom(self):
        self.assertEquals(parse('foo'),                        ('tag', 'foo'))
        self.assertEquals(parse('*oo'),                        ('ltag', 'oo'))
        self.assertEquals(parse('fo*'),                        ('rtag', 'fo'))
        self.assertEquals(parse('*o*'),                        ('btag', 'o'))
        self.assertEquals(parse('"foo"'),                      ('text', 'foo'))
        self.assertEquals(parse('"foo\\"bar\\"baz"'),          ('text', 'foo"bar"baz'))
        self.assertEquals(parse('/foo/'),                      ('regexp', 'foo'))
        self.assertEquals(parse('/foo\\/bar/'),                ('regexp', 'foo/bar'))
        self.assertEquals(parse('.foo'),                       ('ext', '.foo'))
        self.assertEquals(parse('foo:bar'),                    ('foo', 'bar'))
    
    def testSpace(self):
        self.assertEquals(parse('foo'),                        ('tag', 'foo'))
        self.assertEquals(parse('\t \tfoo'),                   ('tag', 'foo'))
        self.assertEquals(parse('foo  \t'),                    ('tag', 'foo'))
        self.assertEquals(parse(' \tfoo\t '),                  ('tag', 'foo'))
    
    def testNot(self):
        self.assertEquals(parse('!foo'),                       ('not', ('tag', 'foo')))
        self.assertEquals(parse('NOT foo'),                    ('not', ('tag', 'foo')))
        self.assertEquals(parse('!NOT foo'),                   ('not', ('not', ('tag', 'foo'))))
    
    def testAnd(self):
        self.assertEquals(parse('foo.bar'),                    ('and', ('tag', 'foo'), ('ext', '.bar')))
        self.assertEquals(parse('foo bar'),                    ('and', ('tag', 'foo'), ('tag', 'bar')))
        self.assertEquals(parse('foo bar baz'),                ('and', ('tag', 'foo'), ('tag', 'bar'), ('tag', 'baz')))
        self.assertEquals(parse('a b c d'),                    ('and', ('tag', 'a'), ('tag', 'b'), ('tag', 'c'), ('tag', 'd')))
        self.assertEquals(parse('a AND b & c && d'),           ('and', ('tag', 'a'), ('tag', 'b'), ('tag', 'c'), ('tag', 'd')))
        self.assertEquals(parse('a OR b | c || d'),            ('or', ('tag', 'a'), ('tag', 'b'), ('tag', 'c'), ('tag', 'd')))
    
    def testOr(self):
        self.assertEquals(parse('a b OR c d'),                 ('or', ('and', ('tag', 'a'), ('tag', 'b')), ('and', ('tag', 'c'), ('tag', 'd'))))
        self.assertEquals(parse('a b | c d'),                  ('or', ('and', ('tag', 'a'), ('tag', 'b')), ('and', ('tag', 'c'), ('tag', 'd'))))
        self.assertEquals(parse('a b || c d'),                 ('or', ('and', ('tag', 'a'), ('tag', 'b')), ('and', ('tag', 'c'), ('tag', 'd'))))
        self.assertEquals(parse('a b ||| c d'),                ('or', ('and', ('tag', 'a'), ('tag', 'b')), ('and', ('tag', 'c'), ('tag', 'd'))))
    
    def testParens(self):
        self.assertEquals(parse('(a) (b) (c) (d)'),            ('and', ('tag', 'a'), ('tag', 'b'), ('tag', 'c'), ('tag', 'd')))
        self.assertEquals(parse('(a b c d)'),                  ('and', ('tag', 'a'), ('tag', 'b'), ('tag', 'c'), ('tag', 'd')))
        self.assertEquals(parse('(a b)  (c d)'),               ('and', ('and', ('tag', 'a'), ('tag', 'b')), ('and', ('tag', 'c'), ('tag', 'd'))))
        self.assertEquals(parse('(a b | c) d'),                ('and', ('or', ('and', ('tag', 'a'), ('tag', 'b')), ('tag', 'c')), ('tag', 'd')))
        self.assertEquals(parse('a (b | c) d'),                ('and', ('tag', 'a'), ('or', ('tag', 'b'), ('tag', 'c')), ('tag', 'd')))
        self.assertEquals(parse('a (b | c d)'),                ('and', ('tag', 'a'), ('or', ('tag', 'b'), ('and', ('tag', 'c'), ('tag', 'd')))))


if __name__ == '__main__':
    unittest.main()

