云计算：简单分布式云服务系统（类似阿里云服务）
# 环境准备
## 软件需求
+ CentOS7
+ python 3.6.8
+ libvirt-python 9.10.0
+ Flask
+ flask_cors
## 硬件需求
+ 至少准备两台以上的物理机，并在同一个局域网下，一个作为主机master，其余的作为slave
+ 在多台物理机上需要安装Linux系统（系统的CPU、内存、硬盘尽可能大）
# 相关问题
 + 在下载libvirt-python时若出现 Running setup.py install for libvirt-python ... error 问题,尝试着先使用以下解决方法：
   + sudo yum install python3-devel
   + sudo yum install libvirt*
 + 使用libvirtAPI ssh 远程连接slave时，需先向slave传递ssh免密登录
 + 配置xml文件，关于镜像文件qcow2的准备
   + 参考链接：[制作qcow2目标镜像](https://blog.csdn.net/yuanfang_way/article/details/79136502)
   + 注意 函数createXML为创建临时虚拟机 defineXML为创建持久化虚拟机
