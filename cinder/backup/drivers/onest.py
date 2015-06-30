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

from oslo_config import cfg
from oslo_log import log as logging

from cinder.backup import chunkeddriver

LOG = logging.getLogger(__name__)

onestbackup_service_opts = [
    cfg.StrOpt('backup_onest_url',
               default=None,
               help='The URL of the oNest endpoint'),
    cfg.StrOpt('backup_onest_user',
               default=None,
               help='oNest user name'),
    cfg.StrOpt('backup_onest_key',
               default=None,
               help='oNest key for authentication'),
    cfg.StrOpt('backup_onest_container',
               default='volumebackups',
               help='The default oNest container to use'),
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
            pass

    def put_container(self, container):
        """Create the container if needed. No failure if it pre-exists."""
        pass

    def get_container_entries(self, container, prefix):
        """Get container entry names"""
        pass

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
        pass

    def _generate_object_name_prefix(self, backup):
        """Generates a onest backup object name prefix."""
        pass

    def update_container_name(self, backup, container):
        """Use the container name as provided - don't update."""
        pass

    def get_extra_metadata(self, backup, volume):
        """onest driver does not use any extra metadata."""
        pass


def get_backup_driver(context):
    return OnestBackupDriver(context)

