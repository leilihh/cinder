# Copyright (C) 2015 Hewlett-Packard Development Company, L.P.

# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Implementation of a backup service that uses oNest as the backend

**Related Flags**

:backup_onest_url: The URL of the oNest endpoint (default: None, use catalog).
:backup_onest_retry_attempts: The number of retries to make for oNest
                                    operations (default: 10).
:backup_onest_retry_backoff: The backoff time in seconds between retrying
                                    failed oNest operations (default: 10).
:backup_compression_algorithm: Compression algorithm to use for volume
                               backups. Supported options are:
                               None (to disable), zlib and bz2 (default: zlib)
"""


from oslo.config import cfg
from cinder.i18n import _, _LE
from cinder.openstack.common import log as logging

from cinder.backup import chunkeddriver
from cinder import exception

import hashlib
import onest_client
import onest_common
import sys
import six


LOG = logging.getLogger(__name__)

onestbackup_service_opts = [
    cfg.StrOpt('backup_onest_host',
               default=None,
               help='The VIP of the oNest master host'),
    cfg.StrOpt('protocol_version',
               default='CMCC',
               help='AUTH_PROTOCOL_VERSION for onest'),
    cfg.StrOpt('backup_onest_accessid',
               default='CIDC-U-OBSAID-0000017030',
               help='oNest user accessID'),
    cfg.StrOpt('backup_onest_key',
               default='q581kvnkipm6bhclojnvxklsddlphyzywkgrba5i',
               help='oNest SecretKey for authentication'),
    cfg.StrOpt('aaa_master_host',
               default='0.0.0.0',
               help='oNest aaa master host VIP'),
    cfg.StrOpt('access_net_mode',
               default=3,
               help='oNest access net mode. '
                    '1 for intrasrvlocation '
                    '2 for intramgrlocation '
                    '3 for outerlocation'),
    cfg.StrOpt('proxy_ip',
               default='proxy.sgp.hp.com',
               help='proxy IP address, default to None if no proxy'),
    cfg.StrOpt('backup_onest_container',
               default='volumebackups',
               help='The default oNest container to use'),
    cfg.IntOpt('proxy_port',
               default='8080',
               help="proxy port, default to -1 if no proxy"),
    cfg.IntOpt('backup_onest_object_size',
               default=52428800,
               help='The size in bytes of oNest backup objects'),
    cfg.IntOpt('backup_onest_block_size',
               default=32768,
               help='The size in bytes that changes are tracked '
                    'for incremental backups. backup_onest_object_size '
                    'has to be multiple of backup_onest_block_size.'),
    cfg.IntOpt('backup_onest_retry_attempts',
               default=3,
               help='The number of retries to make for oNest operations')
    cfg.IntOpt('backup_onest_retry_backoff',
               default=2,
               help='The backoff time in seconds between oNest retries'),
    cfg.BoolOpt('backup_onest_enable_progress_timer',
                default=True,
                help='Enable or Disable the timer to send the periodic '
                     'progress notifications to Ceilometer when backing '
                     'up the volume to the oNest backend storage. The '
                     'default value is True to enable the timer.'),
    cfg.BoolOpt('is_secure',
                default=False,
                help='whether chooses https connection'),
]

CONF = cfg.CONF
CONF.register_opts(onestbackup_service_opts)


class OnestBackupDriver(chunkeddriver.ChunkedBackupDriver):
    """Provides backup, restore and delete of backup objects within oNest."""

    def __init__(self, context, db_driver=None):
        chunk_size_bytes = CONF.backup_onest_object_size
        sha_block_size_bytes = CONF.backup_onest_block_size
        backup_default_container = CONF.backup_onest_container
        enable_progress_timer = CONF.backup_onest_enable_progress_timer
        super(OnestBackupDriver, self).__init__(context, chunk_size_bytes,
                                                sha_block_size_bytes,
                                                backup_default_container,
                                                enable_progress_timer,
                                                db_driver)

        self.backup_onest_host = CONF.backup_onest_host
        self.onest_protocol_version = CONF.onest_protocol_version
        self.access_net_mode = CONF.access_net_mode
        self.backup_onest_accessid = CONF.backup_onest_accessid
        self.backup_onest_key = CONF.backup_onest_key
        self.is_secure = CONF.is_secure

        authinfo = onest_common.AuthInfo(self.onest_protocol_version,
                                         self.backup_onest_accessid,
                                         self.backup_onest_key,
                                         self.is_secure,
                                         self.backup_onest_host,
                                         self.access_net_mode)

        self.conn = onest_client.OnestClient(authinfo, CONF.proxy_ip, CONF.proxy_port)


    class OnestObjectWriter(object):
        def __init__(self, container, object_name, conn):
            self.container = container
            self.object_name = object_name
            self.conn = conn
            self.data = ''

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.close()

        def write(self, data):
            pass

        def close(self):
            pass

    class OnestObjectReader(object):
        def __init__(self, container, object_name, conn):
            self.container = container
            self.object_name = object_name
            self.conn = conn

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

        def read(self):
            data = self.conn.get_object_data(self.container,
                                             self.object_name)
            if data == None:
                LOG.error(_LE("failed to get object: %s"), self.object_name)
            return data

    def put_container(self, container):
        """Create the container if needed. No failure if it pre-exists."""
        ret = self.conn.create_bucket(container)
        if ret == False:
            LOG.error(_LE('failed to create bucket %s'), container)
        return

    def get_container_entries(self, container, prefix):
        """Get container entry names"""
        # response = self.conn.list_objects_of_bucket(container, options={'prefix': prefix})
        response = self.conn.list_objects_of_bucket(container)
        if response == None:
            LOG.error(_LE('failed to get object list of containter %s'), container)

        onest_object_names = [item.object_uri for item in response.entries]
        return onest_object_names

    def get_object_writer(self, container, object_name, extra_metadata=None):
        """Returns a writer object that stores a chunk of volume data in a
           onest object store.
        """
        return self.OnestObjectWriter(container, object_name, self.conn)

    def get_object_reader(self, container, object_name, extra_metadata=None):
        """Returns a reader object that retrieves a chunk of backed-up volume data
           from a onest object store.
        """
        return self.OnestObjectReader(container, object_name, self.conn)

    def delete_object(self, container, object_name):
        """Deletes a backup object from a onest object store."""
        if not self.conn.delete_object(container, object_name):
            LOG.error('failed to delete obejct: %s'
                      % object_name)

    def _generate_object_name_prefix(self, backup):
        """Generates a onest backup object name prefix."""
        pass

    def update_container_name(self, backup, container):
        """Use the container name as provided - don't update."""
        return container

    def get_extra_metadata(self, backup, volume):
        """onest driver does not use any extra metadata."""
        pass


def get_backup_driver(context):
    return OnestBackupDriver(context)

