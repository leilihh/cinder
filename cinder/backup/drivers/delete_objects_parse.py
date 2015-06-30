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
    def __init__(self, key='', status='', errorcode='', errormessage='' ):
        self.key = key
        self.status = status
        self.errorcode = errorcode
        self.errormessage = errormessage
     
class ListObjectsOfMultiDeletedHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.entries = []
        self.curr_entry = None
        self.curr_text = ''
        
        self.owner = ''


    def startElement(self, name, attrs):
        if name == 'Deleted':
            self.curr_entry = ListEntry()

    def endElement(self, name):
        if name == 'Deleted':
            self.entries.append(self.curr_entry)                            
        elif name == 'Key':
            self.curr_entry.key = self.curr_text
        elif name == 'Status':
            self.curr_entry.status = self.curr_text    
        elif name == 'Error':
            self.curr_entry.errorcode = self.curr_text
        elif name == 'Message':
            self.curr_entry.errormessage = self.curr_text
            
        self.curr_text = ''

    def characters(self, content):
        self.curr_text += content






