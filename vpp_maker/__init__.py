#!/usr/python/bin
# -*- coding: utf-8 -*-

import os
from posixpath import basename
import re
import sys
import maker_public


#功能：安装依赖；参数：无；返回：错误码
def make_dep(vpp_ver, vpp_path, vscode_project_maker):
    if maker_public.getOSName()=="ubuntu":
        os.system("apt-get --purge autoremove vpp-ext-deps.x86_64")
    else:
        os.system("yum -y erase vpp-ext-deps.x86_64")
    os.system("cd "+vpp_path+"/vpp-"+vpp_ver+" && make install-dep && make install-ext-dep")
    os.system("cd "+vpp_path+"/vpp-"+vpp_ver+" && make install-dep && make install-ext-dep")
    return ""


#功能：制作vpp工程；参数：无；返回：错误码
def create_vpp_project(vpp_ver, vpp_path, vscode_project_maker):
    if 0 != os.system("python3 "+vscode_project_maker+
        "/__init__.py c app /tmp/vpp"):
        os.system("rm -rf /tmp/vpp")
        return "create vpp project failed"
    os.system("cp -rf /tmp/vpp/.vscode "+
        vpp_path+"/vpp-"+vpp_ver+"/")
    os.system("rm -rf /tmp/vpp")
    #替换工作目录
    launch,sz_err = maker_public.readTxtFile(vpp_path+"/vpp-"+vpp_ver+"/.vscode/"
        "launch.json")
    if "" != sz_err:
        return "create vpp project failed"
    launch = re.sub("\\$\\{workspaceFolder\\}/debug", 
        "${workspaceFolder}/build-root/install-vpp_debug-native/vpp/bin", launch)
    launch = re.sub("\"\\$\\{workspaceFolder\\}\"", 
        "\"${workspaceFolder}/build-root/install-vpp_debug-native/vpp/bin\"", launch)
    launch = re.sub("\"args\"[ \\t]*:[ \\t]*\\[[^\\]]*\\],", 
        "\"args\": [\"-c\",\"${workspaceFolder}/build-root/install-vpp_debug-native/vpp/etc/vpp/startup.conf\"],", launch)
    sz_err = maker_public.writeTxtFile(vpp_path+"/vpp-"+vpp_ver+"/.vscode/"
        "launch.json", launch)
    if "" != sz_err:
        return "create vpp project failed"
    #替换编译TAG
    tasks,sz_err = maker_public.readTxtFile(vpp_path+"/vpp-"+vpp_ver+"/.vscode/"
        "tasks.json")
    if "" != sz_err:
        return "create vpp project failed"
    tasks = re.sub("\"debug\"", "\"build\"", tasks)
    tasks = re.sub("\"clean\"", "\"wipe\"", tasks)
    tasks = re.sub("\\$\\{workspaceFolder\\}/makefile", "${workspaceFolder}/Makefile", tasks)
    #增加安装任务
    tasks = re.sub("\"tasks\":[ \\t]+\\[", 
            "\"tasks\": ["\
            "\n        {"\
            "\n            \"type\": \"shell\","\
            "\n            \"label\": \"gcc init active file\","\
            "\n            \"command\": \"/usr/bin/python3\","\
            "\n            \"args\": ["\
            "\n                \"${workspaceFolder}/dpdk_init.py\","\
            "\n            ],"\
            "\n            \"options\": {"\
            "\n                \"cwd\": \"${workspaceFolder}\""\
            "\n            },"\
            "\n            \"problemMatcher\": ["\
            "\n                \"$gcc\""\
            "\n            ],"\
            "\n            \"group\": {"\
            "\n                \"kind\": \"build\","\
            "\n                \"isDefault\": true"\
            "\n            }"\
            "\n        },"
        , tasks)
    sz_err = maker_public.writeTxtFile(vpp_path+"/vpp-"+vpp_ver+"/.vscode/"
        "tasks.json", tasks)
    if "" != sz_err:
        return "create vpp project failed"
    return ""


#功能：下载配置vpp；参数：无；返回：错误码
def config_vpp(vpp_ver, vpp_path, vscode_project_maker):
    cmakedat,sz_err = maker_public.readTxtFile(vpp_path+"/vpp-"+\
        vpp_ver+"/build/external/packages/dpdk.mk")
    if False == os.path.exists(vscode_project_maker+"/vpp-"+vpp_ver+".zip"):
        os.system("rm -rf "+vscode_project_maker+"/vpp-"+vpp_ver)
        if 0 != os.system(\
            "git clone --branch v"+vpp_ver+" https://ghproxy.com/github.com/FDio/vpp.git "+\
            vscode_project_maker+"/vpp-"+vpp_ver):
            os.system("rm -rf "+vscode_project_maker+"/vpp-"+vpp_ver)
            return "Failed to download vpp-"+vpp_ver
        if 0 != os.system("cd "+vscode_project_maker+\
            " && zip -r "+"vpp-"+vpp_ver+".zip vpp-"+vpp_ver):
            os.system("rm -f "+vscode_project_maker+"/vpp-"+vpp_ver+".zip")
        os.system("rm -rf "+vscode_project_maker+"/vpp-"+vpp_ver) 
    if False == os.path.exists(vpp_path+"/vpp-"+vpp_ver):
        os.system("unzip -d "+vpp_path+"/ "+
            vscode_project_maker+"/vpp-"+vpp_ver+".zip")
    #获取OS版本
    osver = maker_public.getOSName()
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
    #修改DPDK的CMakelist
    cmakedat,sz_err = maker_public.readTxtFile(vpp_path+"/vpp-"+\
        vpp_ver+"/build/external/packages/dpdk.mk")
    cmakedat = re.sub("RTE_EAL_IGB_UIO[ \\t]*,[ \\t]*n", "RTE_EAL_IGB_UIO,y", cmakedat)
    sz_err = maker_public.writeTxtFile(vpp_path+"/vpp-"+vpp_ver+\
        "/build/external/packages/dpdk.mk", 
        cmakedat)
    if "" != sz_err:
        return sz_err
    #下载绑定器
    if ""==maker_public.execCmdAndGetOutput("lspci") and \
        False == os.path.exists(vpp_path+"/vpp-"+vpp_ver+"/driverctl"):
        if 0 != os.system("git clone https://gitlab.com/driverctl/driverctl.git "+\
            vpp_path+"/vpp-"+vpp_ver+"/driverctl"):
            return "download driverctl failed"
    #拷贝dpdk初始化工具
    if 0 != os.system("cp -rf "+os.environ["HOME"]+\
        "/vscode_project_maker/vpp_maker/dpdk_init.py "+vpp_path+"/vpp-"+vpp_ver+"/"):
        return "cp dpdk_init.py failed"
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
    if True == os.path.exists(vpp_path+"/vpp-20.09"):
        if re.search("^2\\..*", sys.version):
            need_continue = \
                raw_input("vpp is already installed, do you want to continue[y/n]:")
        else:
            need_continue = \
                input("vpp is already installed, do you want to continue[y/n]:")
    if "y"==need_continue or "Y"==need_continue:
        szErr = config_vpp("20.09", vpp_path, 
            os.environ["HOME"]+"/vscode_project_maker")
        if "" != szErr:
            print(szErr)
            exit(-1)
        szErr = make_dep("20.09", vpp_path,  os.environ["HOME"]+"/vscode_project_maker")
        if "" != szErr:
            print(szErr)
        else:
            print("config vpp sucess!")
    #生成工程
    szErr = create_vpp_project("20.09", vpp_path,  os.environ["HOME"]+"/vscode_project_maker")
    if "" != szErr:
        print(szErr)
    else:
        print("create vpp project sucess!")
        