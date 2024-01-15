import libvirt

from controller import slave_conn_map

class slave:
    def __init__(self, ip, username):
        self.ip = ip
        self.username = username

    def get_info(self):
        '获取slave的相关信息'
        conn = slave_conn_map[slave]
        try:
            hostname = conn.getHostname()
            version = conn.getVersion()
            print(f"HostName: {hostname};Version: {version}")
        except libvirt.libvirtError as e:
            print(e)
