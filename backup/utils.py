__author__ = 'psteam'

DEFAULT_POOL_NAME = '_pool0'


from cinder import rpc
from oslo.config import cfg
CONF = cfg.CONF



def extract_host(host, level='backend', default_pool_name=False):
    """Extract Host, Backend or Pool information from host string.

    :param host: String for host, which could include host@backend#pool info
    :param level: Indicate which level of information should be extracted
                  from host string. Level can be 'host', 'backend' or 'pool',
                  default value is 'backend'
    :param default_pool_name: this flag specify what to do if level == 'pool'
                              and there is no 'pool' info encoded in host
                              string.  default_pool_name=True will return
                              DEFAULT_POOL_NAME, otherwise we return None.
                              Default value of this parameter is False.
    :return: expected level of information

    For example:
        host = 'HostA@BackendB#PoolC'
        ret = extract_host(host, 'host')
        # ret is 'HostA'
        ret = extract_host(host, 'backend')
        # ret is 'HostA@BackendB'
        ret = extract_host(host, 'pool')
        # ret is 'PoolC'

        host = 'HostX@BackendY'
        ret = extract_host(host, 'pool')
        # ret is None
        ret = extract_host(host, 'pool', True)
        # ret is '_pool0'
    """
    if level == 'host':
        # make sure pool is not included
        hst = host.split('#')[0]
        return hst.split('@')[0]
    elif level == 'backend':
        return host.split('#')[0]
    elif level == 'pool':
        lst = host.split('#')
        if len(lst) == 2:
            return lst[1]
        elif default_pool_name is True:
            return DEFAULT_POOL_NAME
        else:
            return None


def _usage_from_backup(context, backup_ref, **kw):
    usage_info = dict(tenant_id=backup_ref['project_id'],
                      user_id=backup_ref['user_id'],
                      availability_zone=backup_ref['availability_zone'],
                      backup_id=backup_ref['id'],
                      host=backup_ref['host'],
                      display_name=backup_ref['display_name'],
                      created_at=str(backup_ref['created_at']),
                      status=backup_ref['status'],
                      volume_id=backup_ref['volume_id'],
                      size=backup_ref['size'],
                      service_metadata=backup_ref['service_metadata'],
                      service=backup_ref['service'],
                      fail_reason=backup_ref['fail_reason'])

    usage_info.update(kw)
    return usage_info


def notify_about_backup_usage(context, backup, event_suffix,
                              extra_usage_info=None,
                              host=None):
    if not host:
        host = CONF.host

    if not extra_usage_info:
        extra_usage_info = {}

    usage_info = _usage_from_backup(context, backup, **extra_usage_info)

    rpc.get_notifier("backup", host).info(context, 'backup.%s' % event_suffix,
                                          usage_info)

