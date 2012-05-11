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


__all__ = ['load', 'dump', 'loads', 'dumps', 'loadf', 'dumpf']


import sys

from .parser import Parser
from .lexer import Lexer
from .writer import Writer


def load(stream):
    return Parser(Lexer().lex_file(stream)).parse_document()


def dump(stream, document, **kwargs):
    Writer(stream, **kwargs).write_document(document)


def loads(s):
    with closing(StringIO(s)) as f:
        return load(f)


def dumps(document, **kwargs):
    with closing(StringIO()) as f:
        dump(f, document, **kwargs)


def loadf(filename):
    if filename is None:
        return load(sys.stdin)
    else:
        with open(filename, "rb") as f:
            return load(f)


def dumpf(filename, document, **kwargs):
    if filename is None:
        return dump(sys.stdout, document, **kwargs)
    else:
        with open(filename, "wb") as f:
            dump(f, document, **kwargs)
