#!/usr/python/bin
# -*- coding: utf-8 -*-

import os
import platform
import maker_public


#功能：安装hyperscan；参数：版本、安装路径、工程路径；返回：错误描述
def install_hyperscan(ver, install_path, vscode_project_maker, git_proxy):
    hyperscan_url = ("https://%sgithub.com/intel/hyperscan.git" %git_proxy)
    if "aarch64" == platform.machine():
        hyperscan_url = ("https://%sgithub.com/kunpengcompute/hyperscan.git" %git_proxy)
    #安装hyperscan
    sz_err = maker_public.download_src("hyperscan", "v", ver, \
        hyperscan_url, vscode_project_maker, None)
    if "" != sz_err:
        return sz_err
    hyperscan_tmp = "/tmp/hyperscan-"+ver
    hyperscan_src = vscode_project_maker+"/hyperscan-"+ver+".zip"
    #解压缩
    os.system("rm -Rf "+hyperscan_tmp)
    os.system("unzip -d /tmp/ "+hyperscan_src)
    try:
        os.system("rm -Rf "+hyperscan_tmp+"/build")
        os.makedirs(hyperscan_tmp+"/build")
    except:
        os.system("rm -Rf "+hyperscan_tmp)
        return "Make "+hyperscan_tmp+" failed"
    if 0 != os.system("cd %s/build && "\
        "cmake -DCMAKE_BUILD_TYPE=release -DBUILD_STATIC_AND_SHARED=ON "\
        "-DCMAKE_INSTALL_PREFIX=%s ../" %(hyperscan_tmp,install_path)):
        os.system("rm -Rf "+hyperscan_tmp)
        return "Failed to config hyperscan"
    if 0 != os.system("cd "+hyperscan_tmp+"/build && make -j $(nproc) && make install"):
        os.system("rm -Rf "+hyperscan_tmp)
        os.system("rm -Rf %s" %install_path)
        return "Failed to make hyperscan"
    os.system("rm -Rf "+hyperscan_tmp)
    #安装pc文件
    return maker_public.install_pc(maker_public.execCmdAndGetOutput(
        "cd %s/lib*/pkgconfig && pwd" %install_path).split("\n")[0])


#功能：在ubuntu下安装依赖；参数：无；返回：错误描述
def install_ubuntu_dep():
    #安装cmake
    if 0 != os.system("apt-get -y install cmake"):
        return "Install cmake failed"
    #安装ragel
    if 0 != os.system("apt-get -y install ragel"):
        return "Install ragel failed"
    #安装Pcap
    if 0 != os.system("apt-get -y install libpcap-dev"):
        return "Install pcap failed"
    #安装boost
    if 0 != os.system("apt-get -y install libboost-dev"):
        return "Install libboost-dev failed"
    #安装boost
    if 0 != os.system("apt-get -y install pkg-config"):
        return "Install pkg-config failed"
    return ""


#功能：在cenos下安装依赖；参数：无；返回：错误描述
def install_centos_dep():
    #安装cmake
    if 0 != os.system("yum -y install cmake.%s" %platform.machine()):
        return "Install cmake failed"
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
    if 0 != os.system("yum -y install boost-devel.%s" %platform.machine()):
        return "Install cmake failed"
    return ""


#功能：主函数；参数：无；返回：错误描述
def makeropensrc(ins_path, git_proxy):
    osname = maker_public.getOSName()
    #安装apt install autoconf
    if -1 != osname.find("ubuntu"):
        err = install_ubuntu_dep()
    else:
        err = install_centos_dep()
    if "" != err:
        return err        
    #初始化
    if "y"==maker_public.check_reinstall("hyperscan", ins_path+"/hyperscan", \
        ins_path+"/hyperscan/lib/pkgconfig", True):
        szErr = install_hyperscan(maker_public.getVer(platform.machine()+"-hs"), \
            ins_path+"/hyperscan", os.environ["HOME"]+"/vscode_project_maker",git_proxy)
        if "" != szErr:
            return szErr
    print("install hyperscan sucess!") 
    return ""