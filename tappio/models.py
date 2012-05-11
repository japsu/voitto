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
A Tappio ledger contains an account tree and a list of events. These are
encapsulated in the Document class.

Relationships between the classes in pseudo-UML:

Document 1 --> * Account
Document 1 --> * Event 1 --> * Entry 1 --> Account
"""


from datetime import date

import voitto


DEFAULT_IDENTITY = "Tappio"
DEFAULT_VERSION = "Voitto " + voitto.__version__
DEFAULT_BEGIN = date(2010, 1, 1)
DEFAULT_END = date(2010, 12, 31)

DEFAULT_INDENT = "  "


class Document(object):
    """
    Encapsulates a Tappio ledger.

    A note about Document.accounts:

    In Tappio, accounts are represented as forest of three trees. The
    meanings of these trees are associated with the Finnish accounting
    system. The first tree is always "vastaavaa" ("assets"), the second
    is "vastattavaa" ("liabilities") and the third is "earnings" ("tulos").
    """

    def __init__(self, identity=DEFAULT_IDENTITY, version=DEFAULT_VERSION,
            name="", begin=DEFAULT_BEGIN, end=DEFAULT_END, accounts=None,
            events=None):
        self.identity = identity
        self.version = version
        self.name = name
        self.begin = begin
        self.end = end
        self.accounts = accounts if accounts is not None else []
        self.events = events if events is not None else []


class Account(object):
    def __init__(self, number=None, name="", subaccounts=None):
        self.number = number
        self.name = name
        self.subaccounts = subaccounts if subaccounts is not None else []


class Event(object):
    def __init__(self, number, date, description="", entries=None):
        self.number = number
        self.date = date
        self.description = description
        self.entries = entries if entries is not None else []


class Entry(object):
    def __init__(self, account_number, cents):
        self.account_number = account_number
        self.cents = cents
