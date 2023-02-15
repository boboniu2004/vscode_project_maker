#!/usr/python/bin
# -*- coding: utf-8 -*-


import re
import sys
import maker_public
import centosenv_maker
import ubuntuenv_maker


#功能：获取错误字符串；参数：无；返回：错误字符串
def get_format_str():
        format_str = "osenv_maker:    [--work_mod|--deb_src|--go_proxy|--git_proxy]\n"\
            "            --work_mod [mod]        工作模式，online|offline|config_IP。默认是online\n"\
            "            --ip [192.168.137.xx]   在线模式下第二块网卡的IP地址，hyper-v默认为192.168.137.xx；virtualbox默认为192.168.56.xx网段。\n"\
            "            --deb_src [url]         deb源，默认为http://mirrors.aliyun.com/ubuntu。\n"\
            "            --rpm_src [url]         rpm源，centos7下默认为http://mirrors.163.com/.help/CentOS%s-Base-163.repo；centos8下默认为http://mirrors.aliyun.com/repo/Centos-vault-8.5.2111.repo。\n"\
            "            --epel_src [url]        epel源，只在centos7生效，默认http://mirrors.aliyun.com/repo/epel-7.repo。\n"\
            "            --py_src [host] [url]   python源，默认为host=mirrors.aliyun.com url=http://mirrors.aliyun.com/pypi/simple。\n"\
            "            --go_proxy [url]        go的代理，默认为https://proxy.golang.com.cn。\n"\
            "            --git_proxy [url]       github的代理(如ghproxy.com)，默认为空。\n"
        return format_str


#功能：解析参数；参数：无；返回：参数、错误描述
def parse_argv(szOSName):
    lspci = maker_public.execCmdAndGetOutput("lspci")
    sys_par = {"work_mod":"online",\
        "deb_src":"http://mirrors.aliyun.com/ubuntu",\
        "py_host":"mirrors.aliyun.com",\
        "py_url":"http://mirrors.aliyun.com/pypi/simple",\
        "go_proxy":"https://proxy.golang.com.cn",\
        "git_proxy":""}
    if "ubuntu"==szOSName or "ubuntu-wsl2"==szOSName:
        if "" == lspci:
            sys_par["ip"] = "192.168.137.102"
        else:
            sys_par["ip"] = "192.168.56.102"
    else:
        if "" == lspci:
            sys_par["ip"] = "192.168.137.101"
        else:
            sys_par["ip"] = "192.168.56.101"
        centver,err = centosenv_maker.GetCentosVer()
        if "" != err:
            return sys_par,err
        if "8" == centver:
            sys_par["rpm_src"] = "http://mirrors.aliyun.com/repo/Centos-vault-8.5.2111.repo"
        else:
            sys_par["rpm_src"] = ("http://mirrors.163.com/.help/CentOS%s-Base-163.repo" %centver)
            sys_par["epel_src"] = ("http://mirrors.aliyun.com/repo/epel-%s.repo" %centver)

    format_str = get_format_str()
    #循环解析参数
    pos = 1
    while len(sys.argv) > pos:
        if len(sys.argv) <= pos+1:
            return sys_par,("bad param %s\n" %sys.argv[pos])+format_str
        par_name = sys.argv[pos][2:]
        par_val = sys.argv[pos+1]
        if "--work_mod" == sys.argv[pos]:
            if None == re.search("^(online|offline|config_IP)$",\
                par_val):
                return sys_par,("bad work_mod %s\n" %par_val)+format_str
            sys_par[par_name] = par_val
        elif "--ip" == sys.argv[pos]:
            if None == re.search("^192\\.168\\.137\\.\\d+$", par_val):
                return sys_par,("bad ip %s\n" %par_val)+format_str
            sys_par[par_name] = par_val
        elif "--deb_src" == sys.argv[pos]:
            sys_par[par_name] = par_val
        elif "--py_src" == sys.argv[pos]:
            if len(sys.argv) <= pos+2:
                return sys_par,("bad py_src %s\n" %par_val)+format_str
            sys_par["py_host"] = par_val
            sys_par["py_url"] = sys.argv[pos+2]
            pos = pos+1
        elif "--go_proxy" == sys.argv[pos]:
            sys_par[par_name] = par_val
        elif "--git_proxy" == sys.argv[pos]:
            sys_par[par_name] = par_val
        elif "--rpm_src" == sys.argv[pos]:
            sys_par[par_name] = par_val
        elif "--epel_src" == sys.argv[pos]:
            sys_par[par_name] = par_val
        else:
            return sys_par,("unknow param %s\n" %sys.argv[pos])+format_str
        pos = pos+2
    return sys_par,""


#函数功能：主函数
#函数参数：可执行文件全路径，启动时加入的参数
#函数返回：执行成功返回0，否则返回负值的错误码
if __name__ == "__main__":
    #获取发行版本     
    szOSName = maker_public.getOSName()
    #解析参数
    sys_par,szErr = parse_argv(szOSName)
    if "" != szErr:
        print(szErr)
        exit(-1)
    #执行
    if "config_IP"==sys_par["work_mod"]:
        if "centos" == szOSName:
            szErr = centosenv_maker.InitInternalNet(sys_par["ip"])
        elif "ubuntu" == szOSName:
            szErr = ubuntuenv_maker.InitInternalNet(sys_par["ip"])
        else:
            szErr = "Invaild OS"
    else:
        if "centos" == szOSName:
            szErr = centosenv_maker.InitEnv(sys_par)
        elif "ubuntu"==szOSName or "ubuntu-wsl2"==szOSName:
            szErr = ubuntuenv_maker.InitEnv(sys_par)
        else:
            szErr = "Invaild OS"
    #处理返回
    if 0 < len(szErr):
        print(szErr)
        exit(-1)
    elif "config_IP"==sys_par["work_mod"]:
        print("Config IP finish")
    elif re.search("^2\\..*", sys.version):
        maker_public.do_reboot("make development environment of %s finish, "\
            "press any key to reboot..." %(szOSName))
    else:
        maker_public.do_reboot("make development environment of %s finish, "\
            "press any key to reboot..." %(szOSName))
    exit(0)