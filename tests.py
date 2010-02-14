#!/usr/bin/env python
#-*- coding: utf-8 -*-


import unittest


import languages
import storage


class LanguagesTestCase(unittest.TestCase):
    def setUp(self):
        self.lang = languages.Languages()
        
    def testGetItemPython(self):
        py = self.lang['py']
        self.assertEquals(py.name, 'Python')
        self.assertEquals(py.code, 'python')
        
        self.assertTrue('python' in py.codes)
        self.assertTrue('py'     in py.codes)
        self.assertTrue('.py'    in py.codes)
        self.assertTrue('.pyw'   in py.codes)
        
    def testGetItemUnexisting(self):
        def do_get(lang):
            return lang['unexisting']
            
        self.assertRaises(KeyError, do_get, self.lang)
    
    def testNames(self):
        names = self.lang.get_names()
        
        self.assertTrue('Python' in names)
        self.assertTrue('JavaScript' in names)
        
        self.assertFalse('python' in names)
        self.assertFalse('javascript' in names)
    
    def testNamesSort(self):
        names = self.lang.get_names()
        self.assertEquals(names, sorted(names))


class SnippetTestCase(unittest.TestCase):
    def setUp(self):
        self.sn = storage.Snippet('a = "żółw"', 'py var', 'py')
    
    def testAttr(self):
        self.assertEquals(self.sn.id,   None)
        self.assertEquals(self.sn.code, u'a = "żółw"')
        self.assertEquals(self.sn.tags, set([u'py', u'var']))
        self.assertEquals(self.sn.lang, u'py')


if __name__ == '__main__':
    unittest.main()

