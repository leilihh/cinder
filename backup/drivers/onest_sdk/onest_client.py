#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib
import onest_common

httplib.HTTPConnection.debuglevel = 0


class OnestClient:
    def __init__(self, authinfo, proxy_ip=None, proxy_port=-1):
        self.authinfo = authinfo
        self.location = ''
        self.bucketLocationMap = {}
        onest_common.PROXY_INFO = self.get_proxy_info(proxy_ip, proxy_port)

    def get_proxy_info(self, proxy_ip, proxy_port):
        is_proxy = proxy_ip is not None and proxy_port is not -1
        if is_proxy:
            return onest_common.ProxyInfo(proxy_ip, proxy_port)
        else:
            return None

    def resetLocation(self, location):
        authinfo = onest_common.AuthInfo(self.authinfo.auth_protocol_version,
                                         self.authinfo.accessID,
                                         self.authinfo.accessSecretkey,
                                         self.authinfo.is_secure,
                                         location,
                                         self.authinfo.access_net_mode)
        return authinfo

    # get location operate
    def get_location_without_bucket(self):
        if self.authinfo.access_net_mode == 1:
            resp = onest_common.GetLocationResponse(
                onest_common._make_request(self.authinfo, 'GET', 'rest/', '',
                                           {'intrasrvlocation': None}, {}))
            return resp.location
        elif self.authinfo.access_net_mode == 2:
            resp = onest_common.GetLocationResponse(
                onest_common._make_request(self.authinfo, 'GET', 'rest/', '',
                                           {'intramgrlocation': None}, {}))
            return resp.location
        else:
            resp = onest_common.GetLocationResponse(
                onest_common._make_request(self.authinfo, 'GET', 'rest/', '',
                                           {'outerlocation': None}, {}))
            return resp.location

    def get_location(self, bucket):
        if not bucket in self.bucketLocationMap:
            str = 'rest/%s' % bucket
            if self.authinfo.access_net_mode == 1:
                resp = onest_common.GetLocationResponse(
                    onest_common._make_request(self.authinfo, 'GET', str, '',
                                               {'intrasrvlocation': None}, {}))
                if resp.location == '':
                    print 'get lvs location failed...'
                    return ''
                else:
                    self.bucketLocationMap[bucket] = resp.location
            elif self.authinfo.access_net_mode == 2:
                resp = onest_common.GetLocationResponse(
                    onest_common._make_request(self.authinfo, 'GET', str, '',
                                               {'intramgrlocation': None}, {}))
                if resp.location == '':
                    print 'get lvs location failed...'
                    return ''
                else:
                    self.bucketLocationMap[bucket] = resp.location
            else:
                resp = onest_common.GetLocationResponse(
                    onest_common._make_request(self.authinfo, 'GET', str, '',
                                               {'outerlocation': None}, {}))
                if resp.location == '':
                    print 'get lvs location failed...'
                    return ''
                else:
                    self.bucketLocationMap[bucket] = resp.location
        connLocation = self.bucketLocationMap[bucket]
        print 'location:%s' % connLocation
        return connLocation

    #bucket operate
    def create_bucket(self, bucket):
        if self.location == '':
            location = self.get_location_without_bucket()
            if location == '':
                print 'get lvs location failed...'
                return False
            else:
                self.location = location
        print 'location:%s' % self.location

        authinfo2 = self.resetLocation(self.location)
        resp = onest_common.Response(
            onest_common._make_request(authinfo2, 'PUT', bucket, '', {}, {}))
        if resp.http_response.status != 201:
            return False
        else:
            return True

    def list_buckets_of_user(self):
        if self.location == '':
            location = self.get_location_without_bucket()
            if location == '':
                print 'get lvs location failed...'
                return None
            else:
                self.location = location
        print 'location:%s' % self.location

        authinfo2 = self.resetLocation(self.location)
        return onest_common.ListBucketsOfUserResponse(
            onest_common._make_request(authinfo2, 'GET'))

    def list_objects_of_bucket(self, bucket, options={}):
        location = self.get_location(bucket)
        if location == '':
            return None
        else:
            authinfo2 = self.resetLocation(location)
            return onest_common.ListObjectsOfBucketResponse(
                onest_common._make_request(authinfo2, 'GET', bucket, '',
                                           options))

    def delete_bucket(self, bucket):
        location = self.get_location(bucket)
        if location == '':
            return False
        else:
            authinfo2 = self.resetLocation(location)
            resp = onest_common.Response(
                onest_common._make_request(authinfo2, 'DELETE', bucket, '', {}))
            if resp.http_response.status != 204:
                return False
            else:
                return True

    def get_bucket_acl(self, bucket):
        location = self.get_location(bucket)
        if location == '':
            return None
        else:
            authinfo2 = self.resetLocation(location)
            return onest_common.GetAclResponse(
                onest_common._make_request(authinfo2, 'GET', bucket, '',
                                           {'acl': None}))

    def put_bucket_acl(self, bucket, acl_xml_document):
        location = self.get_location(bucket)
        if location == '':
            return False
        else:
            authinfo2 = self.resetLocation(location)
            resp = onest_common.Response(
                onest_common._make_request(authinfo2,
                                           'PUT',
                                           bucket,
                                           '',
                                           {'acl': None},
                                           {},
                                           acl_xml_document))
            if resp.http_response.status != 200:
                return False
            else:
                return True

    #object operate
    def put_object_data(self, bucket, key, objdata):
        location = self.get_location(bucket)
        if location == '':
            return False
        else:
            authinfo2 = self.resetLocation(location)
            f = file(objdata)
            obj = onest_common.OnestObject(f, {})
            resp = onest_common.Response(
                onest_common._make_request(authinfo2,
                                           'PUT',
                                           bucket,
                                           key,
                                           {},
                                           {},
                                           obj.data))
            f.close()
            if resp.http_response.status != 201:
                return False
            else:
                return True

    def put_object(self, bucket, key, objdata, content_length=None):
        location = self.get_location(bucket)
        if location == '':
            return False
        else:
            authinfo2 = self.resetLocation(location)
            resp = onest_common.Response(onest_common._make_request(authinfo2,
                                                                    'PUT',
                                                                    bucket,
                                                                    key,
                                                                    {},
                                                                    {},
                                                                    objdata,
                                                                    content_length))

            if resp.http_response.status != 201:
                return False
            else:
                return True

    def get_object_meta(self, bucket, key):
        location = self.get_location(bucket)
        if location == '':
            return None
        else:
            authinfo2 = self.resetLocation(location)
            resp = onest_common.Response(
                onest_common._make_request(authinfo2, 'GET', bucket, key,
                                           {'meta': None}))
            if resp.http_response.status != 200:
                return None
            else:
                return resp.http_response.msg

    def put_object_meta(self, bucket, key, user_meta):
        location = self.get_location(bucket)
        if location == '':
            return False
        else:
            authinfo2 = self.resetLocation(location)
            resp = onest_common.Response(
                onest_common._make_request(authinfo2,
                                           'PUT',
                                           bucket,
                                           key,
                                           {'meta': None},
                                           user_meta))
            if resp.http_response.status != 200:
                return False
            else:
                return True

    def get_object_data(self, bucket, key, headers={}):
        location = self.get_location(bucket)
        if location == '':
            return None
        else:
            authinfo2 = self.resetLocation(location)
            resp = onest_common.GetResponse(
                onest_common._make_request(authinfo2, 'GET', bucket, key, {},
                                           headers))
            if resp.http_response.status != 200:
                return None
            else:
                return resp.body

    def delete_object(self, bucket, key):
        location = self.get_location(bucket)
        if location == '':
            return False
        else:
            authinfo2 = self.resetLocation(location)
            resp = onest_common.Response(
                onest_common._make_request(authinfo2, 'DELETE', bucket, key))
            if resp.http_response.status != 204:
                return False
            else:
                return True

    #delete_multi_object
    def delete_multi_object(self, bucket, delete_objects_xml_document):
        location = self.get_location(bucket)
        if location == '':
            return False
        else:
            authinfo2 = self.resetLocation(location)
            resp = onest_common.ListObjectsOfMultiDeletedResponse(
                onest_common._make_request(authinfo2, 'POST', bucket, '',
                                           {'delete': None}, {},
                                           delete_objects_xml_document))
            if resp.http_response.status != 200:
                return None
            else:
                return resp

    def get_object_acl(self, bucket, key):
        location = self.get_location(bucket)
        if location == '':
            return None
        else:
            authinfo2 = self.resetLocation(location)
            return onest_common.GetAclResponse(
                onest_common._make_request(authinfo2, 'GET', bucket, key,
                                           {'acl': None}))

    def put_object_acl(self, bucket, key, acl_xml_document):
        location = self.get_location(bucket)
        if location == '':
            return False
        else:
            authinfo2 = self.resetLocation(location)
            resp = onest_common.Response(
                onest_common._make_request(authinfo2,
                                           'PUT',
                                           bucket,
                                           key,
                                           {'acl': None},
                                           {},
                                           acl_xml_document))
            if resp.http_response.status != 200:
                return False
            else:
                return True

    def get_object_open_url(self, bucket, key, expireTime, bAnonymous):
        location = self.get_location(bucket)
        if location == '':
            return False

        if bAnonymous == False:
            authinfo2 = self.resetLocation(location)
            resp = onest_common.Response(
                onest_common._make_request(authinfo2,
                                           'GET',
                                           bucket,
                                           key,
                                           {'checkAcl ': None},
                                           {}))
            if resp.http_response.status != 200:
                return None
            else:
                ret = "http://"
                ret += authinfo2.host
                ret += "/"
                ret += bucket
                ret += "/"
                ret += key
                ret += "?AccessId=" + authinfo2.accessID
                ret += "&Expires="
                ret1 = "%s%d" % (ret, expireTime)
                ret1 += "&Signature="

                s = expireTime

                ret1 += onest_common._gen_access_url_signature(
                    'GET', bucket, key, authinfo2.accessSecretkey, {'Date': s})
                return self.my_urlencode(ret1)
        else:
            authinfo2 = self.resetLocation(location)
            resp = onest_common.Response(
                onest_common._anony_make_request(authinfo2,
                                                 'GET',
                                                 bucket,
                                                 key,
                                                 {'checkAcl ': None},
                                                 {}))
            if resp.http_response.status != 200:
                return None
            else:
                ret = "http://"
                ret += authinfo2.host
                ret += "/"
                ret += bucket
                ret += "/"
                ret += key
                ret += "?Expires="
                ret1 = "%s%d" % (ret, expireTime)
                return self.my_urlencode(ret1)

    def my_urlencode(self, s):
        reprStr = repr(s).replace(r'\x', '%')
        return reprStr[1:-1]
