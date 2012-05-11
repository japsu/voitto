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
Voitto MongoDB database specification
"""


from mongoengine import Document, EmbeddedDocument, StringField, IntField, \
    ReferenceField, ListField, BooleanField, DateTimeField, ObjectIdField, \
    EmbeddedDocumentField, EmailField


class BasicMetaMixin(object):
    title = StringField()
    description = StringField()


class Account(Document, BasicMetaMixin):
    number = IntField()
    title = StringField(required=True)
    description = StringField()
    
    parent = ReferenceField('Account')

    meta = {
        'indexes': [
            {
                # Number may be null, but if it is provided, it must be unique.
                # See http://www.mongodb.org/display/DOCS/Indexes#Indexes-unique%3Atrue
                'fields': ['number'],
                'unique': True,
                'sparse': True,
                'types': False,
            },
        ],
    }


class AccountReference(EmbeddedDocument):
    account = ReferenceField(Account, required=True)

    # Only allow references to accounts with numbers
    number_cached = IntField(required=True)

    title_cached = StringField()


class BitempTotal(Document):
    account = EmbeddedDocumentField(AccountReference, required=True)

    valid_from = DateTimeField(required=True)
    valid_until = DateTimeField()

    recorded = DateTimeField(required=True)
    superseded = DateTimeField()

    total_cents = IntField()


class Entry(EmbeddedDocument):
    account = EmbeddedDocumentField(AccountReference, required=True)
    amount_cents = IntField()


class Party(Document, BasicMetaMixin):
    email = EmailField()


class PartyReference(EmbeddedDocument):
    party = ReferenceField(Party)
    title_cached = StringField()


class EventLogItem(Document, BasicMetaMixin):
    event_id = ObjectIdField()

    recorded = DateTimeField(required=True, default=lambda: datetime.utcnow())
    actual = DateTimeField(required=True, default=lambda: datetime.utcnow())

    other_party = EmbeddedDocumentField(PartyReference)

    entries = ListField(EmbeddedDocumentField(Entry))

    tentative = BooleanField(default=False)
    current = BooleanField(default=True)
