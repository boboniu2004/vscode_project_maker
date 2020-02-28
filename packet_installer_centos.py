#!/usr/python/bin
# -*- coding: utf-8 -*-


import re
import os
import sys
import maker_public


#函数功能：检查rpm包的版本，并且尝试安装该包
#函数参数：rpm包名称，机器版本
#函数返回：错误描述
def installOrUpdateRpm(szRpmName, szMacVer, szRpmPath):
    #获取RPM包的安装信息
    os.system("rm -f /tmp/vscode_tmp")
    os.system("yum list installed | grep -E \""+szRpmName+"\\."+szMacVer+"\" >> /tmp/vscode_tmp")
    szRpmInfo,_ = maker_public.readTxtFile("/tmp/vscode_tmp")
    szRpmInfoArr = szRpmInfo.split("\n")
    InstalledMatchList = None
    for szCurRpm in szRpmInfoArr:
        InstalledMatchList = re.match("^"+szRpmName+"\\."+szMacVer+\
            "[\\s]{1,}([^\\s]{1,})[\\s]{1,}[^\\s]{1,}", szCurRpm)
        if None != InstalledMatchList:
            break
    os.system("rm -f /tmp/vscode_tmp")
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


#函数功能：将系统升级到
#函数参数：无
#函数返回：错误描述
def UpdateSystem():
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
    return ""


#函数功能：配置扩展源
#函数参数：无
#函数返回：错误描述
def ConfigRepo():
    #安装epel扩展库
    szErr = installOrUpdateRpm("epel-release", "noarch", "")
    if 0 < len(szErr):
        return szErr
    #安装WANGdisco
    os.system("rm -f /tmp/vscode_tmp")
    os.system("rpm -q centos-release >> /tmp/vscode_tmp")
    szCentOSVer,_ = maker_public.readTxtFile("/tmp/vscode_tmp")
    MatchList = re.match("^centos\\-release\\-([\\d]+)\\-[\\d]+\\.[\\d]+"+\
        "\\.[\\d]+\\.[^\\.]+\\.centos\\.[^\\.^\\s]+$", szCentOSVer)
    if None == MatchList:
        return ("Unknow OS:%s" %szCentOSVer)
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

#函数功能：配置GCC
#函数参数：无
#函数返回：错误描述
def ConfigGcc():
    return installOrUpdateRpm("gcc", "x86_64", "")


#函数功能：配置GOLANG
#函数参数：无
#函数返回：错误描述
def ConfigGolang():
    #安装 golang
    szErr = installOrUpdateRpm("golang", "x86_64", "")
    if 0 < len(szErr):
        return szErr
    #在gopath下安装x/tools
    os.system("mkdir -p ~/go/bin")
    os.system("mkdir -p ~/go/src/golang.org/x")
    os.system("mkdir -p ~/go/pkg")
    os.system("rm -Rf ~/go/src/golang.org/x/tools")
    os.system("rm -Rf ~/go/src/golang.org/x/lint")
    os.system("rm -Rf ~/go/src/golang.org/x/mod")
    os.system("rm -Rf ~/go/src/golang.org/x/xerrors")
    os.system("rm -Rf ~/go/src/golang.org/x/sync")
    if 0 != os.system("git clone https://github.com/golang/tools.git ~/go/src/golang.org/x/tools"):
        return "Failed to download tools"
    if 0 != os.system("git clone https://github.com/golang/lint.git ~/go/src/golang.org/x/lint"):
        return "Failed to download lint"
    if 0 != os.system("git clone https://github.com/golang/mod.git ~/go/src/golang.org/x/mod"):
        return "Failed to download mod"
    if 0 != os.system("git clone https://github.com/golang/xerrors.git ~/go/src/golang.org/x/xerrors"):
        return "Failed to download xerrors"
    if 0 != os.system("git clone https://github.com/golang/sync.git ~/go/src/golang.org/x/sync"):
        return "Failed to download sync"
    #安装go-outline
    os.system("go get -v github.com/ramya-rao-a/go-outline")
    #安装go-find-references
    os.system("go get -v github.com/lukehoban/go-find-references")
    #安装gocode
    os.system("go get -v github.com/mdempsky/gocode")
    #安装gopkgs
    os.system("go get -v github.com/uudashr/gopkgs/cmd/gopkgs")
    #安装godef
    os.system("go get -v github.com/rogpeppe/godef")
    #安装goreturns
    os.system("go get -v sourcegraph.com/sqs/goreturns")
    #安装gorename
    os.system("go get -v golang.org/x/tools/cmd/gorename")
    #安装go-symbols
    os.system("go get -v github.com/newhook/go-symbols")
    #安装gopls
    os.system("go get -v golang.org/x/tools/gopls")
    #安装dlv
    os.system("go get -v github.com/go-delve/delve/cmd/dlv")
    #安装goimports
    os.system("go get -v golang.org/x/tools/cmd/goimports")
    #安装guru
    os.system("go get -v golang.org/x/tools/cmd/guru")
    #安装golint
    os.system("go get -v golang.org/x/lint/golint")
    #安装gotests
    os.system("go get -v github.com/cweill/gotests")
    #安装gomodifytags
    os.system("go get -v github.com/fatih/gomodifytags")
    #安装impl
    os.system("go get -v github.com/josharian/impl")
    #安装fillstruct
    os.system("go get -v github.com/davidrjenni/reftools/cmd/fillstruct")
    #安装goplay
    os.system("go get -v github.com/haya14busa/goplay/cmd/goplay")
    #安装godoctor
    os.system("go get -v github.com/godoctor/godoctor")
    #
    return ""


#函数功能：配置PYTHON
#函数参数：无
#函数返回：错误描述
def ConfigPython():
    szErr = installOrUpdateRpm("python", "x86_64", "")
    if 0 < len(szErr):
        return szErr
    szErr = installOrUpdateRpm("python2-pip", "noarch", "")
    if 0 < len(szErr):
        return szErr
    #添加网易源
    if 0 != os.system("mkdir -p ~/.pip"):
        return "Add PIP source failed"
    os.system("rm -rf ~/.pip/pip.conf")
    if 0 != os.system("echo \"[global]\nindex-url = https://mirrors.163.com/pypi/simple/\" >> ~/.pip/pip.conf"):
        return szErr
    #安装pylint
    if 0 != os.system("python -m pip install -U \"pylint<2.0.0\" --user"):
        return "Update Pylint failed"
    #升级PIP
    if 0 != os.system("pip install --upgrade pip"):
        return "Update PIP failed"
    return ""


#函数功能：配置JAVA
#函数参数：无
#函数返回：错误描述
def ConfigJava():
    szCurWorkPath = os.path.dirname(os.path.realpath(sys.argv[0]))
    print("First：Please download JDK for https://www.oracle.com/java/technologies/javase-downloads.html.")
    print("Second: Move the RPM filr to %s." %(szCurWorkPath))
    raw_input("Last: Press any key to continue...")
    #获取JDKRPM包的名称
    szJdkRpm = ""
    szJdkName = ""
    FileList = os.listdir(os.path.dirname(os.path.realpath(sys.argv[0])))
    for szCurFile in FileList:
        if None != re.search("jdk\\-.+_linux\\-x64_bin\\.rpm", szCurFile):
            szJdkRpm = str(os.path.dirname(os.path.realpath(sys.argv[0]))+"/"+szCurFile)
            szJdkName = str(re.sub("_linux\\-x64_bin\\.rpm", "", szCurFile))
            break
    if 0 >= len(szJdkRpm):
        return "Can not find any file like jdk_xx.xx.xx_linux-x64_bin.rpm"
    #安装RPM包
    szErr = installOrUpdateRpm(szJdkName, "x86_64", szJdkRpm)
    if 0 < len(szErr):
        return szErr
    #设置配置文件
    szProFileConf,szErr = maker_public.readTxtFile("/etc/profile")
    if 0 < len(szErr):
        return szErr
    if None == re.search("\\nexport[ \\t]+JAVA_HOME[ \\t]*=.+", szProFileConf):
        szProFileConf += "\n\nexport JAVA_HOME=/usr/java/"+szJdkName
    else:
        szProFileConf = re.sub("\\nexport[ \\t]+JAVA_HOME[ \\t]*=.+", \
            "\nexport JAVA_HOME=/usr/java/"+szJdkName, szProFileConf)
    szErr = maker_public.writeTxtFile("/etc/profile", szProFileConf)
    if 0 < len(szErr):
        return szErr
    #返回
    return ""
    
    


#函数功能：配置GIT
#函数参数：无
#函数返回：错误描述
def ConfigGit():
    return installOrUpdateRpm("git", "x86_64", "")


#函数功能：配置SSHD
#函数参数：无
#函数返回：错误描述
def ConfigSshd():
    #读取配置文件
    szSshdConf,szErr = maker_public.readTxtFile("/etc/ssh/sshd_config")
    if 0 < len(szErr):
        return szErr
    #修正配置文件内容
    #
    szSshdConf = re.sub("\\n[ \\t]*PubkeyAuthentication.+", \
        "\nPubkeyAuthentication yes", szSshdConf)
    szSshdConf = re.sub("\\n[ \\t]*#[ \\t]*PubkeyAuthentication.+", \
        "\nPubkeyAuthentication yes", szSshdConf)
    #
    szSshdConf = re.sub("\\n[ \\t]*AllowTcpForwarding.+", \
        "\nAllowTcpForwarding yes", szSshdConf)        
    szSshdConf = re.sub("\\n[ \\t]*#[ \\t]*AllowTcpForwarding.+", \
        "\nAllowTcpForwarding yes", szSshdConf)
    #
    szSshdConf = re.sub("\\n[ \\t]*AuthorizedKeysFile.+", \
        "\nAuthorizedKeysFile .ssh/authorized_keys", szSshdConf)
    szSshdConf = re.sub("\\n[ \\t]*#[ \\t]*AuthorizedKeysFile.+", \
        "\nAuthorizedKeysFile .ssh/authorized_keys", szSshdConf)
    #写入配置文件
    szErr = maker_public.writeTxtFile("/etc/ssh/sshd_config", szSshdConf)
    if 0 < len(szErr):
        return szErr
    #重启服务
    if 0 != os.system("systemctl restart sshd"):
        return "restart sshd failed"
    return ""


#函数功能：主函数
#函数参数：可执行文件全路径，启动时加入的参数
#函数返回：执行成功返回0，否则返回负值的错误码
if __name__ == "__main__":
    #安装扩展库
    szErr = ConfigRepo()
    if 0 < len(szErr):
        print("Config CentOS failed:%s" %(szErr))
        exit(-1)
    #将系统升级到最新版本
    szErr = UpdateSystem()
    if 0 < len(szErr):
        print("Config CentOS failed:%s" %(szErr))
        exit(-1)
    #安装GCC
    szErr = ConfigGcc()
    if 0 < len(szErr):
        print("Config CentOS failed:%s" %(szErr))
        exit(-1)
    #安装GOLANG
    szErr = ConfigGolang()
    if 0 < len(szErr):
        print("Config CentOS failed:%s" %(szErr))
        exit(-1)
    #安装PYTHON和PIP
    szErr = ConfigPython()
    if 0 < len(szErr):
        print("Config CentOS failed:%s" %(szErr))
        exit(-1)
    #安装JAVA
    szErr = ConfigJava()
    if 0 < len(szErr):
        print("Config CentOS failed:%s" %(szErr))
        exit(-1)
    #安装GIT
    szErr = ConfigGit()
    if 0 < len(szErr):
        print("Config CentOS failed:%s" %(szErr))
        exit(-1)
    #配置SSHD
    szErr = ConfigSshd()
    if 0 < len(szErr):
        print("Config CentOS failed:%s" %(szErr))
        exit(-1)
    #关闭图形界面
    if 0 != os.system("systemctl set-default multi-user.target"):
        print("Config CentOS failed: can not disable GNOME")
        exit(-1)
    #升级PIP
    if 0 != os.system("pip install --upgrade pip"):
        print ("Update PIP failed")
        exit(-1)
    #提示关机
    raw_input("Config CentOS success.Please any key to reboot")
    os.system("reboot")
