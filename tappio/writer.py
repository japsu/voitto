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
import sys

import voitto

DEFAULT_IDENTITY = "Tappio"
DEFAULT_BEGIN = datetime.date(2010, 1, 1)
DEFAULT_END = datetime.date(2010, 12, 31)

DEFAULT_INDENT = "  "

class Writer(object):
    def __init__(self, stream=sys.stdout, pretty_print=False, indent=DEFAULT_INDENT):
        self.stream = stream
        self.prev_token = None
        self.indent = indent
        self.indent_depth = 0
        self.pretty_print = pretty_print
        self.new_line_queued = False

    def write(self, *tokens):
        if self.new_line_queued:
            self.actually_write_newline()

        for token in tokens:
            if self.should_put_space_between(self.prev_token, token):
                self.stream.write(" ")
            self.stream.write(str(token))

            self.prev_token = token

    def new_line(self, indent_increment=0):
        self.indent_depth += indent_increment
        self.new_line_queued = True

    def actually_write_newline(self):
        if self.pretty_print:
            self.stream.write("\r\n")
            self.stream.write(self.indent * self.indent_depth)
            self.new_line_queued = False
            self.prev_token = None

    def should_put_space_between(self, prev_token, token):
        if prev_token is None:
            return False
        elif prev_token == ")" and token == "(":
            return True
        else:
            return (prev_token != "(") and (token != ")")

    def write_string(self, string):
        self.write('"' + self.escape_string(string) + '"')

    def write_date(self, date):
        self.write("(", "date", date.year, date.month, date.day, ")")

    def write_money(self, cents):
        self.write("(", "money", cents, ")")

    def escape_string(self, string):
        return "".join(self.escape_char(ch) for ch in string)

    def escape_char(self, ch):
        if ch == '\n':
            return r'\n'
        elif ch == '"':
            return r'\"'
        elif ch == '\\':
            return r'\\'
        else:
            return ch

    def write_document(self, document):
        self.write("(", "identity")
        self.write_string(document.identity)
    
        self.write("version")
        self.write_string(document.version)

        self.write("finances")
        self.new_line(1)

        self.write("(", "fiscal-year")
        self.write_string(document.name)

        self.write_date(document.begin)
        self.write_date(document.end)

        self.new_line(1)
        self.write_accounts(document.accounts)
        self.new_line()
        self.write_events(document.events)

        self.new_line(-1)
        self.write(")")
        self.new_line(-1)
        self.write(")")

        self.actually_write_newline()

        assert self.indent_depth == 0

    def write_accounts(self, accounts):
        self.write("(", "account-map")
        self.new_line(1)
        for account in accounts:
            self.write_account(account)
            self.new_line()
        self.new_line(-1)
        self.write(")")

    def write_account(self, account):
        self.write("(", "account", account.number if account.number is not None else -1)
        self.write_string(account.name)

        if account.subaccounts:
            self.write("(")
            self.new_line(1)
            for subaccount in account.subaccounts:
                self.write_account(subaccount)
                self.new_line()
            self.new_line(-1)
            self.write(")")
        else:
            self.write("(",")")

        self.write(")")

    def write_events(self, events):
        self.write("(")
        self.new_line(1)

        for event in events:
            self.write_event(event)
            self.new_line()

        self.new_line(-1)
        self.write(")")

    def write_event(self, event):
        self.write("(", "event", event.number)
        self.write_date(event.date)
        self.write_string(event.description)
        self.write_entries(event.entries)
        self.write(")")

    def write_entries(self, entries):
        self.write("(")

        if entries:
            self.new_line(1)
            for entry in entries:
                self.write_entry(entry)
                self.new_line()
            self.new_line(-1)

        self.write(")")

    def write_entry(self, entry):
        self.write("(", entry.account_number)
        self.write_money(entry.cents)
        self.write(")")
