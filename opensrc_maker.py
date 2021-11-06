#!/usr/python/bin
# -*- coding: utf-8 -*-


import sys
import os
import fstack_maker


#函数功能：主函数
#函数参数：可执行文件全路径，启动时加入的参数
#函数返回：执行成功返回0，否则返回负值的错误码
if __name__ == "__main__":
    error = "opensrc_maker:  opensrc[f-stack|vpp] [private parameter]"
    #获取发行版本
    if 2>len(sys.argv):
        print(error)
    elif "f-stack"==sys.argv[2]:
        fstack_maker.makeropensrc()
    else:
        print(error)