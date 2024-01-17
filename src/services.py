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
                <name>{name}</name>                                 //虚拟机名称 
                <memory unit='GB'>{memory}</memory>                  //最大内存 
                <currentMemory unit='GB'>{memory}</currentMemory>    //可用内存 
                <vcpu>{cpu}</vcpu>                                                      //虚拟cpu个数 
                <os> 
                    <type arch='x86_64' machine='pc'>hvm</type> 
                    <boot dev='hd'/>                                           //光盘启动 
                </os> 
                <features> 
                    <acpi/> 
                    <apic/> 
                    <pae/> 
                </features> 
                <clock offset='localtime'/> 
                <devices> 
                    <emulator>/usr/libexec/qemu-kvm</emulator> 
                    <disk type='file' device='disk'> 
                        <driver name='qemu' type='qcow2'/>                      //此处关键，要求libvirt版本至少应该在0.9以上才能支持，libvirt版本升级http://blog.csdn.net/gg296231363/article/details/6891460 
                        <source file='/usr/libvirt/{ubuntu}.qcow2'/>            //目的镜像路径 
                        <target dev='hda' bus='ide'/> 
                    </disk> 
                    <disk type='file' device='cdrom'> 
                        <source file='/usr/libvirt/{ubuntu}.iso'/>              //光盘镜像路径 
                        <target dev='hdb' bus='ide'/> 
                    </disk> 
                    <input type='mouse' bus='ps2'/> 
                    <graphics type='vnc' port='-1' autoport='yes' listen = '0.0.0.0' keymap='en-us'/>   //vnc方式登录，端口号自动分配，自动加1 
                </devices> 
            </domain> 
        """
        conn = self.connect_to_remote_slave(slave)
        conn.defineXML(xml_config)
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
                <name>{name}</name>                                 //虚拟机名称 
                <memory unit='GB'>{memory}</memory>                  //最大内存 
                <currentMemory unit='GB'>{memory}</currentMemory>    //可用内存 
                <vcpu>{cpu}</vcpu>                                                      //虚拟cpu个数 
                <os> 
                    <type arch='x86_64' machine='pc'>hvm</type> 
                    <boot dev='hd'/>                                           //光盘启动 
                </os> 
                <features> 
                    <acpi/> 
                    <apic/> 
                    <pae/> 
                </features> 
                <clock offset='localtime'/> 
                <devices> 
                    <emulator>/usr/libexec/qemu-kvm</emulator> 
                    <disk type='file' device='disk'> 
                        <driver name='qemu' type='qcow2'/>            //此处关键，要求libvirt版本至少应该在0.9以上才能支持，libvirt版本升级http://blog.csdn.net/gg296231363/article/details/6891460 
                        <source file='/usr/libvirt/{centos}.qcow2'/>         //目的镜像路径 
                        <target dev='hda' bus='ide'/> 
                    </disk> 
                    <disk type='file' device='cdrom'> 
                        <source file='/usr/libvirt/{centos}.iso'/>              //光盘镜像路径 
                        <target dev='hdb' bus='ide'/> 
                    </disk> 
                    <input type='mouse' bus='ps2'/> 
                    <graphics type='vnc' port='-1' autoport='yes' listen = '0.0.0.0' keymap='en-us'/>//vnc方式登录，端口号自动分配，自动加1 
                </devices> 
            </domain> 
               """
        conn = self.connect_to_remote_slave(slave)
        conn.defineXML(xml_config)
        print(f"Virtual Machine {centos} : {name} created successfully!")
        # 将创建后的虚拟机与slave绑定
        name_to_slave[name] = slave
        conn.close()
        return name

    def is_active(self, slave, vm_name):
        """查看当前虚拟机是否处于开机状态"""
        conn = self.connect_to_remote_slave(slave)
        current_vm = conn.lookupByName(vm_name)
        vm_state = current_vm.state()[0]
        if vm_state == libvirt.VIR_DOMAIN_RUNNING:
            conn.close()
            return True
        conn.close()
        return False

    def is_inactive(self, slave, vm_name):
        """查看当前虚拟机是否处于关机状态"""
        conn = self.connect_to_remote_slave(slave)
        current_vm = conn.lookupByName(vm_name)
        vm_state = current_vm.state()[0]
        if vm_state == libvirt.VIR_DOMAIN_SHUTOFF:
            conn.close()
            return True
        conn.close()
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
        if self.is_active(slave, vm_name):
            conn = self.connect_to_remote_slave(slave)
            dom = conn.lookupByName(vm_name)
            dom.shutdown()
            return True
        else:
            return False

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


