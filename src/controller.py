from flask import Flask, request, jsonify
from flask_cors import CORS
from slaves import slave
from services import kvm_service

# 创建flask对象
app = Flask(__name__)

# 跨域解决
CORS().init_app(app)

# 创建三个slave
slave_a = slave("192.168.45.107", "root", 1, 1, 35)
slave_b = slave("192.168.45.142", "root", 2, 2, 30)
slave_c = slave("192.168.45.122", "root", 2, 2, 30)
slaves = [slave_a, slave_b, slave_c]


@app.route('/new')
def new_vm():
    # 返回信息体
    success = False
    message = "New VM failed"

    # 创建新的虚拟机 参数虚拟机类型 cpu数量 memory大小 和 disk大小
    os = int(request.args.get('operatingSys'))
    cpu = int(request.args.get('cpu'))
    memory = int(request.args.get('memory'))
    disk = int(request.args.get('disk'))

    # 选择到了合适的slave
    res = select_slave(cpu, memory, disk)
    if res is None:
        response_data = {
            'success': success,
            'message': message
        }
        return jsonify(response_data)
    else:
        # 在slave上创建虚拟机
        kvm_new = kvm_service()
        if os == 1:
            # 表示创建一个ubuntu 返回值为虚拟机名称
            name = kvm_new.new_ubuntu_vm(res, cpu, memory)
            message = name
        elif os == 2:
            # 表示创建一个CentOS7
            name = kvm_new.new_centos_vm(res, cpu, memory)
            message = name
        success = True
        response_data = {
            'success': success,
            'message': message
        }
        return jsonify(response_data)


@app.route('/open')
def open_vm():
    """启动虚拟机"""
    vm_name = request.args.get("vm_name")
    kvm_open = kvm_service()
    success = False
    message = f"open {vm_name} failed"
    if kvm_open.run_vm(vm_name):
        # 启动成功
        message = f"open {vm_name} success"
        success = True

    response_data = {
        'success': success,
        'message': message
    }

    return jsonify(response_data)


@app.route('/delete')
def delete_vm():
    """删除虚拟机"""
    vm_name = request.args.get("vm_name")
    kvm_delete = kvm_service()
    success = False
    message = f"delete {vm_name} failed"
    if kvm_delete.delete_vm(vm_name):
        # 启动成功
        message = f"delete {vm_name} success"
        success = True

    response_data = {
        'success': success,
        'message': message
    }

    return jsonify(response_data)


@app.route('/shutdown')
def shutdown_vm():
    """关闭虚拟机"""
    vm_name = request.args.get("vm_name")
    kvm_shutdown = kvm_service()
    success = False
    message = f"shutdown {vm_name} failed"
    if kvm_shutdown.shutdown_vm(vm_name):
        # 启动成功
        message = f"shutdown {vm_name} success"
        success = True

    response_data = {
        'success': success,
        'message': message
    }

    return jsonify(response_data)


@app.route('/reboot')
def reboot_vm():
    """重启虚拟机"""
    vm_name = request.args.get("vm_name")
    kvm_reboot = kvm_service()
    success = False
    message = f"reboot {vm_name} failed"
    if kvm_reboot.reboot_vm(vm_name):
        # 启动成功
        message = f"reboot {vm_name} success"
        success = True

    response_data = {
        'success': success,
        'message': message
    }

    return jsonify(response_data)


def select_slave(cpu, memory, disk):
    """通过对比 寻找合适的slave作为宿主机"""
    for i, slave_item in enumerate(slaves, start=1):
        if cpu < slave_item.get_cpu() and memory < slave_item.get_memory() and disk < slave_item.disk:
            return slave_item
    return None


if __name__ == '__main__':
    app.run()
