#!/usr/python/bin
# -*- coding: utf-8 -*-


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


#函数功能：将数据写入一个文本文件
#函数参数：待写入的文件，待写入的内容
#函数返回：错误描述
def writeTxtFile(szDstFile, szData):
    try:
        CurFile = open(szDstFile, "w")
        CurFile.write(szData)
        CurFile.close()
    except:
        return ("Exception while try to writing %s"  %(szDstFile))
    return ""


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


#函数功能：安装golang工i具
#函数参数：GO可执行程序位置
#函数返回：错误描述
def installGolangTools(szGo):
    #在gopath下安装x/tools
    os.system("su -c \"mkdir -p ~/go/bin\"")
    os.system("su -c \"mkdir -p ~/go/src/golang.org/x\"")
    os.system("su -c \"mkdir -p ~/go/pkg\"")
    if False == os.path.isdir(os.environ["HOME"]+"/go/src/golang.org/x/tools"):
        os.system("su -c \"rm -Rf ~/go/src/golang.org/x/tools\"")
        if 0 != os.system("su -c \"git clone https://github.com/golang/tools.git "\
            "~/go/src/golang.org/x/tools\""):
            return "Failed to download tools"
    if False == os.path.isdir(os.environ["HOME"]+"/go/src/golang.org/x/lint"):
        os.system("su -c \"rm -Rf ~/go/src/golang.org/x/lint\"")
        if 0 != os.system("su -c \"git clone https://github.com/golang/lint.git "\
            "~/go/src/golang.org/x/lint\""):
            return "Failed to download lint"
    if False == os.path.isdir(os.environ["HOME"]+"/go/src/golang.org/x/mod"):
        os.system("su -c \"rm -Rf ~/go/src/golang.org/x/mod\"")
        if 0 != os.system("su -c \"git clone https://github.com/golang/mod.git "\
            "~/go/src/golang.org/x/mod\""):
            return "Failed to download mod"
    if False == os.path.isdir(os.environ["HOME"]+"/go/src/golang.org/x/xerrors"):
        os.system("su -c \"rm -Rf ~/go/src/golang.org/x/xerrors\"")
        if 0 != os.system("su -c \"git clone https://github.com/golang/xerrors.git "\
            "~/go/src/golang.org/x/xerrors\""):
            return "Failed to download xerrors"
    if False == os.path.isdir(os.environ["HOME"]+"/go/src/golang.org/x/sync"):
        os.system("su -c \"rm -Rf ~/go/src/golang.org/x/sync\"")
        if 0 != os.system("su -c \"git clone https://github.com/golang/sync.git "\
            "~/go/src/golang.org/x/sync\""):
            return "Failed to download sync"
    #安装go-outline
    os.system("su -c \""+szGo+" get -v github.com/ramya-rao-a/go-outline\"")
    #安装go-find-references
    os.system("su -c \""+szGo+" get -v github.com/lukehoban/go-find-references\"")
    #安装gocode
    os.system("su -c \""+szGo+" get -v github.com/mdempsky/gocode\"")
    #安装gopkgs
    os.system("su -c \""+szGo+" get -v github.com/uudashr/gopkgs/cmd/gopkgs\"")
    #安装godef
    os.system("su -c \""+szGo+" get -v github.com/rogpeppe/godef\"")
    #安装goreturns
    os.system("su -c \""+szGo+" get -v sourcegraph.com/sqs/goreturns\"")
    #安装gorename
    os.system("su -c \""+szGo+" get -v golang.org/x/tools/cmd/gorename\"")
    #安装go-symbols
    os.system("su -c \""+szGo+" get -v github.com/newhook/go-symbols\"")
    #安装gopls
    os.system("su -c \""+szGo+" get -v golang.org/x/tools/gopls\"")
    #安装dlv
    os.system("su -c \""+szGo+" get -v github.com/go-delve/delve/cmd/dlv\"")
    #安装goimports
    os.system("su -c \""+szGo+" get -v golang.org/x/tools/cmd/goimports\"")
    #安装guru
    os.system("su -c \""+szGo+" get -v golang.org/x/tools/cmd/guru\"")
    #安装golint
    os.system("su -c \""+szGo+" get -v golang.org/x/lint/golint\"")
    #安装gotests
    os.system("su -c \""+szGo+" get -v github.com/cweill/gotests\"")
    #安装gomodifytags
    os.system("su -c \""+szGo+" get -v github.com/fatih/gomodifytags\"")
    #安装impl
    os.system("su -c \""+szGo+" get -v github.com/josharian/impl\"")
    #安装fillstruct
    os.system("su -c \""+szGo+" get -v github.com/davidrjenni/reftools/cmd/fillstruct\"")
    #安装goplay
    os.system("su -c \""+szGo+" get -v github.com/haya14busa/goplay/cmd/goplay\"")
    #安装godoctor
    os.system("su -c \""+szGo+" get -v github.com/godoctor/godoctor\"")
    #
    return ""
    

#函数功能：配置PIP
#函数参数：python可执行文件和PIP可执行文件
#函数返回：错误描述
def configPip(szPython, szPip):
    #添加网易源
    if 0 != os.system("su -c \"mkdir -p ~/.pip\""):
        return "Add PIP source failed"
    os.system("su -c \"rm -rf ~/.pip/pip.conf\"")
    if 0 != os.system("su -c \" echo \\\"[global]\ntimeout = 6000\nindex-url = "\
        "https://mirrors.163.com/pypi/simple/\ntrusted-host =mirrors.163.com\\\" >> ~/.pip/pip.conf\""):
        return "Failed to writr pip.conf"
    #安装pylint
    if 0 != os.system("su -c \""+szPython+" -m pip install -U \\\"pylint<2.0.0\\\" --user\""):
        return "Update Pylint failed"
    #升级PIP
    if 0 != os.system("su -c \""+szPip+" install --upgrade pip\""):
        return "Update PIP failed"
    #
    return ""


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