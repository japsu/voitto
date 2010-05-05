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

import datetime
import libvoitto

DEFAULT_IDENTITY = "Tappio"
DEFAULT_BEGIN = datetime.date(2010, 1, 1)
DEFAULT_END = datetime.date(2010, 12, 31)

class Document(object):
    def __init__(self, identity=DEFAULT_IDENTITY, version=libvoitto.VERSION,
            name="", begin=DEFAULT_BEGIN, end=DEFAULT_END, accounts=[],
            events=[]):
        self.identity = identity
        self.version = version
        self.name = name
        self.begin = begin
        self.end = end
        self.accounts = accounts
        self.events = events 

class Account(object):
    def __init__(self, number=None, name="", subaccounts=[]):
        self.number = number
        self.name = name
        self.subaccounts = subaccounts

class Event(object):
    def __init__(self, number, date, description="", entries=[]):
        self.number = number
        self.date = date
        self.description = description
        self.entries = entries

class Entry(object):
    def __init__(self, account_number, cents):
        self.account_number = account_number
        self.cents = cents

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

class ParserError(RuntimeError):
    pass

class Parser(object):
    """A recursive descent parser for the Tappio file format.

    Takes in a stream of Tokens and makes a Document from them."""

    def __init__(self, tokens):
        self.document = Document()
        self.token_iterator = iter(tokens)
        self.next_token = None

    def error(self, message, *args, **kwargs):
        raise ParserError(message.format(*args, **kwargs))

    def token(self, expected_type=None, expected_value=None):
        if self.next_token is not None:
            token = self.next_token
            self.next_token = None
        else:
            try:
                token = self.token_iterator.next()
            except StopIteration:
                self.error("end of file while expecting {0}", expected_type)

        if expected_type is not None and expected_type != token.token_type:
            self.error("expected {0}, got {1}", expected_type, token.token_type)

        if expected_value is not None and expected_value != token.value:
            self.error("{0}: expected {1}, got {2}", token_type, expected_value, token.value)

        return token.token_type, token.value

    def peek(self):
        if self.next_token is not None:
            token = self.next_token
        else:
            try:
                token = self.token_iterator.next()
                self.next_token = token
            except StopIteration:
                token = None

        if token is None:
            return None, None
        else:
            return token.token_type, token.value

    def parse_document(self):
        self.token("brace_open")
        self.token("symbol", "identity")
        unused, self.document.identity = self.token("string", "Tappio")

        self.token("symbol", "version")
        unused, self.document.version = self.token("string")

        self.token("symbol", "finances")

        self.parse_fiscal_year()

        self.token("brace_close")

        return self.document

    def parse_fiscal_year(self):
        self.token("brace_open")

        self.token("symbol", "fiscal-year")
        unused, self.document.name = self.token("string")

        self.document.begin = self.parse_date()
        self.document.end = self.parse_date()

        self.parse_account_map()
        self.parse_events()

        self.token("brace_close")

    def parse_date(self):
        self.token("brace_open")
        self.token("symbol", "date")

        unused, year = self.token("integer")
        unused, month = self.token("integer")
        unused, day = self.token("integer")

        self.token("brace_close")

        return datetime.datetime(int(year), int(month), int(day))

    def parse_money(self):
        self.token("brace_open")
        self.token("symbol", "money")
        unused, cents = self.token("integer")
        self.token("brace_close")
        return int(cents)

    def parse_account_map(self):
        self.token("brace_open")
        self.token("symbol", "account-map")
        
        next_type, unused = self.peek()
        while next_type == "brace_open":
            self.document.accounts.append(self.parse_account())
            next_type, unused = self.peek()

        self.token("brace_close")

    def parse_account(self):
        self.token("brace_open")
        self.token("symbol", "account")

        unused, account_number = self.token("integer")
        account_number = int(account_number)
        if account_number < -1:
            self.error("invalid account number: {0}", account_number)
        elif account_number == -1:
            # Account group
            account_number = None

        unused, account_name = self.token("string")

        # Sub-accounts
        subaccounts = []
        next_type, unused = self.peek()
        if next_type == "brace_open":
            self.token("brace_open")

            next_type, unused = self.peek()
            while next_type == "brace_open":
                subaccounts.append(self.parse_account())
                next_type, unused = self.peek()

            self.token("brace_close")

        self.token("brace_close")

        return Account(account_number, account_name, subaccounts)

    def parse_events(self):
        self.token("brace_open")

        next_type, unused = self.peek()
        while next_type == "brace_open":
            self.parse_event()
            next_type, unused = self.peek()

        self.token("brace_close")

    def parse_event(self):
        self.token("brace_open")

        self.token("symbol", "event")
        
        unused, number = self.token("integer")
        date = self.parse_date()
        unused, description = self.token("string")
        
        entries = []
        next_type, unused = self.peek()
        if next_type == "brace_open":
            self.token("brace_open")

            next_type, unused = self.peek()
            while next_type == "brace_open":
                entries.append(self.parse_entry())
                next_type, unused = self.peek()

            self.token("brace_close")

        self.token("brace_close")

        event = Event(int(number), date, description, entries)
        self.document.events.append(event)

    def parse_entry(self):
        self.token("brace_open")
        
        unused, account_number = self.token("integer")
        cents = self.parse_money()

        self.token("brace_close")

        return Entry(int(account_number), cents)
