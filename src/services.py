import time
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
                <name>{name}</name>                                     //虚拟机名称 
                <memory unit='GB'>{memory}</memory>                     //最大内存 
                <currentMemory unit='GB'>{memory}</currentMemory>       //可用内存 
                <vcpu>{cpu}</vcpu>                                      //虚拟cpu个数 
                <os> 
                    <type arch='x86_64' machine='pc'>hvm</type> 
                    <boot dev='hd'/>                                    //硬盘启动 
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
                        <driver name='qemu' type='qcow2'/>                      //此处关键，要求libvirt版本至少应该在0.9以上才能支持 
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
        # 更新虚拟机信息
        slave.update_info(-cpu, -memory)
        conn.close()
        return name

    def new_centos_vm(self, slave, cpu, memory):
        """在指定的slave上创建一个CentOS虚拟机"""
        name = str(uuid.uuid4())  # 生成一个唯一的标识符
        xml_config = f"""
            <domain type='kvm'> 
                <name>{name}</name>                                  //虚拟机名称 
                <memory unit='GB'>{memory}</memory>                  //最大内存 
                <currentMemory unit='GB'>{memory}</currentMemory>    //可用内存 
                <vcpu>{cpu}</vcpu>                                   //虚拟cpu个数 
                <os> 
                    <type arch='x86_64' machine='pc'>hvm</type> 
                    <boot dev='hd'/>                                 //硬盘启动 
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
                        <driver name='qemu' type='qcow2'/>                   //此处关键，要求libvirt版本至少应该在0.9以上才能支持
                        <source file='/usr/libvirt/{centos}.qcow2'/>         //目的镜像路径 
                        <target dev='hda' bus='ide'/> 
                    </disk> 
                    <disk type='file' device='cdrom'> 
                        <source file='/usr/libvirt/{centos}.iso'/>           //光盘镜像路径 
                        <target dev='hdb' bus='ide'/> 
                    </disk> 
                    <input type='mouse' bus='ps2'/> 
                    <graphics type='vnc' port='-1' autoport='yes' listen = '0.0.0.0' keymap='en-us'/>   //vnc方式登录，端口号自动分配，自动加1 
                </devices> 
            </domain> 
               """
        conn = self.connect_to_remote_slave(slave)
        conn.defineXML(xml_config)
        print(f"Virtual Machine {centos} : {name} created successfully!")
        # 将创建后的虚拟机与slave绑定
        name_to_slave[name] = slave
        # 更新虚拟机信息
        slave.update_info(-cpu, -memory)
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
            conn.close()
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
            conn.close()
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
        conn.close()
        return True

    def delete_vm(self, vm_name):
        """删除虚拟机"""
        slave = name_to_slave[vm_name]
        if slave is None:
            return False
        conn = self.connect_to_remote_slave(slave)
        dom = conn.lookupByName(vm_name)
        vcpu_count = self.get_cpu(conn, vm_name)
        memory_size = self.get_memory(conn, vm_name)
        print(f"cpu: {vcpu_count} memory: {memory_size}")
        slave.update_info(vcpu_count, memory_size)
        if self.is_active(slave, vm_name):
            dom.destroy()
        dom.undefine()
        conn.close()
        return True

    def get_vm_info(self, vm_name, vm_os):
        """获取虚拟机状态 cpu使用率 内存使用率"""
        slave = name_to_slave[vm_name]
        if slave is None:
            return None
        conn = self.connect_to_remote_slave(slave)
        dom = conn.lookupByName(vm_name)
        current_state = dom.state()[0]
        # 新建一个字典 用于存储各种状态信息
        vm_state = {}
        # 虚拟机状态
        if current_state == libvirt.VIR_DOMAIN_NOSTATE:
            vm_state["state"] = "NOSTATE"
        elif current_state == libvirt.VIR_DOMAIN_RUNNING:
            vm_state["state"] = "RUNNING"
        elif current_state == libvirt.VIR_DOMAIN_SHUTOFF:
            vm_state["state"] = "SHUTOFF"
        else:
            vm_state["state"] = "UNKNOWN"

        # 计算CPU使用率
        time1 = time.time()
        cpu_time_1 = dom.info()[4]  # 获取当前CPU时间
        time.sleep(2)
        time2 = time.time()
        cpu_time_2 = dom.info()[4]  # 再次获取CPU时间
        cpu_cores = int(dom.info()[3])  # CPU的核数
        cpu_time_diff = cpu_time_2 - cpu_time_1
        cpu_usage = round(100 * cpu_time_diff / ((time2 - time1) * cpu_cores * 1e9), 2)
        vm_state["cpu"] = cpu_usage

        # 计算内存使用率 ubuntu不支持available和unused字段
        mem_stats = dom.memoryStats()  # 获取虚拟机的内存统计信息
        if vm_os == 1:
            mem_unused = mem_stats['unused']  # 获取虚拟机的未使用内存
            mem_total = mem_stats['available']  # 获取虚拟机的总内存数
            mem_used = mem_total - mem_unused
            mem_usage = round(100.0 * mem_used / mem_total, 2)
        else:
            mem_used = mem_stats['rss']   # 获取驻留内存数
            mem_total = mem_stats['actual']
            mem_usage = max(0.0, min(round(100.0 * mem_used / mem_total), 100.0))
        vm_state["memory"] = mem_usage

        conn.close()
        return vm_state

    def get_cpu(self, conn, vm_name):
        """获取vCpu个数"""
        dom = conn.lookupByName(vm_name)
        vcpu_count = dom.info()[3]
        return vcpu_count

    def get_memory(self, conn, vm_name):
        """获取内存大小"""
        dom = conn.lookupByName(vm_name)
        mem_size_mb = dom.info()[1] / 1024 / 1024
        mem_size_gb = round(mem_size_mb)
        return mem_size_gb


