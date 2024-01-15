from flask import Flask
from flask_cors import CORS
from slaves import slave
from services import kvm_service

# 创建flask对象
app = Flask(__name__)
# 跨域解决
CORS().init_app(app)

# 每个slave拥有的虚拟机列表
slave_a_vms = []
slave_b_vms = []
slave_c_vms = []

# 创建三个slave
slave_a = slave("192.168.45.1", "user1")
slave_b = slave("192.168.45.2", "user2")
slave_c = slave("192.168.45.3", "user3")


@app.route('/new')
def new_vm():
    # 创建新的虚拟机
    return 'New VM created successfully!'


@app.route('/delete')
def delete_vm():
    # 删除虚拟机
    return "Delete VM created successfully!"


@app.route('/shutdown')
def shutdown_vm():
    # 关闭虚拟机
    return 'Delete VM created successfully!'


@app.route('/reboot')
def reboot_vm():
    # 重启虚拟机
    return 'Reboot VM created successfully!'


if __name__ == '__main__':
    '测试代码'
    # 连接slave
    kvm_ctl = kvm_service()
    # 为该slave创建一个ubuntu虚拟机
    if kvm_ctl.new_ubuntu_vm(slave_a, 2, 2):
        print("yes")
