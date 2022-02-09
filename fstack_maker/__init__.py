#!/usr/python/bin
# -*- coding: utf-8 -*-

import sys
import re
import os
import multiprocessing
import maker_public


#功能：配置f-stack下的tools中的makefile；参数：无；返回：错误码
def config_tools(fstack_path):
    #修改tools下的makefile
    #修改compat
    makedat,sz_err = maker_public.readTxtFile(fstack_path+"/f-stack"+"/tools/compat/Makefile")
    if "" != sz_err:
        return "config f-stack tools failed"
    makedat = re.sub("\\n\\n\\$\\{OBJS\\}:.*", \
        "\n\n${OBJS}: %.o: %.c ${TOPDIR}/lib/ff_msg.h", makedat)
    sz_err = maker_public.writeTxtFile(fstack_path+"/f-stack"+"/tools/compat/Makefile", makedat)
    if "" != sz_err:
        return "config f-stack tools failed"
    #修改prog.mk
    makedat,sz_err = maker_public.readTxtFile(fstack_path+"/f-stack"+"/tools/prog.mk")
    if "" != sz_err:
        return "config f-stack tools failed"
    makedat = re.sub("\\n\\n\\$\\{PROG\\}:.*", "\n\n${PROGDIR}/${PROG}: ${HEADERS} ${OBJS} "\
        "${TOPDIR}/tools/compat/libffcompat.a", makedat)
    makedat = re.sub("\\nall:[ ]+\\$\\{PROG\\}.*", "\nall: ${PROGDIR}/${PROG}", makedat)
    sz_err = maker_public.writeTxtFile(fstack_path+"/f-stack"+"/tools/prog.mk", makedat)
    if "" != sz_err:
        return "config f-stack tools failed"
    return ""

#功能：配置dpdk；参数：fstack路径、工程路径；返回：错误码
def config_dpdk(fstack_path, vscode_project_maker):
    sz_err = maker_public.get_DPDKscrits(fstack_path+"/f-stack")
    if "" != sz_err:
        return sz_err
    #
    scrits,sz_err = maker_public.readTxtFile(\
        fstack_path+"/f-stack/dpdk_scrits/__init__.py")
    if "" != sz_err:
        return sz_err
    scrits = re.sub("\\n[ \\t]+ASLR_flg[ \\t]+=.*", \
        "\n    ASLR_flg = \"0\"", scrits)    
    return maker_public.writeTxtFile(fstack_path+"/f-stack/dpdk_scrits/__init__.py", 
        scrits)


#功能：下载配置f-stack；参数：无；返回：错误码
def config_fstack(fstack_ver, fstack_path, vscode_project_maker):
    if False == os.path.exists(vscode_project_maker+"/f-stack-"+fstack_ver+".zip"):
        os.system("rm -rf "+vscode_project_maker+"/f-stack-"+fstack_ver)
        if 0 != os.system(\
            "git clone --branch v"+fstack_ver+" https://ghproxy.com/github.com/F-Stack/f-stack.git "+\
            vscode_project_maker+"/f-stack-"+fstack_ver):
            os.system("rm -rf "+vscode_project_maker+"/f-stack-"+fstack_ver)
            return "Failed to download f-stack-"+fstack_ver
        if 0 != os.system("cd "+vscode_project_maker+\
            " && zip -r "+"f-stack-"+fstack_ver+".zip f-stack-"+fstack_ver):
            os.system("rm -f "+vscode_project_maker+"/f-stack-"+fstack_ver+".zip")
        os.system("rm -rf "+vscode_project_maker+"/f-stack-"+fstack_ver) 
    if False == os.path.exists(fstack_path+"/f-stack"):
        os.system("unzip -d "+fstack_path+"/ "+
            vscode_project_maker+"/f-stack-"+fstack_ver+".zip")
        if 0!=os.system("mv  "+fstack_path+"/f-stack-"+fstack_ver+" "+fstack_path+"/f-stack"):
            return "Failed to unzip "+vscode_project_maker+"/f-stack-"+fstack_ver+".zip"
    #构建dpdk初始化脚本
    sz_err = config_dpdk(fstack_path, vscode_project_maker)
    if "" != sz_err:
        return sz_err
    #修改lib下的makefile
    lib_make,sz_err = maker_public.readTxtFile(fstack_path+"/f-stack"+"/lib/Makefile")
    if "" != sz_err:
        return "config f-stack failed"
    if 0 >= len(re.findall("\\n#DEBUG[ \\t]*=|\\nDEBUG[ \\t]*=", lib_make)):
        return "can not find DEBUG"
    if 0 >= len(re.findall("\\n#FF_IPFW[ \\t]*=[ \\t]*1|\\nFF_IPFW[ \\t]*=[ \\t]*1", lib_make)):
        return "can not find FF_IPFW"
    lib_make = re.sub("\\n#DEBUG[ \\t]*=", "\nDEBUG=", lib_make)
    lib_make = re.sub("\\n#FF_IPFW[ \\t]*=[ \\t]*1", "\nFF_IPFW=1", lib_make)
    sz_err = maker_public.writeTxtFile(fstack_path+"/f-stack"+"/lib/Makefile", lib_make)
    if "" != sz_err:
        return "config f-stack failed"
    #修改tools下的makefile
    sz_err = config_tools(fstack_path)
    if "" != sz_err:
        return "config f-stack failed"
    #配置nginx
    nginx_path = maker_public.execCmdAndGetOutput(\
        "cd "+fstack_path+"/f-stack"+"/app/nginx-* && pwd").replace("\n", "")
    if "" == nginx_path:
        return "config f-stack failed"
    cwd_dir = os.getcwd()
    try:
        os.chdir(nginx_path)
        if 0 != os.system("./configure --prefix="+fstack_path+"/f-stack"+"/debug "
            "--with-debug --with-stream --with-stream_ssl_module "
            "--with-ff_module --with-stream_ssl_preread_module "
            "--with-http_v2_module"):
            return "config nginx failed"    
        if 0 != os.system("sed -i \"s/ -Os / -O0 /\" objs/Makefile"):
            return "config nginx failed"    
        if 0 != os.system("sed -i \"s/ -g / -g3 /\" objs/Makefile"):
            return "config nginx failed"    
    finally:
        os.chdir(cwd_dir)
    #为f-stack生成总的make文件
    cpunum = str(multiprocessing.cpu_count())
    fstack_make = \
        "update:"\
            "\n\trm -rf ./example/helloworld*"\
            "\n\trm -rf ./app/"+os.path.basename(nginx_path)+"/objs/nginx"\
	        "\n\tcd ./lib && make"+" -j "+cpunum+\
	        "\n\tcd ./tools && make"+" -j "+cpunum+\
            "\n\tcd ./example && make"+" -j "+cpunum+\
	        "\n\tcd ./app/"+os.path.basename(nginx_path)+" && make"+" -j "+cpunum+\
            "\n\tcp -rf ./app/"+os.path.basename(nginx_path)+"/objs/nginx "+fstack_path+"/f-stack"+"/debug/sbin/"\
            "\n\n"\
        "clean:"\
	        "\n\tcd ./lib && make clean"\
	        "\n\tcd ./tools && make clean"\
            "\n\tcd ./example && make clean"\
	        "\n\tcd ./app/"+os.path.basename(nginx_path)+" && make clean"\
            "\n\tcd ./app/"+os.path.basename(nginx_path)+" && ./configure --prefix="+fstack_path+"/f-stack"+"/debug "\
            "--with-debug --with-stream --with-stream_ssl_module "\
            "--with-ff_module --with-stream_ssl_preread_module "\
            "--with-http_v2_module"\
            "\n\tsed -i \"s/ -Os / -O0 /\" ./app/"+os.path.basename(nginx_path)+"/objs/Makefile"\
            "\n\tsed -i \"s/ -g / -g3 /\" ./app/"+os.path.basename(nginx_path)+"/objs/Makefile"\
            "\n\n"\
        "install:"\
            "\n\trm -rf ./example/helloworld*"\
            "\n\trm -rf ./app/"+os.path.basename(nginx_path)+"/objs/nginx"\
	        "\n\tcd ./lib && make"+" -j "+cpunum+\
	        "\n\tcd ./tools && make"+" -j "+cpunum+\
            "\n\tcd ./example && make"+" -j "+cpunum+\
	        "\n\tcd ./app/"+os.path.basename(nginx_path)+" && make"+" -j "+cpunum+\
	        "\n\tmkdir -p "+fstack_path+"/f-stack"+"/debug/net-tools"\
	        "\n\tcp -rf ./tools/sbin/* "+fstack_path+"/f-stack"+"/debug/net-tools/"\
	        "\n\tcd ./app/"+os.path.basename(nginx_path)+" && make install"\
            "\n\tcp -rf ./config.ini "+fstack_path+"/f-stack"+"/debug/conf/f-stack.conf"\
            "\n"
    sz_err = maker_public.writeTxtFile(fstack_path+"/f-stack"+"/makefile", fstack_make)
    if "" != sz_err:
        return "config f-stack failed" 
    return ""


#功能：制作f-stack工程；参数：无；返回：错误码
def create_fstack_project(fstack_path, vscode_project_maker):
    if 0 != os.system("python3 "+vscode_project_maker+"/__init__.py c app /tmp/nginx"):
        os.system("rm -rf /tmp/nginx")
        return "create f-stack project failed"
    os.system("cp -rf /tmp/nginx/.vscode "+fstack_path+"/f-stack"+"/")
    os.system("rm -rf /tmp/nginx")
    #替换工作目录
    launch,sz_err = maker_public.readTxtFile(fstack_path+"/f-stack"+"/.vscode/"\
        "launch.json")
    if "" != sz_err:
        return "create f-stack project failed"
    launch = re.sub("\\$\\{workspaceFolder\\}/debug", 
        "${workspaceFolder}/debug/sbin", launch)
    launch = re.sub("\"\\$\\{workspaceFolder\\}\"", 
        "\"${workspaceFolder}/debug/sbin\"", launch)
    sz_err = maker_public.writeTxtFile(fstack_path+"/f-stack"+"/.vscode/"\
        "launch.json", launch)
    if "" != sz_err:
        return "create f-stack project failed"
    #替换编译TAG
    tasks,sz_err = maker_public.readTxtFile(fstack_path+"/f-stack"+"/.vscode/"\
        "tasks.json")
    if "" != sz_err:
        return "create f-stack project failed"
    tasks = re.sub("\"debug\"", "\"update\"", tasks)
    #增加安装任务
    tasks = re.sub("\"tasks\":[ \\t]+\\[", 
            "\"tasks\": ["\
            "\n        {"\
            "\n            \"type\": \"shell\","\
            "\n            \"label\": \"gcc install active file\","\
            "\n            \"command\": \"/usr/bin/make\","\
            "\n            \"args\": ["\
            "\n                \"-f\","\
            "\n                \"${workspaceFolder}/makefile\","\
            "\n                \"install\""\
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
    sz_err = maker_public.writeTxtFile(fstack_path+"/f-stack"+"/.vscode/"\
        "tasks.json", tasks)
    if "" != sz_err:
        return "create f-stack project failed"
    return ""

#功能：制作f-stack工程；参数：无；返回：错误码
def correct_fstack_code(fstack_path):
    match_type = ""
    #查找
    time_path = "/usr/include/x86_64-linux-gnu/sys/time.h"
    if False == os.path.isfile(time_path):
        time_path = "/usr/include/sys/time.h"
    if False == os.path.isfile(time_path):
        return "Can not find time.h"
    time_cont,sz_err = maker_public.readTxtFile(time_path)
    if ""!=sz_err:
        return sz_err
    gettimeofday_ret = re.search("gettimeofday[ \\t\\n]*\\(([^\\)]+)",time_cont)
    if None == gettimeofday_ret:
        return ""
    search_ret = re.search(",[ \\t\\n]*void[ \\t\\n]*\\*",gettimeofday_ret[1])
    if None == search_ret:
        search_ret = re.search(",[ \\t\\n]*__timezone_ptr_t[ \\t\\n]*",gettimeofday_ret[1])
        if None == search_ret:
            return ""
        else:
            match_type = "centos"
    else:
        match_type = "ubuntu"
    #替换
    nginx_path = maker_public.execCmdAndGetOutput(\
        "cd "+fstack_path+"/f-stack"+"/app/nginx-* && pwd").replace("\n", "")
    if "" == nginx_path:
        return "config f-stack failed"
    ff_mod_cont,sz_err = maker_public.readTxtFile(nginx_path+\
        "/src/event/modules/ngx_ff_module.c")
    if ""!=sz_err:
        return sz_err
    if "ubuntu" == match_type:
        ff_mod_cont = re.sub("gettimeofday[ \\t\\n]*\\(([^\\)]+)", 
            "gettimeofday(struct timeval *tv, void *tz", ff_mod_cont, 1)
    else:
        ff_mod_cont = re.sub("gettimeofday[ \\t\\n]*\\(([^\\)]+)", 
            "gettimeofday(struct timeval *__restrict tv, __timezone_ptr_t tz", 
            ff_mod_cont, 1)        
    sz_err = maker_public.writeTxtFile(nginx_path+\
        "/src/event/modules/ngx_ff_module.c", ff_mod_cont)
    return sz_err

#功能：导入路径参数；参数：无；返回：错误码
def export_path(fstack_path):
    #读取
    profile,sz_err = maker_public.readTxtFile(os.environ["HOME"]+"/.bashrc")
    if "" != sz_err:
        return sz_err
    #修改
    if 0 >= len(re.findall("\nexport[ \\t]+FF_PATH[ \\t]*=.+", profile)):
        profile += "\nexport FF_PATH="+fstack_path+"/f-stack"
    else:
        profile = re.sub("\nexport[ \\t]+FF_PATH[ \\t]*=.+", 
            "\nexport FF_PATH="+fstack_path+"/f-stack", profile)
    if 0 >= len(re.findall("\nexport[ \\t]+FF_DPDK[ \\t]*=.+", profile)):
        profile += "\nexport FF_DPDK=/usr/local/dpdk"
    else:
        profile = re.sub("\nexport[ \\t]+FF_DPDK[ \\t]*=.+", 
            "\nexport FF_DPDK=/usr/local/dpdk", profile)
    #写入
    sz_err = maker_public.writeTxtFile(os.environ["HOME"]+"/.bashrc", profile)
    if "" != sz_err:
        return sz_err
    return ""


#功能：主函数；参数：无；返回：错误描述
def makeropensrc():
    fstack_path = os.getcwd()
    if 2<len(sys.argv):
        fstack_path = sys.argv[2]
    fstack_path = os.path.abspath(fstack_path)
    if False==os.path.isdir(fstack_path):
        return "Invaild f-stack path"
    #检测是否安装了DPDK
    if False == os.path.exists("/usr/local/dpdk"):
        return "please install DPDK"
    #初始化f-stack
    need_continue = "y"
    if True == os.path.exists(fstack_path+"/f-stack"):
        if re.search("^2\\..*", sys.version):
            need_continue = \
                raw_input("f-stack is already installed, do you want to continue[y/n]:")
        else:
            need_continue = \
                input("f-stack is already installed, do you want to continue[y/n]:")
    if "y"==need_continue or "Y"==need_continue:
        szErr = config_fstack("1.21", fstack_path, os.environ["HOME"]+"/vscode_project_maker")
        if "" != szErr:
            return szErr
        print("config f-stack sucess!")
        szErr = create_fstack_project(fstack_path, os.environ["HOME"]+"/vscode_project_maker")
        if "" != szErr:
            return szErr
        print("create f-stack project sucess!")
        szErr = correct_fstack_code(fstack_path)
        if "" != szErr:
            return szErr
        print("correct fstack code sucess!")
        szErr = export_path(fstack_path)
        if "" != szErr:
            return szErr
        print("export path sucess!")
    #
    return ""