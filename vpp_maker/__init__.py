#!/usr/python/bin
# -*- coding: utf-8 -*-

import os
from posixpath import basename
import re
import sys
import maker_public


#功能：安装依赖；参数：无；返回：错误码
def make_dep(vpp_ver, vpp_path, vscode_project_maker):
    return ""



#功能：下载配置vpp；参数：无；返回：错误码
def config_fstack(vpp_ver, vpp_path, vscode_project_maker):
    if False == os.path.exists(vscode_project_maker+"/vpp-"+vpp_ver+".zip"):
        if 0 != os.system(\
            "wget https://ghproxy.com/github.com/FDio/vpp/archive/refs/tags/"
            "v"+vpp_ver+".zip -O "+vscode_project_maker+\
            "/vpp-"+vpp_ver+".zip"):
            os.system("rm -f "+vscode_project_maker+"/vpp-"+vpp_ver+".zip")
            return "Failed to download vpp-"+vpp_ver
    if False == os.path.exists(vpp_path+"/vpp-"+vpp_ver):
        os.system("unzip -d "+vpp_path+"/ "+
            vscode_project_maker+"/vpp-"+vpp_ver+".zip")
    #获取OS版本
    osver = maker_public.getOSName()
    #写入版本信息
    sz_err = maker_public.writeTxtFile(\
        vpp_path+"/vpp-"+vpp_ver+"/src/scripts/.version", vpp_ver)
    if "" != sz_err:
        return sz_err
    #修改makefile
    makedat,sz_err = maker_public.readTxtFile(vpp_path+"/vpp-"+\
        vpp_ver+"/Makefile")
    if "" != sz_err:
        return sz_err
    makedat = re.sub("python-virtualenv", "python3-virtualenv", makedat)
    if "ubuntu" == osver:
        makedat = re.sub("libffi6", "libffi7", makedat)
        makedat = re.sub("python-pip", "python-pip-whl", makedat)
    else:
        makedat = re.sub("centos-release-scl-rh", "", makedat)
        makedat = re.sub("glibc-static", "", makedat)
        makedat = re.sub("mbedtls-devel", "", makedat)
        makedat = re.sub("\\nRPM_DEPENDS[ \\t]+\\+=[ \\t]+ninja-build", 
            "\nRPM_DEPENDS += ", makedat)
        makedat = re.sub("mbedtls-devel", "", makedat)
        makedat = re.sub(" python-devel", 
            " platform-python-devel python2", makedat)
        makedat = re.sub("python36-ply", "python3-ply", makedat)
        makedat = re.sub("python36-jsonschema", "python3-jsonschema", makedat)
        makedat = re.sub("devtoolset-7", "gcc-toolset-10", makedat)
        makedat = re.sub("base-debuginfo", "debuginfo", makedat)
    if False == os.path.isdir(vpp_path+"/vpp-"+vpp_ver+".git"):
        makedat = re.sub("\\n\\tgit[ ]+config", "\n#\tgit config", makedat)
    sz_err = maker_public.writeTxtFile(vpp_path+"/vpp-"+vpp_ver+"/Makefile", 
        makedat)
    if "" != sz_err:
        return sz_err
    #修改CMakeLists.txt
    cmakedat,sz_err = maker_public.readTxtFile(vpp_path+"/vpp-"+\
        vpp_ver+"/src/CMakeLists.txt")
    if "" != sz_err:
        return sz_err
    if "ubuntu" == osver:
        cmakedat = re.sub("VPP_LIB_VERSION[ \\t]+\\${VPP_VERSION}", 
            "VPP_LIB_VERSION \"${VPP_VERSION}\"", cmakedat)
        if None == re.search("CMAKE_REQUIRED_LIBRARIES", cmakedat):
            cmakedat = re.sub(\
                "\\nfind_package[ \\t]*\\([ \\t]*Threads[^\\)]+", 
                "\nset(CMAKE_REQUIRED_LIBRARIES \"-lpthread \")"\
                "\nfind_package(Threads REQUIRED", cmakedat)            
    sz_err = maker_public.writeTxtFile(\
        vpp_path+"/vpp-"+vpp_ver+"/src/CMakeLists.txt", cmakedat)
    if "" != sz_err:
        return sz_err
    #替换github.com
    pkgmkfiles = os.listdir(vpp_path+"/vpp-"+vpp_ver+"/build/external/packages/")
    for mkfile in pkgmkfiles:
        if False == os.path.isfile(\
            vpp_path+"/vpp-"+vpp_ver+"/build/external/packages/"+mkfile):
            continue
        if None == re.search(".+\\.mk$", mkfile):
            continue
        mkcont,err = maker_public.readTxtFile(\
            vpp_path+"/vpp-"+vpp_ver+"/build/external/packages/"+mkfile)
        if ""!=err:
            return err
        mkcont = re.sub("://github\\.com", \
            "://ghproxy.com/github.com", mkcont)
        err = maker_public.writeTxtFile(\
            vpp_path+"/vpp-"+vpp_ver+"/build/external/packages/"+mkfile, 
            mkcont)
        if ""!=err:
            return err
    return ""


#功能：主函数；参数：无；返回：无
def makeropensrc():
    vpp_path = os.getcwd()
    if 2<len(sys.argv):
        vpp_path = sys.argv[2]
    if False==os.path.isdir(vpp_path):
        print("Invaild vpp path")
        exit(-1)
    vpp_path = os.path.realpath(vpp_path)
    #初始化vpp
    need_continue = "y"
    if True == os.path.exists(vpp_path+"/vpp-19.08.3"):
        if re.search("^2\\..*", sys.version):
            need_continue = \
                raw_input("vpp is already installed, do you want to continue[y/n]:")
        else:
            need_continue = \
                input("vpp is already installed, do you want to continue[y/n]:")
    if "y"==need_continue or "Y"==need_continue:
        szErr = config_fstack("19.08.3", vpp_path, 
            os.environ["HOME"]+"/vscode_project_maker")
        if "" != szErr:
            print(szErr)
        else:
            print("config vpp sucess!")