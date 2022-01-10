#!/usr/python/bin
# -*- coding: utf-8 -*-


import sys
import os
import re


#函数功能：读取一个文本文件
#函数参数：待读取的文件
#函数返回：读取到的内容，错误描述
def readTxtFile(szSrcFile):
    try:
        CurFile = open(szSrcFile, "r")
        szContent = CurFile.read()
        CurFile.close()
    except:
        return "", ("Exception while try to reading %s"  %(szSrcFile))
    return szContent, ""


#函数功能：创建一个目录
#函数参数：待创建的目录
#函数返回：错误描述
def makeDirs(szDirs):
    if True==os.path.exists(szDirs) and False==os.path.isdir(szDirs):
        os.remove(szDirs)
    try:
        if False==os.path.isdir(szDirs):
            os.makedirs(szDirs)
    except:
        return ("create dir %s failed" %(szDirs))
    return ""


#函数功能：执行命令并且获取输出
#函数参数：准备执行的命令
#函数返回：获取的输出
def execCmdAndGetOutput(szCmd):
    Ret = os.popen(szCmd)
    szOutput = Ret.read()  
    Ret.close()  
    return str(szOutput)  


#getOSName 获取操作系统名称；参数：无；返回：操作系统名称
def getOSName():
    #获取centos版本
    szOSName = execCmdAndGetOutput("rpm -q centos-release")
    if None != re.search("^centos\\-release\\-[\\d]+\\-[\\d]+\\.[\\d]+"+\
        "\\.[\\d]+\\.[^\\.]+\\.centos\\.[^\\.^\\s]+$", szOSName):
        return "centos"
    else:
        szOSName,sz_err = readTxtFile("/etc/redhat-release")
        if ""==sz_err and None!=re.search(
            "CentOS[ \\t]+Linux[ \\t]+release[ \\t]+\\d+\\.\\d+\\.\\d+", szOSName):
            return "centos"
    #获取ubuntu版本
    szOSName = execCmdAndGetOutput("lsb_release -a")
    if None != re.search("Distributor[ \\t]+ID[ \\t]*:[ \\t]+Ubuntu.*", szOSName):
        return "ubuntu"
    return ""


#功能：加载巨页；参数：无；返回：错误码
def using_hugepage():
    #设置巨页
    node_info = execCmdAndGetOutput("ls /sys/devices/system/node/"
        " | grep -P \"^node\\d+$\" | sort -u").split("\n")
    if 2 >= len(node_info):#这里2的原因是最后结束行是空行
        os.system("echo 256 > /sys/kernel/mm/hugepages/hugepages-2048kB/"
            "nr_hugepages")
    else:
        for cur_nd in node_info:
            os.system("echo 256 > /sys/devices/system/node/"+cur_nd+"/"
                "hugepages/hugepages-2048kB/nr_hugepages")
    #加载巨页文件
    if True == os.path.isdir("/mnt/huge"):
        os.system("umount -f /mnt/huge")
    if True == os.path.exists("/mnt/huge"):
        os.system("rm -Rf /mnt/huge")
    szErr = makeDirs("/mnt/huge")
    if "" != szErr:
        return szErr
    if 0 != os.system("mount -t hugetlbfs nodev /mnt/huge"):
        return "mount /mnt/huge failed!"
    return ""


#功能：关闭ASLR；参数：无；返回：错误码
def close_ASLR():
    if os.system("echo 0 > /proc/sys/kernel/randomize_va_space"):
        return "close ASLR failed!"
    return ""

#功能：加载网卡驱动；参数：dirver_name驱动名称，card_lst网卡名称链表；返回：错误码
def load_driver(dirver_name, card_lst):
    if getOSName() == "ubuntu":
        dirver_path = "build-root/install-vpp_debug-native/external/lib/modules"
    else:
        dirver_path =  "build-root/install-vpp_debug-native/external/lib/modules"
    if "" == execCmdAndGetOutput("lsmod | grep -P \"^uio[ \\t]+\""):
        if 0 != os.system("modprobe uio"):
            return "modprobe uio failed!"
    if "" == execCmdAndGetOutput("lsmod | grep -P \"^"+dirver_name+"[ \\t]+\""):
        if 0 != os.system("insmod "+dirver_path+"/"+dirver_name+".ko"):
            return "insmod "+dirver_name+" failed!"
    #绑定网卡
    drvctl_path = "driverctl"
    devbind_path = "build-root/install-vpp_debug-native/external/sbin"
    if False == os.path.exists(drvctl_path):
        for cur_card in card_lst:
            card_name = cur_card[0]
            card_addr = cur_card[1]
            if ""!=card_name and "" != execCmdAndGetOutput("python3 "+devbind_path+
                "/dpdk-devbind --status-dev net | grep \"if="+
                card_name+"\""):
                os.system("ifconfig "+card_name+" down")
            if "" != execCmdAndGetOutput("python3 "+devbind_path+"/dpdk-devbind "
                "--status-dev net | grep -P \""+card_addr+"[ \\t]+'.+'[ \\t]+drv=.+"
                "[ \\t]unused=.+\""):
                os.system("python3 "+devbind_path+"/dpdk-devbind -u "
                    +card_addr)
            os.system("python3 "+devbind_path+"/dpdk-devbind --b "+
                dirver_name+" "+card_addr)        
        os.system("python3 "+devbind_path+"/dpdk-devbind --status-dev net")
    else:
        for cur_card in card_lst:
            card_name = cur_card[0]
            os.system("cd "+drvctl_path+" && "\
                "DEV_UUID=$(basename $(readlink /sys/class/net/"+card_name+"/device)) && "\
                "./driverctl -b vmbus set-override $DEV_UUID uio_hv_generic")
        os.system("cd "+drvctl_path+" && ./driverctl -b vmbus list-overrides")
    return ""


#函数功能：主函数
#函数参数：可执行文件全路径，启动时加入的参数
#函数返回：执行成功返回0，否则返回负值的错误码
if __name__ == "__main__":
    errstr = using_hugepage()
    if "" != errstr:
        print(errstr)
    else:
        print("初始化巨页完毕")
    #errstr = close_ASLR()
    #if "" != errstr:
    #    print(errstr)
    #else:
    #    print("关闭ASLR完毕")
    if False == os.path.exists("driverctl"):
        #这里修改驱动、网卡、pci地址来绑定PCI设备
        errstr = load_driver("igb_uio", [["enp0s9","0000:00:09.0"]])
    else:
        #这里修改驱动、网卡、pci地址来绑定VMBUS设备
        errstr = load_driver("igb_uio", [["eth2"]])
    if "" != errstr:
        print(errstr)
    else:
        print("加载驱动完毕")