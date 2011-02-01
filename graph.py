#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from __future__ import with_statement

from tappio import read_file
from contextlib import contextmanager
import sys

# TODO: Escape stuff

GRAPH_HEADER = "digraph X {\n"
GRAPH_FOOTER = "}\n"
NODE_TEMPLATE = "%s %s"
EDGE_TEMPLATE = '\t"%s" -> "%s";\n'

def flatten_accounts(accounts):
    result = dict()

    for account in accounts:
        recursively_flatten_account(account, result)

    return result

def recursively_flatten_account(account, flat_accounts={}):
    if account.number is not None:
        flat_accounts[account.number] = account.name

    for subaccount in account.subaccounts:
        recursively_flatten_account(subaccount, flat_accounts)

def print_graph(edges, stream=sys.stdout):
    stream.write(GRAPH_HEADER)
    
    for from_node, to_node in edges:
        stream.write(EDGE_TEMPLATE % (from_node, to_node))

    stream.write(GRAPH_FOOTER)

def construct_graph(events, flat_accounts):
    edges = set()

    for event in events:
        kredit_accounts = set()
        debet_accounts = set()

        for entry in event.entries:
            if entry.cents < 0:
                kredit_accounts.add(entry.account_number)
            elif entry.cents > 0:
                debet_accounts.add(entry.account_number)

        for kredit_account in kredit_accounts:
            kredit_node = NODE_TEMPLATE % (kredit_account, flat_accounts[kredit_account])

            for debet_account in debet_accounts:
                debet_node = NODE_TEMPLATE % (debet_account, flat_accounts[debet_account])

                edges.add((kredit_node, debet_node))
                
    return edges

# TODO move this elsewhere
@contextmanager
def output_stream(output_filename=None, default_stream=sys.stdout, write_mode='wb'):
    if output_filename is None:
        yield default_stream
    else:
        with open(output_filename, write_mode) as f:
            yield f

def main(input_filename=None, output_filename=None):
    document = read_file(input_filename)
    flat_accounts = flatten_accounts(document.accounts)
    edges = construct_graph(document.events, flat_accounts)    

    with output_stream(output_filename) as stream:
        print_graph(edges, stream)

if __name__ == "__main__":
    main(*sys.argv[1:])
