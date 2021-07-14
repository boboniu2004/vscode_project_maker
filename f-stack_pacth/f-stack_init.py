#!/usr/python/bin
# -*- coding: utf-8 -*-

import os
import re

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
            if "" != execCmdAndGetOutput("python3 /usr/local"
                "/dpdk/sbin/dpdk-devbind --status-dev net | grep \"if="+
                card_name+"\""):
        os.system("cd /usr/local/dpdk/sbin/driverctl && ./driverctl -b vmbus list-overrides")
    return ""


#功能：下载胚子f-stack；参数：无；返回：错误码
def config_fstack(fstack_ver):
    if False == os.path.exists("./f-stack-"+fstack_ver+".zip"):
        if 0 != os.system("wget https://github.com/F-Stack/f-stack/archive/refs/tags/"
        "v"+fstack_ver+".zip -O f-stack-"+fstack_ver+".zip"):
            return "Failed to download f-stack-"+fstack_ver
    if False == os.path.exists(os.getcwd()+"/f-stack-"+fstack_ver):
        #解压缩
        os.system("unzip ./f-stack-"+fstack_ver+".zip")
    #修改lib下的makefile
    lib_make,sz_err = readTxtFile(os.getcwd()+"/f-stack-"+fstack_ver+"/lib/Makefile")
    if "" != sz_err:
        return "config f-stack failed"
    if 0 >= len(re.findall("\\n#DEBUG[ \\t]*=|\\nDEBUG[ \\t]*=", lib_make)):
        return "can not find DEBUG"
    if 0 >= len(re.findall("\\n#FF_IPFW[ \\t]*=[ \\t]*1|\\nFF_IPFW[ \\t]*=[ \\t]*1", lib_make)):
        return "can not find FF_IPFW"
    lib_make = re.sub("\\n#DEBUG[ \\t]*=", "\nDEBUG=", lib_make)
    lib_make = re.sub("\\n#FF_IPFW[ \\t]*=[ \\t]*1", "\nFF_IPFW=1", lib_make)
    sz_err = writeTxtFile(os.getcwd()+"/f-stack-"+fstack_ver+"/lib/Makefile", lib_make)
    if "" != sz_err:
        return "config f-stack failed"
    #配置nginx
    cwd_dir = os.getcwd()
    try:
        os.chdir(os.getcwd()+"/f-stack-"+fstack_ver+"/app/nginx-1.16.1")
        if 0 != os.system("./configure --prefix="+cwd_dir+"/f-stack-"+fstack_ver+"/debug "
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
            "\n\tcp -rf ./app/nginx-1.16.1/objs/nginx "+cwd_dir+"/f-stack-"+fstack_ver+"/debug/sbin/"\
            "\n\n"\
        "clean:"\
	        "\n\tcd ./lib && make clean"\
	        "\n\tcd ./tools && make clean"\
	        "\n\tcd ./app/nginx-1.16.1 && make clean"\
            "\n\tcd ./app/nginx-1.16.1 && ./configure --prefix="+cwd_dir+"/f-stack-"+fstack_ver+"/debug "\
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
	        "\n\tmkdir -p "+cwd_dir+"/f-stack-"+fstack_ver+"/debug/net-tools"\
	        "\n\tcp -rf ./tools/sbin/* "+cwd_dir+"/f-stack-"+fstack_ver+"/debug/net-tools/"\
	        "\n\tcd ./app/nginx-1.16.1 && make install"\
            "\n\tcp -rf ./config.ini "+cwd_dir+"/f-stack-"+fstack_ver+"/debug/conf/f-stack.conf"\
            "\n\n"\
        "uninstall:"\
	        "\n\trm -rf "+cwd_dir+"/f-stack-"+fstack_ver+"/debug/*"\
            "\n"
    sz_err = writeTxtFile(os.getcwd()+"/f-stack-"+fstack_ver+"/makefile", fstack_make)
    if "" != sz_err:
        return "config f-stack failed"    
    return ""


#功能：制作f-stack工程；参数：无；返回：错误码
def create_fstack_project(fstack_ver, vscode_project_maker):
    if 0 != os.system("python3 "+vscode_project_maker+
        "/__init__.py c app /tmp/nginx"):
        os.system("rm -rf /tmp/nginx")
        return "create f-stack project failed"
    os.system("cp -rf /tmp/nginx/.vscode "+
        os.getcwd()+"/f-stack-"+fstack_ver+"/")
    os.system("rm -rf /tmp/nginx")
    #替换工作目录
    launch,sz_err = readTxtFile(os.getcwd()+"/f-stack-"+fstack_ver+"/.vscode/"
        "launch.json")
    if "" != sz_err:
        return "create f-stack project failed"
    launch = re.sub("\\$\\{workspaceFolder\\}/debug", 
        "${workspaceFolder}/debug/sbin", launch)
    launch = re.sub("\"\\$\\{workspaceFolder\\}\"", 
        "\"${workspaceFolder}/debug/sbin\"", launch)
    sz_err = writeTxtFile(os.getcwd()+"/f-stack-"+fstack_ver+"/.vscode/"
        "launch.json", launch)
    if "" != sz_err:
        return "create f-stack project failed"
    #替换编译TAG
    tasks,sz_err = readTxtFile(os.getcwd()+"/f-stack-"+fstack_ver+"/.vscode/"
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
    sz_err = writeTxtFile(os.getcwd()+"/f-stack-"+fstack_ver+"/.vscode/"
        "tasks.json", tasks)
    if "" != sz_err:
        return "create f-stack project failed"
    return ""

#功能：导入路径参数；参数：无；返回：错误码
def export_path(fstack_ver):
    #读取
    profile,sz_err = readTxtFile(os.environ["HOME"]+"/.bashrc")
    if "" != sz_err:
        return sz_err
    #修改
    if 0 >= len(re.findall("\nexport[ \\t]+FF_PATH[ \\t]*=.+", profile)):
        profile += "\nexport FF_PATH="+os.getcwd()+"/f-stack-"+fstack_ver
    else:
        profile = re.sub("\nexport[ \\t]+FF_PATH[ \\t]*=.+", 
            "\nexport FF_PATH="+os.getcwd()+"/f-stack-"+fstack_ver, profile)
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
    szErr = load_driver("igb_uio", [["enp0s9","0000:00:09.0"]])
    if "" != szErr:
        print(szErr)
    else:
        print("load driver sucess!")
    szErr = config_fstack("1.21")
    if "" != szErr:
        print(szErr)
    else:
        print("config f-stack sucess!")
    szErr = create_fstack_project("1.21", os.environ["HOME"]+"/vscode_project_maker")
    if "" != szErr:
        print(szErr)
    else:
        print("create f-stack project sucess!")
    szErr = export_path("1.21")
    if "" != szErr:
        print(szErr)
    else:
        print("export path sucess!")