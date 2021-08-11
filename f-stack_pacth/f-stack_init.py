#!/usr/python/bin
# -*- coding: utf-8 -*-

import os
import re
import sys

#功能：读取一个文本文件；参数：待读取的文件；返回：读取到的内容，错误描述
def readTxtFile(szSrcFile):
    try:
        CurFile = open(szSrcFile, "r")
        szContent = CurFile.read()
        CurFile.close()
    except:
        return "", ("Exception while try to reading %s"  %(szSrcFile))
    return szContent, ""


#功能：将数据写入一个文本文件；参数：待写入的文件，待写入的内容；返回：错误描述
def writeTxtFile(szDstFile, szData):
    try:
        CurFile = open(szDstFile, "w")
        CurFile.write(szData)
        CurFile.close()
    except:
        return ("Exception while try to writing %s"  %(szDstFile))
    return ""


#功能：创建一个目录；参数：待创建的目录；返回：错误描述
def makeDirs(szDirs):
    if True==os.path.exists(szDirs) and False==os.path.isdir(szDirs):
        os.remove(szDirs)
    try:
        if False==os.path.isdir(szDirs):
            os.makedirs(szDirs)
    except:
        return ("create dir %s failed" %(szDirs))
    return ""


#功能：执行命令并且获取输出；参数：准备执行的命令；返回：获取的输出
def execCmdAndGetOutput(szCmd):
    Ret = os.popen(szCmd)
    szOutput = Ret.read()  
    Ret.close()  
    return str(szOutput)  


#getOSName 获取操作系统名称；参数：无；返回：操作系统名称
def getOSName():
    #获取centos版本
    szOSName = execCmdAndGetOutput("rpm -q centos-release")
    if None != re.search("^centos\\-release\\-[\\d]+\\-[\\d]+\\.[\\d]+"+\
        "\\.[\\d]+\\.[^\\.]+\\.centos\\.[^\\.^\\s]+$", szOSName):
        return "centos"
    else:
        szOSName,sz_err = readTxtFile("/etc/redhat-release")
        if ""==sz_err and None!=re.search(
            "CentOS[ \\t]+Linux[ \\t]+release[ \\t]+\\d+\\.\\d+\\.\\d+", szOSName):
            return "centos"
    #获取ubuntu版本
    szOSName = execCmdAndGetOutput("lsb_release -a")
    if None != re.search("Distributor[ \\t]+ID[ \\t]*:[ \\t]+Ubuntu.*", szOSName):
        return "ubuntu"
    return ""

#功能：加载巨页；参数：无；返回：错误码
def using_hugepage():
    #设置巨页
    node_info = execCmdAndGetOutput("ls /sys/devices/system/node/"
        " | grep -P \"^node\\d+$\" | sort -u").split("\n")
    if 2 >= len(node_info):#这里2的原因是最后结束行是空行
        os.system("echo 256 > /sys/kernel/mm/hugepages/hugepages-2048kB/"
            "nr_hugepages")
    else:
        for cur_nd in node_info:
            os.system("echo 256 > /sys/devices/system/node/"+cur_nd+"/"
                "hugepages/hugepages-2048kB/nr_hugepages")
    #加载巨页文件
    if True == os.path.isdir("/mnt/huge"):
        os.system("umount -f /mnt/huge")
    if True == os.path.exists("/mnt/huge"):
        os.system("rm -Rf /mnt/huge")
    szErr = makeDirs("/mnt/huge")
    if "" != szErr:
        return szErr
    if 0 != os.system("mount -t hugetlbfs nodev /mnt/huge"):
        return "mount /mnt/huge failed!"
    return ""


#功能：关闭ASLR；参数：无；返回：错误码
def close_ASLR():
    if os.system("echo 0 > /proc/sys/kernel/randomize_va_space"):
        return "close ASLR failed!"
    return ""

#功能：加载网卡驱动；参数：dirver_name驱动名称，card_lst网卡名称链表；返回：错误码
def load_driver(dirver_name, card_lst):
    if "" == execCmdAndGetOutput("lsmod | grep -P \"^uio[ \\t]+\""):
        if 0 != os.system("modprobe uio"):
            return "modprobe uio failed!"
    if "" == execCmdAndGetOutput("lsmod | grep -P \"^"+dirver_name+"[ \\t]+\""):
        if 0 != os.system("insmod /usr/local/dpdk/kmod/"+dirver_name+".ko"):
            return "insmod "+dirver_name+" failed!"
    if "" == execCmdAndGetOutput("lsmod | grep -P \"^rte_kni[ \\t]+\""):
        if 0 != os.system("insmod /usr/local/dpdk/kmod/rte_kni.ko carrier=on"):
            os.system("rmmod "+dirver_name)
            return "insmod rte_kni failed!"
    #绑定网卡
    if False == os.path.exists("/usr/local/dpdk/sbin/driverctl"):
        for cur_card in card_lst:
            card_name = cur_card[0]
            card_addr = cur_card[1]
            if ""!=card_name and "" != execCmdAndGetOutput("python3 /usr/local"
                "/dpdk/sbin/dpdk-devbind --status-dev net | grep \"if="+
                card_name+"\""):
                os.system("ifconfig "+card_name+" down")
            if "" != execCmdAndGetOutput("python3 /usr/local/dpdk/sbin/dpdk-devbind "
                "--status-dev net | grep -P \""+card_addr+"[ \\t]+'.+'[ \\t]+drv=.+"
                "[ \\t]unused=.+\""):
                os.system("python3 /usr/local/dpdk/sbin/dpdk-devbind -u "
                    +card_addr)
            os.system("python3 /usr/local/dpdk/sbin/dpdk-devbind --b "+
                dirver_name+" "+card_addr)        
        os.system("python3 /usr/local/dpdk/sbin/dpdk-devbind --status-dev net")
    else:
        for cur_card in card_lst:
            card_name = cur_card[0]
            os.system("cd /usr/local/dpdk/sbin/driverctl && "\
                "DEV_UUID=$(basename $(readlink /sys/class/net/"+card_name+"/device)) && "\
                "./driverctl -b vmbus set-override $DEV_UUID uio_hv_generic")
        os.system("cd /usr/local/dpdk/sbin/driverctl && ./driverctl -b vmbus list-overrides")
    return ""


#功能：下载胚子f-stack；参数：无；返回：错误码
def config_fstack(fstack_ver, fstack_path, vscode_project_maker):
    if False == os.path.exists(vscode_project_maker+"/f-stack-"+fstack_ver+".zip"):
        if 0 != os.system("wget https://github.com/F-Stack/f-stack/archive/refs/tags/"
            "v"+fstack_ver+".zip -O "+vscode_project_maker+"/f-stack-"+fstack_ver+".zip"):
            os.system("rm -f "+vscode_project_maker+"/f-stack-"+fstack_ver+".zip")
            return "Failed to download f-stack-"+fstack_ver
    #修改lib下的makefile
    lib_make,sz_err = readTxtFile(fstack_path+"/f-stack-"+fstack_ver+"/lib/Makefile")
    if "" != sz_err:
        return "config f-stack failed"
    if 0 >= len(re.findall("\\n#DEBUG[ \\t]*=|\\nDEBUG[ \\t]*=", lib_make)):
        return "can not find DEBUG"
    if 0 >= len(re.findall("\\n#FF_IPFW[ \\t]*=[ \\t]*1|\\nFF_IPFW[ \\t]*=[ \\t]*1", lib_make)):
        return "can not find FF_IPFW"
    lib_make = re.sub("\\n#DEBUG[ \\t]*=", "\nDEBUG=", lib_make)
    lib_make = re.sub("\\n#FF_IPFW[ \\t]*=[ \\t]*1", "\nFF_IPFW=1", lib_make)
    sz_err = writeTxtFile(fstack_path+"/f-stack-"+fstack_ver+"/lib/Makefile", lib_make)
    if "" != sz_err:
        return "config f-stack failed"
    #配置nginx
    cwd_dir = os.getcwd()
    try:
        os.chdir(fstack_path+"/f-stack-"+fstack_ver+"/app/nginx-1.16.1")
        if 0 != os.system("./configure --prefix="+fstack_path+"/f-stack-"+fstack_ver+"/debug "
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
    fstack_make = \
        "update:"\
	        "\n\tcd ./lib && make"\
	        "\n\tcd ./app/nginx-1.16.1 && make"\
            "\n\tcp -rf ./app/nginx-1.16.1/objs/nginx "+fstack_path+"/f-stack-"+fstack_ver+"/debug/sbin/"\
            "\n\n"\
        "clean:"\
	        "\n\tcd ./lib && make clean"\
	        "\n\tcd ./tools && make clean"\
	        "\n\tcd ./app/nginx-1.16.1 && make clean"\
            "\n\tcd ./app/nginx-1.16.1 && ./configure --prefix="+fstack_path+"/f-stack-"+fstack_ver+"/debug "\
            "--with-debug --with-stream --with-stream_ssl_module "\
            "--with-ff_module --with-stream_ssl_preread_module "\
            "--with-http_v2_module"\
            "\n\tsed -i \"s/ -Os / -O0 /\" ./app/nginx-1.16.1/objs/Makefile"\
            "\n\tsed -i \"s/ -g / -g3 /\" ./app/nginx-1.16.1/objs/Makefile"\
            "\n\n"\
        "install:"\
	        "\n\tcd ./lib && make"\
	        "\n\tcd ./tools && make"\
            "\n\tcd ./example && make"\
	        "\n\tcd ./app/nginx-1.16.1 && make"\
	        "\n\tmkdir -p "+fstack_path+"/f-stack-"+fstack_ver+"/debug/net-tools"\
	        "\n\tcp -rf ./tools/sbin/* "+fstack_path+"/f-stack-"+fstack_ver+"/debug/net-tools/"\
	        "\n\tcd ./app/nginx-1.16.1 && make install"\
            "\n\tcp -rf ./config.ini "+fstack_path+"/f-stack-"+fstack_ver+"/debug/conf/f-stack.conf"\
            "\n\n"\
        "uninstall:"\
	        "\n\trm -rf "+fstack_path+"/f-stack-"+fstack_ver+"/debug/*"\
            "\n"
    sz_err = writeTxtFile(fstack_path+"/f-stack-"+fstack_ver+"/makefile", fstack_make)
    if "" != sz_err:
        return "config f-stack failed" 
    return ""


#功能：制作f-stack工程；参数：无；返回：错误码
def create_fstack_project(fstack_ver, fstack_path, vscode_project_maker):
    if 0 != os.system("python3 "+vscode_project_maker+
        "/__init__.py c app /tmp/nginx"):
        os.system("rm -rf /tmp/nginx")
        return "create f-stack project failed"
    os.system("cp -rf /tmp/nginx/.vscode "+
        fstack_path+"/f-stack-"+fstack_ver+"/")
    os.system("rm -rf /tmp/nginx")
    #替换工作目录
    launch,sz_err = readTxtFile(fstack_path+"/f-stack-"+fstack_ver+"/.vscode/"
        "launch.json")
    if "" != sz_err:
        return "create f-stack project failed"
    launch = re.sub("\\$\\{workspaceFolder\\}/debug", 
        "${workspaceFolder}/debug/sbin", launch)
    launch = re.sub("\"\\$\\{workspaceFolder\\}\"", 
        "\"${workspaceFolder}/debug/sbin\"", launch)
    sz_err = writeTxtFile(fstack_path+"/f-stack-"+fstack_ver+"/.vscode/"
        "launch.json", launch)
    if "" != sz_err:
        return "create f-stack project failed"
    #替换编译TAG
    tasks,sz_err = readTxtFile(fstack_path+"/f-stack-"+fstack_ver+"/.vscode/"
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
        , tasks)
    sz_err = writeTxtFile(fstack_path+"/f-stack-"+fstack_ver+"/.vscode/"
        "tasks.json", tasks)
    if "" != sz_err:
        return "create f-stack project failed"
    return ""

#功能：制作f-stack工程；参数：无；返回：错误码
def correct_fstack_code(fstack_ver, fstack_path):
    match_type = ""
    #查找
    time_path = "/usr/include/x86_64-linux-gnu/sys/time.h"
    if False == os.path.isfile(time_path):
        time_path = "/usr/include/sys/time.h"
    if False == os.path.isfile(time_path):
        return "Can not find time.h"
    time_cont,sz_err = readTxtFile(time_path)
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
    ff_mod_cont,sz_err = readTxtFile(fstack_path+"/f-stack-"+fstack_ver+
        "/app/nginx-1.16.1/src/event/modules/ngx_ff_module.c")
    if ""!=sz_err:
        return sz_err
    if "ubuntu" == match_type:
        ff_mod_cont = re.sub("gettimeofday[ \\t\\n]*\\(([^\\)]+)", 
            "gettimeofday(struct timeval *tv, void *tz", ff_mod_cont, 1)
    else:
        ff_mod_cont = re.sub("gettimeofday[ \\t\\n]*\\(([^\\)]+)", 
            "gettimeofday(struct timeval *__restrict tv, __timezone_ptr_t tz", 
            ff_mod_cont, 1)        
    sz_err = writeTxtFile(fstack_path+"/f-stack-"+fstack_ver+
        "/app/nginx-1.16.1/src/event/modules/ngx_ff_module.c", ff_mod_cont)
    return sz_err

#功能：导入路径参数；参数：无；返回：错误码
def export_path(fstack_ver, fstack_path):
    #读取
    profile,sz_err = readTxtFile(os.environ["HOME"]+"/.bashrc")
    if "" != sz_err:
        return sz_err
    #修改
    if 0 >= len(re.findall("\nexport[ \\t]+FF_PATH[ \\t]*=.+", profile)):
        profile += "\nexport FF_PATH="+fstack_path+"/f-stack-"+fstack_ver
    else:
        profile = re.sub("\nexport[ \\t]+FF_PATH[ \\t]*=.+", 
            "\nexport FF_PATH="+fstack_path+"/f-stack-"+fstack_ver, profile)
    if 0 >= len(re.findall("\nexport[ \\t]+FF_DPDK[ \\t]*=.+", profile)):
        profile += "\nexport FF_DPDK=/usr/local/dpdk"
    else:
        profile = re.sub("\nexport[ \\t]+FF_DPDK[ \\t]*=.+", 
            "\nexport FF_DPDK=/usr/local/dpdk", profile)
    #写入
    sz_err = writeTxtFile(os.environ["HOME"]+"/.bashrc", profile)
    if "" != sz_err:
        return sz_err
    return ""


#函数功能：主函数
#函数参数：可执行文件全路径，启动时加入的参数
#函数返回：执行成功返回0，否则返回负值的错误码
if __name__ == "__main__":
    fstack_path = os.getcwd()
    if 1<len(sys.argv):
        fstack_path = sys.argv[1]
    if False==os.path.isdir(fstack_path):
        print("Invaild f-stack path")
        exit(-1)
    fstack_path = os.path.realpath(fstack_path)
    #检测是否安装了DPDK
    if False == os.path.exists("/usr/local/dpdk"):
        print("please install DPDK")
        exit(-1)
    szErr = using_hugepage()
    if "" != szErr:
        print(szErr)
    else:
        print("using hugepage sucess!")
    szErr = close_ASLR()
    if "" != szErr:
        print(szErr)
    else:
        print("close ASLR sucess!")
    if False == os.path.exists("/usr/local/dpdk/sbin/driverctl"):
        szErr = load_driver("igb_uio", [["enp0s9","0000:00:09.0"]])
    else:
        szErr = load_driver("igb_uio", [["eth2"],["eth3"]])
    if "" != szErr:
        print(szErr)
    else:
        print("load driver sucess!")
    #初始化f-stack
    need_continue = "y"
    if True == os.path.exists(fstack_path+"/f-stack-1.21"):
        if re.search("^2\\..*", sys.version):
            need_continue = \
                raw_input("f-stack is already installed, do you want to continue[y/n]:")
        else:
            need_continue = \
                input("f-stack is already installed, do you want to continue[y/n]:")
    if "y"==need_continue or "Y"==need_continue:
        szErr = config_fstack("1.21", fstack_path, 
            os.environ["HOME"]+"/vscode_project_maker")
        if "" != szErr:
            print(szErr)
        else:
            print("config f-stack sucess!")
        szErr = create_fstack_project("1.21", fstack_path, 
            os.environ["HOME"]+"/vscode_project_maker")
        if "" != szErr:
            print(szErr)
        else:
            print("create f-stack project sucess!")
        szErr = correct_fstack_code("1.21", fstack_path)
        if "" != szErr:
            print(szErr)
        else:
            print("correct fstack code sucess!")
        szErr = export_path("1.21", fstack_path)
        if "" != szErr:
            print(szErr)
        else:
            print("export path sucess!")