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

"""Implementation of a backup service that backup/restore(s) 3par to ONet
   object storage"""

import os
import re
import subprocess
import time

from oslo_config import cfg
from oslo_log import log as logging
from swiftclient import client as swift

from cinder.backup import driver
from cinder.backup import chunkeddriver
from cinder import exception

LOG = logging.getLogger(__name__)

ONestbackup_service_opts = [
    cfg.StrOpt('backup_onest_conf', default='/etc/onest/onest.conf',
               help='onest configuration file to use.')
]

CONF = cfg.CONF
CONF.register_opts(service_opts)



class ONestBackupDriver(driver.BackupDriver):
    """Backup Cinder 3par volumes to Onet Object Store."""

    def __init__(self, context, db_driver=None, execute=None):
        super(3PARBackupDriver, self).__init__(context, db_driver)
        

    def backup(self, backup, volume_file, backup_metadata=False):
        pass
    

    def restore(self, backup, volume_id, volume_file):
        pass


    def delete(self, backup):
        pass

    """
    
    def put_container(self, container):
        pass

    def get_container_entries(self, container, prefix):
        pass

    def get_object_writer(self, container, object_name, extra_metadata=None):
        pass

    def get_object_reader(self, container, object_name, extra_metadata=None):
        pass

    def delete_object(self, container, object_name):
        pass


def get_backup_driver(context):
    return ONestBackupDriver(context)

