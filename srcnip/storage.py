#!/usr/bin/env python


import os
import os.path
import re
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


def snipet_match_query(snippet, query):
    if query[0] == 'tag':
        return query[1] in snippet.tags
    if query[0] == 'ltag':
        return any(tag.endswith(query[1]) for tag in snippet.tags)
    if query[0] == 'rtag':
        return any(tag.startswith(query[1]) for tag in snippet.tags)
    if query[0] == 'btag':
        return any(query[1] in tag for tag in snippet.tags)
        
    if query[0] == 'lang':
        return snippet.lang == languages[query[1]].code
    if query[0] == 'ext':
        return snippet.lang == languages[query[1]].code
    
    if query[0] == 'text':
        return query[1] in snippet.code
    if query[0] == 'regexp':
        return re.search(query[1], snippet.code)
    
    if query[0] == 'not':
        return not snipet_match_query(snippet, query[1])
    if query[0] == 'and':
        return all(snipet_match_query(snippet, i) for i in query[1:])
    if query[0] == 'or':
        return any(snipet_match_query(snippet, i) for i in query[1:])


class Storage:
    def __init__(self, location):
        pass
    
    def search(self, query):
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
    
    def search(self, query):
        result = []
        for item in self._data:
            if snipet_match_query(item, query):
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
