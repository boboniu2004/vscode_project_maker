#!/usr/python/bin
# -*- coding: utf-8 -*-

import os
import platform
import maker_public


#install_meson_dpdk 编译安装普通版本的DPDK；参数：dpdk源码路径；返回：错误描述
def install_normal_dpdk(ins_path, fstack_ver):
    #打开驱动
    sz_err = maker_public.replace_content("/tmp/f-stack-"+fstack_ver+\
        "/dpdk/config/common_base", 
        [
            [
                "\\n[ \\t]*CONFIG_RTE_LIBRTE_PMD_AF_PACKET[ \\t]*=.*",
                "\nCONFIG_RTE_LIBRTE_PMD_AF_PACKET=y",
            ],
            [
                "\\n[ \\t]*CONFIG_RTE_LIBRTE_PMD_PCAP[ \\t]*=.*",
                "\nCONFIG_RTE_LIBRTE_PMD_PCAP=y",
            ],
        ])
    #关闭IGB_UIO
    sz_err = maker_public.replace_content("/tmp/f-stack-"+fstack_ver+\
        "/dpdk/kernel/linux/Makefile", 
        [
            [
                "\\n[ \\t]*DIRS-\\$\\(CONFIG_RTE_EAL_IGB_UIO\\).*",
                "\n",
            ],
        ])    
    if "" != sz_err:
        return ("config DPDK failed[%s]" %(sz_err))
    #配置
    if 0 != os.system("cd /tmp/f-stack-"+fstack_ver+"/dpdk && make defconfig"):
        return "config DPDK failed"
    #编译安装
    if 0 != os.system("cd /tmp/f-stack-%s/dpdk && "\
        "make -j $(nproc) && make install prefix=%s" %(fstack_ver,ins_path)):
        return "config DPDK failed"
    #设置
    sz_err = maker_public.build_s_link(ins_path+"/include/dpdk", 
        ins_path+"/include", None)
    if "" != sz_err:
        return sz_err
    if 0 != os.system("cp -rf /tmp/f-stack-%s/dpdk/build/kmod %s/" \
        %(fstack_ver,ins_path)):
        return "config DPDK failed"       
    os.system("rm -rf %s/kernel_verion && "\
        "uname -r >> %s/kernel_verion" %(ins_path,ins_path))
    return ""


#install_meson_dpdk 编译安装meson版本的DPDK；参数：无；返回：错误描述
def install_meson_dpdk(ins_path, fstack_ver):
    #打开PMD驱动
    sz_err = maker_public.replace_content("/tmp/f-stack-"+fstack_ver+
        "/dpdk/config/common_base", 
        [
            [
                "\\n[ \\t]*CONFIG_RTE_LIBRTE_PMD_AF_PACKET[ \\t]*=.*",
                "\nCONFIG_RTE_LIBRTE_PMD_AF_PACKET=y",
            ],
            [
                "\\n[ \\t]*CONFIG_RTE_LIBRTE_PMD_PCAP[ \\t]*=.*",
                "\nCONFIG_RTE_LIBRTE_PMD_PCAP=y",
            ]
        ])
    if "" != sz_err:
        return ("config DPDK failed[%s]" %(sz_err))
    #编译安装meson版本
    if 0 != os.system("cd /tmp/f-stack-%s/dpdk && "\
        "meson ./dpdk_build && cd ./dpdk_build && "\
        "meson configure -Dprefix=%s "\
        "-Dibverbs_link=static -Ddefault_library=static" %(fstack_ver, ins_path)):
        return "config DPDK failed"
    if 0 != os.system("cd /tmp/f-stack-"+fstack_ver+"/dpdk/dpdk_build && "\
        "ninja -j $(nproc) && ninja install"):
        return "config DPDK failed"
    #设置
    if 0 != os.system("mkdir -p %s/kmod && "\
        "cp -rf /tmp/f-stack-%s/dpdk/dpdk_build/kernel/linux/*/*.ko "\
        "%s/kmod" %(ins_path, fstack_ver, ins_path)):
        return "config DPDK failed"  
    os.system("rm -rf %s/kernel_verion && "\
        "uname -r >> %s/kernel_verion" %(ins_path, ins_path))
    pkg_path = ("%s/lib64/pkgconfig" %ins_path)
    if True == os.path.exists("%s/lib" %ins_path):
        pkg_path = maker_public.execCmdAndGetOutput(
        "cd %s/lib/*/pkgconfig && pwd" %ins_path).split("\n")[0]
    return maker_public.install_pc(pkg_path)


#功能：安装dpdk；参数：版本、安装路径、工程路径；返回：错误描述
def install_dpdk(ver, install_path, work_path, \
    complie_type, git_proxy):
    sz_err = maker_public.download_src("f-stack", "v", ver, \
        ("https://%sgithub.com/F-Stack/f-stack.git" %git_proxy), work_path, None)
    if "" != sz_err:
        return sz_err
    #测试DPDK的版本是否需要更新
    os.system("unzip -d /tmp/ "+work_path+"/f-stack-"+ver+".zip")
    #编译安装DPDK
    if "normal" == complie_type:
        sz_err = install_normal_dpdk(install_path, ver)
    else:
        sz_err = install_meson_dpdk(install_path, ver)
    os.system("rm -Rf /tmp/f-stack-"+ver)
    if "" != sz_err:
        return sz_err
    return ""


#功能：在ubuntu下安装依赖；参数：无；返回：错误描述
def install_ubuntu_dep():
    #安装gawk
    if 0 != os.system("apt-get -y install gawk"):
        return "Install gawk failed"
    #安装ssl
    if 0 != os.system("apt-get -y install libssl-dev"):
        return "Install libssl-dev failed"
    #安装libnuma-dev
    if 0 != os.system("apt-get -y install libnuma-dev"):
        return "Install libnuma-dev failed"
    #安装libpcre3-dev
    if 0 != os.system("apt-get -y install libpcre3-dev"):
        return "Install libpcre3-dev failed"
    #安装zlib
    if 0 != os.system("apt-get -y install zlib1g-dev"):
        return "Install libpcre3-dev failed"
    ubuntu_ver,sz_err = maker_public.getUbuntuVer()
    if "" != sz_err:
        return sz_err
    if ("20.04" <= ubuntu_ver):
        if 0 != os.system("apt-get -y install python-is-python3 libpcap-dev"):
            return "Install python-is-python3,libpcap failed"
    else:
        if 0 != os.system("apt-get -y install libpcap-dev"):
            return "Install libpcap failed"
    #安装ninja
    if 0 != os.system("python3 -m pip install ninja"):
        return "Install ninja failed"
    #安装meson
    if 0 != os.system("python3 -m pip install meson"):
        return "Install meson failed"
    return ""


#功能：在cenos下安装依赖；参数：无；返回：错误描述
def install_centos_dep():
    #安装libnuma-dev
    if 0 != os.system("yum -y install numactl-devel.%s" %platform.machine()):
        return "Install cmake failed"
    #安装pcre
    if 0 != os.system("yum -y install pcre-devel.%s" %platform.machine()):
        return "Install cmake failed"
    #安装openssl
    if 0 != os.system("yum -y install openssl-devel.%s" %platform.machine()):
        return "Install cmake failed"
    #安装zlib
    if 0 != os.system("yum -y install zlib-devel.%s" %platform.machine()):
        return "Install cmake failed"
    #安装pcap
    if 0 != os.system("dnf --enablerepo=PowerTools install -y libpcap-devel"):
        return "Can not install libpcap-devel"
    #安装ninja
    if 0 != os.system("python3 -m pip install ninja"):
        return "Install ninja failed"
    #安装meson
    if 0 != os.system("python3 -m pip install meson"):
        return "Install meson failed"
    return ""


#功能：主函数；参数：无；返回：错误描述
def makeropensrc(work_path, ins_path, complie_type, git_proxy):
    osname = maker_public.getOSName()
    #安装apt install autoconf
    if -1 != osname.find("ubuntu"):
        err = install_ubuntu_dep()
    else:
        err = install_centos_dep()
    if "" != err:
        return err
    if "normal" == complie_type: 
        pkg_path = None
    else:
        pkg_path = ("%s/dpdk/lib64/pkgconfig" %ins_path)
        if True == os.path.exists("%s/dpdk/lib" %ins_path):
            pkg_path = maker_public.execCmdAndGetOutput(
                "cd %s/dpdk/lib/*/pkgconfig && pwd" %ins_path).split("\n")[0]
    #初始化
    if "y"==maker_public.check_reinstall("dpdk", ins_path+"/dpdk", \
        pkg_path, True==maker_public.issame_kernel_ver(ins_path+"/dpdk")):
        szErr = install_dpdk(maker_public.getVer("f-stack"), \
            ins_path+"/dpdk", work_path, \
            complie_type, git_proxy)
        if "" != szErr:
            return szErr
    print("install dpdk sucess!") 
    return ""