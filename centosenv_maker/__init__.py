#!/usr/python/bin
# -*- coding: utf-8 -*-


import re
import os
import sys
import maker_public


#installOrUpdateRpm 检查rpm包的版本，并且尝试安装该包；参数：rpm包名称，机器版本；返回：错误描述
def installOrUpdateRpm(szRpmName, szMacVer, szRpmPath):
    #获取RPM包的安装信息
    szRpmInfo= maker_public.execCmdAndGetOutput(\
        "yum list installed | grep -E \""+szRpmName+"."+szMacVer+"\"")
    szRpmInfoArr = szRpmInfo.split("\n")
    InstalledMatchList = None
    for szCurRpm in szRpmInfoArr:
        InstalledMatchList = re.match("^"+szRpmName+"\\."+szMacVer+\
            "[\\s]{1,}([^\\s]{1,})[\\s]{1,}[^\\s]{1,}", szCurRpm)
        if None != InstalledMatchList:
            break
    #如果没有安装则进行安装，否则就进行升级
    if None == InstalledMatchList:
        if 0 >= len(szRpmPath):
            if 0 != os.system("yum -y install %s.%s" %(szRpmName, szMacVer)):
                return ("Failed to Install %s.%s"  %(szRpmName, szMacVer))
        else:
            if 0 != os.system("yum -y install %s" %(szRpmPath)):
                return ("Install %s.%s failed"  %(szRpmName, szMacVer))
    else:
        if 0 >= len(szRpmPath):
            if 0 != os.system("yum -y update %s.%s" %(szRpmName, szMacVer)):
                return ("Update %s.%s failed"  %(szRpmName, szMacVer))
        else:
            if 0 != os.system("yum -y update %s" %(szRpmPath)):
                return ("Update %s.%s failed"  %(szRpmName, szMacVer))     
    #打印安装成功信息
    print("Install/Update %s success\n" %(szRpmName))
    #返回
    return ""


#configRepo 配置扩展源；参数：无；返回：错误描述
def configRepo():
    #获取centos版本
    szCentOSVer = maker_public.execCmdAndGetOutput("rpm -q centos-release")
    MatchList = re.match("^centos\\-release\\-([\\d]+)\\-[\\d]+\\.[\\d]+"+\
        "\\.[\\d]+\\.[^\\.]+\\.centos\\.[^\\.^\\s]+$", szCentOSVer)
    if None == MatchList:
        return ("Unknow OS:%s" %szCentOSVer)
    #安装epel扩展库(阿里源)
    os.system("yum erase -y epel-release.noarch")
    if 0 != os.system( ("wget -O /etc/yum.repos.d/epel-%s.repo http://mirrors.aliyun.com/repo/epel-%s.repo" \
        %(MatchList.group(1),MatchList.group(1))) ):
        return "Download epel failed"
    os.system("yum clean all; yum makecache")
    #安装WANGdisco
    szRpmPath = ("http://opensource.wandisco.com/centos/%s"\
        "/git/x86_64/wandisco-git-release-%s-2.noarch.rpm" %(MatchList.group(1),MatchList.group(1)))
    szErr = installOrUpdateRpm("wandisco-git-release", "noarch", szRpmPath)
    if 0 >= len(szErr):
       return ""
    szRpmPath = ("http://opensource.wandisco.com/centos/%s"\
        "/git/x86_64/wandisco-git-release-%s-1.noarch.rpm" %(MatchList.group(1),MatchList.group(1)))
    szErr = installOrUpdateRpm("wandisco-git-release", "noarch", szRpmPath)
    if 0 < len(szErr):
        return szErr
    #
    return ""


#updateSystem 将系统升级到最新版本；参数：无；返回：错误描述
def updateSystem():
    os.system("yum clean all")
    if 0 != os.system("yum -y update"):
        return "Update CentOS failed"
    #关闭防火墙
    os.system("systemctl stop firewalld.service")
    if 0 != os.system("systemctl disable firewalld.service"):
        return "Disable firewalld failed"
    #关闭SELINUX
    szSelinux,szErr = maker_public.readTxtFile("/etc/selinux/config")
    if 0 < len(szErr):
        return "Disable SELINUX failed"
    szSelinux = re.sub("\\n[ \\t]*SELINUX[ \\t]*=[ \\t]*.+", "\nSELINUX=disabled", szSelinux)
    szErr = maker_public.writeTxtFile("/etc/selinux/config", szSelinux)
    if 0 < len(szErr):
        return "Disable SELINUX failed"
    #配置时钟同步
    os.system("systemctl disable chronyd.service")
    os.system("systemctl enable ntpd.service")
    os.system("systemctl stop ntpd.service")
    os.system("systemctl start ntpd.service")
    os.system("systemctl status ntpd.service")
    return ""


#configSshd 配置SSHD；参数：无；返回：错误描述
def configSshd():
    #安装
    szErr = installOrUpdateRpm("openssh-server", "x86_64", "")
    if 0 < len(szErr):
        return szErr
    #读取配置文件
    return maker_public.ConfigSshd()


#configGit 配置GIT；参数：无；返回：错误描述
def configGit():
    return installOrUpdateRpm("git", "x86_64", "")


#configGcc 配置GcCC；参数：无；返回：错误描述
def configGcc():
    return installOrUpdateRpm("gcc", "x86_64", "")


#configGolang 配置GOLANG；参数：无；返回：错误描述
def configGolang():
    #安装 golang
    szErr = installOrUpdateRpm("golang", "x86_64", "")
    if 0 < len(szErr):
        return szErr
    #安装工具
    szErr = maker_public.installGolangTools("go")
    if 0 < len(szErr):
        return szErr
    #
    return ""


#configPython 配置PYTHON；参数：无；返回：错误描述
def configPython():
    szErr = installOrUpdateRpm("python", "x86_64", "")
    if 0 < len(szErr):
        return szErr
    szErr = installOrUpdateRpm("python2-pip", "noarch", "")
    if 0 < len(szErr):
        return szErr
    #配置PIP
    szErr = maker_public.configPip("python", "pip")
    if 0 < len(szErr):
        return szErr
    return ""


#configJava 配置JAVA；参数：无；返回：错误描c述
def configJava():
    #安装RPM包
    szErr = installOrUpdateRpm("java-11-openjdk", "x86_64", "")
    if 0 < len(szErr):
        return szErr
    szErr = installOrUpdateRpm("java-11-openjdk-jmods", "x86_64", "")
    if 0 < len(szErr):
        return szErr
    os.system("java -version")
    #返回
    return ""


#configPlanUML 配置PlanUML；参数：无；返回：错误描述
def configPlanUML():
    #下载
    if False == os.path.exists(os.path.dirname(os.path.realpath(sys.argv[0]))+\
        "/graphviz-2.30.1-21.el7.x86_64.rpm"):
        if 0 != os.system("wget -P "+os.path.dirname(os.path.realpath(sys.argv[0]))+\
            " http://rpmfind.net/linux/centos/7.7.1908/os/x86_64/Packages/"\
            "graphviz-2.30.1-21.el7.x86_64.rpm "):
            return "Failed to download graphviz"
    #安装
    szErr = installOrUpdateRpm("graphviz", "x86_64", \
        os.path.dirname(os.path.realpath(sys.argv[0]))+"/graphviz-2.30.1-21.el7.x86_64.rpm")
    if 0 < len(szErr):
        return szErr
    #
    return ""


#configInternalNet 配置内部网络；参数：内部网卡的中英文名称，szIpAddr本机的IP地址；返回：错误描述
def configInternalNet(szEthChName, szEthEnName, szIpAddr):
    #获取设备对应的UUID
    szDevConf = maker_public.execCmdAndGetOutput("nmcli con")
    MatchList = re.match(".*"+szEthChName+"[ \\t]+([\\S]+)[ \\t]+[\\S]+[ \\t]+.*", \
        szDevConf, re.DOTALL)
    if None == MatchList:
        MatchList = re.match(".*"+szEthEnName+"[ \\t]+([\\S]+)[ \\t]+[\\S]+[ \\t]+.*", \
            szDevConf, re.DOTALL)
    if None == MatchList:
        return "Can not find "+szEthEnName
    szConfig = \
        "TYPE=\"Ethernet\"\n"+\
        "PROXY_METHOD=\"none\"\n"+\
        "BROWSER_ONLY=\"no\"\n"+\
        "BOOTPROTO=\"static\"\n"+\
        "DEFROUTE=\"no\"\n"+\
        "IPV4_FAILURE_FATAL=\"no\"\n"+\
        "IPV6INIT=\"yes\"\n"+\
        "IPV6_AUTOCONF=\"yes\"\n"+\
        "IPV6_DEFROUTE=\"yes\"\n"+\
        "IPV6_FAILURE_FATAL=\"no\"\n"+\
        "IPV6_ADDR_GEN_MODE=\"stable-privacy\"\n"+\
        "NAME=\""+szEthEnName+"\"\n"+\
        "UUID=\""+MatchList.group(1)+"\"\n"+\
        "DEVICE=\""+szEthEnName+"\"\n"+\
        "ONBOOT=\"yes\"\n"+\
        "IPADDR="+szIpAddr+"\n"+\
        "NETMASK=255.255.255.0\n"+\
        "GATEWAY=192.168.137.1\n"+\
        "DNS1=192.168.137.1\n"
    #写入配置
    szErr = maker_public.writeTxtFile("/etc/sysconfig/network-scripts/ifcfg-"+szEthEnName, szConfig)
    if 0 < len(szErr):
        return szErr
    #重启服务
    os.system("systemctl restart network.service")
    os.system("systemctl status network.service")
    os.system("ifconfig")
    #
    return ""


#InitEnv 初始化环境；参数：无；返回：错误描述
def InitEnv():
    #安装扩展库
    szErr = configRepo()
    if 0 < len(szErr):
        return("Config CentOS failed:%s" %(szErr))
    #将系统升级到最新版本
    szErr = updateSystem()
    if 0 < len(szErr):
        return("Config CentOS failed:%s" %(szErr))
    #配置SSHD
    szErr = configSshd()
    if 0 < len(szErr):
        return("Config CentOS failed:%s" %(szErr))
    #安装GIT
    szErr = configGit()
    if 0 < len(szErr):
        return("Config CentOS failed:%s" %(szErr))
    #安装GCC
    szErr = configGcc()
    if 0 < len(szErr):
        return("Config CentOS failed:%s" %(szErr))
    #安装GOLANG
    szErr = configGolang()
    if 0 < len(szErr):
        return("Config CentOS failed:%s" %(szErr))
    #安装PYTHON和PIP
    szErr = configPython()
    if 0 < len(szErr):
        return("Config CentOS failed:%s" %(szErr))
    #安装JAVA
    szErr = configJava()
    if 0 < len(szErr):
        return("Config CentOS failed:%s" %(szErr))
    #配置PLANUML
    szErr = configPlanUML()
    if 0 < len(szErr):
        return("Config CentOS failed:%s" %(szErr))
    #关闭图形界面
    if 0 != os.system("systemctl set-default multi-user.target"):
        return("Config CentOS failed: can not disable GNOME")
    #升级PIP
    if 0 != os.system("pip install --upgrade pip"):
        return("Update PIP failed")
    #配置内部网络
    if 1 < len(sys.argv):
        szErr = configInternalNet("有线连接 1", "eth1", sys.argv[1])
        if 0 < len(szErr):
            return("Config CentOS failed:%s" %(szErr))
    #
    return ""


#InitInternalNet 初始化内部网络；参数：内部网络的IP地址；返回：错误描述
def InitInternalNet():
    szErr = configInternalNet("有线连接 1", "eth1", sys.argv[2])
    if 0 < len(szErr):
        return("Config IP failed:%s" %(szErr))
    #
    return ""
