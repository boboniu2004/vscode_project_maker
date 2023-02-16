#!/usr/python/bin
# -*- coding: utf-8 -*-


import re
import os
import maker_public


#openRoot 打开root用户；参数：无；返回：错误描述
def releaseApt():
    os.system("killall -9 /usr/lib/apt/methods/http")
    return

#openRoot 打开root用户；参数：无；返回：错误描述
def openRoot():
    if 0 != os.system("passwd root"):
        return "Failed to change password of root"
    #修改第一个文件项
    szConfig, szErr = maker_public.readTxtFile("/usr/share/lightdm/lightdm.conf.d/50-ubuntu.conf")
    if 0 < len(szErr):
        return szErr
    if None==re.search("\n[ \\t]*greeter-show-manual-login[ \\t]*=[ \\t]*.+", szConfig) and \
        None==re.search("^[ \\t]*greeter-show-manual-login[ \\t]*=[ \\t]*.+", szConfig):
        szConfig += "\ngreeter-show-manual-login=true"
    if None==re.search("\n[ \\t]*all-guest[ \\t]*=[ \\t]*.+", szConfig) and \
        None==re.search("^[ \\t]*all-guest[ \\t]*=[ \\t]*.+", szConfig):
        szConfig += "\nall-guest=false"
    szErr = maker_public.writeTxtFile("/usr/share/lightdm/lightdm.conf.d/50-ubuntu.conf", szConfig)
    if 0 < len(szErr):
        return szErr
    #修改第二个文件项
    szConfig, szErr = maker_public.readTxtFile("/etc/pam.d/gdm-autologin")
    if 0 < len(szErr):
        return szErr
    szConfig = re.sub("\n[ \\t]*auth[ \\t]+required[ \\t]+pam_succeed_if.so[ \\t]+"\
        "user[ \\t]+!=[ \\t]+root[ \\t]+quiet_success", \
        "\n#auth required pam_succeed_if.so user != root quiet_success", szConfig)
    szConfig = re.sub("^[ \\t]*auth[ \\t]+required[ \\t]+pam_succeed_if.so[ \\t]+"\
        "user[ \\t]+!=[ \\t]+root[ \\t]+quiet_success", \
        "#auth required pam_succeed_if.so user != root quiet_success", szConfig)
    szErr = maker_public.writeTxtFile("/etc/pam.d/gdm-password", szConfig)
    if 0 < len(szErr):
        return szErr
    #修改第三个文件
    szConfig, szErr = maker_public.readTxtFile("/etc/pam.d/gdm-password")
    if 0 < len(szErr):
        return szErr
    szConfig = re.sub("\n[ \\t]*auth[ \\t]+required[ \\t]+pam_succeed_if.so[ \\t]+"\
        "user[ \\t]+!=[ \\t]+root[ \\t]+quiet_success", \
        "\n#auth required pam_succeed_if.so user != root quiet_success", szConfig)
    szConfig = re.sub("^[ \\t]*auth[ \\t]+required[ \\t]+pam_succeed_if.so[ \\t]+"\
        "user[ \\t]+!=[ \\t]+root[ \\t]+quiet_success", \
        "#auth required pam_succeed_if.so user != root quiet_success", szConfig)
    szErr = maker_public.writeTxtFile("/etc/pam.d/gdm-password", szConfig)
    if 0 < len(szErr):
        return szErr
    #修改第四个文件
    szConfig, szErr = maker_public.readTxtFile("/root/.profile")
    if 0 < len(szErr):
        return szErr
    if None==re.search("\n[ \\t]*tty[ \\t]+-s[ \\t]*&&[ \\t]*mesg[ \\t]+n[ \\t]+\\|\\|[ \\t]+.+", \
            szConfig) and \
        None==re.search("^[ \\t]*tty[ \\t]+-s[ \\t]*&&[ \\t]*mesg[ \\t]+n[ \\t]+\\|\\|[ \\t]+.+", \
            szConfig):
        szConfig = re.sub("\n[ \\t]*mesg[ \\t]+n[ \\t]+\\|\\|[ \\t]+.+", "\ntty -s&&mesg n || true", 
            szConfig)
        szConfig = re.sub("^[ \\t]*mesg[ \\t]+n[ \\t]+\\|\\|[ \\t]+.+", "\ntty -s&&mesg n || true", 
            szConfig)

    szErr = maker_public.writeTxtFile("/root/.profile", szConfig)
    if 0 < len(szErr):
        return szErr
    #
    return ""


#configDebSource配置扩展源；参数：os类型；返回：错误描述
def configDebSource(szOSName, deb_src):
    if "ubuntu" == szOSName:
        #获取Ubuntu的版本名称
        CodeNameObj = re.match("^Codename[ \\t]*\\:[ \\t]*([\\S]+)", \
            maker_public.execCmdAndGetOutput("lsb_release -c"))
        if None == CodeNameObj:
            return "Can not find codename!"
        szCodeName = CodeNameObj.group(1)
        #安装阿里源
        szAptSource = \
            ("deb %s %s main restricted universe multiverse\n"\
            "deb %s %s-security main restricted universe multiverse\n"\
            "deb %s %s-updates main restricted universe multiverse\n"\
            "deb %s %s-proposed main restricted universe multiverse\n"\
            "deb %s %s-backports main restricted universe multiverse\n"\
            "deb-src %s %s main restricted universe multiverse\n"\
            "deb-src %s %s-security main restricted universe multiverse\n"\
            "deb-src %s %s-updates main restricted universe multiverse\n"\
            "deb-src %s %s-proposed main restricted universe multiverse\n"\
            "deb-src %s %s-backports main restricted universe multiverse\n" \
            %(deb_src,szCodeName, deb_src,szCodeName, deb_src,szCodeName, \
              deb_src,szCodeName, deb_src,szCodeName, \
              deb_src,szCodeName, deb_src,szCodeName, deb_src,szCodeName, 
              deb_src,szCodeName, deb_src,szCodeName))
        #
        szErr = maker_public.writeTxtFile("/etc/apt/sources.list", szAptSource)
        if 0 < len(szErr):
            return szErr
    if "ubuntu" == szOSName:
        if 0 != os.system("apt-get update"):
            return "Update sources.list failed"
    else:
        os.system("apt-get update")
    return ""


#updateSystem 将系统升级到；参数：无；返回：错误描述
def updateSystem():
    #关闭防火墙
    os.system("systemctl stop ufw.service")
    if 0 != os.system("systemctl disable ufw.service"):
        return "Disable firewalld failed"
    if 0 != os.system("apt-get -y upgrade"):
        return "Update failed"
    os.system("apt-get -y autoremove libwayland-egl1-mesa")
    if 0 != os.system("apt-get -y install net-tools"):
        return "Install net-tools failed"
    if 0 != os.system("apt-get -y install curl"):
        return "Install curl failed"
    if 0 != os.system("apt-get -y install zip"):
        return "Install curl failed"
    return ""


#configGit 配置GIT；参数：无；返回：错误描述
def configGitSvn():
    if 0 != os.system("apt-get -y install git subversion"):
        return "Install git failed"
    #
    return ""


#configGcc 配置GCC；参数：无；返回：错误描述
def configGcc():
    if 0 != os.system("apt-get -y install gcc gdb"):
        return "Install gcc failed"
    return ""


#configGolang配置GOLANG；参数：无；返回：错误描述
def configGolang(go_proxy):
    gover = maker_public.getVer("go")
    gomac = "amd64"
    if "" != maker_public.execCmdAndGetOutput("lscpu | grep -E \"aarch64\""):
        gomac = "arm64"
    #安装 golang
    if False == os.path.exists("./go"+gover+".linux-"+gomac+".tar.gz"):
        if 0 != os.system("wget https://studygolang.com/dl/golang/go"+gover+".linux-"+gomac+".tar.gz"):
            return "Failed to download go"+gover
    if -1 == maker_public.execCmdAndGetOutput(\
        "su -c \"/usr/local/go/bin/go version\"").find("go"+gover):
        os.system("rm -Rf /usr/local/go")
        if 0 != os.system("tar -C /usr/local -zxvf ./go"+gover+".linux-"+gomac+".tar.gz"):
            return "Failed to uncompress go"+gover
    #设置环境变量
    go_path = "/usr/local/go/gopath"
    if False == os.path.exists(go_path):
        os.system("mkdir -p %s" %go_path)
    os.system("rm -rf ~/go")
    szConfig,szErr = maker_public.readTxtFile("/etc/profile")
    if 0 < len(szErr):
        return szErr
    if None == re.search("\\nexport[ \\t]+GOPATH[ \\t]*=.*", szConfig):
        szConfig += ("\nexport GOPATH=%s" %go_path)
    else:
        szConfig = re.sub("\\nexport[ \\t]+GOPATH[ \\t]*=.*", \
            ("\nexport GOPATH=%s" %go_path),szConfig)
    if None == re.search("\\nexport[ \\t]+PATH[ \\t]*=[ \\t]*\\$PATH:\\$GOPATH/bin.*", \
        szConfig):
        szConfig += "\nexport PATH=$PATH:$GOPATH/bin:/usr/local/go/bin"
    else:
        szConfig = re.sub("\\nexport[ \\t]+PATH[ \\t]*=[ \\t]*\\$PATH:\\$GOPATH/bin.*", \
            "\nexport PATH=$PATH:$GOPATH/bin:/usr/local/go/bin",szConfig)
    szErr = maker_public.writeTxtFile("/etc/profile", szConfig)
    if 0 < len(szErr):
        return szErr
    #安装工具
    szErr = maker_public.installGolangTools("/usr/local/go/bin/go", go_proxy,go_path)
    if 0 < len(szErr):
        return szErr
    #
    return ""


#configPython 配置PYTHON；参数：OS版本；返回：错误描述
def configPython(py_host, py_url):
    if 0 != os.system("apt-get -y install python3"):
        return "Install python3 failed"
    if 0 != os.system("apt-get -y install python3-pip"):
        return "Install  python3-pip failed"
    #获取python版本
    pyver = maker_public.getVer("python")
    match_lst = re.search("(\\d+\\.\\d+)\\.\\d+", \
        maker_public.execCmdAndGetOutput("python3 --version"))
    if None == match_lst:
        cur_pyver = ""
    else:
        cur_pyver = match_lst.group(1)
    if ""==cur_pyver or cur_pyver<pyver:
        if 0 != os.system("apt-get install -y python%s" %pyver):
            return ("Install python%s failed" %pyver)
    #配置PIP
    szErr = maker_public.configPip("python3", "pip3", py_host, py_url)
    if 0 < len(szErr):
        return szErr
    if ""==cur_pyver or cur_pyver<pyver:
        szErr = maker_public.configPip("python"+pyver, "pip3", py_host, py_url)
        if 0 < len(szErr):
            return szErr
    return ""


#configJava 配置JAVA；参数：无；返回：错误描述
def configJava():
    #安装JDK
    if 0 != os.system("apt-get -y install openjdk-"+maker_public.getVer("java")+\
        "-jdk-headless"):
        return "Install openjdk-11 failed"
    #返回
    return ""


#configCompletion 配置自动补齐；参数：无；返回：错误描述
def configCompletion():
    #配置
    szConfig,szErr = maker_public.readTxtFile("/etc/bash.bashrc")
    if 0 < len(szErr):
        return szErr
    szConfig = szConfig.replace("#if ! shopt -oq posix; then\n"
        "#  if [ -f /usr/share/bash-completion/bash_completion ]; then\n"
        "#    . /usr/share/bash-completion/bash_completion\n"
        "#  elif [ -f /etc/bash_completion ]; then\n"
        "#    . /etc/bash_completion\n"
        "#  fi\n"
        "#fi\n", 
        "if ! shopt -oq posix; then\n"
        "  if [ -f /usr/share/bash-completion/bash_completion ]; then\n"
        "    . /usr/share/bash-completion/bash_completion\n"
        "  elif [ -f /etc/bash_completion ]; then\n"
        "    . /etc/bash_completion\n"
        "  fi\n"
        "fi\n")
    szErr = maker_public.writeTxtFile("/etc/bash.bashrc", szConfig)
    if 0 < len(szErr):
        return szErr
    return ""


#configSshd 配置SSHD；参数：无；返回：错误描述
def configSshd():
    #安装
    if 0 != os.system("apt-get -y install openssh-server"):
        return "Install openssh-server failed"
    #读取配置文件
    return maker_public.ConfigSshd()


#configInternalNet 配置内部网络；参数：内部网卡的名称，szIpAddr本机的IP地址；返回：错误描述
def configInternalNet(szEthEnName, szIpAddr):
    net_prefx = re.sub("\\.\\d+$", "", szIpAddr)
    if os.path.isfile("/etc/netplan/01-network-manager-all.yaml"):
        szConfig = \
            "# Let NetworkManager manage all devices on this system\n"+\
            "network:\n"\
            "  version: 2\n"\
            "  renderer: NetworkManager\n"\
            "  ethernets:\n"\
            "    "+szEthEnName+":\n"\
            "      addresses: ["+szIpAddr+"/24]\n"\
            "      dhcp4: no\n"\
            "      gateway4: "+net_prefx+".1\n"\
            "      nameservers:\n"\
            "        addresses: ["+net_prefx+".1]"
        #写入配置
        szErr = maker_public.writeTxtFile("/etc/netplan/01-network-manager-all.yaml", szConfig)
        if 0 < len(szErr):
            return szErr
        #生效配置
        os.system("netplan apply")
    else:
        szConfig = \
            "# interfaces(5) file used by ifup(8) and ifdown(8)\n"+\
            "auto lo\n"+\
            "iface lo inet loopback\n\n"+\
            "auto "+szEthEnName+"\n"+\
            "iface "+szEthEnName+" inet static\n"+\
            "address "+szIpAddr+"\n"+\
            "netmask 255.255.255.0\n"+\
            "gateway 192.168.137.1\n"+\
            "dns1 192.168.137.1\n"+\
            "route add -net 192.168.137.0/24 netmask 255.255.255.0 gw 192.168.137.1 "+szEthEnName+"\n"
        #写入配置
        szErr = maker_public.writeTxtFile("/etc/network/interfaces", szConfig)
        if 0 < len(szErr):
            return szErr
        #重启服务
        os.system("systemctl restart networking.service")
        szStatus = maker_public.execCmdAndGetOutput("systemctl status networking.service")
        print(szStatus)
    os.system("ifconfig")
    #
    return ""

#configWSLmodules 添加内核模块编译功能；参数：无；返回：错误描述
def configWSLmodules():
    vscode_project_maker = os.environ["HOME"]+"/vscode_project_maker"
    szOSName = maker_public.execCmdAndGetOutput("uname -r")
    match_ret = re.match("([\d\\.]+)-", szOSName)
    if None == match_ret:
        return "Can not get WSL kernel version"
    #安装依赖包
    if 0 != os.system("apt-get -y install build-essential flex bison libssl-dev libelf-dev dwarves"):
        return "Install build-essential flex bison libssl-dev libelf-dev failed"
    #下载内核，这里不用download_src函数替代的原因是因为库太大，用git下载太慢。
    if False == os.path.isfile(vscode_project_maker+"/linux-msft-wsl-"+match_ret.group(1)+".zip"):
        if 0 != os.system("wget https://ghproxy.com/github.com/microsoft/"\
            "WSL2-Linux-Kernel/archive/refs/tags/linux-msft-wsl-"+match_ret.group(1)+\
            ".zip -O "+vscode_project_maker+"/linux-msft-wsl-"+match_ret.group(1)+".zip"):
            os.system("rm -rf "+vscode_project_maker+"/linux-msft-wsl-"+match_ret.group(1)+".zip")
            return "failed to download linux-msft-wsl-"+match_ret.group(1)+".zip"
    if False == os.path.isdir("/usr/src/WSL2-Linux-Kernel-linux-msft-wsl-"+match_ret.group(1)):
        #删除旧版本的数据
        os.system("rm -rf /usr/src/WSL2-Linux-Kernel-linux-msft-wsl*")
        if 0 != os.system("unzip -d /usr/src/ "+
            vscode_project_maker+"/linux-msft-wsl-"+match_ret.group(1)+".zip"):
            return "Failed to unzip "+vscode_project_maker+"/linux-msft-wsl-"+match_ret.group(1)+".zip"        
    if False == os.path.isdir("/lib/modules/"+match_ret.group(1)+"-microsoft-standard-WSL2"):
        #删除旧版本的数据
        os.system("rm -rf /lib/modules/*-microsoft-standard-WSL2")
        #编译内核
        if 0 != os.system("cd /usr/src/WSL2-Linux-Kernel-linux-msft-wsl-"+match_ret.group(1)+" && zcat /proc/config.gz > .config "\
            "&& make -j $(nproc) scripts && make -j $(nproc) modules && make -j $(nproc) modules_install && make clean"):
            os.system("rm -rf /lib/modules/"+match_ret.group(1)+"-microsoft-standard-WSL2")
            return "Failed to make kmod"
    return ""


#InitEnv 初始化环境；参数：参数字典；返回：错误描述
def InitEnv(sys_par):
    par_dic = dict(sys_par)
    szOSName = maker_public.getOSName()
    #释放apt资源
    releaseApt()
    #打开ROOT
    if "ubuntu" == szOSName and "online" == par_dic["work_mod"]:
        szErr = openRoot()
        if 0 < len(szErr):
            return("Config Ubuntu failed:%s" %(szErr))
    #初始化源
    szErr = configDebSource(szOSName, par_dic["deb_src"])
    if 0 < len(szErr):
        return("Config Ubuntu failed:%s" %(szErr))
    #将系统升级到最新版本
    szErr = updateSystem()
    if 0 < len(szErr):
        return("Config Ubuntu failed:%s" %(szErr))
    #配置SSHD
    if "ubuntu" == szOSName and "online" == par_dic["work_mod"]:
        szErr = configSshd()
        if 0 < len(szErr):
            return("Config Ubuntu failed:%s" %(szErr))
    #安装GIT
    szErr = configGitSvn()
    if 0 < len(szErr):
        return("Config Ubuntu failed:%s" %(szErr))
    #安装GCC
    szErr = configGcc()
    if 0 < len(szErr):
        return("Config Ubuntu failed:%s" %(szErr))
    #安装GOLANG
    szErr = configGolang(par_dic["go_proxy"])
    if 0 < len(szErr):
        return("Config Ubuntu failed:%s" %(szErr))
    #安装PYTHON和PIP
    szErr = configPython(par_dic["py_host"],par_dic["py_url"])
    if 0 < len(szErr):
        return("Config Ubuntu failed:%s" %(szErr))
    #安装JAVA
    szErr = configJava()
    if 0 < len(szErr):
        return("Config Ubuntu failed:%s" %(szErr))
    #配置自动补齐
    szErr = configCompletion()
    if 0 < len(szErr):
        return("Config Ubuntu failed:%s" %(szErr))
    #关闭图形界面
    if "ubuntu" == szOSName and "online" == par_dic["work_mod"]:
        if 0 != os.system("systemctl set-default multi-user.target"):
            return("Config Ubuntu failed: can not disable GNOME")
    #配置内部网络
    if "ubuntu" == szOSName and "online" == par_dic["work_mod"]:
        szErr = configInternalNet("eth1", par_dic["ip"])
        if 0 < len(szErr):
            return("Config CentOS failed:%s" %(szErr))
    if "ubuntu-wsl2" == szOSName and "online" == par_dic["work_mod"]:
        szErr = configWSLmodules()
        if 0 < len(szErr):
            return("Config Ubuntu failed:%s" %(szErr))
    #
    return ""


#InitInternalNet 初始化内部网络；参数：内部网络的IP地址；返回：错误描述
def InitInternalNet(ip_addr):
    szErr = configInternalNet("eth1", ip_addr)
    if 0 < len(szErr):
        return("Config IP failed:%s" %(szErr))
    #
    return ""