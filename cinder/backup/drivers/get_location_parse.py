#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import hmac
import httplib
import re
import sha
import sys
import time
import urllib
import urlparse
import xml.sax

httplib.HTTPConnection.debuglevel=0

class ListEntry:
    def __init__(self, location=''):
        self.location = location
     
class GetLocationHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.entries = []
        self.curr_entry = None
        self.curr_text = ''
        
    def startElement(self, name, attrs):
        if name == 'Entry':
            self.curr_entry = ListEntry()

    def endElement(self, name):            
        if name == 'Entry':
            self.curr_entry.location = self.curr_text
            self.entries.append(self.curr_entry)
                   
        self.curr_text = ''

    def characters(self, content):
        self.curr_text += content






