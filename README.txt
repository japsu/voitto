=============================================
Voitto - a simple yet efficient double ledger
=============================================

Copyright (C) 2010 Santtu Pajukanta <santtu@pajukanta.fi>

Voitto is licensed under the GNU General Public License, version 3 or later.
See the file COPYING.GPLv3 for the complete license.


Introduction
============

My long term vision is to make a bookkeeping system that supports distributed
operation (in the DVCS sense). Some "web 2.0" features (e-invoices/social debt
tracking via a REST API) are also being planned.


Installation
============

The use of pip is recommended::

    pip install voitto

Standard setup.py magic works, too (including setup.py develop).

Tappio utilities
================

At the moment Voitto only consists of a small collection of tools to work
with Tappio, a simple closed-source freeware bookkeeping application for
Windows. For more information about Tappio, see 
http://www.lahdenniemi.fi/jussi/tappio/

Current utilities in descending order of usefulness:

* tappio-renumber - sort and renumber events by date
* tappio-extract - extract a period of time from a TLK file (with opening balances)
* tappio-merge - merge two or more TLK files
* tappio-move-entries - all entries from one account number to another
* tappio-indent - a Tappio pretty-printer, useful for "git diff" (see below)
* tappio-missing-accounts - print accounts that are in some but not all input files
* tappio-print-accounts - print the account tree
* tappio-print-earnings - print incomes and expenses in CSV for nice pie graphs
* tappio-graph - print a totally useless GrahpViz graph of money flows

The utilities *generally* accept an input file as the first argument and
an output file as the second argument, with the notable exception of tappio-merge,
which takes an *output* file as the first argument and any number of input files
as the rest. Better documentation pending, so UTSL for the time being (and please
take backups of your .tlk files before overwriting them with Voitto!).

And BTW, it's safe to do this (as long as you have backups)::

    tappio-renumber old.tlk old.tlk

The whole file is read in first, then transmogrified and only then written out,
so this isn't like shell redirections where you'd end up with an empty old.tlk.


Using indent.py as a pretty-printer for "git diff"
==================================================

In ~/.gitconfig, add this::

    [diff "tappio"]
    textconv = /path/to/voitto/indent.py

In the .gitattributes of your git repository, add this::

    *.tlk diff=tappio

Now "git diff" should use indent.py for pretty printing.
