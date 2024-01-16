import libvirt

"""
slave的相关操作
"""


class slave:
    def __init__(self, ip, username, cpu, memory, disk):
        self.ip = ip
        self.username = username
        self.cpu = cpu
        self.memory = memory
        self.disk = disk

    def get_username(self):
        return self.username

    def get_ip(self):
        return self.ip

    def get_cpu(self):
        return self.cpu

    def get_disk(self):
        return self.disk

    def get_memory(self):
        return self.memory

    def set_cpu(self, new_cpu):
        self.cpu = new_cpu

    def set_disk(self, new_disk):
        self.disk = new_disk

    def set_memory(self, new_memory):
        self.memory = new_memory

    def get_info(self, conn):
        """获取slave的相关信息"""
        try:
            hostname = conn.getHostname()
            version = conn.getVersion()
            print(f"HostName: {hostname};Version: {version}")
        except libvirt.libvirtError as e:
            print(e)
