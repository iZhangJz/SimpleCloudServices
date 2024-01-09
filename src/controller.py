from flask import Flask
from flask_cors import CORS

# 创建flask对象
app = Flask(__name__)
# 跨域解决
CORS().init_app(app)

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
    app.run()
