#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tappio import Lexer, Parser, Writer
import sys

def sort_events(events):
    events.sort(key=lambda x: (x.date, x.number))

def renumber_events(events, start=1):
    for num, event in enumerate(events):
        event.number = num

def main(input_filename, output_filename):
    with open(input_filename, "rb") as input_file:
        with open(output_filename, "wb") as output_file:
            document = Parser(Lexer().lex_file(input_file)).parse_document()
            sort_events(document.events)
            renumber_events(document.events)
            Writer(output_file).write_document(document)

if __name__ == "__main__":
    main(*sys.argv[1:])
