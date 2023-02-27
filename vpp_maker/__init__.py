#!/usr/python/bin
# -*- coding: utf-8 -*-

import os
import re
import sys
import maker_public
import platform


#功能：安装依赖；参数：无；返回：错误码
def make_dep(vpp_path):
    #非root模式直接退出
    if 0 != os.geteuid():
        return ""
    
    cpuarch = platform.machine()
    osname = maker_public.getOSName()
    #设置用户组
    #os.system("groupadd -f -r vpp")
    #获取OS版本
    osver = maker_public.getOSName()
    if osver == "centos":
        os.system("yum erase -y epel-release.noarch")
    if osname=="ubuntu" or osname=="ubuntu-wsl2":
        os.system("apt-get --purge autoremove vpp-ext-deps."+cpuarch)
        if 0!=os.system("cd "+vpp_path+"/vpp && make UNATTENDED=y install-dep"):
            return "make install-dep failed!"
    else:
        os.system("yum -y erase vpp-ext-deps."+cpuarch)
        if 0 != os.system("cd "+vpp_path+"/vpp && make install-dep"):
            return "make install-dep failed!"
    return ""


#功能：制作vpp工程；参数：无；返回：错误码
def create_vpp_project(vpp_path, work_path):
    if 0 != os.system(maker_public.get_python()+" "+work_path+\
        "/__init__.py c app /tmp/vpp"):
        os.system("rm -rf /tmp/vpp")
        return "create vpp project failed"
    os.system("cp -rf /tmp/vpp/.vscode "+ vpp_path+"/vpp/")
    os.system("rm -rf /tmp/vpp")
    #替换工作目录
    launch,sz_err = maker_public.readTxtFile(vpp_path+"/vpp/.vscode/"
        "launch.json")
    if "" != sz_err:
        return "create vpp project failed"
    launch = re.sub("\\$\\{workspaceFolder\\}/debug", 
        "${workspaceFolder}/build-root/install-vpp_debug-native/vpp/bin", launch)
    launch = re.sub("\"\\$\\{workspaceFolder\\}\"", 
        "\"${workspaceFolder}/build-root/install-vpp_debug-native/vpp/bin\"", launch)
    launch = re.sub("\"args\"[ \\t]*:[ \\t]*\\[[^\\]]*\\],", 
        "\"args\": [\"-c\",\"${workspaceFolder}/build-root/install-vpp_debug-native/vpp/etc/vpp/startup.conf\"],", launch)
    sz_err = maker_public.writeTxtFile(vpp_path+"/vpp/.vscode/"
        "launch.json", launch)
    if "" != sz_err:
        return "create vpp project failed"
    #替换编译TAG
    tasks,sz_err = maker_public.readTxtFile(vpp_path+"/vpp/.vscode/"
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
            "\n                \"${workspaceFolder}/dpdk_scrits/__init__.py\","\
            "\n                \"initenv\","\
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
    sz_err = maker_public.writeTxtFile(vpp_path+"/vpp/.vscode/"
        "tasks.json", tasks)
    if "" != sz_err:
        return "create vpp project failed"
    return ""


#功能：配置dpdk；参数：vpp路径、工程路径；返回：错误码
def config_dpdk(vpp_path, work_path):
    #拷贝dpdk初始化工具
    sz_err = maker_public.get_DPDKscrits(vpp_path+"/vpp")
    if "" != sz_err:
        return sz_err
    #
    rep_list = [["\\n[ \\t]+ASLR_flg[ \\t]+=.*", "\n    ASLR_flg = \"0\""]]
    return maker_public.replace_content(vpp_path+"/vpp/dpdk_scrits/__init__.py",
        rep_list)

    
#功能：下载配置vpp；参数：无；返回：错误码
def config_vpp(vpp_ver, vpp_path, work_path, git_proxy):
    if False == os.path.exists(work_path+"/vpp-"+vpp_ver+".zip"):
        os.system("rm -rf "+work_path+"/vpp-"+vpp_ver)
        if 0 != os.system(\
            "git clone --branch v%s https://%sgithub.com/FDio/vpp.git "\
            "%s/vpp-%s" %(vpp_ver,git_proxy,work_path,vpp_ver)):
            os.system("rm -rf "+work_path+"/vpp-"+vpp_ver)
            return "Failed to download vpp-"+vpp_ver
        if 0 != os.system(\
            "git clone http://dpdk.org/git/dpdk-kmods "+\
            work_path+"/vpp-"+vpp_ver+"/dpdk-kmods"):
            os.system("rm -rf "+work_path+"/vpp-"+vpp_ver+"/dpdk-kmods")
            return "Failed to download dpdk-kmods"
        if 0 != os.system("cd "+work_path+\
            " && zip -r "+"vpp-"+vpp_ver+".zip vpp-"+vpp_ver):
            os.system("rm -f "+work_path+"/vpp-"+vpp_ver+".zip")
        os.system("rm -rf "+work_path+"/vpp-"+vpp_ver) 
    if False == os.path.exists(vpp_path+"/vpp"):
        if 0!=os.system("unzip -d "+vpp_path+"/ "+
            work_path+"/vpp-"+vpp_ver+".zip"):
            return "Failed to unzip "+work_path+"/vpp-"+vpp_ver+".zip"
        if 0!=os.system("mv  "+vpp_path+"/vpp-"+vpp_ver+" "+vpp_path+"/vpp"):
            return "Failed to unzip "+work_path+"/vpp-"+vpp_ver+".zip"
    #修改makefile
    makedat,sz_err = maker_public.readTxtFile(vpp_path+"/vpp"+"/Makefile")
    if "" != sz_err:
        return sz_err
    if "centos" == osver:
        makedat = re.sub(" yum[ \\t]+install ", " yum install -y ", makedat)
        makedat = re.sub(" yum[ \\t]+groupinstall ", " yum groupinstall -y ", makedat)
        makedat = re.sub(" dnf[ \\t]+install ", " dnf install -y ", makedat)
        makedat = re.sub(" dnf[ \\t]+groupinstall ", " dnf groupinstall -y ", makedat)
    sz_err = maker_public.writeTxtFile(vpp_path+"/vpp"+"/Makefile", makedat)
    if "" != sz_err:
        return sz_err
    #替换github.com
    pkgmkfiles = os.listdir(vpp_path+"/vpp"+"/build/external/packages/")
    for mkfile in pkgmkfiles:
        if False == os.path.isfile(\
            vpp_path+"/vpp"+"/build/external/packages/"+mkfile):
            continue
        if None == re.search(".+\\.mk$", mkfile):
            continue
        mkcont,err = maker_public.readTxtFile(\
            vpp_path+"/vpp"+"/build/external/packages/"+mkfile)
        if ""!=err:
            return err
        if "" != git_proxy:
            mkcont = re.sub("://github\\.com", "://%sgithub.com", mkcont)
        err = maker_public.writeTxtFile(vpp_path+"/vpp"+"/build/external/packages/"+mkfile, 
            mkcont)
        if ""!=err:
            return err
    #修改DPDK的编译文件
    return config_dpdk(vpp_path, work_path)


#功能：主函数；参数：无；返回：错误描述
def makeropensrc(work_path, ins_path, git_proxy):
    #初始化vpp
    need_continue = "y"
    if True == os.path.exists(ins_path+"/vpp"):
        if re.search("^2\\..*", sys.version):
            need_continue = \
                raw_input("vpp is already installed, do you want to continue[y/n]:")
        else:
            need_continue = \
                input("vpp is already installed, do you want to continue[y/n]:")
    if "y"==need_continue or "Y"==need_continue:
        szErr = config_vpp(maker_public.getVer("vpp"), ins_path, work_path, git_proxy)
        if "" != szErr:
            return szErr
        szErr = make_dep(ins_path)
        if "" != szErr:
            return szErr
        print("config vpp sucess!")
        #生成工程
        szErr = create_vpp_project(ins_path, work_path)
        if "" != szErr:
            return szErr
        print("create vpp project sucess!")
    #
    return ""
        