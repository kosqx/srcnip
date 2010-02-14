#!/usr/bin/env python


import os
import os.path
import hashlib


from languages import Languages


def to_unicode(string):
    if string is None:
        return None
    elif isinstance(string, unicode):
        return string
    elif isinstance(string, str):
        return unicode(string, 'utf8')


class Snippet(object):
    def __init__(self, code, tags, lang, id=None):
        super(Snippet, self).__init__()
        
        self.id = id
        self.code = to_unicode(code)
        self.tags = set(to_unicode(tags).split())
        self.lang = to_unicode(lang)


def parse_query(query):
    SHORT = {
        'l':        'lang',
        'lang':     'lang',
        'language': 'lang',
        'a':        'age',
        'age':      'age',
    }
    
    result = {'tags': set()}
    
    parts = query.split()
    for part in parts:
        if ':' in part:
            tmp = part.split(':', 1)
            if tmp[0] in SHORT:
                result[SHORT[tmp[0]]] = tmp[1]
        else:
            result['tags'].add(part)
    

class Storage:
    def __init__(self, location):
        pass
    
    def search(self, tags, lang):
        pass
    
    def add(self, content, tags, lang):
        pass
    
    def tags_count(self):
        pass
    
    def lang_count(self):
        pass


class FileStorage(Storage):
    def __init__(self, location='~/.snipper'):
        self._languages = Languages()
        self._data = []
        self._do_location(location)
        
        for name in os.listdir(self._location):
            path = os.path.join(self._location, name)
            if not name.startswith('.') and os.path.isfile(path):
                self._read(path)
    
    def _do_location(self, location):
        location = os.path.abspath(os.path.expanduser(location))
        if os.path.exists(location):
            if not os.path.isdir(location):
                raise IOError, '%r is not a directory' % location
        else:
            os.makedirs(location)
        
        self._location = location
    
    def _read(self, filename):
        f = open(filename)
        lines = f.read().splitlines()
        f.close()
        
        content = ''
        tags = set()
        lang = None
        
        for i, line in enumerate(lines):
            if line.startswith('lang:'):
                lang = line[5:].strip()
                try:
                    lang = self._languages[lang].code
                except KeyError:
                    pass
            if line.startswith('tags:'):
                tags = set(line[5:].strip().split())
            if line.startswith('----'):
                content = '\n'.join(lines[i + 1:])
        
        self._data.append((content, tags, lang))
    
    def search(self, tags=[], lang=None):
        tags = set(tags)
        result = []
        for item in self._data:
            if item[1].issuperset(tags) and (item[2] == lang or lang is None):
                result.append(item)
        
        return result
    
    
    def add(self, content, tags, lang):
        tags = set(tags)
        try:
            lang = self._languages[lang].code
        except KeyError:
            pass
        self._data.append((content, tags, lang))
        self._write(content, tags, lang)

    def _write(self, content, tags, lang):
        name = hashlib.md5(content).hexdigest()
        
        data = []
        if lang:
            data.append('lang: %s' % lang)
        if tags:
            data.append('tags: %s' % ' '.join(tags))
        data.append('----')
        data.append(content)
        data = '\n'.join(data)
        
        f = open(os.path.join(self._location, name), 'w')
        f.write(data)
        f.close()

