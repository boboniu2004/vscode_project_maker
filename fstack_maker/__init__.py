#!/usr/python/bin
# -*- coding: utf-8 -*-

import sys
import re
import os
import maker_public
import platform


#功能：配置f-stack下的tools中的makefile；参数：stack路径；返回：错误码
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
    makedat = re.sub("-lpthread[ \\t]+-lnuma[ \\t]*\\n", "-lpthread -lnuma -lpcap\n", makedat)
    sz_err = maker_public.writeTxtFile(fstack_path+"/f-stack"+"/tools/prog.mk", makedat)
    if "" != sz_err:
        return "config f-stack tools failed"
    return ""

#功能：配置f-stack下的example；参数：fstack路径；返回：错误码
def config_example(fstack_path):
    sz_err = maker_public.replace_content(fstack_path+"/f-stack/example/Makefile",
        [
            ["-pthread[ \\t]+-lnuma[ \\t]*\\n", "-pthread -lnuma -lpcap\n"],
        ])
    if "" != sz_err:
        return "config f-stack example failed"
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
    sz_err = maker_public.download_src("f-stack", "v", fstack_ver, \
        "https://ghproxy.com/github.com/F-Stack/f-stack.git", vscode_project_maker, None)
    if "" != sz_err:
        return sz_err
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
    if 0 >= len(re.findall("\\n#FF_IPFW[ \\t]*=[ \\t]*1|\\nFF_IPFW[ \\t]*=[ \\t]*1", lib_make)):
        return "can not find FF_IPFW"
    if 0 >= len(re.findall("\\nifndef[ \\t]+DEBUG\\nHOST_CFLAGS[ \\t]*=", lib_make)):
        return "can not find HOST_CFLAGS"
    lib_make = re.sub("\\n#FF_IPFW[ \\t]*=[ \\t]*1", "\nFF_IPFW=1", lib_make)
    if None == re.search(\
        "\\nifndef[ \\t]+DEBUG\\nHOST_CFLAGS[ \\t]*=[ \\t]*-DNDEBUG[ \\t] ", lib_make):
        lib_make = re.sub("\\nifndef[ \\t]+DEBUG\\nHOST_CFLAGS[ \\t]*=", 
            "\nifndef DEBUG\nHOST_CFLAGS = -DNDEBUG ", lib_make)
    sz_err = maker_public.writeTxtFile(fstack_path+"/f-stack"+"/lib/Makefile", lib_make)
    if "" != sz_err:
        return "config f-stack failed"
    #修改tools下的makefile
    sz_err = config_tools(fstack_path)
    if "" != sz_err:
        return sz_err
    #修改example
    sz_err = config_example(fstack_path)
    if "" != sz_err:
        return sz_err
    #配置nginx
    nginx_path = maker_public.execCmdAndGetOutput(\
        "cd "+fstack_path+"/f-stack"+"/app/nginx-* && pwd").replace("\n", "")
    if "" == nginx_path:
        return "config f-stack failed"
    #为f-stack生成总的make文件
    fstack_make = \
        "DEBUG_FLAG:=\"-O0 -gdwarf-2 -g3 -Wno-format-truncation\"\n"\
        "EXIST_DBG := $(shell if [ -d "+fstack_path+"/f-stack"+"/debug ]; then echo \"exist\"; else echo \"noexist\"; fi)\n\n"\
        "debug:"\
            "\n\trm -rf ./example/helloworld*"\
            "\n\trm -rf ./app/"+os.path.basename(nginx_path)+"/objs/nginx"\
	        "\n\tcd ./lib && make"+" DEBUG=$(DEBUG_FLAG) -j $(nproc)"\
	        "\n\tcd ./tools && make"+" DEBUG=$(DEBUG_FLAG) -j $(nproc)"\
            "\n\tcd ./example && make"+" DEBUG=$(DEBUG_FLAG) -j $(nproc)"\
	        "\n\tcd ./app/"+os.path.basename(nginx_path)+" && make"+" -j $(nproc)"\
            "\nifeq (\"$(EXIST_DBG)\", \"noexist\")"\
	        "\n\tmkdir -p "+fstack_path+"/f-stack"+"/debug/net-tools"\
	        "\n\tcd ./app/"+os.path.basename(nginx_path)+" && make install"\
            "\n\tcp -rf ./config.ini "+fstack_path+"/f-stack"+"/debug/conf/f-stack.conf"\
            "\n\tmkdir -p "+fstack_path+"/f-stack"+"/debug/lib"\
            "\nendif"\
            "\n\tcp $(FF_HS)/lib/libhs.so "+fstack_path+"/f-stack"+"/debug/lib/libhs.so"\
            "\n\tcp -rf ./tools/sbin/* "+fstack_path+"/f-stack"+"/debug/net-tools/"\
            "\n\tcp -rf ./app/"+os.path.basename(nginx_path)+"/objs/nginx "+fstack_path+"/f-stack"+"/debug/sbin/"\
            "\n\n"\
        "release:"\
	        "\n\tcd ./lib && make clean"\
	        "\n\tcd ./tools && make clean"\
	        "\n\tcd ./app/"+os.path.basename(nginx_path)+" && make clean"\
            "\n\tcd ./app/"+os.path.basename(nginx_path)+" && ./configure "\
            "--prefix="+fstack_path+"/f-stack"+"/release "\
            "--with-stream --with-stream_ssl_module "\
            "--with-ff_module --with-stream_ssl_preread_module "\
            "--with-http_v2_module"\
            "\n\tsed -i \"s/-lnuma/-lnuma -lpcap/\" ./app/"+os.path.basename(nginx_path)+"/objs/Makefile"\
	        "\n\tcd ./lib && make"+" -j $(nproc)"\
	        "\n\tcd ./tools && make"+" -j $(nproc)"\
	        "\n\tcd ./app/"+os.path.basename(nginx_path)+" && make"+" -j $(nproc)"\
	        "\n\tmkdir -p "+fstack_path+"/f-stack"+"/release/net-tools"\
	        "\n\tcp -rf ./tools/sbin/* "+fstack_path+"/f-stack"+"/release/net-tools/"\
	        "\n\tcd ./app/"+os.path.basename(nginx_path)+" && make install"\
            "\n\tcp -rf ./config.ini "+fstack_path+"/f-stack"+"/release/conf/f-stack.conf"\
            "\n\tmkdir -p "+fstack_path+"/f-stack"+"/release/lib"\
            "\n\tcp $(FF_HS)/lib/libhs.so "+fstack_path+"/f-stack"+"/release/lib/libhs.so"\
            "\n\tcp -rf ./app/"+os.path.basename(nginx_path)+"/objs/nginx "+fstack_path+"/f-stack"+"/release/sbin/"\
            "\n\n"\
        "clean:"\
	        "\n\tcd ./lib && make clean"\
	        "\n\tcd ./tools && make clean"\
            "\n\tcd ./example && make clean"\
	        "\n\tcd ./app/"+os.path.basename(nginx_path)+" && make clean"\
            "\n\tcd ./app/"+os.path.basename(nginx_path)+" && ./configure "\
            "--prefix="+fstack_path+"/f-stack"+"/debug "\
            "--with-debug --with-stream --with-stream_ssl_module "\
            "--with-ff_module --with-stream_ssl_preread_module "\
            "--with-http_v2_module"\
            "\n\tsed -i \"s/-lnuma/-lnuma -lpcap/\" ./app/"+os.path.basename(nginx_path)+"/objs/Makefile"\
            "\n\tsed -i \"s/ -Os / -O0 /\" ./app/"+os.path.basename(nginx_path)+"/objs/Makefile"\
            "\n\tsed -i \"s/ -g / -g3 /\" ./app/"+os.path.basename(nginx_path)+"/objs/Makefile"\
            "\n\n"\
            "\n.PHONY: debug release clean\n"
    sz_err = maker_public.writeTxtFile(fstack_path+"/f-stack"+"/makefile", fstack_make)
    if "" != sz_err:
        return "config f-stack failed"
    #配置nginx
    os.system("cd "+fstack_path+"/f-stack/app/"+os.path.basename(nginx_path)+" && ./configure")
    if 0 != os.system("cd "+fstack_path+"/f-stack && make clean"):
        return "config f-stack failed"
    return ""


#功能：制作f-stack工程的c_cpp_properties.json文件；参数：DPDK和hyperscan路径；返回：错误码
def create_fstack_properties(fstack_path):
    properties,sz_err = maker_public.readTxtFile(fstack_path+"/f-stack"+"/.vscode/"\
        "c_cpp_properties.json")
    if "" != sz_err:
        return "create f-stack project failed"
    properties = re.sub("\\n                [^/]/usr/local/dpdk/include", 
        "\n                \"${FF_DPDK}/include\","\
        "\n                \"${FF_HS}/include", properties)
    sz_err = maker_public.writeTxtFile(fstack_path+"/f-stack"+"/.vscode/"\
        "c_cpp_properties.json", properties)
    if "" != sz_err:
        return "create f-stack project failed"
    return ""


#功能：制作f-stack工程；参数：无；返回：错误码
def create_fstack_project(fstack_path, vscode_project_maker):
    if 0 != os.system(maker_public.get_python()+" "+vscode_project_maker+\
        "/__init__.py c app-dpdk /tmp/nginx"):
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
    tasks = re.sub("\"O=debug\"", "\"debug\"", tasks)
    tasks = re.sub("\"O=clean\"", "\"clean\"", tasks)
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
    sz_err = maker_public.writeTxtFile(fstack_path+"/f-stack"+"/.vscode/"\
        "tasks.json", tasks)
    if "" != sz_err:
        return "create f-stack project failed"
    return create_fstack_properties(fstack_path)


#功能：修改ff_host_interface.c文件；参数：fstack安装路径；返回：错误码
def correct_ff_host_interface(fstack_path):
    src_cont,sz_err = maker_public.readTxtFile(fstack_path+"/f-stack/lib/ff_host_interface.c")
    if ""!=sz_err:
        return sz_err
    if None != re.search("#ifndef[ \\t]+NDEBUG", src_cont):
        return ""
    src_cont  = re.sub(
        "\\n[ \\t]*int[ \\t]+rv[ \\t]*;",
        "\n    int rv = 0;",
        src_cont, 1)
    src_cont = re.sub(
        "\\n[ \\t]*rv[ \\t]*=[ \\t]*clock_gettime[ \\t]*\\([^\\)]+\\)[ \\t]*;[ \\t]*"\
        "\\n[ \\t]*assert[ \\t]*\\([^\\)]+\\)[ \\t]*;[ \\t]*", 
        "\n#ifndef NDEBUG"\
        "\n    rv = clock_gettime(host_id, &ts);"\
        "\n    assert(0 == rv);"\
        "\n#else"\
        "\n    clock_gettime(host_id, &ts);"\
        "\n#endif", 
        src_cont, 1) 
    src_cont = re.sub(
        "\\n[ \\t]*int[ \\t]+rv[ \\t]*=[ \\t]*clock_gettime[ \\t]*\\([^\\)]+\\)[ \\t]*;[ \\t]*"\
        "\\n[ \\t]*assert[ \\t]*\\([^\\)]+\\)[ \\t]*;[ \\t]*",
        "\n#ifndef NDEBUG"\
        "\n    int rv = clock_gettime(CLOCK_REALTIME, &current_ts);"\
        "\n    assert(rv == 0);"\
        "\n#else"\
        "\n    clock_gettime(CLOCK_REALTIME, &current_ts);"\
        "\n#endif",
        src_cont, 1)   
    sz_err = maker_public.writeTxtFile(
        fstack_path+"/f-stack/lib/ff_host_interface.c",src_cont)
    return sz_err


#功能：制作f-stack工程；参数：fstack安装路径；返回：错误码
def correct_fstack_code(fstack_path):
    cpuarch = platform.machine()
    match_type = ""
    #查找
    time_path = "/usr/include/"+cpuarch+"-linux-gnu/sys/time.h"
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
    if "" != sz_err:
        return sz_err
    return correct_ff_host_interface(fstack_path)


#功能：导入路径参数；参数：无；返回：错误码
def export_path(fstack_path, dpdk_path, hs_path):
    #读取
    profile,sz_err = maker_public.readTxtFile(os.environ["HOME"]+"/.bashrc")
    if "" != sz_err:
        return sz_err
    #修改
    if 0 >= len(re.findall("\\nexport[ \\t]+FF_PATH[ \\t]*=.+", profile)):
        profile += "\nexport FF_PATH="+fstack_path+"/f-stack"
    else:
        profile = re.sub("\\nexport[ \\t]+FF_PATH[ \\t]*=.+", 
            "\nexport FF_PATH="+fstack_path+"/f-stack", profile)
    if 0 >= len(re.findall("\\nexport[ \\t]+FF_DPDK[ \\t]*=.+", profile)):
        profile += "\nexport FF_DPDK="+dpdk_path
    else:
        profile = re.sub("\\nexport[ \\t]+FF_DPDK[ \\t]*=.+", 
            "\nexport FF_DPDK="+dpdk_path, profile)
    if "" != hs_path:
        if 0 >= len(re.findall("\\nexport[ \\t]+FF_HS[ \\t]*=.+", profile)):
            profile += "\nexport FF_HS="+hs_path
        else:
            profile = re.sub("\\nexport[ \\t]+FF_HS[ \\t]*=.+", 
                "\nexport FF_HS="+hs_path, profile)
    else:
            profile = re.sub("\\nexport[ \\t]+FF_HS[ \\t]*=.+", "", profile)        
    #写入
    sz_err = maker_public.writeTxtFile(os.environ["HOME"]+"/.bashrc", profile)
    return sz_err


#功能：主函数；参数：无；返回：错误描述
def makeropensrc():
    fstack_path = os.getcwd()
    if 2<len(sys.argv):
        fstack_path = sys.argv[2]
    if False==os.path.isdir(fstack_path):
        return "Invaild f-stack path"
    fstack_path = os.path.abspath(fstack_path)
    dpdk_path = "/usr/local/dpdk"
    if 3<len(sys.argv):
        dpdk_path = sys.argv[3]
    if False==os.path.isdir(dpdk_path):
        return "Invaild dpdk path"
    dpdk_path = os.path.abspath(dpdk_path)
    hs_path = ""
    if 4<len(sys.argv):
        hs_path = sys.argv[4]
    if "" != hs_path:
        if False==os.path.isdir(hs_path):
            return "Invaild hyperscan path"
        hs_path = os.path.abspath(hs_path)
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
        szErr = config_fstack(maker_public.getVer("f-stack"), fstack_path, \
            os.environ["HOME"]+"/vscode_project_maker")
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
        szErr = export_path(fstack_path, dpdk_path, hs_path)
        if "" != szErr:
            return szErr
        print("export path sucess!")
    #
    return ""