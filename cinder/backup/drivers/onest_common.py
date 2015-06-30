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
import list_objects_of_bucket_parse
import list_buckets_of_user_parse
import get_acl_parse
import get_location_parse
import delete_objects_parse
import hmac_sha1

GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
METADATA_PREFIX = ''
PROXY_INFO = None


def query_args_hash_to_string(query_args):
    pairs = []
    for k, v in query_args.items():
        piece = k
        if v != None:
            piece += "=%s" % urllib.quote_plus(str(v))
        pairs.append(piece)

    return '&'.join(pairs)


def merge_meta(headers, metadata):
    final_headers = headers.copy()
    for k in metadata.keys():
        final_headers[METADATA_PREFIX + k] = metadata[k]

    return final_headers


def _gen_access_url_signature(method, bucket, key, accessSecretkey, headers):
    strToSign = method + '\n'

    if 'Content-MD5' in headers:
        strToSign += headers['Content-MD5']
    strToSign += '\n'
    if 'Content-Type' in headers:
        strToSign += headers['Content-Type']
    strToSign += '\n'
    if 'Date' in headers:
        strToSign += headers['Date']
    strToSign += '\n'

    tt = headers.keys()
    tt.sort()
    for h in tt:
        if h.startswith('x-cmcc-'):
            strToSign += h
            strToSign += ':'
            strToSign += headers[h]
            strToSign += '\n'

    strToSign += '/'
    if bucket != '':
        strToSign += bucket
    if key != '':
        strToSign += '/' + key

    # if len(query_args):
    # strToSign += "?" + query_args_hash_to_string(query_args)

    print  strToSign
    signature = hmac_sha1.hmac_sha1(strToSign, accessSecretkey)

    return signature


def _add_onest_auth_header(authinfo, headers, method, bucket, key, query_args):
    strToSign = method + '\n'

    if 'Content-MD5' in headers:
        strToSign += headers['Content-MD5']
    strToSign += '\n'
    if 'Content-Type' in headers:
        strToSign += headers['Content-Type']
    strToSign += '\n'
    if 'Date' in headers:
        strToSign += headers['Date']
    strToSign += '\n'

    tt = headers.keys()
    tt.sort()
    for h in tt:
        if h.lower().startswith('x-cmcc-'):
            strToSign += h.lower()
            strToSign += ':'
            strToSign += headers[h]
            strToSign += '\n'

    strToSign += '/'
    if bucket != '':
        strToSign += bucket
    if key != '':
        strToSign += '/' + key

    # if len(query_args):
    # strToSign += "?" + query_args_hash_to_string(query_args)

    print  strToSign
    signature = hmac_sha1.hmac_sha1(strToSign, authinfo.accessSecretkey)

    headers['Authorization'] = "%s %s:%s" % (authinfo.auth_protocol_version, authinfo.accessID, signature )


def _make_request(authinfo, method, bucket='', key='', query_args={}, headers={}, data='', metadata={}):
    headers['Host'] = authinfo.host
    headers['Date'] = time.strftime(GMT_FORMAT, time.gmtime(time.time()))
    if data == '':
        headers['Content-Length'] = '0'

    path = ''
    path += "/%s" % bucket
    if key != '':
        path += "/%s" % key

    if len(query_args):
        path += "?" + query_args_hash_to_string(query_args)

    is_secure = authinfo.is_secure
    # server = authinfo.server
    # host = "%s:%d" % (server, authinfo.port)
    while True:
        if PROXY_INFO is None:  # 非代理模式
            connection = is_secure and httplib.HTTPSConnection(authinfo.host) or httplib.HTTPConnection(authinfo.host)
        else:  # 代理模式
            connection = httplib.HTTPConnection(PROXY_INFO.proxy_ip, PROXY_INFO.proxy_port)
            path = is_secure and "https://" + authinfo.host + path or "http://" + authinfo.host + path

        final_headers = merge_meta(headers, metadata)
        # add auth header
        _add_onest_auth_header(authinfo, final_headers, method, bucket, key, query_args)

        print method
        print authinfo.host
        print path
        print final_headers
        print data

        connection.request(method, path, data, final_headers)
        resp = connection.getresponse()
        print resp.status, resp.reason
        if resp.status < 300 or resp.status >= 400:
            return resp
        # handle redirect
        location = resp.getheader('location')
        if not location:
            return resp
        # (close connection)
        resp.read()
        scheme, host, path, params, query, fragment = urlparse.urlparse(location)
        if scheme == "http":
            is_secure = True
        elif scheme == "https":
            is_secure = False
        # else: raise invalidURL("Not http/https: " + location)
        if query: path += "?" + query
        # retry with redirect


def _anony_make_request(authinfo, method, bucket='', key='', query_args={}, headers={}, data='', metadata={}):
    headers['Host'] = authinfo.host
    headers['Date'] = time.strftime(GMT_FORMAT, time.gmtime(time.time()))
    if data == '':
        headers['Content-Length'] = '0'

    path = ''
    path += "/%s" % bucket
    if key != '':
        path += "/%s" % key

    if len(query_args):
        path += "?" + query_args_hash_to_string(query_args)

    is_secure = authinfo.is_secure
    # server = authinfo.server
    # host = "%s:%d" % (server, authinfo.port)
    while True:
        if PROXY_INFO is None:  # 非代理模式
            connection = is_secure and httplib.HTTPSConnection(authinfo.host) or httplib.HTTPConnection(authinfo.host)
        else:  # 代理模式
            connection = httplib.HTTPConnection(PROXY_INFO.proxy_ip, PROXY_INFO.proxy_port)
            path = is_secure and "https://" + authinfo.host + path or "http://" + authinfo.host + path

        final_headers = merge_meta(headers, metadata)

        # add auth header
        # _add_onest_auth_header(authinfo,final_headers, method, bucket, key, query_args)

        print method
        print authinfo.host
        print path
        print final_headers
        print data

        connection.request(method, path, data, final_headers)
        resp = connection.getresponse()
        print resp.status, resp.reason
        if resp.status < 300 or resp.status >= 400:
            return resp
        # handle redirect
        location = resp.getheader('location')
        if not location:
            return resp
        # (close connection)
        resp.read()
        scheme, host, path, params, query, fragment = urlparse.urlparse(location)
        if scheme == "http":
            is_secure = True
        elif scheme == "https":
            is_secure = False
        # else: raise invalidURL("Not http/https: " + location)
        if query: path += "?" + query
        # retry with redirect


class AuthInfo:
    def __init__(self, auth_protocol_version, accessID, accessSecretkey, is_secure, host, access_net_mode):
        self.auth_protocol_version = auth_protocol_version
        self.accessID = accessID
        self.accessSecretkey = accessSecretkey
        # self.server = server
        # self.port = port
        self.is_secure = is_secure
        self.host = host
        self.access_net_mode = access_net_mode


class ProxyInfo:
    def __init__(self, proxy_ip, proxy_port):
        self.proxy_ip = proxy_ip
        self.proxy_port = proxy_port


class OnestObject:
    def __init__(self, data, metadata={}):
        self.data = data
        self.metadata = metadata


class Response:
    def __init__(self, http_response):
        self.http_response = http_response
        # you have to do this read, even if you don't expect a body.
        # otherwise, the next request fails.
        try:
            self.body = http_response.read()
        except:
            self.body = None
        if http_response.status >= 300 and self.body:
            self.message = self.body
        else:
            self.message = "%03d %s" % (http_response.status, http_response.reason)


class GetResponse(Response):
    def __init__(self, http_response):
        Response.__init__(self, http_response)
        response_headers = http_response.msg  # older pythons don't have getheaders
        metadata = self.get_onest_metadata(response_headers)
        self.object = OnestObject(self.body, metadata)

    def get_onest_metadata(self, headers):
        metadata = {}
        for hkey in headers.keys():
            if hkey.lower().startswith(METADATA_PREFIX):
                metadata[hkey[len(METADATA_PREFIX):]] = headers[hkey]
                del headers[hkey]

        return metadata


class ListObjectsOfBucketResponse(Response):
    def __init__(self, http_response):
        Response.__init__(self, http_response)
        if http_response.status < 300:
            handler = list_objects_of_bucket_parse.ListObjectsOfBucketHandler()
            xml.sax.parseString(self.body, handler)

            self.container_name = handler.container_name
            self.prefix = handler.prefix
            self.max_results = handler.max_results
            self.marker = handler.marker
            self.is_truncated = handler.is_truncated
            self.entries = handler.entries

        else:
            self.entries = []


class ListBucketsOfUserResponse(Response):
    def __init__(self, http_response):
        Response.__init__(self, http_response)
        if http_response.status < 300:
            handler = list_buckets_of_user_parse.ListBucketsOfUserHandler()
            xml.sax.parseString(self.body, handler)

            self.owner = handler.owner
            self.entries = handler.entries

        else:
            self.entries = []


class GetAclResponse(Response):
    def __init__(self, http_response):
        Response.__init__(self, http_response)
        if http_response.status < 300:
            handler = get_acl_parse.GetAclHandler()
            xml.sax.parseString(self.body, handler)

            self.owner = handler.owner
            self.entries = handler.entries

        else:
            self.entries = []


class GetLocationResponse(Response):
    def __init__(self, http_response):
        Response.__init__(self, http_response)
        if http_response.status < 300:
            handler = get_location_parse.GetLocationHandler()
            xml.sax.parseString(self.body, handler)
            self.entries = handler.entries
            if len(self.entries) > 0:
                self.location = self.entries.pop(0).location
            else:
                self.location = ''
        else:
            self.location = ''


class ListObjectsOfMultiDeletedResponse(Response):
    def __init__(self, http_response):
        Response.__init__(self, http_response)
        if http_response.status < 300:
            handler = delete_objects_parse.ListObjectsOfMultiDeletedHandler()
            if self.body:
                xml.sax.parseString(self.body, handler)
            self.owner = handler.owner
            self.entries = handler.entries
        else:
            self.entries = []
