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

from tappio import *

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
                                    (account -1 "Vastattavaa" ((account 201 "Oma p\xe4\xe4oma"))
                                    (account -1 "Tulos" ((account 300 "Tulot") (account 400 "Menot")))))
                       ((event 1 (date 2003 1 1) "Tilinavaus" ((101 (money 123456)) (201 (money -123456)))))))
"""

class TestFailure(RuntimeError):
    pass

def fail_on(condition, message):
    if condition:
        raise TestFailure(message)

def fail_unless(condition, message):
    fail_on(not condition, message)

def test_lexer(input_string, expected_tokens):
    lex = Lexer()
    expected_tokens = [Token(*tup) for tup in expected_tokens]
    tokens = list(lex.lex_string(input_string))

    fail_unless(tokens == expected_tokens, "INPUT: {0}\nEXPECTED: {1}\nGOT: {2}".format(
        repr(input_string),
        repr(expected_tokens),
        repr(tokens)
    ))

def test_lexer_error(input_string):
    try:
        lex = Lexer()
        tokens = list(lex.lex_string(input_string))
    except LexerError:
        return

    raise TestFailure("INPUT: {0}\nEXPECTED ERROR\nGOT: {1}".format(repr(input_string), repr(tokens)))

def run_lexer_tests():
    # integer tests
    test_lexer("101", [("integer", "101")])
    test_lexer("-1252", [("integer", "-1252")])
    test_lexer("101 102 103", [("integer", "101"), ("integer", "102"), ("integer", "103")])
    test_lexer("102-102", [("integer", "102"), ("integer", "-102")])

    # symbol tests
    test_lexer("foobar", [("symbol", "foobar")])
    test_lexer("identity version finances fiscal-year account event date money", [
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
    test_lexer('"foobar"', [("string", "foobar")])
    test_lexer_error('"foobar')
    test_lexer(r'"foo\"bar"', [("string", 'foo"bar')])
    test_lexer(r'"foo\\bar"', [("string", r'foo\bar')])

    # complex tests
    test_lexer(COMPLEX_EXAMPLE, [
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

        # ((account 201 "Oma pääoma""))
        ('brace_open', ''), ('brace_open', ''),
        ('symbol', 'account'), ('integer', '201'), ('string', 'Oma p\xe4\xe4oma'),
        ('brace_close', ''), ('brace_close', ''),

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
        ('brace_close', ''), ('brace_close', ''), ('brace_close', ''), ('brace_close', ''), ('brace_close', ''),

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

def test_parser(input):
    lex = Lexer()

    try:
        print Parser(lex.lex_string(input)).parse_document()
    except ParserError, e:
        print lex.linenum, lex.chnum
        raise e

def run_parser_tests():
    test_parser(SIMPLE_EXAMPLE)
    test_parser(COMPLEX_EXAMPLE)

def run_tests():
    run_lexer_tests()
    run_parser_tests()

if __name__ == "__main__":
    run_tests()
