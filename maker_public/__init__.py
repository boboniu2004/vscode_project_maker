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
    #设置GO模块代理
    if 0 != os.system("su -c \""+szGo+" env -w GO111MODULE=on\""):
        return "Set GO111MODULE=on failed"
    if 0 != os.system("su -c \""+szGo+" env -w GOPROXY=\\\"https://goproxy.io,direct\\\"\""):
        return "Set GOPROXY failed"
    os.system("su -c \""+szGo+" env\"")
    #安装go-outline
    os.system("su -c \""+szGo+" get -v -u github.com/ramya-rao-a/go-outline\"")
    #安装go-find-references
    os.system("su -c \""+szGo+" get -v -u github.com/lukehoban/go-find-references\"")
    #安装gocode
    os.system("su -c \""+szGo+" get -v -u github.com/mdempsky/gocode\"")
    #安装gopkgs
    os.system("su -c \""+szGo+" get -v -u github.com/uudashr/gopkgs/cmd/gopkgs\"")
    #安装godef
    os.system("su -c \""+szGo+" get -v -u github.com/rogpeppe/godef\"")
    #安装goreturns
    os.system("su -c \""+szGo+" get -v -u sourcegraph.com/sqs/goreturns\"")
    #安装gorename
    os.system("su -c \""+szGo+" get -v -u golang.org/x/tools/cmd/gorename\"")
    #安装go-symbols
    os.system("su -c \""+szGo+" get -v -u github.com/newhook/go-symbols\"")
    #安装gopls
    os.system("su -c \""+szGo+" get -v -u golang.org/x/tools/gopls\"")
    #安装dlv
    os.system("su -c \""+szGo+" get -v -u github.com/go-delve/delve/cmd/dlv\"")
    #安装goimports
    os.system("su -c \""+szGo+" get -v -u golang.org/x/tools/cmd/goimports\"")
    #安装guru
    os.system("su -c \""+szGo+" get -v -u golang.org/x/tools/cmd/guru\"")
    #安装golint
    os.system("su -c \""+szGo+" get -v -u golang.org/x/lint/golint\"")
    #安装gotests
    os.system("su -c \""+szGo+" get -v -u github.com/cweill/gotests\"")
    #安装gomodifytags
    os.system("su -c \""+szGo+" get -v -u github.com/fatih/gomodifytags\"")
    #安装impl
    os.system("su -c \""+szGo+" get -v -u github.com/josharian/impl\"")
    #安装fillstruct
    os.system("su -c \""+szGo+" get -v -u github.com/davidrjenni/reftools/cmd/fillstruct\"")
    #安装goplay
    os.system("su -c \""+szGo+" get -v -u github.com/haya14busa/goplay/cmd/goplay\"")
    #安装godoctor
    os.system("su -c \""+szGo+" get -v -u github.com/godoctor/godoctor\"")
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
        "http://mirrors.aliyun.com/pypi/simple/\ntrusted-host = mirrors.aliyun.com\\\" >> ~/.pip/pip.conf\""):
        return "Failed to writr pip.conf"
    #安装pylint
    if 0 != os.system("su -c \""+szPython+" -m pip install -U \\\"pylint\\\" --user\""):
        return "Update Pylint failed"
    #升级PIP
    #if 0 != os.system("su -c \""+szPip+" install --upgrade pip\""):
    #    return "Update PIP failed"
    #
    return ""


#函数功能：配置SSHD
#函数参数：无
#函数返回：错误描述
def ConfigSshd():
    #读取配置文件
    szSshdConf,szErr = readTxtFile("/etc/ssh/sshd_config")
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
    #打开root登陆
    szSshdConf = re.sub("\\n[ \\t]*PermitRootLogin.+", \
        "\nPermitRootLogin yes", szSshdConf)
    szSshdConf = re.sub("\\n[ \\t]*#[ \\t]*PermitRootLogin.+", \
        "\nPermitRootLogin yes", szSshdConf)
    #写入配置文件
    szErr = writeTxtFile("/etc/ssh/sshd_config", szSshdConf)
    if 0 < len(szErr):
        return szErr
    #重启服务
    if 0 != os.system("systemctl restart sshd"):
        return "restart sshd failed"
    return ""


#getOSName 获取操作系统名称；参数：无；返回：操作系统名称
def getOSName():
    #获取centos版本
    szOSName = execCmdAndGetOutput("rpm -q centos-release")
    if None != re.search("^centos\\-release\\-[\\d]+\\-[\\d]+\\.[\\d]+"+\
        "\\.[\\d]+\\.[^\\.]+\\.centos\\.[^\\.^\\s]+$", szOSName):
        return "centos"
    #获取ubuntu版本
    szOSName = execCmdAndGetOutput("lsb_release -a")
    if None != re.search("Distributor[ \\t]+ID[ \\t]*:[ \\t]+Ubuntu.*", szOSName):
        return "ubuntu"
    return ""


#buildDPDK 编译DPDK；参数：无；返回：错误码
def buildDPDK():
    #安装 DPDK
    if False == os.path.exists("./f-stack-1.21.zip"):
        if 0 != os.system("wget https://github.com/F-Stack/f-stack/archive/refs/tags/v1.21.zip "+
            "-O f-stack-1.21.zip"):
            return "Failed to download f-stack-1.21"
    if False == os.path.exists("/usr/local/dpdk"):
        #解压缩
        os.system("unzip -d /tmp/ ./f-stack-1.21.zip")
        #修改DPDK的dpdk-setup.sh
        dpdk_setup,sz_err = readTxtFile(
                "/tmp/f-stack-1.21/dpdk/usertools/dpdk-setup.sh")
        if "" != sz_err:
            os.system("rm -Rf /tmp/f-stack-1.21")
            return "config DPDK failed"
        dpdk_setup = re.sub("\n\tread[ \\t]+our_entry\n\t", 
            "\n\t#read our_entry\n\tour_entry=41\n\t", dpdk_setup)
        dpdk_setup = re.sub("\n\t\techo[ \\t]+-n[ \\t]+\"Press[ \\t]+enter[ \\t]+"
            "to[ \\t]+continue[ \\t]+...\";[ \\t]+read\n\t", 
            "\n\t\tquit\n\t", dpdk_setup)
        sz_err = writeTxtFile("/tmp/f-stack-1.21/dpdk/usertools/dpdk-setup.sh", 
            dpdk_setup)
        if "" != sz_err:
            os.system("rm -Rf /tmp/f-stack-1.21")
            return "config DPDK failed"
        #编译安装DPDK
        pwd_dir = os.getcwd()
        try:
            os.chdir("/tmp/f-stack-1.21/dpdk/usertools")
            if 0 != os.system("./dpdk-setup.sh"):
                os.chdir(pwd_dir)
                os.system("rm -Rf /tmp/f-stack-1.21")
                return "config DPDK failed"
            os.chdir("/tmp/f-stack-1.21/dpdk/x86_64-native-linuxapp-gcc")
            if 0 != os.system("make install prefix=/usr/local/dpdk"):
                os.chdir(pwd_dir)
                os.system("rm -Rf /tmp/f-stack-1.21")
                return "config DPDK failed"
            if 0 != os.system("cp -r ./kmod /usr/local/dpdk/"):
                os.chdir(pwd_dir)
                os.system("rm -Rf /tmp/f-stack-1.21")
                return "config DPDK failed"
            #移动头文件
            if True == os.path.isdir("/usr/local/dpdk/include/dpdk"):
                os.system("rm -Rf /usr/local/dpdk/include-dpdk")
                os.rename("/usr/local/dpdk/include/dpdk", "/usr/local/dpdk/include-dpdk")
                os.system("rm -Rf /usr/local/dpdk/include")
                os.rename("/usr/local/dpdk/include-dpdk", "/usr/local/dpdk/include")
        finally:
            os.chdir(pwd_dir)
        os.system("rm -Rf /tmp/f-stack-1.21")
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
    return ""
