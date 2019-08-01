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


from io import StringIO
from pkg_resources import load_entry_point

from nose.tools import *

SCRIPTS = [
    'tappio-extract',
    'tappio-graph',
    'tappio-indent',
    'tappio-merge',
    'tappio-missing-accounts',
    'tappio-move-entries',
    'tappio-print-accounts',
    'tappio-print-earnings',
    'tappio-renumber',
]

def script_import_test():
    for script in SCRIPTS:
        main = load_entry_point('voitto', 'console_scripts', script)
        assert_true(callable(main))
