#!/usr/python/bin
# -*- coding: utf-8 -*-

import os
import sys
import re
import maker_public


#功能：卸载pc文件；参数：原路径；返回：错误码
def uninstall_pc(pkgconfig_path):
    #尝试删除pc文件
    if ""!=pkgconfig_path and None!=re.search("^\\d+\\.\\d+\\.\\d+\\n$", 
        maker_public.execCmdAndGetOutput("pkg-config --version")):
        pkg_path_lst = maker_public.execCmdAndGetOutput(
            "pkg-config --variable pc_path pkg-config").split(":")
        for pkg_path in pkg_path_lst:
            if "\n" == pkg_path[len(pkg_path)-1:]:
                pkg_path = pkg_path[:len(pkg_path)-1]
            if "" == pkg_path:
                continue
            maker_public.remove_s_link(pkgconfig_path, pkg_path)
    return ""


#功能：检查是否要继续进行安装；参数：工程名、安装路径：返回：继续安装返回y
def check_reinstall(proj_name, proj_path):
    need_reinstall = "y"
    if True == os.path.exists(proj_path):
        if re.search("^2\\..*", sys.version):
            need_reinstall = \
                raw_input(proj_name+" is already installed, do you want to reinstall[y/n]:")
        else:
            need_reinstall = \
                input(proj_name+" is already installed, do you want to reinstall[y/n]:")
    if True==os.path.isdir(proj_path) and ("y"==need_reinstall or "Y"==need_reinstall):
        uninstall_pc(maker_public.execCmdAndGetOutput(
        "cd "+proj_path+"/lib/pkgconfig && pwd").split("\n")[0])
        maker_public.remove_s_link(proj_path+"/lib", "/usr/local/lib")
        maker_public.remove_s_link(proj_path+"/include", "/usr/local/include")
        os.system("rm -rf "+proj_path)
        need_reinstall = "y"
    return need_reinstall


#功能：安装libunwind；参数：版本、安装路径、工程路径；返回：错误描述
def install_libunwind(ver, install_path, vscode_project_maker):
    #下载
    sz_err = maker_public.download_src("libunwind", "v", ver, \
        "https://ghproxy.com/github.com/libunwind/libunwind.git", vscode_project_maker,"/tmp")
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
def install_gperftools(ver, install_path, vscode_project_maker):
    #下载
    sz_err = maker_public.download_src("gperftools", "gperftools-", ver, \
        "https://ghproxy.com/github.com/gperftools/gperftools.git", vscode_project_maker,"/tmp")
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
def makeropensrc():
    gperftools_path = os.getcwd()
    if 2<len(sys.argv):
        gperftools_path = sys.argv[2]
    if False==os.path.isdir(gperftools_path):
        return "Invaild gperftools path"
    gperftools_path = os.path.abspath(gperftools_path)
    #安装apt install autoconf
    if 0 != os.system("apt-get -y install autoconf libtool"):
        return "Install autoconf failed"    
    #初始化
    if "y"==check_reinstall("libunwind", gperftools_path+"/libunwind"):
        szErr = install_libunwind(maker_public.getVer("libunwind"), \
            gperftools_path+"/libunwind", os.environ["HOME"]+"/vscode_project_maker")
        if "" != szErr:
            return szErr
    print("install libunwind sucess!")      
    if "y"==check_reinstall("gperftools", gperftools_path+"/gperftools"):
        szErr = install_gperftools(maker_public.getVer("gperftools"), \
            gperftools_path+"/gperftools", os.environ["HOME"]+"/vscode_project_maker")
        if "" != szErr:
            return szErr
    print("install gperftools sucess!")    
    return ""