#!/usr/bin/env python


import os
import os.path
import hashlib

LANGUAGES = [
    ('AWK',          ('awk',), (), 5),
    ('ActionScript', ('actionscript',), (), 5),
    ('Ada',          ('ada',), (), 5),
    ('Asembler',     ('asembler',), (), 5),
    ('C',            ('c',), (), 5),
    ('C#',           ('c#',), (), 5),
    ('C++',          ('c++',), (), 5),
    ('C++/CLI',      ('c++/cli',), (), 5),
    ('COBOL', ('cobol',), (), 5),
    ('Clojure', ('clojure',), (), 5),
    ('Common Lisp', ('common lisp',), (), 5),
    ('D', ('d',), (), 5),
    ('Delphi', ('delphi',), (), 5),
    ('Delphi Prism', ('delphi prism',), (), 5),
    ('Delphi.NET', ('delphi.net',), (), 5),
    ('Eiffel', ('eiffel',), (), 5),
    ('Erlang', ('erlang',), (), 5),
    ('F#', ('f#',), (), 5),
    ('Forth', ('forth',), (), 5),
    ('Fortran', ('fortran',), (), 5),
    ('Haskell', ('haskell',), (), 5),
    ('Icon', ('icon',), (), 5),
    ('Java', ('java',), (), 5),
    ('JavaScript', ('javascript',), (), 5),
    ('Lisp', ('lisp',), (), 5),
    ('Lua', ('lua',), (), 5),
    ('ML', ('ml',), (), 5),
    ('Modula-2', ('modula-2',), (), 5),
    ('Nemerle', ('nemerle',), (), 5),
    ('OCaml', ('ocaml',), (), 5),
    ('Oberon', ('oberon',), (), 5),
    ('Object Pascal', ('object pascal',), (), 5),
    ('Objective-C', ('objective-c',), (), 5),
    ('Oxygene', ('oxygene',), (), 5),
    ('PHP', ('php',), (), 5),
    ('PL/SQL', ('pl/sql',), (), 5),
    ('PLEX', ('plex',), (), 5),
    ('Pascal', ('pascal',), (), 5),
    ('Perl', ('perl',), (), 5),
    ('Processing', ('processing',), (), 5),
    ('Prolog', ('prolog',), (), 5),
    ('Python', ('python',), (), 5),
    ('REXX', ('rexx',), (), 5),
    ('Ruby', ('ruby',), (), 5),
    ('Scala', ('scala',), (), 5),
    ('Scheme', ('scheme',), (), 5),
    ('Smalltalk', ('smalltalk',), (), 5),
    ('Snobol', ('snobol',), (), 5),
    ('VB.NET', ('vb.net',), (), 5),
    ('Visual Basic', ('visual basic',), (), 5)
]

def get_language_dict():
    result = {}
    for name, codes, _1, _2 in LANGUAGES:
        result[name] = codes[0]
    return result

def get_languages():
    return [name for name, codes, _1, _2 in LANGUAGES]

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

