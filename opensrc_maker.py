#!/usr/python/bin
# -*- coding: utf-8 -*-


import sys
import os
import fstack_maker
import vpp_maker


#函数功能：主函数
#函数参数：可执行文件全路径，启动时加入的参数
#函数返回：执行成功返回0，否则返回负值的错误码
if __name__ == "__main__":
    error = "opensrc_maker: [ vpp [vpp path] ] | [ f-stack [dpdk path] [hyperscan path] ]"
    #获取发行版本
    if 2>len(sys.argv):
        print(error)
        exit(-1)
    elif "f-stack"==sys.argv[1]:
        error = fstack_maker.makeropensrc()
    elif "vpp"==sys.argv[1]:
        error  = vpp_maker.makeropensrc()
    if ""!=error:
        print(error)
        exit(-1)
    exit(0)