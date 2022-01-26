#!/usr/python/bin
# -*- coding: utf-8 -*-


import sys
import os
import dpdk_scrits
import maker_public
import logging


#功能：初始化日志；参数：日志大小、错误描述；返回：无
def init_log(file_size, error):
    #设置日志
    if 2>len(sys.argv):
        print(error)
        exit(-1)
    if 3 <= len(sys.argv):
        try:
            CurFile = open(sys.argv[2], "a")
            CurFile.close()
        except:
            print("Exception while try to writing %s"  %(sys.argv[2]))
            exit(-1)
        log_path = os.path.abspath(sys.argv[2])
        if file_size < os.path.getsize(log_path):
            os.system("rm -rf "+log_path)
        logging.basicConfig(filename=log_path, filemode="a", \
            format="%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s",\
            level=logging.INFO)
    else:
        logging.basicConfig(format="%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s",\
            level=logging.INFO)

#函数功能：主函数
#函数参数：可执行文件全路径，启动时加入的参数
#函数返回：执行成功返回0，否则返回负值的错误码
if __name__ == "__main__":
    #错误描述
    error = "dpdk_opt: [install|uninstall|initenv|monitor] [log file]"

    #初始化日志文件，大小限制为512MB
    init_log(512*1024*1024, error)

    #所有的参数
    #需要隔离的CPU清单，从0开始，格式为1,4,5,6
    cpu_list = "3"
    #需要监控的进程的信息，两层list，内层list每个节点有三个参数：程序路径、工作路径、启动参数
    app_list = [["/usr/bin/more", "", "/etc/default/grub"]]
    #动态库路径清单，每个元素代表一个应用需要的动态库路径，他们会被添加到系统中，供启动时查找
    dll_list = [""]
    #地址随机化开启标志：1表示开启、0表示关闭
    ASLR_flg = "1"
    #需要开启的巨页的尺寸，有2048kb和1048576kb两种
    page_size = 2048
    #需要开启的巨页的数量，按照NUMA节点进行分配，在非NUMA结构下，只能配置node0
    page_cnt_lst = [["node0", 128]]
    #PCI设备的DPDK绑定脚本所在的路径，一般在DPDK安装路径的usertools下
    devbind_path = ""#"/usr/local/dpdk/share/dpdk/usertools"
    #VMBUS设备的DPDK绑定脚本所在的路径，该设备是微软hyper-v虚拟机的绑定程序，
    # 可以从https://gitlab.com/driverctl/driverctl下载。devbind_path和drvctl_path
    # 不能同时配置，必须配置一个，置为空串一个。
    drvctl_path = "/usr/local/dpdk/sbin/driverctl"
    #DPDK内核模块所在的路径，主要是igb_uio.ko和rte_kni.ko所在的路径，在编译DPDK时获取。
    # 注意：在DPDK20以后版本中默认是不打开igb_uio的，需要额外下载igb_uio源代码并且构建
    # 编译脚本，具体可以参见本工程中对VPP的DPDK的编译方法。
    kmod_path = "/usr/local/dpdk/kmod"
    #需要加载的内核模块，可以是igb_uio、rte_kni、uio_pci_generic、vfio_pci、uio_hv_generic。
    # 其中uio_pci_generic是linux提供的uio驱动，大部分场景可以替代igb_uio，只有一些比较老的设备
    # 才会需要igb_uio驱动；vfio_pci是3.6之后的内核提供的一种uio驱动，可以支持IO虚拟化技术，如
    # INTEL的VT-d、AMD的AMD-V、ARM的SMMU；uio_hv_generic是微软hyper-v虚拟机中的uio驱动。
    kmod_list = ["uio_hv_generic"]
    #需要绑定的设备，两层list，内层list每个节点有两个参数：网卡名、网卡的PCI地址。在PCI环境中，
    # 网卡的PCI地址是必须的；在VMBUS环境中，网卡名是必须的。
    dev_lst = [["eth2", "04:00.3"]]
    #解析参数
    if "install"==sys.argv[1]:
        error = dpdk_scrits.Install_dpdkenv(sys.argv[0], cpu_list, page_size, dll_list)
    elif "uninstall"==sys.argv[1]:
        error  = dpdk_scrits.Uinstall_dpdkenv(sys.argv[0], app_list)
    elif "initenv"==sys.argv[1]:
        error  = dpdk_scrits.Set_dpdkenv(ASLR_flg, page_size, page_cnt_lst, devbind_path, \
            drvctl_path, kmod_path, kmod_list, dev_lst)
    elif "monitor"==sys.argv[1]:
        error  = dpdk_scrits.Monitor_dpdkapp(app_list)
    if ""!=error:
        logging.error(error)
        exit(-1)
    if "install"==sys.argv[1] or "uninstall"==sys.argv[1]:
        maker_public.do_reboot("press any key to reboot...")
    exit(0)