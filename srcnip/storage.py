#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Copyright (C) 2010 Krzysztof Kosyl <krzysztof.kosyl@gmail.com>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""


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
    def __init__(self, code, tags, lang, id=None, date=None):
        super(Snippet, self).__init__()
        
        self.id = id
        self.date = date
        self.code = to_unicode(code)
        
        if isinstance(tags, basestring):
            self.tags = set(to_unicode(tags).split())
        else:
            self.tags = set([unicode(i) for i in tags])
        
        if lang in languages:
            self.lang = to_unicode(languages[lang].code)
        else:
            self.lang = None


def parse_timediff(text):
    SUFIXES = [
        ('s', 1),
        ('m', 60),
        ('h', 60 * 60),
        ('d', 60 * 60 * 24),
        ('w', 60 * 60 * 24 * 7),
        ('m', 60 * 60 * 24 * 30),
        ('y', 60 * 60 * 24 * 365),
    ]
    
    text = text.lower()
    
    multiply = 60 * 60 * 24
    for sufix, mul in SUFIXES:
        if text.endswith(sufix):
            multiply = mul
            text = text[:-len(sufix)]
            break
    
    try:
        return float(text) * multiply
    except ValueError:
        return None

def compare(query, date):
    
    if date == None:
        return ''
    print query, date
    requested = parse_timediff(query)
    if requested == None:
        return ''
    current = datetime.now() - date
    current = current.days * 24 * 60 * 60 + current.seconds
    
    print current, requested 
    if current >= requested:
        print 'old'
        return 'older'
    else:
        print 'new'
        return 'newer'
    
    

def snipet_match_query(snippet, query):
    if query[0] == 'none':
        return False
    if query[0] == 'all':
        return True
    
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
        
    if query[0] == 'older':
        return compare(query[1], snippet.date) == 'older'
        
    if query[0] == 'newer':
        return compare(query[1], snippet.date) == 'newer'
    
    if query[0] == 'not':
        return not snipet_match_query(snippet, query[1])
    if query[0] == 'and':
        return all(snipet_match_query(snippet, i) for i in query[1:])
    if query[0] == 'or':
        return any(snipet_match_query(snippet, i) for i in query[1:])


class Storage(object):
    def __init__(self):
        super(Storage, self).__init__()
    
    def search(self, query):
        pass
    
    def save(self, snippet):
        pass
    
    def delete(self, snippet):
        pass
    
    def tags_count(self):
        pass
    
    def lang_count(self):
        pass


class MemoryStorage(Storage):
    def __init__(self):
        super(MemoryStorage, self).__init__()
        self._data = []
    
    def search(self, query):
        result = []
        for item in self._data:
            if snipet_match_query(item, query):
                result.append(item)
        
        return result
    
    def save(self, snippet):
        id = self._do_save(snippet)
        
        snippet.id = id
        self._data.append(snippet)
        return id
    
    def delete(self, snippet):
        assert snippet.id is not None
        
        self._do_delete(snippet)
        
        for i, s in enumerate(self._data):
            if s.id == snippet.id:
                del self._data[i]
                break
        
        
    def tags_count(self):
        result = {}
        for item in self._data:
            for tag in item.tags:
                result[tag] = result.get(tag, 0) + 1
        return result
    
    def lang_count(self):
        result = {}
        for item in self._data:
            result[item.lang] = result.get(item.lang, 0) + 1
        return result
    
    def _do_save(self, snippet):
        data, id = self._format(snippet)
        return id
    
    def _do_delete(self, snippet):
        pass
    
    def _parse(self, data, id=None):
        lines = data.splitlines()
        code = ''
        tags = set()
        lang = None
        date = None
        
        for i, line in enumerate(lines):
            if line.startswith('lang:'):
                lang = line[5:].strip()
            if line.startswith('tags:'):
                tags = set(line[5:].strip().split())
            if line.startswith('date:'):
                date = datetime.strptime(line[5:].strip(), '%Y-%m-%d %H:%M:%S')
            if line.startswith('----'):
                code = '\n'.join(lines[i + 1:])
                break
        
        return Snippet(code, tags, lang, id, date)
    
    def _format(self, snippet):
        id = hashlib.md5(snippet.code.encode('utf8')).hexdigest()
        
        data = []
        if snippet.lang:
            data.append(u'lang: %s' % snippet.lang)
        if snippet.tags:
            data.append(u'tags: %s' % ' '.join(sorted(list(snippet.tags))))
        data.append(u'date: %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        data.append(u'----')
        data.append(snippet.code)
        data = u'\n'.join(data)
        
        return data, id

class FileStorage(MemoryStorage):
    def __init__(self, location='~/.srcnip/file'):
        super(FileStorage, self).__init__()
        
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
        data = unicode(f.read(), 'utf8')
        f.close()
        
        return self._parse(data, os.path.basename(filename))
        
    
    def _do_save(self, snippet):
        data, id = self._format(snippet)
        
        f = open(os.path.join(self._location, id), 'w')
        f.write(data.encode('utf8'))
        f.close()
        
        return id
    
    def _do_delete(self, snippet):
        filename = os.path.join(self._location, snippet.id)
        os.remove(filename)




