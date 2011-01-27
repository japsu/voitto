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

from pymongo import Connection
from pymongo.objectid import ObjectId
from tappio import read_file

TAPPIO_ENCODING = "ISO-8859-1"

def import_document(db, document):
    import_metadata(db, document)
    import_account_tree(db, *document.accounts)
    import_events(db, document.events)

def import_metadata(db, document):
    pass # TODO

def import_account_tree(db, vastaavaa, vastattavaa, tulos):
    import_subaccounts(db, vastaavaa, "vastaavaa")
    import_subaccounts(db, vastattavaa, "vastattavaa")
    import_subaccounts(db, tulos, "tulos")

def create_account(db, account, account_type, parent_id=None):
        account_mongo = {
            "name": account.name.decode(TAPPIO_ENCODING),
            "number": account.number,
            "type": account_type,
            "parent": parent_id,
        }
        
        return db.accounts.save(account_mongo)

def import_subaccounts(db, account, account_type, parent_id=None):
    for subaccount in account.subaccounts:
        cur_id = create_account(db, subaccount, account_type, parent_id)
        import_subaccounts(db, subaccount, account_type, cur_id)

def import_events(db, events):
    for event in events:
        create_event(db, event)

def build_entry(db, entry):
    account_mongo = db.accounts.find_one({"number": entry.account_number})

    entry_mongo = {
        "account": {
            "number": account_mongo["number"],
            "name": account_mongo["name"],
        },
        "amount": entry.cents,
    }

    return entry_mongo

def create_event(db, event):
    event_mongo = {
        "event_id": ObjectId(),
        "created": event.date,
        "actual": event.date,
        "current": True,
        "description": event.description.decode(TAPPIO_ENCODING),
        "entries": [build_entry(db, entry) for entry in event.entries]
    }
        
    return db.events.save(event_mongo)

def main(input_filename=None):
    document = read_file(input_filename)
    db = Connection().test # XXX
    import_document(db, document)

if __name__ == "__main__":
    from sys import argv
    main(*argv[1:])
    
