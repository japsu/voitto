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


from datetime import date

from .models import Document, Account, Event, Entry


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

        return date(int(year), int(month), int(day))

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
