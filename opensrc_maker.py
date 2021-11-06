#!/usr/python/bin
# -*- coding: utf-8 -*-


import sys
import os


#函数功能：主函数
#函数参数：可执行文件全路径，启动时加入的参数
#函数返回：执行成功返回0，否则返回负值的错误码
if __name__ == "__main__":
    #获取发行版本
    szOSName = maker_public.getOSName()
    if 2<len(sys.argv) and "config_IP"==sys.argv[1]:
        if "config_IP"==sys.argv[1]:
            if "centos" == szOSName:
                szErr = centosenv_maker.InitInternalNet()
            elif "ubuntu" == szOSName:
                szErr = ubuntuenv_maker.InitInternalNet()
            else:
                szErr = "Invaild OS"
        else:
            szErr = "Invaild operation" 
    elif 2<len(sys.argv) and -1!=str(sys.argv[1]).find("config_DPDK"):
        #判断是否具备运行DPDK的环境
        first_ver,second_ver,_ = maker_public.get_kernel_ver()
        if ""==maker_public.execCmdAndGetOutput("lspci") and (None==first_ver or \
            first_ver<4 or (first_ver==4 and second_ver<18)):
            szErr = "Invaild virture machine"
        else:
            if "centos" == szOSName:
                szErr = centosenv_maker.ConfigDPDK(sys.argv[1], sys.argv[2])
            elif "ubuntu" == szOSName:
                szErr = ubuntuenv_maker.ConfigDPDK(sys.argv[1], sys.argv[2])
            else:
                szErr = "Invaild OS"
    elif 1<len(sys.argv) and None==re.match("^\\d+\\.\\d+\\.\\d+\\.\\d+$",
        sys.argv[1]):
        szErr = "vs_progject_maker: null|config_IP [xx.xx.xx.xx]|"\
            "config_DPDK [install/uninstall]|config_DPDK-meson [install/uninstall]"
    else:
        if "centos" == szOSName:
            szErr = centosenv_maker.InitEnv()
        elif "ubuntu" == szOSName:
            szErr = ubuntuenv_maker.InitEnv()
        else:
            szErr = "Invaild OS"
    if 0 < len(szErr):
        print(szErr)
    elif 2<len(sys.argv) and "config_IP"==sys.argv[1]:
        print("Config IP finish")
    elif 2<len(sys.argv) and -1!=str(sys.argv[1]).find("config_DPDK"):
        print("Config DPDK finish")
    elif re.search("^2\\..*", sys.version):
        raw_input("make development environment of %s finish, press any key to reboot..." %(szOSName))
        os.system("reboot")
    else:
        input("make development environment of %s finish, press any key to reboot..." %(szOSName))
        os.system("reboot")