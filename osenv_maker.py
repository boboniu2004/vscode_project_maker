#!/usr/python/bin
# -*- coding: utf-8 -*-


import re
import sys
import os
import maker_public
import centosenv_maker
import ubuntuenv_maker

#函数功能：主函数
#函数参数：可执行文件全路径，启动时加入的参数
#函数返回：执行成功返回0，否则返回负值的错误码
if __name__ == "__main__":
    #获取发行版本
    szOSName = maker_public.getOSName()
    if 2<len(sys.argv):
        if "config_IP"!=sys.argv[1]:
            szErr = "Invaild operation" 
        else:
            if "centos" == szOSName:
                szErr = centosenv_maker.InitInternalNet()
            elif "ubuntu" == szOSName:
                szErr = ubuntuenv_maker.InitInternalNet()
            else:
                szErr = "Invaild OS"
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
    elif re.search("^2\\..*", sys.version):
        raw_input("make development environment of %s finish, please any key to reboot..." %(szOSName))
        os.system("reboot")
    else:
        input("make development environment of %s finish, please any key to reboot..." %(szOSName))
        os.system("reboot")