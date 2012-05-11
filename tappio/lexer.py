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

"""
A lexer for the Tappio file format.
"""

TOKENS = (
    'brace_open',
    'brace_close',
    'integer',
    'symbol',
    'string',
)

def build_set(*args):
    s = set()

    for arg in args:
        if type(arg) is tuple:
            begin, end = arg
            for k in range(ord(begin), ord(end) + 1):
                s.add(chr(k))
        else:
            for ch in arg:
                assert type(ch) in (str, unicode)
                assert len(ch) == 1
                s.add(ch)

    return s

DIGITS = "0123456789"
SYMBOL_CHARS = build_set(('a', 'z'), ('A', 'Z'), '!$%&/+?-_*')
WHITESPACE = " \t\r\n"

class Token(object):
    def __init__(self, token_type, value=None):
        assert token_type in TOKENS, "Invalid token: {0}".format(token_type)
        self.token_type = token_type
        self.value = value

    def __repr__(self):
        token_type = getattr(self, "token_type", None)
        value = repr(getattr(self, "value", None))
        return "<Token: {0} {1}>".format(token_type, value)

    def __eq__(self, other):
        return self.token_type == other.token_type and self.value == other.value

class LexerError(RuntimeError):
    pass

class Lexer(object):
    def __init__(self):
        self.state = "generic"
        self.current_value = []
        self.tokens = []

    def save(self, ch):
        self.current_value.append(ch)

    def emit(self, token_type):
        self.tokens.append(Token(token_type, "".join(self.current_value)))
        self.current_value = []

    def lex_file(self, f):
        for linenum, line in enumerate(f, start=1):
            self.linenum = linenum
            for tok in self.feed(line):
                yield tok
        for tok in self.eof():
            yield tok

    def lex_string(self, s):
        for linenum, line in enumerate(s.split("\n"), start=1):
            self.linenum = linenum
            for tok in self.feed(line):
                yield tok
        for tok in self.eof():
            yield tok

    def feed(self, s):
        for chnum, ch in enumerate(s, start=1):
            self.chnum = chnum
            getattr(self, self.state)(ch)
            while self.tokens:
                yield self.tokens.pop(0)

    def eof(self):
        for tok in self.feed(' '):
            yield tok
        if self.state != "generic":
            raise LexerError("eof in {0}".format(self.state))

    def expect(self, ch, expected_ch):
        if ch != expected_ch:
            raise LexerError("expected {0}, got {1}".format(repr(expected_ch), repr(ch)))

    def enter(self, state):
        self.state = state

    # STATE METHODS BEGIN

    def generic(self, ch):
        self.enter("generic")

        if ch in WHITESPACE:
            return
        elif ch == '(':
            self.emit("brace_open")
        elif ch == ')':
            self.emit("brace_close")
        elif ch == '-':
            self.integer_negative(ch)
        elif ch in DIGITS:
            self.integer(ch)
        elif ch in SYMBOL_CHARS:
            self.symbol(ch)
        elif ch == '"':
            self.string_start(ch)
        else:
            raise LexerError("unexpected {0} in generic".format(repr(ch)))
        
    def integer_negative(self, ch):
        self.enter("integer")
        self.expect(ch, "-")
        self.save(ch)

    def integer(self, ch):
        self.enter("integer")

        if ch in DIGITS:
            self.save(ch)
        else:
            self.emit("integer")
            self.generic(ch)

    def symbol(self, ch):
        self.enter("symbol")

        if ch in SYMBOL_CHARS:
            self.save(ch)
        else:
            self.emit("symbol")
            self.generic(ch)

    def string_start(self, ch):
        self.enter("string")
        self.expect(ch, '"')
    
    def string(self, ch):
        self.enter("string")
        
        if ch == '"':
            self.emit("string")
            self.enter("generic")
        elif ch == '\\':
            self.enter("string_escape")
        else:
            self.save(ch)

    def string_escape(self, ch):
        self.save(ch)
        self.enter("string")
