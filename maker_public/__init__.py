#!/usr/python/bin
# -*- coding: utf-8 -*-


import os
import re
import sys
import multiprocessing
import platform
import time


#存储了所有需要配置的版本信息，方便后续对脚本中用到的模块的版本进行管理
g_verconfig = {
    "python"            :  "3.8",
    "java"              :  "11",
    "ragel"             :  "6.10",
    "f-stack"           :  "1.21",
    "launch"            :  "0.2.0",
    "task"              :  "2.0.0",
    "prop"              :  "4",
    "libunwind"         :  "1.6.2",
    "gperftools"        :  "2.9.1",
    "go"                :  "1.18",
    "vpp"               :  "20.09",
    "x86_64-hs"         :  "5.4.0",
    "aarch64-hs"        :  "5.3.0.aarch64"
}


#获取模块对应的版本；参数：模块名；返回：模块对应的版本
def getVer(module):
    return g_verconfig.get(module)

##############################################################################################
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


#功能：下载；参数：名称、版本、工程路径、解压缩路径；返回：错误描述
def download_src(name, versufx, ver, url, vscode_project_maker, uncomp_path):
    store_path = vscode_project_maker+"/"+name+"-"+ver
    if False == os.path.exists(store_path+".zip"):
        #下载
        os.system("rm -rf "+store_path)
        if 0 != os.system("git clone --branch "+versufx+ver+" "+url+" "+store_path):
            os.system("rm -rf "+store_path)
            return "Failed to download "+name+"-"+ver
        if 0 != os.system("cd "+vscode_project_maker+\
            " && zip -r "+name+"-"+ver+".zip "+name+"-"+ver):
            os.system("rm -f "+store_path+".zip")
        os.system("rm -rf "+store_path)
    #解压缩
    if None != uncomp_path:
        os.system("rm -rf "+uncomp_path+"/"+name+"-"+ver)
        os.system("unzip -d "+uncomp_path+"/ "+store_path+".zip")
    return ""


#函数功能：安装golang工i具
#函数参数：GO可执行程序位置
#函数返回：错误描述
def installGolangTools(szGo,go_proxy,go_path):
    tmformat = "%Y %m %d %H:%M:%S"
    curtime_str = time.strftime(tmformat, time.localtime(time.time()))
    if True == os.path.isfile("%s/go_install_log" %go_path):
        date_str,sz_err = readTxtFile("%s/go_install_log" %go_path)
        date_str = date_str.replace("\n", "")
        if "" != sz_err:
            return sz_err
        try:
            date = time.strptime(date_str, tmformat)
        except:
            date = time.strptime("1970 1 1 00:00:00", tmformat)
    else:
        date = time.strptime("1970 1 1 00:00:00", tmformat)
    #半年不用更新
    if time.localtime(time.time()-24*3600*31*3)<date:
        return ""
    #设置GO模块代理
    if 0 != os.system("su -c \""+szGo+" env -w GO111MODULE=on\""):
        return "Set GO111MODULE=on failed"
    if 0 != os.system("su -c \" %s env -w GOPROXY=\\\"%s,direct\\\"\"" %(szGo,go_proxy)):
        return "Set GOPROXY failed"
    if 0 != os.system("su -c \"%s env -w GOPATH=\\\"%s\\\"\"" %(szGo,go_path)):
        return "Set GOPROXY failed"
    os.system("su -c \""+szGo+" env\"")
    #staticcheck
    os.system("su -c \"%s install honnef.co/go/tools/cmd/staticcheck@latest\"" %(szGo))
    #安装go-outline
    os.system("su -c \"%s install github.com/ramya-rao-a/go-outline@latest\"" %(szGo))
    #安装go-find-references
    os.system("su -c \"%s install github.com/lukehoban/go-find-references@latest\"" %(szGo))
    #安装gocode
    os.system("su -c \"%s install github.com/mdempsky/gocode@latest\"" %(szGo))
    #安装gopkgs
    os.system("su -c \"%s install github.com/uudashr/gopkgs/cmd/gopkgs@latest\"" %(szGo))
    #安装godef
    os.system("su -c \"%s install github.com/rogpeppe/godef@latest\"" %(szGo))
    #安装goreturns
    os.system("su -c \"%s install sourcegraph.com/sqs/goreturns@latest\"" %szGo)
    #安装gorename
    os.system("su -c \"%s install golang.org/x/tools/cmd/gorename@latest\"" %szGo)
    #安装go-symbols
    os.system("su -c \"%s install github.com/newhook/go-symbols@latest\"" %(szGo))
    #安装gopls
    os.system("su -c \"%s install golang.org/x/tools/gopls@latest\"" %szGo)
    os.system("su -c \"%s mod download golang.org/x/tools/gopls\"" %szGo)
    #安装dlv
    os.system("su -c \"%s install github.com/go-delve/delve/cmd/dlv@latest\"" %(szGo))
    #安装staticcheck
    os.system("su -c \"%s install honnef.co/go/tools/cmd/staticcheck@latest\"" %szGo)
    #安装goimports
    os.system("su -c \"%s install golang.org/x/tools/cmd/goimports@latest\"" %szGo)
    #安装guru
    os.system("su -c \"%s install golang.org/x/tools/cmd/guru@latest\"" %szGo)
    #安装golint
    os.system("su -c \"%s install golang.org/x/lint/golint@latest\"" %szGo)
    #安装gotests
    os.system("su -c \"%s install github.com/cweill/gotests@latest\"" %(szGo))
    #安装gomodifytags
    os.system("su -c \"%s install github.com/fatih/gomodifytags@latest\"" %(szGo))
    #安装impl
    os.system("su -c \"%s install github.com/josharian/impl@latest\"" %(szGo))
    #安装fillstruct
    os.system("su -c \"%s install github.com/davidrjenni/reftools/cmd/fillstruct@latest\"" %(szGo))
    #安装goplay
    os.system("su -c \"%s install github.com/haya14busa/goplay/cmd/goplay@latest\"" %(szGo))
    #安装godoctor
    os.system("su -c \"%s install github.com/godoctor/godoctor@latest\"" %(szGo))
    #
    os.system("rm -rf %s/go_install_log && echo \"%s\" > %s/go_install_log" \
        %(go_path,curtime_str,go_path))
    return ""
    

#函数功能：配置PIP
#函数参数：python可执行文件和PIP可执行文件
#函数返回：错误描述
def configPip(szPython, py_host, py_url):
    #添加源
    if 0 != os.system("su -c \"mkdir -p ~/.pip\""):
        return "Add PIP source failed"
    os.system("su -c \"rm -rf ~/.pip/pip.conf\"")
    if 0 != os.system("su -c \" echo \\\"[global]\ntimeout = 6000\nindex-url = "\
        "%s\ntrusted-host = %s\\\" >> ~/.pip/pip.conf\"" %(py_url,py_host)):
        return "Failed to writr pip.conf"
    #升级PIP
    if 0 != os.system("su -c \""+szPython+" -m pip install --upgrade pip \""):
        return "Update PIP failed"
    #安装pylint
    if 0 != os.system("su -c \""+szPython+" -m pip install --upgrade pylint \""):
        return "Update Pylint failed"
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
        kerver = execCmdAndGetOutput("uname -r")
        if None != re.search("-WSL2.*", kerver):
            return "ubuntu-wsl2"
        else:
            return "ubuntu"
    return ""


#get_kernel_ver 获取内核版本；参数：无；返回：操作系统内核的版本
def get_kernel_ver():
    szOSName = execCmdAndGetOutput("uname -r")
    match_ret = re.match("^(\\d+)\\.(\\d+)\\.(\\d+)[-\\.]\\d+", szOSName)
    if None == match_ret:
        return None, None, None
    return int(match_ret.group(1)),int(match_ret.group(2)),\
        int(match_ret.group(3))
    

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


#build_s_link 将源目录中的全部文件在目的目录中建立软链接；参数：源目录、目标目录；
#返回：错误描述
def build_s_link(src_dir, dst_dir, ignore_files):
    src_dir = os.path.abspath(src_dir)
    dst_dir = os.path.abspath(dst_dir)
    src_dir_list = os.listdir(src_dir)
    for cur_dir in src_dir_list:
        if "."==cur_dir or ".."==cur_dir:
            continue
        if None!=ignore_files and (cur_dir in list(ignore_files)):
            continue
        os.system("rm -rf "+dst_dir+"/"+cur_dir)
        if 0 != os.system("ln -s "+src_dir+"/"+cur_dir+" "+dst_dir+"/"+cur_dir):
            return "ln -s "+src_dir+"/"+cur_dir+" "+dst_dir+"/"+cur_dir+" failed"
    return ""


#install_pc 安装PC文件；参数：pc所在目录；返回：错误码
def install_pc(src_path):
    if None == re.search("^\\d+\\.\\d+\\.\\d+\\n$", 
        execCmdAndGetOutput("pkg-config --version")):
        print ("have no pkg-config")
        return ""
    pkg_path_lst = execCmdAndGetOutput(
        "pkg-config --variable pc_path pkg-config").split(":")
    if 0 >= len(pkg_path_lst):
        return "have no pc_path"
    pkg_path = pkg_path_lst[0]
    if "\n" == pkg_path[len(pkg_path)-1:]:
        pkg_path = pkg_path[:len(pkg_path)-1]
    os.system("mkdir -p "+pkg_path)
    sz_err = build_s_link(src_path, pkg_path, None)
    if ""==sz_err:
        os.system("ldconfig")
    return sz_err


#功能：重启；参数：重启提示信息；返回：无
def do_reboot(msg):
    if re.search("^2\\..*", sys.version):
        raw_input(msg)
    else:
        input(msg)
    os.system("reboot")


#功能：获取pyhon命令；参数：无；返回：python命令
def get_python():
    man_ver = re.search("^(\d+)\\..*", sys.version)
    if None==man_ver or "2"==man_ver.group(1):
        return "python"
    else:
        return "python"+man_ver.group(1)


#功能：替换文件中的内容；参数：文件路径，待替换的文本正则，替换的内容；返回：错误码
def replace_content(file_path, replace_lst):
    #修改lib下的makefile
    file_dat,err = readTxtFile(file_path)
    if "" != err:
        return err
    for replace in replace_lst:
        pattern = replace[0]
        dst_dat = replace[1]
        ignore_err = False
        if 2 < len(replace):
            ignore_err = replace[2]
        if False==ignore_err and  0>=len(re.findall(pattern, file_dat)):
            return ("can not find pattern( %s )" %pattern)
    for replace in replace_lst:
        pattern = replace[0]
        dst_dat = replace[1]
        file_dat = re.sub(pattern, dst_dat, file_dat)
    return writeTxtFile(file_path, file_dat)


#getUbuntuVer 获取ubuntu版本；参数：无；返回：ubuntu版本、错误描述
def getUbuntuVer():
    osinfo = execCmdAndGetOutput("lsb_release -a")
    ubuntu_ver = re.search("\\nRelease[ \\t]*:[ \\t]*(\d+\\.\d+)", osinfo)
    if None == ubuntu_ver:
        return "","have no version"
    return ubuntu_ver.group(1), ""


#remove_s_link 将源目录中的全部文件对应的软链接删除；参数：源目录、目标目录；
#返回：错误描述
def remove_s_link(src_dir, dst_dir):
    src_dir = os.path.abspath(src_dir)
    dst_dir = os.path.abspath(dst_dir)
    src_dir_list = os.listdir(src_dir)
    for cur_dir in src_dir_list:
        if "."==cur_dir or ".."==cur_dir:
            continue
        os.system("rm -rf "+dst_dir+"/"+cur_dir)
    return ""


#功能：卸载pc文件；参数：原路径；返回：错误码
def uninstall_pc(pkgconfig_path):
    #尝试删除pc文件
    if ""!=pkgconfig_path and None!=re.search("^\\d+\\.\\d+\\.\\d+\\n$", 
        execCmdAndGetOutput("pkg-config --version")):
        pkg_path_lst = execCmdAndGetOutput(
            "pkg-config --variable pc_path pkg-config").split(":")
        for pkg_path in pkg_path_lst:
            if "\n" == pkg_path[len(pkg_path)-1:]:
                pkg_path = pkg_path[:len(pkg_path)-1]
            if "" == pkg_path:
                continue
            remove_s_link(pkgconfig_path, pkg_path)
    return ""


#功能：检查是否要继续进行安装；参数：工程名、安装路径：返回：继续安装返回y
def check_reinstall(proj_name, proj_path, pkg_path, other_condit):
    need_reinstall = "y"
    if True == os.path.exists(proj_path) and True == other_condit:
        if re.search("^2\\..*", sys.version):
            need_reinstall = \
                raw_input(proj_name+" is already installed, do you want to reinstall[y/n]:")
        else:
            need_reinstall = \
                input(proj_name+" is already installed, do you want to reinstall[y/n]:")
    if True==os.path.isdir(proj_path) and ("y"==need_reinstall or "Y"==need_reinstall):
        if None != pkg_path:
            uninstall_pc(execCmdAndGetOutput("cd %s && pwd" %pkg_path).split("\n")[0])
        if True == os.path.exists(proj_path+"/lib"):
            remove_s_link(proj_path+"/lib", "/usr/local/lib")
        if True == os.path.exists(proj_path+"/lib64"):
            remove_s_link(proj_path+"/lib64", "/usr/local/lib64")
        if True == os.path.exists(proj_path+"/include"):
            remove_s_link(proj_path+"/include", "/usr/local/include")
        os.system("rm -rf "+proj_path)
        need_reinstall = "y"
    return need_reinstall


#uninstallDPDK 卸载DPDK；参数：无；返回：错误码
def uninstallDPDK(ins_path):
    #尝试删除pc文件
    if None != re.search("^\\d+\\.\\d+\\.\\d+\\n$", 
        execCmdAndGetOutput("pkg-config --version")):
        pkg_path_lst = execCmdAndGetOutput(
        "pkg-config --variable pc_path pkg-config").split(":")
        meson_pkg_path = ("%s/dpdk/lib64/pkgconfig" %ins_path)
        if True == os.path.exists("%s/dpdk/lib" %ins_path):
            meson_pkg_path = execCmdAndGetOutput(
                "cd %s/dpdk/lib/*/pkgconfig && pwd" %ins_path).split("\n")[0]
        for pkg_path in pkg_path_lst:
            if "\n" == pkg_path[len(pkg_path)-1:]:
                pkg_path = pkg_path[:len(pkg_path)-1]
            if "" == pkg_path:
                continue
            if True == os.path.isdir(meson_pkg_path):
                remove_s_link(meson_pkg_path, pkg_path)
            remove_s_link(execCmdAndGetOutput(
        "cd %s/hyperscan/lib*/pkgconfig && pwd" %ins_path).split("\n")[0], pkg_path)
    #删除其他文件
    os.system("rm -rf %s/dpdk" %ins_path)


#获取DPDK管理脚本；参数：管理脚本存储路径，会在该路径下创建dpdk_scrits目录；返回：错误码
def get_DPDKscrits(work_path, store_path):
    #创建目录
    if False == os.path.isdir(store_path):
        return ("Faile to find dir %s" %store_path)
    store_path = os.path.abspath(store_path)+"/dpdk_scrits"
    if False == os.path.isdir(store_path):
        try:
            os.makedirs(store_path)
        except:
            return ("Faile to make dir %s" %store_path)
    #拷贝数据
    if 0 != os.system("mkdir -p "+store_path+"/maker_public && cp -rf "+\
        work_path+"/maker_public/*.py "+store_path+"/maker_public/"):
        return "Faile to cp maker_public"
    if 0 != os.system("cp -rf "+work_path+"/dpdk_scrits.py "+\
        store_path+"/__init__.py"):
        return "Faile to cp dpdk_scrits"
    return ""
    
