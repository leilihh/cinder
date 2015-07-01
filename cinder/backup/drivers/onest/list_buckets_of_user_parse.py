#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib
import xml.sax

httplib.HTTPConnection.debuglevel = 0


class ListEntry:
    def __init__(self, container_name='', create_date=''):
        self.container_name = container_name
        self.create_date = create_date


class ListBucketsOfUserHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.entries = []
        self.curr_entry = None
        self.curr_text = ''

        self.owner = ''

    def startElement(self, name, attrs):
        if name == 'Container':
            self.curr_entry = ListEntry()

    def endElement(self, name):
        if name == 'Container':
            self.entries.append(self.curr_entry)

        elif name == 'ID':
            self.owner = self.curr_text

        elif name == 'ContainerName':
            self.curr_entry.container_name = self.curr_text
        elif name == 'CreationDate':
            self.curr_entry.create_date = self.curr_text

        self.curr_text = ''

    def characters(self, content):
        self.curr_text += content
