import slave
import libvirt

class kvm_service:
    def connect_to_remote_slave(self,slave):
        # 目标slave URL地址
        url = f"qemu+ssh://{slave.username}@/system?password={slave.password}"
        conn = libvirt.open(url)
        return conn