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
    os.system("cd "+vpp_path+"/vpp-"+vpp_ver+" && make install-dep")
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


#功能：配置dpdk；参数：无；返回：错误码
def config_dpdk(vpp_ver, vpp_path, vscode_project_maker):
    #拷贝dpdk初始化工具
    if 0 != os.system("cp -rf "+vscode_project_maker+\
        "/vpp_maker/dpdk_init.py "+vpp_path+"/vpp-"+vpp_ver+"/"):
        return "cp dpdk_init.py failed"
    #写入igb_uio的meson文件
    err = maker_public.writeTxtFile(vpp_path+"/vpp-"+vpp_ver+\
        "/dpdk-kmods/linux/igb_uio/meson.build", \
            "# SPDX-License-Identifier: BSD-3-Clause\n"\
            "# Copyright(c) 2017 Intel Corporation\n"\
            "\n"\
            "uio_mkfile = custom_target('igb_uio_makefile',\n"\
            "        output: 'Makefile',\n"\
            "        command: ['touch', '@OUTPUT@'])\n"\
            "\n"\
            "uio_sources = files(\n"\
            "        'igb_uio.c',\n"\
            "        'Kbuild',\n"\
            ")\n"\
            "\n"\
            "custom_target('igb_uio',\n"\
            "        input: uio_sources,\n"\
            "        output: 'igb_uio.ko',\n"\
            "        command: ['make', '-j4', '-C', kernel_build_dir,\n"\
            "                'M=' + meson.current_build_dir(),\n"\
            "                'src=' + meson.current_source_dir(),\n"\
            "                'MODULE_CFLAGS=-include ' + meson.source_root() + '/config/rte_config.h' +\n"\
            "                ' -I' + meson.source_root() + '/lib/eal/include' +\n"\
            "                ' -I' + meson.build_root() +\n"\
            "                ' -I' + meson.current_source_dir(),\n"\
            "           'modules'] + cross_args,\n"\
            "        depends: uio_mkfile,\n"\
            "        install: install,\n"\
            "        install_dir: kernel_install_dir,\n"\
            "        build_by_default: get_option('enable_kmods'))\n")
    if ""!=err:
        return err
    #修改DPDK的CMakelist
    cmakedat,sz_err = maker_public.readTxtFile(vpp_path+"/vpp-"+\
        vpp_ver+"/build/external/packages/dpdk.mk")
    #打开内核模块编译开关
    dstdat = "\n\nDPDK_MESON_ARGS += \"-Denable_kmods=true\"\n\nPIP_DOWNLOAD_DIR"
    cmakedat = cmakedat.replace("\n\nPIP_DOWNLOAD_DIR", dstdat)
    #打开igb_uio.ko的编译
    dstdat = "\n\ndefine dpdk_config_cmds"+\
        "\n\tcp -rf "+vpp_path+"/vpp-"+vpp_ver+"/dpdk-kmods/linux/* $(dpdk_src_dir)/kernel/linux/"+\
        " && \\"+\
        "\n\tsed -i 's/\['\"'\"'kni'\"'\"'\]/\['\"'\"'kni'\"'\"','\"'\"'igb_uio'\"'\"'\]/' $(dpdk_src_dir)/kernel/linux/meson.build"+\
        " && \\"
    cmakedat = cmakedat.replace("\n\ndefine dpdk_config_cmds", dstdat)
    #将ko文件安装到安装目录
    dstdat = "\n\tmeson install && \\"+\
        "\n\tmkdir -p $(dpdk_install_dir)/lib/modules && \\"+\
        "\n\tcp -rf $(dpdk_build_dir)/kernel/linux/igb_uio/igb_uio.ko $(dpdk_install_dir)/lib/modules/ && \\"+\
        "\n\tcp -rf $(dpdk_build_dir)/kernel/linux/kni/rte_kni.ko $(dpdk_install_dir)/lib/modules/"
    cmakedat = cmakedat.replace("\n\tmeson install", dstdat)
    sz_err = maker_public.writeTxtFile(vpp_path+"/vpp-"+vpp_ver+\
        "/build/external/packages/dpdk.mk", 
        cmakedat)
    if "" != sz_err:
        return sz_err
    return ""

    
#功能：下载配置vpp；参数：无；返回：错误码
def config_vpp(vpp_ver, vpp_path, vscode_project_maker):
    if False == os.path.exists(vscode_project_maker+"/vpp-"+vpp_ver+".zip"):
        os.system("rm -rf "+vscode_project_maker+"/vpp-"+vpp_ver)
        if 0 != os.system(\
            "git clone --branch v"+vpp_ver+" https://ghproxy.com/github.com/FDio/vpp.git "+\
            vscode_project_maker+"/vpp-"+vpp_ver):
            os.system("rm -rf "+vscode_project_maker+"/vpp-"+vpp_ver)
            return "Failed to download vpp-"+vpp_ver
        if 0 != os.system(\
            "git clone http://dpdk.org/git/dpdk-kmods "+\
            vscode_project_maker+"/vpp-"+vpp_ver+"/dpdk-kmods"):
            os.system("rm -rf "+vscode_project_maker+"/vpp-"+vpp_ver+"/dpdk-kmods")
            return "Failed to download dpdk-kmods"
        #下载绑定器
        if ""==maker_public.execCmdAndGetOutput("lspci") and \
            False == os.path.exists(vscode_project_maker+"/vpp-"+vpp_ver+"/driverctl"):
            if 0 != os.system("git clone https://gitlab.com/driverctl/driverctl.git "+\
                vscode_project_maker+"/vpp-"+vpp_ver+"/driverctl"):
                return "download driverctl failed"
        if 0 != os.system("cd "+vscode_project_maker+\
            " && zip -r "+"vpp-"+vpp_ver+".zip vpp-"+vpp_ver):
            os.system("rm -f "+vscode_project_maker+"/vpp-"+vpp_ver+".zip")
        os.system("rm -rf "+vscode_project_maker+"/vpp-"+vpp_ver) 
    if False == os.path.exists(vpp_path+"/vpp-"+vpp_ver):
        os.system("unzip -d "+vpp_path+"/ "+
            vscode_project_maker+"/vpp-"+vpp_ver+".zip")
    #设置用户组
    os.system("groupadd -f -r vpp")
    #获取OS版本
    osver = maker_public.getOSName()
    if osver == "centos":
        os.system("yum erase -y epel-release.noarch")
    #修改makefile
    makedat,sz_err = maker_public.readTxtFile(vpp_path+"/vpp-"+vpp_ver+"/Makefile")
    if "" != sz_err:
        return sz_err
    if "centos" == osver:
        makedat = re.sub(" yum[ \\t]+install ", " yum install -y ", makedat)
        makedat = re.sub(" yum[ \\t]+groupinstall ", " yum groupinstall -y ", makedat)
        makedat = re.sub(" dnf[ \\t]+install ", " dnf install -y ", makedat)
        makedat = re.sub(" dnf[ \\t]+groupinstall ", " dnf groupinstall -y ", makedat)
    #设置链接库
    makedat = re.sub("_debug,\\$\\(addsuffix[ ]+-install,.*", \
        "_debug,$(addsuffix -install,$(TARGETS)))\n\t"\
        "-rm -rf /etc/ld.so.conf.d/vpp-debug.conf\n\t"\
        "-echo '"+vpp_path+"/vpp-"+vpp_ver+"/build-root/install-vpp_debug-native/"\
        "vpp/lib64' > /etc/ld.so.conf.d/vpp-debug.conf\n\t"\
        "-ldconfig", makedat)
    makedat = re.sub("_debug,\\$\\(addsuffix[ ]+-wipe,.*", \
        "_debug,$(addsuffix -wipe,$(TARGETS)))\n\t"\
        "-rm -rf /etc/ld.so.conf.d/vpp-debug.conf\n\t"\
        "-ldconfig", makedat)
    sz_err = maker_public.writeTxtFile(vpp_path+"/vpp-"+vpp_ver+"/Makefile", makedat)
    if "" != sz_err:
        return sz_err
    #修改CMakeLists.txt
    #cmakedat,sz_err = maker_public.readTxtFile(vpp_path+"/vpp-"+\
    #    vpp_ver+"/src/CMakeLists.txt")
    #if "" != sz_err:
    #    return sz_err
    #if "ubuntu" == osver:
    #    cmakedat = re.sub("VPP_LIB_VERSION[ \\t]+\\${VPP_VERSION}", 
    #        "VPP_LIB_VERSION \"${VPP_VERSION}\"", cmakedat)
    #    if None == re.search("CMAKE_REQUIRED_LIBRARIES", cmakedat):
    #        cmakedat = re.sub(\
    #            "\\nfind_package[ \\t]*\\([ \\t]*Threads[^\\)]+", 
    #            "\nset(CMAKE_REQUIRED_LIBRARIES \"-lpthread \")"\
    #            "\nfind_package(Threads REQUIRED", cmakedat)         
    #sz_err = maker_public.writeTxtFile(\
    #    vpp_path+"/vpp-"+vpp_ver+"/src/CMakeLists.txt", cmakedat)
    #if "" != sz_err:
    #    return sz_err
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
    #修改DPDK的编译文件和打开内核模块
    return config_dpdk(vpp_ver, vpp_path, vscode_project_maker)


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
    if True == os.path.exists(vpp_path+"/vpp-21.10"):
        if re.search("^2\\..*", sys.version):
            need_continue = \
                raw_input("vpp is already installed, do you want to continue[y/n]:")
        else:
            need_continue = \
                input("vpp is already installed, do you want to continue[y/n]:")
    if "y"==need_continue or "Y"==need_continue:
        szErr = config_vpp("21.10", vpp_path, 
            os.environ["HOME"]+"/vscode_project_maker")
        if "" != szErr:
            print(szErr)
            exit(-1)
        szErr = make_dep("21.10", vpp_path,  os.environ["HOME"]+"/vscode_project_maker")
        if "" != szErr:
            print(szErr)
        else:
            print("config vpp sucess!")
    #生成工程
    szErr = create_vpp_project("21.10", vpp_path,  os.environ["HOME"]+"/vscode_project_maker")
    if "" != szErr:
        print(szErr)
    else:
        print("create vpp project sucess!")
        