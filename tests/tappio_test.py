#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab
#
# Voitto - a simple yet efficient double ledger bookkeeping system
# Copyright (C) 2010 Santtu Pajukanta <santtu@pajukanta.fi>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


from StringIO import StringIO

from nose.tools import *

from tappio.lexer import Lexer, LexerError
from tappio.writer import Writer
from tappio.parser import Parser, ParserError

SIMPLE_EXAMPLE = """
(identity "Tappio" version "versio 0.22" finances (fiscal-year "test" (date 2010 1 1) (date 2010 12 31) (account-map (account -1 "Vastaavaa" ()) (account -1 "Vastattavaa" ()) (account -1 "Tulos" ())) ()))
"""

# http://www.lahdenniemi.fi/jussi/tappio/formaatti.html
COMPLEX_EXAMPLE = """
(identity "Tappio"
 version "versio 0.10"
 finances (fiscal-year "Esimerkkiyhdistys ery"
                       (date 2003 1 1)
                       (date 2003 12 31)
                       (account-map (account -1 "Vastaavaa" ((account 101 "Pankkitili")))
                                    (account -1 "Vastattavaa" ((account 201 "Oma p\xe4\xe4oma")))
                                    (account -1 "Tulos" ((account 300 "Tulot") (account 400 "Menot"))))              
                       ((event 1 (date 2003 1 1) "Tilinavaus" ((101 (money 123456)) (201 (money -123456)))))))
"""

def lexer_single(input, expected_tokens):
    tokens = list(Lexer().lex_string(input))
    assert_equal(expected_tokens, tokens)

def lexer_test():
    # integer tests
    lexer_single("101", [("integer", "101")])
    lexer_single("-1252", [("integer", "-1252")])
    lexer_single("101 102 103", [("integer", "101"), ("integer", "102"), ("integer", "103")])
    lexer_single("102-102", [("integer", "102"), ("integer", "-102")])

    # symbol tests
    lexer_single("foobar", [("symbol", "foobar")])
    lexer_single("identity version finances fiscal-year account event date money", [
        ("symbol", "identity"),
        ("symbol", "version"),
        ("symbol", "finances"),
        ("symbol", "fiscal-year"),
        ("symbol", "account"),
        ("symbol", "event"),
        ("symbol", "date"),
        ("symbol", "money"),
    ])

    # string tests
    lexer_single('"foobar"', [("string", "foobar")])

    assert_raises(LexerError, lexer_single, '"foobar', [])

    lexer_single(r'"foo\"bar"', [("string", 'foo"bar')])
    lexer_single(r'"foo\\bar"', [("string", r'foo\bar')])

    # complex tests
    lexer_single(COMPLEX_EXAMPLE, [
        # (identity "Tappio" version "versio 0.10" finances (
        ('brace_open', ''),
        ('symbol', 'identity'), ('string', 'Tappio'),
        ('symbol', 'version'), ('string', 'versio 0.10'),
        ('symbol', 'finances'), ('brace_open', ''),

        # fiscal-year "Esimerkkiyhdistys ery"
        ('symbol', 'fiscal-year'), ('string', 'Esimerkkiyhdistys ery'),

        # (date 2003 1 1)
        ('brace_open', ''),
        ('symbol', 'date'), ('integer', '2003'), ('integer', '1'), ('integer', '1'),
        ('brace_close', ''),

        # (date 2003 12 31)
        ('brace_open', ''),
        ('symbol', 'date'), ('integer', '2003'), ('integer', '12'), ('integer', '31'),
        ('brace_close', ''),

        # (account-map
        ('brace_open', ''), ('symbol', 'account-map'),

        # (account -1 "Vastaavaa"
        ('brace_open', ''),
        ('symbol', 'account'), ('integer', '-1'), ('string', 'Vastaavaa'),

        # ((account 101 "Pankkitili")))
        ('brace_open', ''), ('brace_open', ''),
        ('symbol', 'account'), ('integer', '101'), ('string', 'Pankkitili'),
        ('brace_close', ''), ('brace_close', ''), ('brace_close', ''),

        # (account -1 "Vastattavaa"
        ('brace_open', ''),
        ('symbol', 'account'), ('integer', '-1'), ('string', 'Vastattavaa'),

        # ((account 201 "Oma pääoma"")))
        ('brace_open', ''), ('brace_open', ''),
        ('symbol', 'account'), ('integer', '201'), ('string', 'Oma p\xe4\xe4oma'),
        ('brace_close', ''), ('brace_close', ''), ('brace_close', ''),

        # (account -1 "Tulos"
        ('brace_open', ''),
        ('symbol', 'account'), ('integer', '-1'), ('string', 'Tulos'),

        # ((account 300 "Tulot")
        ('brace_open', ''), ('brace_open', ''),
        ('symbol', 'account'), ('integer', '300'), ('string', 'Tulot'),
        ('brace_close', ''),

        # (account 400 "Menot")))))
        ('brace_open', ''),
        ('symbol', 'account'), ('integer', '400'), ('string', 'Menot'),
        ('brace_close', ''), ('brace_close', ''), ('brace_close', ''), ('brace_close', ''),

        # ((event 1
        ('brace_open', ''), ('brace_open', ''), ('symbol', 'event'), ('integer', '1'),
        
        # (date 2003 1 1)
        ('brace_open', ''),
        ('symbol', 'date'), ('integer', '2003'), ('integer', '1'), ('integer', '1'),
        ('brace_close', ''),

        # "Tilinavaus"
        ('string', 'Tilinavaus'),

        # ((101 (money 123456))
        ('brace_open', ''), ('brace_open', ''),
        ('integer', '101'), ('brace_open', ''), ('symbol', 'money'), ('integer', '123456'),
        ('brace_close', ''), ('brace_close', ''),

        # (201 (money -123456)))))))
        ('brace_open', ''),
        ('integer', '201'), ('brace_open', ''), ('symbol', 'money'), ('integer', '-123456'),
        ('brace_close', ''), ('brace_close', ''), ('brace_close', ''), ('brace_close', ''),
        ('brace_close', ''), ('brace_close', ''), ('brace_close', ''),
    ])  

def parser_single(input):
    lex = Lexer()

    try:
        print Parser(lex.lex_string(input)).parse_document()
    except ParserError, e:
        print lex.linenum, lex.chnum
        raise e

def writer_single(input):
    good_tokens = list(Lexer().lex_string(input))
    document = Parser(good_tokens).parse_document()

    sio = StringIO()
    Writer(stream=sio).write_document(document)

    potentially_bad_tokens = list(Lexer().lex_string(sio.getvalue()))

    assert_equal(good_tokens, potentially_bad_tokens)

def parser_test():
    parser_single(SIMPLE_EXAMPLE)
    parser_single(COMPLEX_EXAMPLE)

def writer_test():
    writer_single(SIMPLE_EXAMPLE)
    writer_single(COMPLEX_EXAMPLE)
