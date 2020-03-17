#!/usr/python/bin
# -*- coding: utf-8 -*-


import re
import sys
import maker_public
import centosenv_maker
import ubuntuenv_maker


#getOSName 获取操作系统名称；参数：无；返回：操作系统名称
def getOSName():
    #获取centos版本
    szOSName = maker_public.execCmdAndGetOutput("rpm -q centos-release")
    if None != re.search("^centos\\-release\\-[\\d]+\\-[\\d]+\\.[\\d]+"+\
        "\\.[\\d]+\\.[^\\.]+\\.centos\\.[^\\.^\\s]+$", szOSName):
        return "centos"
    return ""

#函数功能：主函数
#函数参数：可执行文件全路径，启动时加入的参数
#函数返回：执行成功返回0，否则返回负值的错误码
if __name__ == "__main__":
    #获取发行版本
    szOSName = getOSName()
    if 2<len(sys.argv) and "config_IP"==sys.argv[1]:
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
    else:
        if 2<len(sys.argv) and "config_IP"==sys.argv[1]:
            print("Config IP finish")
        else:
            raw_input("make development environment of %s finish, please any key to reboot..." %(szOSName))
            os.system("reboot")

    #安装扩展库