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
    def __init__(self, object_uri='', ctime='',  size=''):
        self.object_uri = object_uri
        self.ctime = ctime
        self.size = size
     
class ListObjectsOfBucketHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.entries = []
        self.curr_entry = None
        self.curr_text = ''
        
        self.container_name = ''
        self.prefix = ''
        self.max_results = ''
        self.marker = ''
        self.is_truncated = ''

    def startElement(self, name, attrs):
        if name == 'ObjectUnit':
            self.curr_entry = ListEntry()

    def endElement(self, name):
        if name == 'ObjectUnit':
            self.entries.append(self.curr_entry)
            
        elif name == 'ContainerName':
            self.container_name = self.curr_text 
        elif name == 'Prefix':
            self.prefix = self.curr_text         
        elif name == 'MaxResults':
            self.max_results = self.curr_text             
        elif name == 'Marker':
            self.marker = self.curr_text             
        elif name == 'IsTruncated ':
            self.is_truncated = self.curr_text 
                       
        elif name == 'ObjectURI':
            self.curr_entry.object_uri = self.curr_text
        elif name == 'Ctime':
            self.curr_entry.ctime = self.curr_text
        elif name == 'Size':
            self.curr_entry.size = self.curr_text                   
            
        self.curr_text = ''

    def characters(self, content):
        self.curr_text += content






