#!/usr/python/bin
# -*- coding: utf-8 -*-

import os
import re

#功能：读取一个文本文件；参数：待读取的文件；返回：读取到的内容，错误描述
def readTxtFile(szSrcFile):
    try:
        CurFile = open(szSrcFile, "r")
        szContent = CurFile.read()
        CurFile.close()
    except:
        return "", ("Exception while try to reading %s"  %(szSrcFile))
    return szContent, ""


#功能：将数据写入一个文本文件；参数：待写入的文件，待写入的内容；返回：错误描述
def writeTxtFile(szDstFile, szData):
    try:
        CurFile = open(szDstFile, "w")
        CurFile.write(szData)
        CurFile.close()
    except:
        return ("Exception while try to writing %s"  %(szDstFile))
    return ""


#功能：创建一个目录；参数：待创建的目录；返回：错误描述
def makeDirs(szDirs):
    if True==os.path.exists(szDirs) and False==os.path.isdir(szDirs):
        os.remove(szDirs)
    try:
        if False==os.path.isdir(szDirs):
            os.makedirs(szDirs)
    except:
        return ("create dir %s failed" %(szDirs))
    return ""


#功能：执行命令并且获取输出；参数：准备执行的命令；返回：获取的输出
def execCmdAndGetOutput(szCmd):
    Ret = os.popen(szCmd)
    szOutput = Ret.read()  
    Ret.close()  
    return str(szOutput)  


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
    if "" == execCmdAndGetOutput("lsmod | grep -P \"^uio[ \\t]+\""):
        if 0 != os.system("modprobe uio"):
            return "modprobe uio failed!"
    if "" == execCmdAndGetOutput("lsmod | grep -P \"^"+dirver_name+"[ \\t]+\""):
        if 0 != os.system("insmod /usr/local/dpdk/kmod/"+dirver_name+".ko"):
            return "insmod "+dirver_name+" failed!"
    if "" == execCmdAndGetOutput("lsmod | grep -P \"^rte_kni[ \\t]+\""):
        if 0 != os.system("insmod /usr/local/dpdk/kmod/rte_kni.ko carrier=on"):
            os.system("rmmod "+dirver_name)
            return "insmod rte_kni failed!"
    #绑定网卡
    for cur_card in card_lst:
        card_name = cur_card[0]
        card_addr = cur_card[1]
        if ""!=card_name and "" != execCmdAndGetOutput("python3 /usr/local"
            "/dpdk/sbin/dpdk-devbind --status-dev net | grep \"if="+
            card_name+"\""):
            os.system("ifconfig "+card_name+" down")
        if "" != execCmdAndGetOutput("python3 /usr/local/dpdk/sbin/dpdk-devbind "
            "--status-dev net | grep -P \""+card_addr+"[ \\t]+'.+'[ \\t]+drv=.+"
            "[ \\t]unused=.+\""):
            os.system("python3 /usr/local/dpdk/sbin/dpdk-devbind -u "
                +card_addr)
        os.system("python3 /usr/local/dpdk/sbin/dpdk-devbind --b "+
            dirver_name+" "+card_addr)        
    os.system("python3 /usr/local/dpdk/sbin/dpdk-devbind --status-dev net")
    return ""


#功能：导入路径参数；参数：无；返回：错误码
def export_path():
    #读取
    profile,sz_err = readTxtFile("/root/.profile")
    if "" != sz_err:
        return sz_err
    #修改
    if 0 >= len(re.findall("\nexport[ \\t]+FF_PATH[ \\t]*=.+", profile)):
        profile += "\nexport FF_PATH="+os.getcwd()
    else:
        profile = re.sub("\nexport[ \\t]+FF_PATH[ \\t]*=.+", 
            "\nexport FF_PATH="+os.getcwd(), profile)
    if 0 >= len(re.findall("\nexport[ \\t]+FF_DPDK[ \\t]*=.+", profile)):
        profile += "\nexport FF_DPDK=/usr/local/dpdk"
    else:
        profile = re.sub("\nexport[ \\t]+FF_DPDK[ \\t]*=.+", 
            "\nexport FF_DPDK=/usr/local/dpdk", profile)
    #写入
    sz_err = writeTxtFile("/root/.profile", profile)
    if "" != sz_err:
        return sz_err
    sz_err = writeTxtFile("/tmp/root_source_profile.sh", 
        "#!/bin/bash\nsource /root/.profile\n")
    if "" != sz_err:
        return sz_err
    #生效
    os.system("bash /tmp/root_source_profile.sh")
    os.system("rm -f /tmp/root_source_profile.sh")
    os.system("export | grep \"FF_\"")
    return ""


#函数功能：主函数
#函数参数：可执行文件全路径，启动时加入的参数
#函数返回：执行成功返回0，否则返回负值的错误码
if __name__ == "__main__":
    szErr = using_hugepage()
    if "" != szErr:
        print(szErr)
    else:
        print("using hugepage sucess!")
    szErr = close_ASLR()
    if "" != szErr:
        print(szErr)
    else:
        print("close ASLR sucess!")
    szErr = load_driver("igb_uio", [["enp0s9","0000:00:09.0"]])
    if "" != szErr:
        print(szErr)
    else:
        print("load driver sucess!")
    szErr = export_path()
    if "" != szErr:
        print(szErr)
    else:
        print("export path sucess!")