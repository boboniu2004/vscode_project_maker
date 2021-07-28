#!/usr/python/bin
# -*- coding: utf-8 -*-


import os
import re
import multiprocessing


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
    else:
        szOSName,sz_err = readTxtFile("/etc/redhat-release")
        if ""==sz_err and None!=re.search(
            "CentOS[ \\t]+Linux[ \\t]+release[ \\t]+\\d+\\.\\d+\\.\\d+", szOSName):
            return "centos"
    #获取ubuntu版本
    szOSName = execCmdAndGetOutput("lsb_release -a")
    if None != re.search("Distributor[ \\t]+ID[ \\t]*:[ \\t]+Ubuntu.*", szOSName):
        return "ubuntu"
    return ""

#get_kernel_ver 获取内核版本；参数：无；返回：操作系统内核的版本
def get_kernel_ver():
    szOSName = execCmdAndGetOutput("uname -r")
    match_ret = re.match("^(\\d+)\\.(\\d+)\\.(\\d+)\\-\\d+", szOSName)
    if None == match_ret:
        return None, None, None
    return int(match_ret[1]),int(match_ret[2]),int(match_ret[3])
    

#issame_kernel_ver 比较编译时的内额内核版本和当前的内核版本是否一致；
# 参数：dpdk_path安装目录；返回：bool变量
def issame_kernel_ver(dpdk_path):
    ker_ver_build,sz_err = readTxtFile(dpdk_path+"/kernel_verion")
    if ""!=sz_err or ""==ker_ver_build:
        return False
    ker_ver_cur = execCmdAndGetOutput("uname -r")
    if ker_ver_build!=ker_ver_cur:
        print("ker_ver_build=%s,ker_ver_cur=%s" %(ker_ver_build, ker_ver_cur))
        return False
    return True

#build_normal_dpdk 编译普通版本的DPDK；参数：无；返回：错误描述
def build_normal_dpdk():
    if False==issame_kernel_ver("/usr/local/dpdk") or \
        False==os.path.exists("/usr/local/dpdk"):
        os.system("rm -Rf /usr/local/dpdk")
        #解压缩
        os.system("unzip -d /tmp/ ./f-stack-1.21.zip")
        #配置
        if 0 != os.system("cd /tmp/f-stack-1.21/dpdk && make defconfig"):
            os.system("rm -Rf /tmp/f-stack-1.21")
            return "config DPDK failed"
        #编译安装
        if 0 != os.system("cd /tmp/f-stack-1.21/dpdk && "\
            "make -j"+str(multiprocessing.cpu_count())+
            " && make install prefix=/usr/local/dpdk"):
            os.system("rm -Rf /tmp/f-stack-1.21")
            return "config DPDK failed"
        #设置
        dir_list = os.listdir("/usr/local/dpdk/include/dpdk")
        for cur_dir in dir_list:
            if "."==cur_dir or ".."==cur_dir:
                continue
            if os.path.islink("/usr/local/dpdk/include/dpdk/"+cur_dir):
                continue
            if "dpdk" == cur_dir:
                os.system("rm -Rf /tmp/f-stack-1.21")
                return "invaild path(dpdk)"
            if 0 != os.system("ln -s /usr/local/dpdk/include/dpdk/"+cur_dir+" "\
                "/usr/local/dpdk/include/"+cur_dir):
                os.system("rm -Rf /tmp/f-stack-1.21")
                return "config DPDK failed"
        if 0 != os.system("cp -rf /tmp/f-stack-1.21/dpdk/build/kmod /usr/local/dpdk/"):
            os.system("rm -Rf /tmp/f-stack-1.21")
            return "config DPDK failed"       
        os.system("rm -rf /usr/local/dpdk/kernel_verion && "\
            "uname -r >> /usr/local/dpdk/kernel_verion")
    return ""


#build_meson_dpdk 编译meson版本的DPDK；参数：无；返回：错误描述
def build_meson_dpdk():
    if False==issame_kernel_ver("/usr/local/dpdk-meson") or \
        False==os.path.exists("/usr/local/dpdk-meson"):
        os.system("rm -Rf /usr/local/dpdk-meson")
        #解压缩
        if False == os.path.exists("/tmp/f-stack-1.21"):
            os.system("unzip -d /tmp/ ./f-stack-1.21.zip")
        #编译安装meson版本
        if 0 != os.system("cd /tmp/f-stack-1.21/dpdk && "\
            "meson ./dpdk_build && cd ./dpdk_build && "\
            "meson configure -Dprefix=/usr/local/dpdk-meson "\
            "-Dibverbs_link=static -Ddefault_library=static"):
            os.system("rm -Rf /tmp/f-stack-1.21")
            return "config DPDK failed"
        if 0 != os.system("cd /tmp/f-stack-1.21/dpdk/dpdk_build && "\
            "ninja -j"+str(multiprocessing.cpu_count())+" && ninja install"):
            os.system("rm -Rf /tmp/f-stack-1.21")
            return "config DPDK failed"
        #设置
        if 0 != os.system("mkdir -p /usr/local/dpdk-meson/kmod && "\
            "cp -rf /tmp/f-stack-1.21/dpdk/dpdk_build/kernel/linux/*/*.ko "\
            "/usr/local/dpdk-meson/kmod"):
            os.system("rm -Rf /tmp/f-stack-1.21")
            return "config DPDK failed"  
        os.system("mkdir -p /usr/local/dpdk-meson/sbin")
        os.system("rm -rf /usr/local/dpdk-meson/kernel_verion && "\
            "uname -r >> /usr/local/dpdk-meson/kernel_verion")
    return ""


#install_pc_for_dpdk 为DPDK安装PC文件
def install_pc_for_dpdk():
    os.system("mkdir -p /usr/local/share/pkgconfig")
    if 0 != os.system("cp -rf /usr/local/dpdk-meson/lib/*/pkgconfig/* "\
        "/usr/local/share/pkgconfig/"):
        return "copy pkgconfig failed"
    dpdk_pc,sz_err = readTxtFile("/usr/local/share/pkgconfig/libdpdk.pc")
    if ""!=sz_err:
        return sz_err
    dpdk_pc = re.sub("-l:librte_.+\\.a ", "", dpdk_pc)
    dpdk_pc = re.sub("-L\\$\\{libdir\\}", "-L${libdir} -ldpdk", dpdk_pc)
    dpdk_pc = re.sub("/usr/local/dpdk-meson", "/usr/local/dpdk", dpdk_pc)
    dpdk_pc = re.sub("\\nlibdir=.+", "\nlibdir=${prefix}/lib", dpdk_pc)
    sz_err = writeTxtFile("/usr/local/share/pkgconfig/libdpdk.pc", dpdk_pc)
    if "" != sz_err:
        return sz_err
    dpdk_pc,sz_err = readTxtFile("/usr/local/share/pkgconfig/libdpdk-libs.pc")
    if ""!=sz_err:
        return sz_err
    dpdk_pc = re.sub("/usr/local/dpdk-meson", "/usr/local/dpdk", dpdk_pc)
    dpdk_pc = re.sub("\\nlibdir=.+", "\nlibdir=${prefix}/lib", dpdk_pc)
    sz_err = writeTxtFile("/usr/local/share/pkgconfig/libdpdk-libs.pc", dpdk_pc)
    if "" != sz_err:
        return sz_err
    return ""


#buildDPDK 编译DPDK；参数：无；返回：错误码
def buildDPDK():
    #安装 DPDK
    if False == os.path.exists("./f-stack-1.21.zip"):
        if 0 != os.system("wget https://github.com/F-Stack/f-stack/archive/refs/tags/v1.21.zip "+
            "-O f-stack-1.21.zip"):
            os.system("rm -f ./f-stack-1.21.zip")
            return "Failed to download f-stack-1.21"
    #测试DPDK的版本是否需要更新
    #编译安装DPDK
    sz_err = build_normal_dpdk()
    if "" != sz_err:
        return sz_err
    sz_err = build_meson_dpdk()
    if "" != sz_err:
        return sz_err
    #修改PC文件
    sz_err = install_pc_for_dpdk()
    if "" != sz_err:
        return sz_err
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
    #下载绑定工具
    first_ver,second_ver,_ = get_kernel_ver()
    if None==first_ver or first_ver<4 or (first_ver==4 and second_ver<18):
        return ""
    if ""==execCmdAndGetOutput("lspci") and \
        True == os.path.exists("/usr/local/dpdk/sbin") and \
        False == os.path.exists("/usr/local/dpdk/sbin/driverctl"):
        if 0 != os.system("git clone https://gitlab.com/driverctl/driverctl.git "\
            "/usr/local/dpdk/sbin/driverctl"):
            return "download driverctl failed"
    if ""==execCmdAndGetOutput("lspci") and \
        True == os.path.exists("/usr/local/dpdk-meson/sbin") and \
        False == os.path.exists("/usr/local/dpdk-meson/sbin/driverctl"):
        if 0 != os.system("cp -rf /usr/local/dpdk/sbin/driverctl "\
            "/usr/local/dpdk-meson/sbin/"):
            return "copy driverctl failed"
    return ""


    #功能：安装hyperscan；参数：无；返回：错误码
def buildHYPERSCAN():
    #安装hyperscan
    if False == os.path.exists("./hyperscan-5.4.0.zip"):
        if 0 != os.system("wget https://github.com/intel/hyperscan/archive/refs/tags/v"\
            "5.4.0.zip -O ./hyperscan-5.4.0.zip"):
            os.system("rm -f ./hyperscan-5.4.0.zip")
            return "Failed to download hyperscan"
    if False == os.path.exists("/usr/local/hyperscan"):
        #解压缩
        os.system("unzip -d /tmp/ ./hyperscan-5.4.0.zip")
        try:
            os.system("rm -Rf /tmp/hyperscan-5.4.0/build")
            os.makedirs("/tmp/hyperscan-5.4.0/build")
        except:
            os.system("rm -Rf /tmp/hyperscan-5.4.0")
            return "Make /tmp/hyperscan-5.4.0/build failed"
        if 0 != os.system("cd /tmp/hyperscan-5.4.0/build && "\
            "cmake -DCMAKE_BUILD_TYPE=release "\
            "-DCMAKE_INSTALL_PREFIX=/usr/local/hyperscan ../"):
            os.system("rm -Rf /tmp/hyperscan-5.4.0")
            return "Failed to config hyperscan"
        if 0 != os.system("cd /tmp/hyperscan-5.4.0/build && make -j"+\
            str(multiprocessing.cpu_count())+" && make install"):
            os.system("rm -Rf /tmp/hyperscan-5.4.0")
            os.system("rm -Rf /usr/local/hyperscan")
            return "Failed to make hyperscan"
        os.system("rm -Rf /tmp/hyperscan-5.4.0")

    return ""


#uninstallDPDK 卸载DPDK；参数：无；返回：错误码
def uninstallDPDK():
    os.system("rm -rf /usr/local/dpdk")
    os.system("rm -rf /usr/local/dpdk-meson")
    os.system("rm -rf /usr/local/share/pkgconfig/libdpdk*")
    os.system("rm -rf /usr/local/hyperscan")
    #如果pkgconfig，则删除
    try:
        dir_lst = os.listdir("/usr/local/share/pkgconfig")
    except:
        dir_lst = None
    for cur_dir in dir_lst:
        if "."!=cur_dir and ".."!=cur_dir:
            return 
    os.system("rm -rf /usr/local/share/pkgconfig")