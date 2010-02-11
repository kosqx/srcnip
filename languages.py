#!/usr/bin/env python
#-*- coding: utf-8 -*-


class Language(object):
    def __init__(self, data):
        super(Language, self).__init__()
        
        self.name  = data[0]
        self.code  = data[1]
        self.codes = frozenset(data[1:])


class Languages(object):
    def __init__(self):
        super(Languages, self).__init__()
        
        self._list = [
            ('AWK',             'awk'),
            ('ActionScript',    'actionscript'),
            ('Ada',             'ada'),
            ('Asembler',        'asembler'),
            ('C',               'c'),
            ('C#',              'c#'),
            ('C++',             'c++'),
            ('C++/CLI',         'c++/cli'),
            ('COBOL',           'cobol'),
            ('Clojure',         'clojure', 'clj', '.clj'),
            ('Common Lisp',     'common-lisp'),
            ('D',               'd'),
            ('Delphi',          'delphi'),
            ('Delphi Prism',    'delphi-prism'),
            ('Delphi.NET',      'delphi.net'),
            ('Eiffel',          'eiffel'),
            ('Erlang',          'erlang', 'erl', '.erl'),
            ('F#',              'f#'),
            ('Forth',           'forth'),
            ('Fortran',         'fortran'),
            ('Haskell',         'haskell'),
            ('Icon',            'icon'),
            ('Io',              'io', '.io'),
            ('Java',            'java'),
            ('JavaScript',      'javascript', 'js', '.js'),
            ('Lisp',            'lisp'),
            ('Lua',             'lua', '.lua'),
            ('ML',              'ml'),
            ('Modula-2',        'modula-2'),
            ('MiniD',           'minid', '.md'),
            ('Nemerle',         'nemerle'),
            ('OCaml',           'ocaml'),
            ('Oberon',          'oberon'),
            ('Object Pascal',   'object-pascal'),
            ('Objective-C',     'objective-c'),
            ('Oxygene',         'oxygene'),
            ('PHP',             'php'),
            ('PL/SQL',          'pl/sql'),
            ('PLEX',            'plex'),
            ('Pascal',          'pascal'),
            ('Perl',            'perl', 'pl', 'pm', '.pl', '.pm'),
            ('Processing',      'processing'),
            ('Prolog',          'prolog'),
            ('Python',          'python', 'py', '.py', '.pyw', '.sc'),
            ('REXX',            'rexx'),
            ('Ruby',            'ruby', 'rb', '.rb', '.rbw'),
            ('Scala',           'scala'),
            ('Scheme',          'scheme'),
            ('Smalltalk',       'smalltalk'),
            ('Snobol',          'snobol'),
            ('TCL',             'tcl', '.tcl'),
            ('VB.NET',          'vb.net'),
            ('Visual Basic',    'visual-basic')
        ]
        
        # TODO: optional read aditional languages from file
        
        self._list.sort()
        
        self._dict = {}
        for row in self._list:
            lang = Language(row)
            for i in row:
                assert i not in self._dict
                self._dict[i] = lang
    
    def __getitem__(self, key):
        return self._dict[key.lower()]
    
    def get_names(self):
        return [row[0] for row in self._list]

