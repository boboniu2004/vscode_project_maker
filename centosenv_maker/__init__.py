#!/usr/python/bin
# -*- coding: utf-8 -*-


import platform
import re
import os
import sys
import maker_public


#GetCentosVer 获取centos版本；参数：版本，错误描述
def GetCentosVer():
    szCentOSVer = maker_public.execCmdAndGetOutput("rpm -q centos-release")
    MatchList = re.match("^centos\\-release\\-([\\d]+)\\-[\\d]+\\.[\\d]+"+\
        "\\.[\\d]+\\.[^\\.]+\\.centos\\.[^\\.^\\s]+$", szCentOSVer)
    if None == MatchList:
        szCentOSVer,sz_err = maker_public.readTxtFile("/etc/redhat-release")
        if "" != sz_err:
            return None,"can not read /etc/redhat-release"
        MatchList = re.search("CentOS[ \\t]+Linux[ \\t]+release[ \\t]+(\\d+)\\.\\d+\\.\\d+", 
            szCentOSVer)
        if None == MatchList:
            return None,("Unknow OS:%s" %szCentOSVer)
    return MatchList.group(1),""


#installOrUpdateRpm 检查rpm包的版本，并且尝试安装该包；参数：rpm包名称，机器版本；返回：错误描述
def installOrUpdateRpm(szRpmName, szMacVer, szRpmPath):
    #获取RPM包的安装信息
    tmpinf = maker_public.execCmdAndGetOutput("yum list installed | grep %s" %szRpmName)
    if "" != szMacVer:
        InstalledMatchList = re.match("(^|\\n)"+szRpmName+"\\."+szMacVer+\
            "[\\s]{1,}([^\\s]{1,})[\\s]{1,}[^\\s]{1,}", tmpinf)
    else:
        InstalledMatchList = re.match("(^|\\n)"+szRpmName+\
            "[\\s]{1,}([^\\s]{1,})[\\s]{1,}[^\\s]{1,}", tmpinf)
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


#releaseYum 杀死当前占有yum资源的进程，释放资源；参数：无；返回：错误描述
def releaseYum():
    szOtherProc,szErr = maker_public.readTxtFile("/var/run/yum.pid")
    if ""!=szErr:
        return
    if True == szOtherProc.isdigit():
        os.system("kill -9 "+szOtherProc)
    os.system("rm -rf /var/run/yum.pid")

#configRepo 配置扩展源；参数：软件源；返回：错误描述
def configRepo(rpm_src, epel_src):
    #获取centos版本
    osver,err = GetCentosVer()
    if "" != err:
        return err
    #更新基础源
    os.system( ("rm -Rf /etc/yum.repos.d/Centos-%s.repo" %(osver)) )
    if True == os.path.exists("/etc/yum.repos.d/CentOS-Base.repo"):
        os.system("rm -Rf /etc/yum.repos.d/CentOS-Base.repo.bark")
        os.system("mv /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/"\
            "CentOS-Base.repo.bark")
    if 0!=os.system( "wget -O /etc/yum.repos.d/CentOS-Base.repo %s" %rpm_src):
        os.system("rm -Rf /etc/yum.repos.d/CentOS-Base.repo")
        os.system("mv /etc/yum.repos.d/CentOS-Base.repo.bark "\
            "/etc/yum.repos.d/CentOS-Base.repo")
        return ("Download %s failed" %rpm_src)
    if "8" == osver:
        #删除不要的源
        os.system("mv /etc/yum.repos.d/CentOS-Linux-AppStream.repo "\
            "/etc/yum.repos.d/CentOS-Linux-AppStream.repo.bark")
        os.system("mv /etc/yum.repos.d/CentOS-Linux-BaseOS.repo "\
            "/etc/yum.repos.d/CentOS-Linux-BaseOS.repo.bark")
        os.system("mv /etc/yum.repos.d/CentOS-Linux-Extras.repo "\
            "/etc/yum.repos.d/CentOS-Linux-Extras.repo.bark")
        os.system("mv /etc/yum.repos.d/CentOS-Linux-Plus.repo "\
            "/etc/yum.repos.d/CentOS-Linux-Plus.repo.bark")
        os.system("mv /etc/yum.repos.d/CentOS-Linux-PowerTools.repo "\
            "/etc/yum.repos.d/CentOS-Linux-PowerTools.repo.bark")
        os.system( ("rm -Rf /etc/yum.repos.d/CentOS%s-Base-163.repo" %(osver)) )
        #安装epel源
        os.system("yum erase -y epel-release.noarch")
        szErr = installOrUpdateRpm("epel-release", "noarch", "")
        if 0 < len(szErr):
            return "Install epel failed"
    else:
        #删除不要的源
        os.system( ("rm -Rf /etc/yum.repos.d/CentOS%s-Base-163.repo" %(osver)) )  
        #安装epel源
        os.system("yum erase -y epel-release.noarch")
        if False==os.path.exists( ("/etc/yum.repos.d/epel-%s.repo" %(osver)) ) or \
            0==os.path.getsize( ("/etc/yum.repos.d/epel-%s.repo" %(osver)) ):
            if 0!=os.system( ("wget -O /etc/yum.repos.d/epel-%s.repo %s" \
                %(osver, epel_src)) ):
                return "Download epel.repo failed"
    os.system("yum clean all; yum makecache")
    #安装WANGdisco
    cpuarch = platform.machine()
    if "8" != osver:
        szRpmPath = ("http://opensource.wandisco.com/centos/%s"\
            "/git/"+cpuarch+"/wandisco-git-release-%s-2.noarch.rpm" 
            %(osver,osver))
        szErr = installOrUpdateRpm("wandisco-git-release", "noarch", szRpmPath)
        if 0 >= len(szErr):
            return ""
        szRpmPath = ("http://opensource.wandisco.com/centos/%s"\
            "/git/"+cpuarch+"/wandisco-git-release-%s-1.noarch.rpm" 
            %(osver,osver))
        szErr = installOrUpdateRpm("wandisco-git-release", "noarch", szRpmPath)
        if 0 < len(szErr):
            return szErr
    #
    return ""


#updateSystem 将系统升级到最新版本；参数：无；返回：错误描述
def updateSystem():
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
    #将时钟同步重启加入计划任务
    szRet = maker_public.execCmdAndGetOutput("crontab -l")
    if None != re.search(".+systemctl[ \\t]+restart[ \\t]+ntpd\\.service", szRet):
        szRet = re.sub(".+systemctl[ \\t]+restart[ \\t]+ntpd\\.service", \
            "*/2 * * * * systemctl restart ntpd.service", szRet)
    elif 0>=len(szRet) or "\n" == szRet[len(szRet)-1]:
        szRet += "*/2 * * * * systemctl restart ntpd.service\n"
    else:
        szRet += "\n*/2 * * * * systemctl restart ntpd.service\n"
    #将新的定时任务写入文件
    szErr = maker_public.writeTxtFile("/tmp/vscode_project_maker_crontab", szRet)
    if 0 < len(szErr):
        os.system("rm -Rf /tmp/vscode_project_maker_crontab")
        return szErr
    if 0 != os.system("crontab /tmp/vscode_project_maker_crontab"):
        os.system("rm -Rf /tmp/vscode_project_maker_crontab")
        return "Run crontab failed"
    os.system("rm -Rf /tmp/vscode_project_maker_crontab")
    return ""


#configSshd 配置SSHD；参数：无；返回：错误描述
def configSshd():
    #安装
    szErr = installOrUpdateRpm("openssh-server", platform.machine(), "")
    if 0 < len(szErr):
        return szErr
    #读取配置文件
    return maker_public.ConfigSshd()


#configGit 配置GIT；参数：无；返回：错误描述
def configGitSvn():
    err = installOrUpdateRpm("subversion", platform.machine(), "")
    if 0 < len(err):
        return err
    return installOrUpdateRpm("git", platform.machine(), "")


#configGcc 配置GcCC；参数：无；返回：错误描述
def configGcc():
    return installOrUpdateRpm("gcc", platform.machine(), "")


#configGolang 配置GOLANG；参数：无；返回：错误描述
def configGolang(work_path, go_proxy):
    gover = maker_public.getVer("go")
    gomac = "amd64"
    if "" != maker_public.execCmdAndGetOutput("lscpu | grep -E \"aarch64\""):
        gomac = "arm64"
    #安装 golang
    if False == os.path.exists("%s/go%s.linux-%s.tar.gz" %(work_path,gover,gomac)):
        if 0 != os.system("wget https://studygolang.com/dl/golang/go%s.linux-%s.tar.gz "\
            "-O %s/go%s.linux-%s.tar.gz" %(gover,gomac,work_path,gover,gomac)):
            return ("Failed to download go%s" %gover)
    if -1 == maker_public.execCmdAndGetOutput(\
        "su -c \"/usr/local/go/bin/go version\"").find("go%s" %gover):
        os.system("rm -Rf /usr/local/go")
        if 0 != os.system("tar -C /usr/local -zxvf %s/go%s.linux-%s.tar.gz" \
            %(work_path,gover,gomac)):
            return ("Failed to uncompress go%s" %gover)
    #安装工具
    szErr = maker_public.installGolangTools("/usr/local/go", go_proxy)
    if 0 < len(szErr):
        return szErr
    #
    return ""


#configPython 配置PYTHON；参数：无；返回：错误描述
def configPython(py_host,py_url):
    pyver = maker_public.getVer("python")
    tmpinf = maker_public.execCmdAndGetOutput(\
        "yum list installed | grep -E \"python3\"")
    if None == re.search(("(^python3\\d+\\.)|(\\npython3\\d+\\.)"),tmpinf):
        installOrUpdateRpm("python"+pyver.replace(".",""), platform.machine(), "")
    match_lst = re.search("[pP]ython[ \\t]+(3\\.\d+)\\.\d+.*", 
        maker_public.execCmdAndGetOutput("python3 --version"))
    if None == match_lst:
        cur_pyver = ""
    else:
        cur_pyver = match_lst.group(1)
    if ""==cur_pyver or cur_pyver<pyver:
        szErr = installOrUpdateRpm("python"+pyver.replace(".",""), platform.machine(), "")
        if 0 < len(szErr):
            return szErr
    #
    szErr = installOrUpdateRpm("python3-pip", "noarch", "")
    if 0 < len(szErr):
        return szErr
    #配置PIP
    szErr = maker_public.configPip("python3", py_host, py_url)
    if 0 < len(szErr):
        return szErr
    if ""==cur_pyver or cur_pyver<pyver:
        szErr = maker_public.configPip("python"+pyver, py_host, py_url)
        if 0 < len(szErr):
            return szErr
    return ""


#configJava 配置JAVA；参数：无；返回：错误描c述
def configJava():
    #安装RPM包
    szErr = installOrUpdateRpm("java-"+maker_public.getVer("java")+"-openjdk", 
        platform.machine(), "")
    if 0 < len(szErr):
        return szErr
    szErr = installOrUpdateRpm("java-"+maker_public.getVer("java")+"-openjdk-jmods", 
        platform.machine(), "")
    if 0 < len(szErr):
        return szErr
    os.system("java -version")
    #返回
    return ""


#configInternalNet 配置内部网络；参数：内部网卡的中英文名称，szIpAddr本机的IP地址；返回：错误描述
def configInternalNet(szEthChName, szEthEnName, szIpAddr):
    net_prefx = re.sub("\\.\\d+$", "", szIpAddr)
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
        "GATEWAY="+net_prefx+".1\n"+\
        "DNS1="+net_prefx+".1\n"
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


#InitEnv 初始化环境；参数：参数字典；返回：错误描述
def InitEnv(sys_par):
    par_dic = dict(sys_par)
    work_path = par_dic["work_path"]
    #释放yum资源
    releaseYum()
    #安装扩展库
    szErr = configRepo(par_dic["rpm_src"],par_dic.get("epel_src"))
    if 0 < len(szErr):
        return("Config CentOS failed:%s" %(szErr))
    #将系统升级到最新版本
    szErr = updateSystem()
    if 0 < len(szErr):
        return("Config CentOS failed:%s" %(szErr))
    #配置SSHD
    if "online" == par_dic["work_mod"]:
        szErr = configSshd()
        if 0 < len(szErr):
            return("Config CentOS failed:%s" %(szErr))
    #安装GIT和svn
    szErr = configGitSvn()
    if 0 < len(szErr):
        return("Config CentOS failed:%s" %(szErr))
    #安装GCC
    szErr = configGcc()
    if 0 < len(szErr):
        return("Config CentOS failed:%s" %(szErr))
    #安装GOLANG
    szErr = configGolang(work_path, par_dic["go_proxy"])
    if 0 < len(szErr):
        return("Config CentOS failed:%s" %(szErr))
    #安装PYTHON和PIP
    szErr = configPython(par_dic["py_host"],par_dic["py_url"])
    if 0 < len(szErr):
        return("Config CentOS failed:%s" %(szErr))
    #安装JAVA
    szErr = configJava()
    if 0 < len(szErr):
        return("Config CentOS failed:%s" %(szErr))
    #关闭图形界面
    if "online" == par_dic["work_mod"]:
        if 0 != os.system("systemctl set-default multi-user.target"):
            return("Config CentOS failed: can not disable GNOME")
    #配置内部网络
    if "online" == par_dic["work_mod"]:
        szErr = configInternalNet("有线连接 1", "eth1", par_dic["ip"])
        if 0 < len(szErr):
            return("Config CentOS failed:%s" %(szErr))
    #
    return ""


#InitInternalNet 初始化内部网络；参数：内部网络的IP地址；返回：错误描述
def InitInternalNet(ip_addr):
    szErr = configInternalNet("有线连接 1", "eth1", ip_addr)
    if 0 < len(szErr):
        return("Config IP failed:%s" %(szErr))
    #
    return ""
