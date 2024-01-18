import libvirt

"""
slave的相关操作
"""


class slave:
    def __init__(self, ip, username, cpu, memory, disk, os):
        self.ip = ip
        self.username = username
        self.cpu = cpu
        self.memory = memory
        self.disk = disk
        self.os = os    # os为1代表只能创建ubuntu os为2代表只能创建centos os为0代表都能创建

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

    def get_os(self):
        return self.os

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

    def update_info(self, cpu, memory):
        if self.cpu == 0 or self.memory == 0:
            return False
        self.cpu += cpu
        self.memory += memory
        return True

