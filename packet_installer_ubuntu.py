#!/usr/python/bin
# -*- coding: utf-8 -*-


import re
import os
import sys
import maker_public


#函数功能：打开root用户
#函数参数：无
#函数返回：错误描述
def OpenRoot():
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
    szConfig = re.sub("\n[ \\t]*auth[ \\t]+required[ \\t]+pam_succeed_if.so[ \\t]+user[ \\t]+!=[ \\t]+root[ \\t]+quiet_success", \
        "\n#auth required pam_succeed_if.so user != root quiet_success", szConfig)
    szConfig = re.sub("^[ \\t]*auth[ \\t]+required[ \\t]+pam_succeed_if.so[ \\t]+user[ \\t]+!=[ \\t]+root[ \\t]+quiet_success", \
        "#auth required pam_succeed_if.so user != root quiet_success", szConfig)
    szErr = maker_public.writeTxtFile("/etc/pam.d/gdm-password", szConfig)
    if 0 < len(szErr):
        return szErr
    #修改第三个文件
    szConfig, szErr = maker_public.readTxtFile("/etc/pam.d/gdm-password")
    if 0 < len(szErr):
        return szErr
    szConfig = re.sub("\n[ \\t]*auth[ \\t]+required[ \\t]+pam_succeed_if.so[ \\t]+user[ \\t]+!=[ \\t]+root[ \\t]+quiet_success", \
        "\n#auth required pam_succeed_if.so user != root quiet_success", szConfig)
    szConfig = re.sub("^[ \\t]*auth[ \\t]+required[ \\t]+pam_succeed_if.so[ \\t]+user[ \\t]+!=[ \\t]+root[ \\t]+quiet_success", \
        "#auth required pam_succeed_if.so user != root quiet_success", szConfig)
    szErr = maker_public.writeTxtFile("/etc/pam.d/gdm-password", szConfig)
    if 0 < len(szErr):
        return szErr
    #修改第四个文件
    szConfig, szErr = maker_public.readTxtFile("/root/.profile")
    if 0 < len(szErr):
        return szErr
    if None==re.search("\n[ \\t]*tty[ \\t]+-s[ \\t]*&&[ \\t]*mesg[ \\t]+n[ \\t]+\\|\\|[ \\t]+.+", szConfig) and \
        None==re.search("^[ \\t]*tty[ \\t]+-s[ \\t]*&&[ \\t]*mesg[ \\t]+n[ \\t]+\\|\\|[ \\t]+.+", szConfig):
        szConfig = re.sub("\n[ \\t]*mesg[ \\t]+n[ \\t]+\\|\\|[ \\t]+.+", "\ntty -s&&mesg n || true", szConfig)
        szConfig = re.sub("^[ \\t]*mesg[ \\t]+n[ \\t]+\\|\\|[ \\t]+.+", "\ntty -s&&mesg n || true", szConfig)

    szErr = maker_public.writeTxtFile("/root/.profile", szConfig)
    if 0 < len(szErr):
        return szErr
    #
    return ""


#函数功能：配置扩展源
#函数参数：无
#函数返回：错误描述
def ConfigDebSource():
    #获取Ubuntu的版本名称
    CodeNameObj = re.match("^Codename[ \\t]*\\:[ \\t]*([\\S]+)", maker_public.execCmdAndGetOutput("lsb_release -c"))
    if None == CodeNameObj:
        return "Can not find codename!"
    szCodeName = CodeNameObj[1]
    #安装网易源
    szAptSource = \
        "deb http://mirrors.163.com/ubuntu/ "+szCodeName+" main restricted universe multiverse\n"\
        "deb http://mirrors.163.com/ubuntu/ "+szCodeName+"-security main restricted universe multiverse\n"\
        "deb http://mirrors.163.com/ubuntu/ "+szCodeName+"-updates main restricted universe multiverse\n"\
        "deb http://mirrors.163.com/ubuntu/ "+szCodeName+"-proposed main restricted universe multiverse\n"\
        "deb http://mirrors.163.com/ubuntu/ "+szCodeName+"-backports main restricted universe multiverse\n"\
        "deb-src http://mirrors.163.com/ubuntu/ "+szCodeName+" main restricted universe multiverse\n"\
        "deb-src http://mirrors.163.com/ubuntu/ "+szCodeName+"-security main restricted universe multiverse\n"\
        "deb-src http://mirrors.163.com/ubuntu/ "+szCodeName+"-updates main restricted universe multiverse\n"\
        "deb-src http://mirrors.163.com/ubuntu/ "+szCodeName+"-proposed main restricted universe multiverse\n"\
        "deb-src http://mirrors.163.com/ubuntu/ "+szCodeName+"-backports main restricted universe multiverse\n"
    #
    szErr = maker_public.writeTxtFile("/etc/apt/sources.list", szAptSource)
    if 0 < len(szErr):
        return szErr
    if 0 != os.system("apt-get update"):
        return "Update sources.list failed"
    return ""


#函数功能：将系统升级到
#函数参数：无
#函数返回：错误描述
def UpdateSystem():
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
    return ""


#函数功能：配置GIT
#函数参数：无
#函数返回：错误描述
def ConfigGit():
    #if 0 != os.system("add-apt-repository ppa:git-core/ppa"):
    #    return "Install git failed"
    #if 0 != os.system("apt-get update"):
    #    return "Install git failed"
    if 0 != os.system("apt-get -y install git"):
        return "Install git failed"
    
    return ""


#函数功能：配置GCC
#函数参数：无
#函数返回：错误描述
def ConfigGcc():
    if 0 != os.system("apt-get -y install gcc"):
        return "Install gcc failed"
    return ""


#函数功能：配置GOLANG
#函数参数：无
#函数返回：错误描述
def ConfigGolang():
    #安装 golang
    if False == os.path.exists("./go1.13.6.linux-amd64.tar.gz"):
        if 0 != os.system("wget https://studygolang.com/dl/golang/go1.13.6.linux-amd64.tar.gz"):
            return "Failed to download golang1.13.6"
    if -1 == maker_public.execCmdAndGetOutput(\
        "su -c \"/usr/local/go/bin/go version\"").find("go1.13.6"):
        os.system("rm -Rf /usr/local/go")
        if 0 != os.system("tar -C /usr/local -zxvf ./go1.13.6.linux-amd64.tar.gz"):
            return "Failed to uncompress golang1.13.6"
        #设置环境变量
        szConfig,szErr = maker_public.readTxtFile("/etc/profile")
        if 0 < len(szErr):
            return szErr
        if None == re.search("\\nexport[ \\t]+GOPATH[ \\t]*=[ \\t]*\\/root/go", szConfig):
            szConfig += "\nexport GOPATH=/root/go"
        if None == re.search("\\nexport[ \\t]+PATH[ \\t]*=[ \\t]*\\$PATH:\\$GOPATH/bin:/usr/local/go/bin", szConfig):
            szConfig += "\nexport PATH=$PATH:$GOPATH/bin:/usr/local/go/bin"
        szErr = maker_public.writeTxtFile("/etc/profile", szConfig)
        if 0 < len(szErr):
            return szErr
    #安装工具
    szErr = maker_public.installGolangTools("/usr/local/go/bin/go")
    if 0 < len(szErr):
        return szErr
    #
    return ""


#函数功能：配置PYTHON
#函数参数：无
#函数返回：错误描述
def ConfigPython():
    if 0 != os.system("apt-get -y install python3"):
        return "Install python3 failed"
    if 0 != os.system("apt-get -y install python3-pip"):
        return "Install  python3-pip failed"
    #配置PIP
    szErr = maker_public.configPip("python3", "pip3")
    if 0 < len(szErr):
        return szErr
    return ""


#函数功能：配置JAVA
#函数参数：无
#函数返回：错误描述
def ConfigJava():
    #安装JDK
    if 0 != os.system("apt-get -y install openjdk-11-jdk-headless"):
        return "Install openjdk-11 failed"
    #返回
    return ""


#函数功能：配置PlanUML
#函数参数：无
#函数返回：错误描述
def ConfigPlanUML():
    #安装
    if 0 != os.system("apt-get -y install graphviz"):
        return "Install graphviz failed"
    return ""


#函数功能：配置SSHD
#函数参数：无
#函数返回：错误描述
def ConfigSshd():
    #安装
    if 0 != os.system("apt-get -y install openssh-server"):
        return "Install openssh-server failed"
    #读取配置文件
    return maker_public.ConfigSshd()


#函数功能：配置内部网络
#函数参数：内部网卡的名称，szIpAddr本机的IP地址
#函数返回：错误描述
def configInternalNet(szEthEnName, szIpAddr):
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
    os.system("systemctl status networking.service")
    os.system("ifconfig")
    #
    return ""

#函数功能：主函数
#函数参数：可执行文件全路径，启动时加入的参数
#函数返回：执行成功返回0，否则返回负值的错误码
if __name__ == "__main__":
    if 2<len(sys.argv) and "config_IP"==sys.argv[1]:
        szErr = configInternalNet("eth1", sys.argv[2])
        if 0 < len(szErr):
            print("Config IP failed:%s" %(szErr))
            exit(-1)
        exit(0)
    #打开ROOT
    szErr = OpenRoot()
    if 0 < len(szErr):
        print("Config Ubuntu failed:%s" %(szErr))
        exit(-1)
    #安装网易源
    szErr = ConfigDebSource()
    if 0 < len(szErr):
        print("Config Ubuntu failed:%s" %(szErr))
        exit(-1)
    #将系统升级到最新版本
    szErr = UpdateSystem()
    if 0 < len(szErr):
        print("Config Ubuntu failed:%s" %(szErr))
        exit(-1)
    #配置SSHD
    szErr = ConfigSshd()
    if 0 < len(szErr):
        print("Config Ubuntu failed:%s" %(szErr))
        exit(-1)
    #安装GIT
    szErr = ConfigGit()
    if 0 < len(szErr):
        print("Config Ubuntu failed:%s" %(szErr))
        exit(-1)
    #安装GCC
    szErr = ConfigGcc()
    if 0 < len(szErr):
        print("Config Ubuntu failed:%s" %(szErr))
        exit(-1)
    #安装GOLANG
    szErr = ConfigGolang()
    if 0 < len(szErr):
        print("Config Ubuntu failed:%s" %(szErr))
        exit(-1)
    #安装PYTHON和PIP
    szErr = ConfigPython()
    if 0 < len(szErr):
        print("Config Ubuntu failed:%s" %(szErr))
        exit(-1)
    #安装JAVA
    szErr = ConfigJava()
    if 0 < len(szErr):
        print("Config Ubuntu failed:%s" %(szErr))
        exit(-1)
    #配置PLANUML
    szErr = ConfigPlanUML()
    if 0 < len(szErr):
        print("Config CentOS failed:%s" %(szErr))
        exit(-1)
    #关闭图形界面
    if 0 != os.system("systemctl set-default multi-user.target"):
        print("Config Ubuntu failed: can not disable GNOME")
        exit(-1)
    #升级PIP
    if 0 != os.system("pip3 install --upgrade pip"):
        print ("Update PIP3 failed")
        exit(-1)
    #配置内部网络
    if 1 < len(sys.argv):
        szErr = configInternalNet("eth1", sys.argv[1])
        if 0 < len(szErr):
            print("Config CentOS failed:%s" %(szErr))
            exit(-1)
    #提示关机
    input("Config Ubuntu success.Please any key to reboot")
    os.system("reboot")
