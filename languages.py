#!/usr/bin/env python
#-*- coding: utf-8 -*-


class Language(object):
    def __init__(self, data):
        super(Language, self).__init__()
        
        self.name  = data[0]
        self.code  = data[1]
        self.codes = frozenset(data[1:])


class Languages(object):
    def __init__(self, list):
        super(Languages, self).__init__()
        
        # TODO: optional read aditional languages from file
        self._list = list
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


languages_list = [
    ## LLVM assembly, Cython
    ('AppleScript',         'applescript', '.applescript'),
    ('AWK',                 'awk'),
    ('ActionScript',        'actionscript', 'as', '.as'),
    ('Ada',                 'ada'),
    ('Assembler::Intel',    'nasm', 'asm', '.asm'),
    ('Assembler::AT&T',     'gas', 's', '.s'),
    ('Boo',                 'boo', '.boo'),
    ('Bash',                'bash', 'sh', '.sh'),
    ('Batch',               'batch', 'bat', '.bat', '.cmd'),
    ('C',                   'c', '.c', '.h'),
    ('C#',                  'c#', 'csharp', '.cs'),
    ('C++',                 'c++', 'cpp', '.cpp', '.hpp', '.c++', '.h++', '.cc', '.hh', '.cxx', '.hxx'),
    ('C++/CLI',             'c++/cli'),
    ('COBOL',               'cobol'),
    ('Clojure',             'clojure', 'clj', '.clj'),
    ('CSS',                 'css', '.css'),
    ('Common Lisp',         'common-lisp', 'cl', '.cl', '.lisp', '.el'),
    ('D',                   'd', '.d', '.di'),
    ('Delphi',              'delphi'),
    ('Delphi Prism',        'delphi-prism'),
    ('Delphi.NET',          'delphi.net'),
    ('Dylan',               'dylan', '.dylan'),
    ('Eiffel',              'eiffel'),
    ('Erlang',              'erlang', 'erl', '.erl', '.hrl'),
    ('F#',                  'f#'),
    ('Forth',               'forth'),
    ('Fortran',             'fortran', '.f', '.f90'),
    ('Gettext',             'gettext', 'pot', 'po', '.pot', '.po'),
    ('GLSL',                'glsl', '.vert', '.frag', '.geo'),
    ('Go',                  'go', '.go'),
    ('Haskell',             'haskell', 	'hs', '.hs'),
    ('HTML',                'html', '.html', '.htm', '.xhtml'),
    ('Icon',                'icon'),
    ('Io',                  'io', '.io'),
    ('Java',                'java', '.java'),
    ('JavaScript',          'javascript', 'js', '.js'),
    ('Lisp',                'lisp'),
    ('Lua',                 'lua', '.lua'),
    ('Makefile',            'makefile', 'make', 'mk'),
    ('Matlab',              'matlab', 'octave'), # Also '.m'
    ('MuPAD',               'mupad', 'mu' '.mu'),
    ('ML',                  'ml'),
    ('Modula-2',            'modula-2'),
    ('MiniD',               'minid', '.md'),
    ('Nemerle',             'nemerle'),
    ('OCaml',               'ocaml', '.mli', '.mll', '.mly'), #Also: '.ml'
    ('Oberon',              'oberon'),
    ('Object Pascal',       'object-pascal'),
    ('Objective-C',         'objective-c', 'objectivec', 'obj-c', 'objc', '.m'),
    ('Oxygene',             'oxygene'),
    ('PHP',                 'php', '.php', '.php3', '.php4', '.php5'),
    ('PL/SQL',              'pl/sql'),
    ('PLEX',                'plex'),
    ('Pascal',              'pascal'),
    ('Perl',                'perl', 'pl', 'pm', '.pl', '.pm'),
    ('Processing',          'processing'),
    ('Prolog',              'prolog', '.prolog', '.pro'), # also: '.pl'
    ('Python',              'python', 'py', '.py', '.pyw', '.sc'),
    ('REXX',                'rexx'),
    ('Ruby',                'ruby', 'rb', '.rb', '.rbw'),
    ('Scala',               'scala', '.scala'),
    ('Scheme',              'scheme', 'scm', '.scm'),
    ('Smalltalk',           'smalltalk', 'squeak', 'st', '.st'),
    ('Snobol',              'snobol'),
    ('SQL',                 'sql', '.sql'),
    ('TCL',                 'tcl', '.tcl'),
    ('Vala',                'vala', 'vapi', '.vala', '.vapi'),
    ('VB.NET',              'vb.net'),
    ('Visual Basic',        'visual-basic'),
    ('XML',                 'xml', '.xml'),
    ('XSLT',                'xslt', 'xsl', '.xsl', '.xslt'),
    ('Yaml',                'yaml', '.yaml', '.yml'),
]


languages = Languages(languages_list)

