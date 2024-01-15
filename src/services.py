import libvirt
import uuid

ubuntu = "ubuntu 20.04"
centos = "CentOS 7"


class kvm_service:

    def connect_to_remote_slave(self, slave):
        '连接到slave上'
        url = f"qemu+ssh://{slave.username}@{slave.ip}/system"
        conn = libvirt.open(url)
        if conn is None:
            Exception(f"Connect to {slave.ip} failed!")
        return conn

    def close_conn(self, conn):
        '关闭指定slave的conn'
        conn.close()
        return True

    def new_ubuntu_vm(self, slave, cpu, memory):
        '在指定的slave上创建一个Ubuntu虚拟机'
        name = uuid.uuid4()  # 生成一个唯一的标识符
        xml_config = f"""
        <domain type='kvm'>
            <name>{name}</name>
            <memory unit='GB'>{memory}</memory>
            <vcpu placement='static'>{cpu}</vcpu>
            <os>
                <type arch='x86_64' machine='pc-i440fx-2.12'>hvm</type>
                <boot dev='hd'/>
            </os>
            <devices>
                <disk type='file' device='disk'>
                    <driver name='qemu' type='qcow2'/>
                    <source file='/usr/libvirt/{ubuntu}.qcow2'/>S
                    <target dev='vda' bus='virtio'/>
                    <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
                </disk>
                <interface type='network'>
                    <mac address='52:54:00:aa:bb:cc'/>
                    <source network='default'/>
                    <model type='virtio'/>
                    <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
                </interface>
            </devices>
        </domain>
        """
        conn = self.connect_to_remote_slave(slave)
        conn.createXML(xml_config, 0)
        print(f"Virtual Machine {ubuntu} : {name} created successfully!")
        conn.close()
        return True

    def new_centos_vm(self, slave, cpu, memory):
        '在指定的slave上创建一个CentOS虚拟机'
        name = uuid.uuid4()  # 生成一个唯一的标识符
        xml_config = f"""
               <domain type='kvm'>
                   <name>{name}</name>
                   <memory unit='GB'>{memory}</memory>
                   <vcpu placement='static'>{cpu}</vcpu>
                   <os>
                       <type arch='x86_64' machine='pc-i440fx-2.12'>hvm</type>
                       <boot dev='hd'/>
                   </os>
                   <devices>
                       <disk type='file' device='disk'>
                           <driver name='qemu' type='qcow2'/>
                           <source file='/usr/libvirt/{centos}.qcow2'/>S
                           <target dev='vda' bus='virtio'/>
                           <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
                       </disk>
                       <interface type='network'>
                           <mac address='52:54:00:aa:bb:cc'/>
                           <source network='default'/>
                           <model type='virtio'/>
                           <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
                       </interface>
                   </devices>
               </domain>
               """
        conn = self.connect_to_remote_slave(slave)
        conn.createXML(xml_config, 0)
        print(f"Virtual Machine {centos} : {name} created successfully!")
        conn.close()
        return True

    def get_active_vms(self, slave):
        '获取处于开机状态的instance，返回虚拟机的名字'
        vms_list = []
        conn = self.connect_to_remote_slave(slave)
        for id in conn.listDomainsID():
            vms_list.append(conn.lookupByID(id).name())
        conn.close()
        return vms_list

    def get_inactive_vms(self, slave):
        '获取处于关机状态的instance，返回虚拟机的名字'
        vms_list = []
        conn = self.connect_to_remote_slave(slave)
        for id in conn.listDomainsID():
            vms_list.append(conn.lookupByID(id).name())
        conn.close()
        return vms_list

    def run_vm(self, slave, vm_name):
        '打开虚拟机并运行'
        conn = self.connect_to_remote_slave(slave)
        dom = conn.lookupByName(vm_name)
        dom.create()
        return True

    def shutdown_vm(self, slave, vm_name):
        '关闭虚拟机'
        conn = self.connect_to_remote_slave(slave)
        dom = conn.lookupByName(vm_name)
        dom.shutdown()
        return True

    def reboot_vm(self, slave, vm_name):
        '重启虚拟机'
        conn = self.connect_to_remote_slave(slave)
        dom = conn.lookupByName(vm_name)
        dom.reboot()
        return True
