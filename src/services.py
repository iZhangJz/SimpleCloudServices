import libvirt
import uuid

ubuntu = "ubuntu-20.04"
centos = "CentOS-7"

# 一个字典 用于存储创建的虚拟机的名字对应的slave
name_to_slave = {}


class kvm_service:

    def connect_to_remote_slave(self, slave):
        """连接到slave上"""
        url = f"qemu+ssh://{slave.username}@{slave.ip}/system"
        conn = libvirt.open(url)
        if conn is None:
            raise Exception(f"Connect to {slave.ip} failed!")
        return conn

    def new_ubuntu_vm(self, slave, cpu, memory):
        """在指定的slave上创建一个Ubuntu虚拟机"""
        name = str(uuid.uuid4())  # 生成一个唯一的标识符
        xml_config = f"""
        <domain type='kvm'>
            <name>{name}</name>
            <memory unit='GB'>{memory}</memory>
            <currentMemory>{memory}</memory>
            <vcpu placement='static'>{cpu}</vcpu>
            <os>
                <type arch='x86_64' machine='pc'>hvm</type>
                <boot dev='cdrom'/>
            </os>
            <devices>
                <disk type='file' device='disk'>
                    <driver name='qemu' type='qcow2'/>
                    <source file='/usr/libvirt/{ubuntu}.qcow2'/>
                    <target dev='vda' bus='virtio'/>
                    <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
                </disk>
                <disk type='file' device='cdrom'>
                    <source file='/usr/libvirt/{ubuntu}.iso'/>
                    <target dev='vda' bus='virtio'/>
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
        # 将创建后的虚拟机与slave绑定
        name_to_slave[name] = slave
        conn.close()
        return name

    def new_centos_vm(self, slave, cpu, memory):
        """在指定的slave上创建一个CentOS虚拟机"""
        name = str(uuid.uuid4())  # 生成一个唯一的标识符
        xml_config = f"""
               <domain type='kvm'>
                   <name>{name}</name>
                   <memory unit='GB'>{memory}</memory>
                   <vcpu placement='static'>{cpu}</vcpu>
                   <os>
                       <type arch='x86_64' machine='pc'>hvm</type>
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
        # 将创建后的虚拟机与slave绑定
        name_to_slave[name] = slave
        conn.close()
        return name

    def get_active_vms(self, slave):
        """获取处于开机状态的instance，返回虚拟机的名字"""
        vms_list = []
        conn = self.connect_to_remote_slave(slave)
        for id in conn.listDomainsID():
            vms_list.append(conn.lookupByID(id).name())
        conn.close()
        return vms_list

    def is_inactive(self, slave, vm_name):
        """查看当前虚拟机是否处于关机状态"""
        vms_list = []
        conn = self.connect_to_remote_slave(slave)
        for id in conn.listDomainsID():
            vms_list.append(conn.lookupByID(id).name())
        conn.close()
        if vm_name in vms_list:
            return True
        return False

    def run_vm(self, vm_name):
        """打开虚拟机并运行"""
        slave = name_to_slave[vm_name]
        if slave is None:
            return False
        if self.is_inactive(slave, vm_name):
            conn = self.connect_to_remote_slave(slave)
            dom = conn.lookupByName(vm_name)
            dom.create()
            return True
        else:
            return False

    def shutdown_vm(self, vm_name):
        """关闭虚拟机"""
        slave = name_to_slave[vm_name]
        if slave is None:
            return False
        conn = self.connect_to_remote_slave(slave)
        dom = conn.lookupByName(vm_name)
        dom.shutdown()
        return True

    def reboot_vm(self, vm_name):
        """重启虚拟机"""
        slave = name_to_slave[vm_name]
        if slave is None:
            return False
        conn = self.connect_to_remote_slave(slave)
        dom = conn.lookupByName(vm_name)
        dom.reboot()
        return True

    def delete_vm(self, vm_name):
        """删除虚拟机"""
        slave = name_to_slave[vm_name]
        if slave is None:
            return False
        conn = self.connect_to_remote_slave(slave)
        dom = conn.lookupByName(vm_name)
        dom.destroy()
        return True
