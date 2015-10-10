__author__ = 'psteam'

from sqlalchemy import Column, MetaData, String, Table

from cinder.i18n import _LE
from cinder.openstack.common import log as logging

LOG = logging.getLogger(__name__)


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    backups = Table('backups', meta, autoload=True)
    parent_id = Column('parent_id', String(length=36))

    try:
        backups.create_column(parent_id)
        backups.update().values(parent_id=None).execute()
    except Exception:
        LOG.error(_LE("Adding parent_id column to backups table failed."))
        raise


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    backups = Table('backups', meta, autoload=True)
    parent_id = backups.columns.parent_id

    try:
        backups.drop_column(parent_id)
    except Exception:
        LOG.error(_LE("Dropping parent_id column from backups table failed."))
        raise
