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


import re


import ply.lex
import ply.yacc


class ParseError(Exception):
    pass

class LexerError(ParseError):
    pass

class SyntaxError(ParseError):
    pass
    
    

tokens = [
    #'NAMED',
    'EXT', 'TAG', 'LTAG', 'RTAG', 'BTAG', 'REGEXP', 'TEXT', 'ALL',
    'OR','AND', 'NOT', 'COLON',
    'LPAREN','RPAREN',
]
reserved = ['NOT', 'AND', 'OR']

t_NOT     = r'!|NOT'
t_AND     = r'&+|AND'
t_OR      = r'\|+|OR'
t_COLON   = r':'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_ALL     = r'\*'
t_EXT     = r'\.[a-zA-Z_0-9]+'


def t_BTAG(t):
    r'\*[a-zA-Z_0-9_-]+\*'
    t.value = t.value[1:-1]
    return t

def t_LTAG(t):
    r'\*[a-zA-Z_0-9_-]+'
    t.value = t.value[1:]
    return t

def t_RTAG(t):
    r'[a-zA-Z_0-9_-]+\*'
    t.value = t.value[:-1]
    return t

def t_TAG(t):
    r'[a-zA-Z_0-9_-]+'
    if t.value in reserved:
        t.type = t.value
    else:
        t.type = 'TAG'
    return t


def t_REGEXP(t):
    r'/([^/]|\/)+/'
    t.value = t.value[1:-1].replace(r'\/', '/')
    return t

def t_TEXT(t):
    r'"([^"]|\")+"'
    t.value = t.value[1:-1].replace(r'\"', '"')
    return t

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    raise LexerError("Illegal character '%s'" % t.value[0])


# Parsing rules

def p_statement_disjunction(t):
    'statement : disjunction'
    t[0] = t[1]
    #print t[1]
    
def p_disjunction_many(t):
    'disjunction : disjunction OR conjunction'
    #print `t[1]`, `t[2]`
    #t[0] = ('or' , t[1], t[3])
    t[0] = t[1] + (t[3],)
    
def p_disjunction_one(t):
    'disjunction : conjunction'
    #print `t[1]`
    t[0] = ('or', t[1])
    
def p_conjunction_and(t):
    'conjunction : conjunction AND negation'
    #print `t[1]`, `t[2]`
    t[0] = t[1] + (t[3], )
    
def p_conjunction_many(t):
    'conjunction : conjunction negation'
    #print `t[1]`, `t[2]`
    t[0] = t[1] + (t[2], )

def p_conjunction_one(t):
    'conjunction : negation'
    #print `t[1]`
    t[0] = ('and', t[1])

def p_negation_neg(t):
    'negation : NOT negation'
    #print `t[1]`
    t[0] = ('not', t[2])

#def p_negation_one(t):
#    'negation : NOT TAG'
#    #print `t[1]`
#    t[0] = ('not', t[2])
    
def p_negation_pseudo(t):
    'negation : term'
    #print `t[1]`
    t[0] = t[1]

def p_negation_paren(p):
    'negation : LPAREN disjunction RPAREN'
    p[0] = p[2]
    
def p_term_tag(t):
    'term : TAG'
    t[0] = ('tag', t[1])
    
def p_term_ltag(t):
    'term : LTAG'
    t[0] = ('ltag', t[1])
    
def p_term_rtag(t):
    'term : RTAG'
    t[0] = ('rtag', t[1])
    
def p_term_btag(t):
    'term : BTAG'
    t[0] = ('btag', t[1])
    
def p_term_text(t):
    'term : TEXT'
    t[0] = ('text', t[1])
    
def p_term_regexp(t):
    'term : REGEXP'
    t[0] = ('regexp', t[1])
    
def p_term_named(t):
    'term : TAG COLON TAG'
    #t[0] = tuple(t[1].split(':'))
    t[0] = (t[1], t[3])
    
def p_term_ext(t):
    'term : EXT'
    t[0] = ('ext', t[1])
    
def p_term_all(t):
    'term : ALL'
    t[0] = ('all', )



def p_error(t):
    raise SyntaxError("Syntax error at '%s'" % t.value)


lexer  = ply.lex.lex(optimize=0)
parser = ply.yacc.yacc(write_tables=0, debug=0)


def simplify(ast):
    if not isinstance(ast, tuple):
        return ast
    elif len(ast) == 2 and ast[0] in ('or', 'and'):
        return simplify(ast[1])
    else:
        return (ast[0], ) + tuple(simplify(i) for i in ast[1:])


def parse(query):
    if query.strip() == '':
        return ('none', )
    else:
        ast = parser.parse(query)
        return simplify(ast)


def parse_tags(tags_str):
    tags = set()
    lang = None
    
    parts = re.split('((?:lang:)?\.?[a-zA-Z_0-9_-]+)', tags_str)[1::2]
    for part in parts:
        if part.startswith('lang:'):
            lang = part[5:].lower()
        elif part.startswith('.'):
            lang = part.lower()
        else:
            tags.add(part)
    
    return tags, lang


if __name__ == '__main__':
    import readline
    
    while 1:
        try:
            s = raw_input('calc > ')
        except EOFError:
            break
        print yacc.parse(s)

