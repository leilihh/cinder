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
    def __init__(self, grantee='', permission=''):
        self.grantee = grantee
        self.permission = permission
     
class GetAclHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.entries = []
        self.curr_entry = None
        self.curr_text = ''
        
        self.owner = ''


    def startElement(self, name, attrs):
        if name == 'Grant':
            self.curr_entry = ListEntry()

    def endElement(self, name):
        if name == 'Grant':
            self.entries.append(self.curr_entry)
            
        elif name == 'UserID':
            self.owner = self.curr_text 
                    
        elif name == 'ID':
            self.curr_entry.grantee = self.curr_text
        elif name == 'Permission':
            self.curr_entry.permission = self.curr_text              
            
        self.curr_text = ''

    def characters(self, content):
        self.curr_text += content






