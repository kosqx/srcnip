#!/usr/bin/env python


import os
import os.path
import hashlib
from datetime import datetime

from languages import languages


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
        
        if isinstance(tags, basestring):
            self.tags = set(to_unicode(tags).split())
        else:
            self.tags = set([unicode(i) for i in tags])
        
        if lang in languages:
            self.lang = to_unicode(languages[lang].code)
        else:
            self.lang = None


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
    
    def add(self, snippet):
        pass
    
    def delete(self, snippet):
        pass
    
    def tags_count(self):
        pass
    
    def lang_count(self):
        pass


class FileStorage(Storage):
    def __init__(self, location='~/.srcnip'):
        self._data = []
        self._do_location(location)
        
        for name in os.listdir(self._location):
            path = os.path.join(self._location, name)
            if not name.startswith('.') and os.path.isfile(path):
                self._data.append(self._read(path))
    
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
        lines = unicode(f.read(), 'utf8').splitlines()
        f.close()
        
        id = os.path.basename(filename)
        code = ''
        tags = set()
        lang = None
        
        for i, line in enumerate(lines):
            if line.startswith('lang:'):
                lang = line[5:].strip()
            if line.startswith('tags:'):
                tags = set(line[5:].strip().split())
            if line.startswith('----'):
                code = '\n'.join(lines[i + 1:])
                break
        
        return Snippet(code, tags, lang, id)
    
    def search(self, tags=[], lang=None):
        tags = set(tags)
        result = []
        for item in self._data:
            if item.tags.issuperset(tags) and (item.lang == lang or lang is None):
                result.append(item)
        
        return result
    
    def add(self, snippet):
        id = self._write(snippet)
        snippet.id = id
        self._data.append(snippet)
        return id
    
    def delete(self, snippet):
        assert snippet.id is not None
        
        filename = os.path.join(self._location, snippet.id)
        os.remove(filename)
        
        for i, s in enumerate(self._data):
            if s.id == snippet.id:
                del self._data[i]
                break
    
    def _write(self, snippet):
        name = hashlib.md5(snippet.code.encode('utf8')).hexdigest()
        
        data = []
        if snippet.lang:
            data.append(u'lang: %s' % snippet.lang)
        if snippet.tags:
            data.append(u'tags: %s' % ' '.join(sorted(list(snippet.tags))))
        data.append(u'date: %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        data.append(u'----')
        data.append(snippet.code)
        data = u'\n'.join(data)
        
        f = open(os.path.join(self._location, name), 'w')
        f.write(data.encode('utf8'))
        f.close()
        
        return name

    def lang_count(self):
        result = {}
        
        for item in self._data:
            result[item.lang] = result.get(item.lang, 0) + 1
        
        return result
