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

#configRepo 配置扩展源；参数：无；返回：错误描述
def configRepo():
    #获取centos版本
    osver,err = GetCentosVer()
    if "" != err:
        return err
    #更新基础源为阿里源rue
    if "8" == osver:
        os.system( ("rm -Rf /etc/yum.repos.d/Centos-%s.repo" %(osver)) )
        if True == os.path.exists("/etc/yum.repos.d/CentOS-Base.repo"):
            os.system("rm -Rf /etc/yum.repos.d/CentOS-Base.repo.bark")
            os.system("mv /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/"\
                "CentOS-Base.repo.bark")
        if 0!=os.system( "wget -O /etc/yum.repos.d/CentOS-Base.repo "\
                "http://mirrors.aliyun.com/repo/Centos-vault-8.5.2111.repo"):
            os.system("rm -Rf /etc/yum.repos.d/CentOS-Base.repo")
            os.system("mv /etc/yum.repos.d/CentOS-Base.repo.bark "\
                "/etc/yum.repos.d/CentOS-Base.repo")
            return "Download aliyun.repo failed"
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
        #szRpmPath = ("https://mirrors.aliyun.com/epel/epel-release-latest-%s.noarch.rpm" 
        #    %(osver))
        szErr = installOrUpdateRpm("epel-release", "noarch", "")
        if 0 < len(szErr):
            return "Install epel failed"
        #if 0 != os.system("sed -i 's|^[ \\t]*#[ \\t]*baseurl[ \\t]*=.*|"\
        #    "baseurl=https://mirrors.aliyun.com/epel/%s/Modular/SRPMS|' "\
        #    "/etc/yum.repos.d/epel* && "\
        #    "sed -i 's|^metalink|#metalink|' /etc/yum.repos.d/epel*" %(osver)):
        #    return "Install epel failed"
    else:
        os.system(("rm -Rf /etc/yum.repos.d/Centos-%s.repo" %(osver)))  
        if False==os.path.exists( ("/etc/yum.repos.d/CentOS%s-Base-163.repo" \
            %(osver)) ) and \
            0!=os.system( ("wget -O /etc/yum.repos.d/CentOS%s-Base-163.repo "\
                "http://mirrors.163.com/.help/CentOS%s-Base-163.repo" 
                %(osver, osver)) ):
            os.system( ("rm -Rf /etc/yum.repos.d/CentOS%s-Base-163.repo" 
                %(osver)) )
            os.system("mv /etc/yum.repos.d/CentOS-Base.repo.bark "\
                "/etc/yum.repos.d/CentOS-Base.repo")
            return "Download aliyun.repo failed"    
        #安装epel源
        os.system("yum erase -y epel-release.noarch")
        if False==os.path.exists( ("/etc/yum.repos.d/epel-%s.repo" %(osver)) ) or \
            0==os.path.getsize( ("/etc/yum.repos.d/epel-%s.repo" %(osver)) ):
            if 0!=os.system( ("wget -O /etc/yum.repos.d/epel-%s.repo "\
                "http://mirrors.aliyun.com/repo/epel-%s.repo" 
                %(osver, osver)) ):
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
def configGolang(go_proxy):
    #安装 golang
    szErr = installOrUpdateRpm("golang", platform.machine(), "")
    if 0 < len(szErr):
        return szErr
    #设置环境变量
    go_path = "/usr/local/go/gopath"
    if False == os.path.exists(go_path):
        os.system("mkdir -p %s" %go_path)
    szConfig,szErr = maker_public.readTxtFile("/etc/profile")
    if 0 < len(szErr):
        return szErr
    if None == re.search("\\nexport[ \\t]+GOPATH[ \\t]*=.*", szConfig):
        szConfig += ("\nexport GOPATH=%s" %go_path)
    else:
        szConfig = re.sub("\\nexport[ \\t]+GOPATH[ \\t]*=.*", \
            ("\nexport GOPATH=%s" %go_path),szConfig)
    if None == re.search("\\nexport[ \\t]+PATH[ \\t]*=[ \\t]*\\$PATH:\\$GOPATH/bin", \
        szConfig):
        szConfig += "\nexport PATH=$PATH:$GOPATH/bin"
    szErr = maker_public.writeTxtFile("/etc/profile", szConfig)
    if 0 < len(szErr):
        return szErr
    #安装工具
    szErr = maker_public.installGolangTools("go",go_proxy,go_path)
    if 0 < len(szErr):
        return szErr
    #
    return ""


#configPython 配置PYTHON；参数：无；返回：错误描述
def configPython(py_host,py_url):
    pyver = maker_public.getVer("python-centos")
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
    szErr = maker_public.configPip("python3", "pip3", py_host, py_url)
    if 0 < len(szErr):
        return szErr
    if ""==cur_pyver or cur_pyver<pyver:
        szErr = maker_public.configPip("python"+pyver, "pip3", py_host, py_url)
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


#installDPDK配置DPDK；参数：无；返回：错误描述
def installDPDK(complie_type):
    #安装libnuma-dev
    szErr = installOrUpdateRpm("numactl-devel", platform.machine(), "")
    if 0 < len(szErr):
        return szErr
    #安装pcre
    szErr = installOrUpdateRpm("pcre-devel", platform.machine(), "")
    if 0 < len(szErr):
        return szErr
    #安装openssl
    szErr = installOrUpdateRpm("openssl-devel", platform.machine(), "")
    if 0 < len(szErr):
        return szErr
    #安装zlib
    szErr = installOrUpdateRpm("zlib-devel", platform.machine(), "")
    if 0 < len(szErr):
        return szErr
    #安装pcap
    if 0 != os.system("dnf --enablerepo=PowerTools install -y libpcap-devel"):
        return "Can not install libpcap-devel"
    #安装libbpf
    #if 0 != os.system("dnf --enablerepo=PowerTools install -y libbpf-devel"):
    #    return "Can not install libpcap-devel"
    #安装ninja
    if 0 != os.system("pip3 install ninja"):
        return "Install ninja failed"
    #安装meson
    if 0 != os.system("pip3 install meson"):
        return "Install meson failed"
    #安装 DPDK
    return maker_public.buildDPDK(complie_type)


#installHYPERSCAN配置hyperscan；参数：无；返回：错误描述
def installHYPERSCAN():
    #安装cmake
    szErr = installOrUpdateRpm("cmake", platform.machine(), "")
    if 0 < len(szErr):
        return szErr
    #安装ragel
    ragel_ver = maker_public.getVer("ragel")
    if False == os.path.exists("./ragel-"+ragel_ver+".tar.gz"):
        if 0 != os.system("wget http://www.colm.net/files/ragel/ragel-"+ragel_ver+".tar.gz "\
            "-O ./ragel-"+ragel_ver+".tar.gz"):
            os.system("rm -f ./ragel-"+ragel_ver+".tar.gz")
            return "Failed to download ragel"
    if False == os.path.exists("/usr/local/ragel"):
        os.system("tar -xvf ./ragel-"+ragel_ver+".tar.gz  -C /tmp/")
        if 0 != os.system("cd /tmp/ragel-"+ragel_ver+" && ./configure --prefix=/usr/local/ragel "\
            "&& make -j $(nproc) && make install"):
            os.system("make uninstall")
            os.system("rm -Rf /tmp/ragel-"+ragel_ver)
            return "Failed to make hyperscan"
        os.system("ln -s /usr/local/ragel/bin/ragel /usr/local/bin/")
        os.system("rm -Rf /tmp/ragel-"+ragel_ver)
    #安装boost
    szErr = installOrUpdateRpm("boost-devel", platform.machine(), "")
    if 0 < len(szErr):
        return szErr
    #安装 HYPERSCAN
    return maker_public.buildHYPERSCAN()


#InitEnv 初始化环境；参数：无；返回：错误描述
def InitEnv(sys_par):
    par_dic = dict(sys_par)
    configGolang(par_dic["go_proxy"])
    configPython(par_dic["py_host"],par_dic["py_url"])
    return ""
    #释放yum资源
    releaseYum()
    #安装扩展库
    szErr = configRepo()
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
    szErr = configGolang(par_dic["go_proxy"])
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


#InitDPDK 配置DPDK；参数：编译类型；返回：错误描述
def ConfigDPDK(complie_type, szOperation):
    if "install" == szOperation:
        szErr = installDPDK(complie_type)
        if 0 < len(szErr):
            return("Config DPDK failed:%s" %(szErr))
        szErr = installHYPERSCAN()
        if 0 < len(szErr):
            return("Config HYPERSCAN failed:%s" %(szErr))
    else:
        maker_public.uninstallDPDK()
        os.system("rm -rf /usr/bin/ragel")
        os.system("rm -rf /usr/local/ragel")
    #
    return ""
