#!/usr/bin/env python
#-*- coding: utf-8 -*-


import unittest


from languages import languages
from storage import Snippet


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


if __name__ == '__main__':
    unittest.main()

