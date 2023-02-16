#!/usr/python/bin
# -*- coding: utf-8 -*-


import sys
import re
import os
import dpdk_maker
import hyperscan_maker
import fstack_maker
import vpp_maker
import gperftools_maker


#功能：获取错误字符串；参数：无；返回：错误字符串
def get_format_str():
        format_str = "osenv_maker:    [--dpdk|--hyperscan|--gperftools|--fstack|--vpp|--ins_path|--wor_mod]\n"\
            "            --dpdk        [normal|meson]         安装dpdk，可选传统编译模式，或者meson编译模式。默认normal\n"\
            "            --hyperscan                          安装hyperscan。\n"\
            "            --gperftools                         安装google的性能分析工具，包括tcmalloc内存池。\n"\
            "            --fstack      [dpdk_path] [hs_path]  安装f-stack用户态协议栈，需要设置dpdk路径和hyperscan路径。\n"\
            "            --vpp                                安装VPP框架。\n"\
            "            --ins_path    [path]                 安装目录，必须指明，如/usr/local。\n"\
            "            --git_proxy   [url]                  github的代理(如ghproxy.com)，默认为空。\n"
        return format_str


#功能：解析参数；参数：无；返回：参数、错误描述
def parse_argv():
    sys_par = {"git_proxy":""}

    format_str = get_format_str()
    #循环解析参数
    pos = 1
    while len(sys.argv) > pos:
        if "--dpdk" == sys.argv[pos]:
            if len(sys.argv) <= pos+1:
                return sys_par,("bad param %s\n" %sys.argv[pos])+format_str
            if None == re.search("^(normal|meson)$", sys.argv[pos+1]):
                return sys_par,("bad param %s\n" %sys.argv[pos])+format_str
            sys_par["opensrc"] = "dpdk"
            sys_par["dpdk_ctype"] = sys.argv[pos+1]
            pos = pos+2
        elif "--fstack" == sys.argv[pos]:
            if len(sys.argv) <= pos+2:
                return sys_par,("bad param %s\n" %sys.argv[pos])+format_str
            if False == os.path.exists(sys.argv[pos+1]):
                return sys_par,("bad param %s\n" %sys.argv[pos])+format_str
            if False == os.path.exists(sys.argv[pos+2]):
                return sys_par,("bad param %s\n" %sys.argv[pos])+format_str
            sys_par["opensrc"] = "fstack"
            sys_par["dpdk_path"] = sys.argv[pos+1]
            sys_par["hs_path"] = sys.argv[pos+2]
            pos = pos+3
        elif "--gperftools" == sys.argv[pos] or "--hyperscan" == sys.argv[pos] or \
            "--vpp" == sys.argv[pos]:
            sys_par["opensrc"] = sys.argv[pos][2:]
            pos = pos+1
        elif "--ins_path" == sys.argv[pos]:
            if len(sys.argv) <= pos+1:
                return sys_par,("bad param %s\n" %sys.argv[pos])+format_str
            if False == os.path.exists(sys.argv[pos+1]):
                return sys_par,("bad param %s\n" %sys.argv[pos])+format_str
            sys_par["ins_path"] = sys.argv[pos+1]
            pos = pos+2
        elif "--git_proxy" == sys.argv[pos]:
            if len(sys.argv) <= pos+1:
                return sys_par,("bad param %s\n" %sys.argv[pos])+format_str
            sys_par["git_proxy"] = sys.argv[pos+1]
            pos = pos+2
        else:
            return sys_par,("unknow param %s\n" %sys.argv[pos])+format_str
    #检查参数正确性
    if "" != sys_par["git_proxy"] and "/" != sys_par["git_proxy"][-1]:
         sys_par["git_proxy"] =  sys_par["git_proxy"]+"/"
    if None == sys_par["ins_path"]:
        return sys_par,"need ins_path param.\n"+format_str
    if None == sys_par["opensrc"]:
        return sys_par,"need --dpdk|--hyperscan|--gperftools|--fstack|--vpp param.\n"\
            +format_str
    return sys_par,""


#函数功能：主函数
#函数参数：可执行文件全路径，启动时加入的参数
#函数返回：执行成功返回0，否则返回负值的错误码
if __name__ == "__main__":
    #读取参数
    sys_par, err = parse_argv()
    if "" != err:
       print(err)
       exit(-1)        
    #进行检测
    if "dpdk"==sys_par["opensrc"]:
        err = dpdk_maker.makeropensrc(sys_par["ins_path"], sys_par["dpdk_ctype"], \
            sys_par["git_proxy"])
    elif "hyperscan"==sys_par["opensrc"]:
        err = hyperscan_maker.makeropensrc(sys_par["ins_path"], sys_par["git_proxy"])
    elif "gperftools"==sys_par["opensrc"]:
        err = gperftools_maker.makeropensrc(sys_par["ins_path"], sys_par["git_proxy"])
    elif "fstack"==sys_par["opensrc"]:
        err = fstack_maker.makeropensrc(sys_par["ins_path"],\
            sys_par["dpdk_path"],sys_par["hs_path"], sys_par["git_proxy"])
    elif "vpp"==sys_par["opensrc"]:
        err = vpp_maker.makeropensrc(sys_par["ins_path"], sys_par["git_proxy"])
    else:
        err = ("bad opensrc %s.\b%s" %(sys_par["opensrc"],get_format_str()))
    if ""!=err:
        print(err)
        exit(-1)
    exit(0)