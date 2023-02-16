#!/usr/python/bin
# -*- coding: utf-8 -*-

import os
import sys
import re
import maker_public


#功能：安装libunwind；参数：版本、安装路径、工程路径；返回：错误描述
def install_libunwind(ver, install_path, vscode_project_maker, git_proxy):
    #下载
    sz_err = maker_public.download_src("libunwind", "v", ver, \
        ("https://%sgithub.com/libunwind/libunwind.git" %git_proxy), \
        vscode_project_maker,"/tmp")
    if "" != sz_err:
        return sz_err
    #编译
    if 0!=os.system("cd /tmp/libunwind-"+ver+" && "\
        "autoreconf -i && "\
        "./configure --prefix="+install_path+" && "\
        "make -j $(nproc) && make install"):
        os.system("rm -rf /tmp/libunwind-"+ver)
        return "Failed to build libunwind"
    os.system("rm -rf /tmp/libunwind-"+ver)
    #安装
    maker_public.build_s_link(install_path+"/lib", "/usr/local/lib", ["pkgconfig"])
    maker_public.build_s_link(install_path+"/include", "/usr/local/include", None)
    sz_err = maker_public.install_pc(maker_public.execCmdAndGetOutput(
        "cd "+install_path+"/lib/pkgconfig && pwd").split("\n")[0])
    if "" != sz_err:
        os.system("rm -rf "+install_path)
    return ""


#功能：安装gperftools；参数：版本、安装路径、工程路径；返回：错误描述
def install_gperftools(ver, install_path, vscode_project_maker, git_proxy):
    #下载
    sz_err = maker_public.download_src("gperftools", "gperftools-", ver, \
        ("https://%sgithub.com/gperftools/gperftools.git" %git_proxy), \
        vscode_project_maker,"/tmp")
    if "" != sz_err:
        return sz_err
    #编译
    if 0!=os.system("cd /tmp/gperftools-"+ver+" && "\
        "sh ./autogen.sh && "\
        "./configure --prefix="+install_path+" --enable-shared=yes --enable-static=yes && "\
        "make -j $(nproc) && make install"):
        os.system("rm -rf /tmp/gperftools-"+ver)
        return "Failed to build gperftools"
    os.system("rm -rf /tmp/gperftools-"+ver)
    sz_err = maker_public.install_pc(maker_public.execCmdAndGetOutput(
        "cd "+install_path+"/lib/pkgconfig && pwd").split("\n")[0])
    if "" != sz_err:
        os.system("rm -rf "+install_path)
    return ""


#功能：主函数；参数：无；返回：错误描述
def makeropensrc(ins_path, git_proxy):
    osname = maker_public.getOSName()
    #安装apt install autoconf
    if -1 != osname.find("ubuntu"):
        if 0 != os.system("apt-get -y install autoconf libtool"):
            return "Install autoconf failed"
    else:
        if 0 != os.system("yum -y install autoconf libtool"):
            return "Install autoconf failed"          
    #初始化
    if "y"==maker_public.check_reinstall("libunwind", ins_path+"/libunwind",\
        ins_path+"/libunwind/lib/pkgconfig", True):
        szErr = install_libunwind(maker_public.getVer("libunwind"), \
            ins_path+"/libunwind", os.environ["HOME"]+"/vscode_project_maker", \
            git_proxy)
        if "" != szErr:
            return szErr
    print("install libunwind sucess!")      
    if "y"==maker_public.check_reinstall("gperftools", ins_path+"/gperftools", \
        ins_path+"/gperftools/lib/pkgconfig", True):
        szErr = install_gperftools(maker_public.getVer("gperftools"), \
            ins_path+"/gperftools", os.environ["HOME"]+"/vscode_project_maker", \
            git_proxy)
        if "" != szErr:
            return szErr
    print("install gperftools sucess!")    
    return ""