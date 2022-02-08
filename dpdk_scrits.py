#!/usr/python/bin
# -*- coding: utf-8 -*-

import os
import re
import sys
import logging
import multiprocessing
import maker_public


####################################优化LINUX#############################################
#功能：获取系统总的内存大小；参数：无；返回：内存字节大小
def get_memory():
    total_mem = 0
    meminf = maker_public.execCmdAndGetOutput("dmidecode | grep -P -A5 \"Memory\\s+Device\" "\
        "| grep Size | grep -v Range | grep -P \"Size:\\s+\\d.*\"").split("\n")
    for slotmeme in meminf:
        sizeret = re.search("Size:[ \\t]+(\d+)[ \\t]+", slotmeme)
        baseret = re.search("Size:[ \\t]+\d+[ \\t]+(KB|MB|GB)", slotmeme)
        if None == baseret:
            continue
        base = baseret.group(1)
        memsize = int(sizeret.group(1))
        if "KB" == base:
            total_mem += memsize*1024
        elif "MB" == base:
            total_mem += memsize*1024*1024
        elif "GB" == base:
            total_mem += memsize*1024*1024*1024
    return total_mem


#功能：获取grub-mkconfig命令；参数：无；返回：grub版本、命令、错误描述
def get_mkconfcmd():
    if "" != maker_public.execCmdAndGetOutput("grub2-mkconfig --version | "\
        "grep -P \"^grub2-mkconfig[ ]+\\(GRUB\\)\""):
        return "grub2", "grub2-mkconfig", ""
    elif "" != maker_public.execCmdAndGetOutput("grub-mkconfig --version | "\
        "grep -P \"^grub-mkconfig[ ]+\\(GRUB\\)\""):
        return "grub", "grub-mkconfig", ""
    return "", "", "Failed to find grub2-mkconfig|grub-mkconfig"


#功能：禁止一个服务；参数：服务名；返回：错误描述
def disable_onesrv(srv_name):
    if "" == maker_public.execCmdAndGetOutput(\
        "systemctl status "+srv_name+" | grep Active:"):
        return ""
    os.system("systemctl stop "+srv_name)
    os.system("systemctl disable "+srv_name)
    return ""


#功能：禁止不必要的服务；参数：无；返回：错误描述
def disable_services():
    all_err = disable_onesrv("irqbalance.service")
    all_err += disable_onesrv("ufw.service")
    all_err += disable_onesrv("firewalld.service")
    all_err += disable_onesrv("auditd.service")
    all_err += disable_onesrv("kdump.service")
    all_err += disable_onesrv("bluetooth.service")
    all_err += disable_onesrv("ksm.service")
    all_err += disable_onesrv("ksmtuned.service")
    #这个服务关闭会导致无法远程连接，所以不开启
    #all_err += disable_onesrv("NetworkManager.service")
    return all_err


#功能：检查CPU参数；参数：需要隔离的CPU清单；返回：错误描述
def check_cpuflg(cpu_lst):
    if ""!=cpu_lst and None == re.search("^(\\d+|\\d+-\\d+,)*(\\d+|\\d+-\\d+)$", cpu_lst):
        return "The format of cpu_list is 1,2,5,7,4-5)"
    if "" == cpu_lst:
        return ""
    cpu_param = str(cpu_lst).split(",")
    all_cpu = []
    for cpu in cpu_param:
        ret = re.search("(\\d+)-(\\d+)", cpu)
        if None != ret:
            beg = int(ret.group(1))
            end = int(ret.group(2))
            if beg>=end:
                return ("Invaild cpu_list (%s)" %cpu)
        else:
            beg = int(cpu)
            end = int(cpu)
        while beg <= end:
            all_cpu.append(beg)
            beg = beg+1
    last_cpu = -1
    for cpu in all_cpu:
        if cpu >= multiprocessing.cpu_count():
            return "Invaild cpu "+str(cpu)
        if last_cpu == cpu:
            return "Repetitive cpu "+str(cpu)
        last_cpu = cpu
    return ""


#功能：隔离CPU；参数：需要隔离的CPU清单、巨页参数；返回：错误描述
def isolate_cpu(cpu_lst, page_size):
    #检测cpu_lst的格式
    cpu_lst = str(cpu_lst).strip()
    sz_err = check_cpuflg(cpu_lst)
    if "" != sz_err:
        return sz_err
    #检查巨页参数
    if 2048!=page_size and 1048576!=page_size:
        return "page_size must be 2048 or 1048576"
    #获取grub-mkconfig命令
    grubver,mkconfig,sz_err = get_mkconfcmd()
    if "" != sz_err:
        return sz_err
    #设置iommu，ARM下默认开启smmu
    iommu_flg = "nmi_watchdog=0 selinux=0 nosoftlockup "
    if "" != maker_public.execCmdAndGetOutput("lscpu | grep -P \" vmx \""):
        iommu_flg += "iommu=pt intel_iommu=on "
    elif "" != maker_public.execCmdAndGetOutput("lscpu | grep -P \" svm \""):
        iommu_flg += "iommu=pt amd_iommu=on "
    #设置巨页参数
    if 2048 == page_size:
        iommu_flg += "default_hugepagesz=2M "
    else:
        iommu_flg += "default_hugepagesz=1G "
    #设置核隔离参数
    cpu_flg = ""
    if "" != cpu_lst:
        cpu_flg += "isolcpus="+cpu_lst+" "
        cpu_flg += "nohz_full="+cpu_lst+" "
        cpu_flg += "rcu_nocbs="+cpu_lst+" "
    #读取grub配置文件
    grub,err = maker_public.readTxtFile("/etc/default/grub")
    if "" != err:
        return err
    #替换配置文件
    if None != re.search("\nGRUB_CMDLINE_LINUX_DEFAULT.*\nGRUB_CMDLINE_LINUX[ \\t]*=.*",grub):
        grub = re.sub("\nGRUB_CMDLINE_LINUX[ \\t]*=.*", \
            ("\nGRUB_CMDLINE_LINUX=\"%s%s\"" %(iommu_flg, cpu_flg) ),grub )
    elif None != re.search("\nGRUB_CMDLINE_LINUX[ \\t]*=.+rhgb[ \\t]+quiet.*",grub):
        grub = re.sub("[ \\t]+rhgb[ \\t]+quiet.*", \
            (" rhgb quiet %s%s\"" %(iommu_flg, cpu_flg) ),grub )
    else:
        return "Failed to make grub.cfg"
    #写入grub配置文件
    err = maker_public.writeTxtFile("/etc/default/grub", grub)
    if "" != err:
        return err
    #重新生成启动文件
    if 0 != os.system(mkconfig+" -o /boot/"+grubver+"/grub.cfg"):
        return "Failed to make grub.cfg"
    return ""


#功能：优化系统；参数：监控脚本、cpu清单(格式化为1,2,5,7,8)、巨页信息；返回：错误描述
def Optim_system(cpu_lst, page_size):
    #关闭服务
    sz_err = disable_services()
    if "" != sz_err:
        return sz_err
    #关闭UI
    if "ubuntu-wsl2" != maker_public.getOSName():
        if 0 != os.system("systemctl set-default multi-user.target"):
            return "Failed to close UI"
    #核隔离和开启iommu
    if "ubuntu-wsl2" != maker_public.getOSName():
        sz_err = isolate_cpu(cpu_lst, page_size)
        if "" != sz_err:
            enable_onesrv("irqbalance.service")
            return sz_err 
    return ""


####################################恢复针对DPDK的优化##########################################
#功能：启动一个服务；参数：服务名；返回：错误描述
def enable_onesrv(srv_name):
    if "" != maker_public.execCmdAndGetOutput(\
        "systemctl status "+srv_name+" | grep Active:"):
        os.system("systemctl enable "+srv_name)
        os.system("systemctl restart "+srv_name)
    return ""


#功能：释放CPU；参数：无；返回：错误描述
def free_cpu():
    #获取grub-mkconfig命令
    grubver,mkconfig,sz_err = get_mkconfcmd()
    if "" != sz_err:
        return sz_err
    #读取grub配置文件
    grub,err = maker_public.readTxtFile("/etc/default/grub")
    if "" != err:
        return err
    #替换配置文件
    if None != re.search("\nGRUB_CMDLINE_LINUX_DEFAULT.*\nGRUB_CMDLINE_LINUX[ \\t]*=.*",grub):
        grub = re.sub("\nGRUB_CMDLINE_LINUX[ \\t]*=.*", "\nGRUB_CMDLINE_LINUX=\"\"",grub )
    elif None != re.search("\nGRUB_CMDLINE_LINUX[ \\t]*=.+rhgb[ \\t]+quiet.*",grub):
        grub = re.sub("[ \\t]+rhgb[ \\t]+quiet.*", " rhgb quiet\"",grub)
    else:
        return "Failed to make grub.cfg"
    #写入grub配置文件
    err = maker_public.writeTxtFile("/etc/default/grub", grub)
    if "" != err:
        return err
    #重新生成启动文件
    if 0 != os.system(mkconfig+" -o /boot/"+grubver+"/grub.cfg"):
        return "Failed to make grub.cfg"
    return ""    

    
#功能：复原针对DPDK的优化；参数：监控脚本和监控的进程；返回：错误描述
def Recov_system():
    #开启服务
    sz_err = enable_onesrv("irqbalance.service")
    if "" != sz_err:
        return sz_err
    #核隔离和关闭iommu
    if "ubuntu-wsl2" != maker_public.getOSName():
        sz_err = free_cpu()
        if "" != sz_err:
            return sz_err
    #删除动态库链接路径配置
    os.system("rm -rf /etc/ld.so.conf.d/dpdkapp_lib.conf && ldconfig")
    return ""


####################################初始化#################################################
#功能：设置ASLR；参数：无；返回：错误码
def set_ASLR(opt):
    if "0"!=opt and "1"!=opt:
        return "ASLR_FLG must be 0 or 1"
    if os.system("echo "+opt+" > /proc/sys/kernel/randomize_va_space"):
        return "set ASLR failed!"
    return ""


#功能：加载巨页；参数：巨页大小、巨页数量；返回：错误码
def set_one_hugepage(node_path, page_name, page_cnt):
    #检测page_cnt是否是2的幂次方，并且修正到2的幂次方
    highest_1 = 0
    cnt_1 = 0
    cur_pos = 0
    tmp_page_cnt = page_cnt
    while 0 < tmp_page_cnt:
        if tmp_page_cnt%2:
            cnt_1 = cnt_1+1
            highest_1 = cur_pos
        cur_pos = cur_pos+1
        tmp_page_cnt = int(tmp_page_cnt/2)
    if 1 != cnt_1:
        page_cnt = pow(2, highest_1+1)
    #设置
    if False == os.path.isfile(node_path+"/"+page_name+"/nr_hugepages"):
        return "Failed to set "+node_path+"/"+page_name+"/nr_hugepages"
    old_hugepages = maker_public.execCmdAndGetOutput(\
        "grep -P \"\\d+\" "+node_path+"/"+page_name+"/nr_hugepages").replace("\n", "")
    if "" == old_hugepages:
        return "Failed to set "+node_path+"/"+page_name+"/nr_hugepages"
    if 0 != os.system("echo "+str(page_cnt)+" > "+node_path+"/"+page_name+"/nr_hugepages"):
        os.system("echo "+old_hugepages+" > "+node_path+"/"+page_name+"/nr_hugepages")
        return "Failed to set "+node_path+"/"+page_name+"/nr_hugepages"
    cur_hugepages = maker_public.execCmdAndGetOutput(\
        "grep -P \"\\d+\" "+node_path+"/"+page_name+"/nr_hugepages").replace("\n", "")
    if cur_hugepages != str(page_cnt):
        os.system("echo "+old_hugepages+" > "+node_path+"/"+page_name+"/nr_hugepages")
        return "Failed to set "+node_path+"/"+page_name+"/nr_hugepages"
    return ""  


#功能：加载巨页；参数：巨页大小、巨页数量；返回：错误码
def set_hugepage(page_size, page_cnt_lst):
    #检测类型大小
    if 2048!=page_size and 1048576!=page_size:
        return "page_size must be 2048 or 1048576"
    #逐个设置
    for  page_info in page_cnt_lst:
        if False == os.path.isdir("/sys/devices/system/node"):
            sz_err = set_one_hugepage("/sys/kernel/mm/hugepages", \
                ("hugepages-%dkB" %page_size), page_info[1])
            if "" != sz_err:
                return sz_err
            break
        else:
            sz_err = set_one_hugepage("/sys/devices/system/node/"+page_info[0]+"/hugepages", \
                ("hugepages-%dkB" %page_size), page_info[1])
            if "" != sz_err:
                return sz_err
    #加载巨页文件
    if True == os.path.isdir("/mnt/huge"):
        os.system("umount -f /mnt/huge")
    if True == os.path.exists("/mnt/huge"):
        os.system("rm -Rf /mnt/huge")
    szErr = maker_public.makeDirs("/mnt/huge")
    if "" != szErr:
        return szErr
    if 0 != os.system("mount -t hugetlbfs nodev /mnt/huge"):
        return "mount /mnt/huge failed!"
    return ""


#功能：绑定网卡；参数：绑定参数、内核模块名称清单、网卡名称-pci地址；返回：错误码
def bind_device(devbind_path, drvctl_path, kmod_path, kmod_list, dev_lst):
    #加载内核模块
    for kmod in kmod_list:
        if "uio_pci_generic"==kmod or "vfio_pci"==kmod or "uio_hv_generic"==kmod:
            os.system("modprobe "+kmod)
        else:
            imsmod_cmd = "insmod "+kmod_path+"/"+kmod+".ko"
            if "rte_kni" == kmod:
                imsmod_cmd += " carrier=on"
            if "" == maker_public.execCmdAndGetOutput("lsmod | grep uio"):
                os.system("modprobe uio")
            os.system(imsmod_cmd)
        if "" == maker_public.execCmdAndGetOutput("lsmod | grep "+kmod):
            return "Failed to load "+kmod
    kmod = kmod_list[0]
    #绑定网卡设备
    python = maker_public.get_python()
    all_err = ""
    if False == os.path.exists(drvctl_path):
        dpdk_devbind = devbind_path+"/dpdk-devbind"
        if False == os.path.isfile(dpdk_devbind):
            dpdk_devbind = devbind_path+"/dpdk-devbind.py"
        for dev in dev_lst:
            dev_name = dev[0]
            dev_addr = dev[1]
            if "" == dev_addr:
                all_err += "No PCI address\n"
                continue
            if ""!=dev_name and "" != maker_public.execCmdAndGetOutput(python+" "+dpdk_devbind+\
                " --status-dev net | grep \"if="+dev_name+"\""):
                os.system("ifconfig "+dev_name+" down")
            if "" != maker_public.execCmdAndGetOutput(\
                python+" "+dpdk_devbind+" --status-dev net | "\
                "grep -P \""+dev_addr+"[ \\t]+'.+'[ \\t]+drv=.+[ \\t]unused=.+\""):
                os.system(python+" "+dpdk_devbind+" -u "+dev_addr)
            if 0 != os.system(python+" "+dpdk_devbind+" --b "+kmod+" "+dev_addr):
                all_err += "Failed to bind "+dev_addr+"\n"
        os.system(python+" "+dpdk_devbind+" --status-dev net")
    else:
        for dev in dev_lst:
            dev_name = dev[0]
            if "" == dev_name:
                all_err += "No device name\n"
                continue
            if False == os.path.exists("/sys/class/net/"+dev_name+"/device"):
                logging.warning("Failed to find "+dev_name)
            else:
                if 0 != os.system("cd "+drvctl_path+" && "\
                    "DEV_UUID=$(basename $(readlink /sys/class/net/"+dev_name+"/device)) && "\
                    "./driverctl -b vmbus set-override $DEV_UUID "+kmod):
                    all_err += "Failed to bind "+dev_name+"\n"
        os.system("cd "+drvctl_path+" && ./driverctl -b vmbus list-overrides")
    return all_err


#功能：启动后初始化DPDK的环境参数；参数：巨页大小、巨页数量、是否开启地址随机化；返回：错误码
def Init_dpdkenv(ASLR_flg, page_size, page_cnt_lst, devbind_path, drvctl_path, \
    kmod_path, kmod_list, dev_lst):
    #设置地址随机化
    sz_err = set_ASLR(ASLR_flg)
    if "" != sz_err:
        return sz_err
    #设置巨页
    sz_err = set_hugepage(page_size, page_cnt_lst)
    if "" != sz_err:
        return sz_err
    #绑定设备
    return bind_device(devbind_path, drvctl_path, kmod_path, kmod_list, dev_lst)


####################################安装程序################################################
#功能：根据app_list计算MD5值；参数：app路径；返回：MD5值，错误描述
def get_appname(app_list):
    return "",""

#功能：注册计划任务；参数：脚本位置；返回：错误描述
def register_cron(monitor_scrits):
    python = maker_public.get_python()
    szret = maker_public.execCmdAndGetOutput("crontab -l")
    pyregpath = monitor_scrits.replace(".", "\\.")
    if None != re.search(".+python\\d*[ \\t]+"+pyregpath+"[\\s]+monitor", szret):
        szret = re.sub(".+python\\d*[ \\t]+"+pyregpath+"[\\s]+monitor", \
            "*/1 * * * * "+python+" "+monitor_scrits+" monitor", szret)
    elif 0>=len(szret) or "\n" == szret[len(szret)-1]:
        szret += "*/1 * * * * "+python+" "+monitor_scrits+" monitor\n"
    sz_err = maker_public.writeTxtFile("/tmp/dpdk_scrits_crontab", szret)
    if 0 < len(sz_err):
        os.system("rm -Rf /tmp/dpdk_scrits_crontab")
        return sz_err
    if 0 != os.system("crontab /tmp/dpdk_scrits_crontab"):
        os.system("rm -Rf /tmp/dpdk_scrits_crontab")
        return "Failed to register cron"
    os.system("rm -Rf /tmp/dpdk_scrits_crontab")
    return ""
    

#功能：设置DPDK及其APP的链接库路径；参数：链接库路径；返回：错误描述
def set_dpdkapplib(app_name, dllpath_list):
    path_info = ""
    sz_err = ""
    for dllpath in dllpath_list:
        if False == os.path.isdir(os.path.abspath(dllpath)):
            return "Failed to find "+dllpath
        path_info += os.path.abspath(dllpath)+"\n"
    if "" != path_info:
        sz_err = maker_public.writeTxtFile(\
            ("/etc/ld.so.conf.d/dpdkapp_%s_lib.conf" %app_name), path_info)
        os.system("ldconfig")
    return sz_err


def Install_app(monitor_scrits, app_lst, dllpath_list):
    #挂载定时任务  
    sz_err = register_cron(monitor_scrits)
    if "" != sz_err:
        enable_onesrv("irqbalance.service")
        return sz_err
    #设置动态库链接路径
    app_name,sz_err = get_appname(app_lst)
    if "" != sz_err:
        return sz_err
    sz_err = set_dpdkapplib(app_name, dllpath_list)
    if "" != sz_err:
        return sz_err
    return ""
    
####################################卸载程序################################################
#功能：关闭一个进程；参数：进程信息；返回：已经执行了关闭操作的进程
def do_killproc(app_lst):
    kill_cmd = ""
    proc_lst = []
    for appinfo in app_lst:    
        if False == os.path.isfile(os.path.abspath(appinfo[0])):
            return []
        app_name = os.path.abspath(appinfo[0])
        kill_cmd += "killall -9 "+app_name+" || "
        proc_lst.append(app_name)
    if "" != kill_cmd:
        kill_cmd = str(kill_cmd).rstrip(" || ")
        os.system(kill_cmd)
    return proc_lst


#功能：等待进程关闭；参数：进程信息；返回：错误描述
def do_waitproc(proc_lst):
    exists = True
    while exists:
        curexiste = 0
        app_stat = maker_public.execCmdAndGetOutput("ps -aux")
        for proc in proc_lst:
            if None != re.search("[ \\t]+"+proc+"[ \\t]+|[ \\t]+"+proc+"$", app_stat):
                curexiste = curexiste+1
                break
        if 0 >= curexiste:
            exists = False
    return ""


#功能：关闭进程；参数：进程名称清单；返回：错误描述
def close_proc(app_lst):
    proc_lst = do_killproc(app_lst)
    if 0 >= len(proc_lst):
        return ""
    return do_waitproc(proc_lst)


#功能：注册计划任务；参数：脚本位置；返回：错误描述
def unregister_cron(monitor_scrits):
    szret = maker_public.execCmdAndGetOutput("crontab -l")
    pyregpath = monitor_scrits.replace(".", "\\.")
    if None != re.search(".+python\\d*[ \\t]+"+pyregpath+"[^\\n]+\\n", szret):
        szret = re.sub(".+python\\d*[ \\t]+"+monitor_scrits+"[^\\n]+\\n", "", szret)
    sz_err = maker_public.writeTxtFile("/tmp/dpdk_scrits_crontab", szret)
    if 0 < len(sz_err):
        os.system("rm -Rf /tmp/dpdk_scrits_crontab")
        return sz_err
    if 0 != os.system("crontab /tmp/dpdk_scrits_crontab"):
        os.system("rm -Rf /tmp/dpdk_scrits_crontab")
        return "Failed to unregister cron"
    os.system("rm -Rf /tmp/dpdk_scrits_crontab")
    return ""


#功能：卸载应用；参数：监控脚本和监控的进程；返回：错误描述
def Uninstall_app(monitor_scrits, app_lst):
    #注销定时任务
    sz_err = unregister_cron(monitor_scrits)
    if "" != sz_err:
        return sz_err
    #关闭全部进程
    sz_err = close_proc(app_lst)
    if "" != sz_err:
        return sz_err
    #删除动态库链接路径配置
    app_name,sz_err = get_appname(app_lst)
    if "" != sz_err:
        return sz_err
    os.system(\
        ("rm -rf /etc/ld.so.conf.d/dpdkapp_%s_lib.conf && ldconfig" %app_name) )
    return ""
####################################监控进程################################################
#功能：监控一个应用；参数：app名称-app启动路径及参数；返回：错误码
def monitor_oneapp(appinfo):
    if False == os.path.isfile(appinfo[0]):
        return "Failed to find "+appinfo[0]
    if ""!=appinfo[1] and False == os.path.isdir(appinfo[1]):
        return ("Failed to find work_dir(%s)" %appinfo[1])
    app_path = os.path.abspath(appinfo[0])
    app_name = str(app_path).replace(".", "\\.")
    work_dir = os.path.abspath(appinfo[1])
    app_param = appinfo[2]
    #检测进程是否存在
    app_stat = maker_public.execCmdAndGetOutput("ps -aux | grep "+app_name)
    app_stat = re.sub(".*grep[ \\t]+"+app_name+".*\\n", "", app_stat)
    if ""==app_stat:
        logging.info("try to start ("+app_path+" "+app_param+")")
        os.system("cd "+work_dir+" && "+app_path+" "+app_param+" &")
    return ""


#功能：监控DPDK的应用；参数：app列表，包括app名称-app启动路径及参数；返回：错误码
def Monitor_dpdkapp(app_lst):
    sz_err = ""
    for appinfo in app_lst:
        sz_err += monitor_oneapp(appinfo)
    return sz_err
    

###############################主流程###################################################
#功能：初始化日志；参数：日志大小、错误描述；返回：无
def init_log(file_size, error):
    #设置日志
    if 2>len(sys.argv):
        print(error)
        exit(-1)
    if 3 <= len(sys.argv):
        try:
            CurFile = open(sys.argv[2], "a")
            CurFile.close()
        except:
            print("Exception while try to writing %s"  %(sys.argv[2]))
            exit(-1)
        log_path = os.path.abspath(sys.argv[2])
        if file_size < os.path.getsize(log_path):
            os.system("rm -rf "+log_path)
        logging.basicConfig(filename=log_path, filemode="a", \
            format="%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s",\
            level=logging.INFO)
    else:
        logging.basicConfig(format="%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s",\
            level=logging.INFO)


#函数功能：主函数
#函数参数：可执行文件全路径，启动时加入的参数
#函数返回：执行成功返回0，否则返回负值的错误码
if __name__ == "__main__":
    #错误描述
    error = "dpdk_opt: [optimsys|recovsys|initenv|install|uninstall|monitor] [log file]"
    #初始化日志文件，大小限制为512MB
    init_log(512*1024*1024, error)


    #所有的参数
    #需要隔离的CPU清单，从0开始，格式为1,4,5,6,2-3
    cpu_list = "2-3"
    #需要监控的进程的信息，两层list，内层list每个节点有三个参数：程序路径、工作路径、启动参数
    app_list = [["/usr/bin/more", "", "/etc/default/grub"]]
    #动态库路径清单，每个元素代表一个应用需要的动态库路径，他们会被添加到系统中，供启动时查找
    dllpath_list = [""]
    #地址随机化开启标志：1表示开启、0表示关闭
    ASLR_flg = "1"
    #需要开启的巨页的尺寸，有2048kb和1048576kb两种
    page_size = 2048
    #需要开启的巨页的数量，按照NUMA节点进行分配，在非NUMA结构下，只能配置node0
    page_cnt_lst = [["node0", 128]]
    #PCI设备的DPDK绑定脚本所在的路径，一般在DPDK安装路径的usertools下
    devbind_path = ""#"/usr/local/dpdk/share/dpdk/usertools"
    #VMBUS设备的DPDK绑定脚本所在的路径，该设备是微软hyper-v虚拟机的绑定程序，
    # 可以从https://gitlab.com/driverctl/driverctl下载。devbind_path和drvctl_path
    # 不能同时配置，必须配置一个，置为空串一个。
    drvctl_path = "/usr/local/dpdk/sbin/driverctl"
    #DPDK内核模块所在的路径，主要是igb_uio.ko和rte_kni.ko所在的路径，在编译DPDK时获取。
    # 注意：在DPDK20以后版本中默认是不打开igb_uio的，需要额外下载igb_uio源代码并且构建
    # 编译脚本，具体可以参见本工程中对VPP的DPDK的编译方法。
    kmod_path = "/usr/local/dpdk/kmod"
    #需要加载的内核模块，可以是igb_uio、rte_kni、uio_pci_generic、vfio_pci、uio_hv_generic。
    # 其中uio_pci_generic是linux提供的uio驱动，大部分场景可以替代igb_uio，只有一些比较老的设备
    # 才会需要igb_uio驱动；vfio_pci是3.6之后的内核提供的一种uio驱动，可以支持IO虚拟化技术，如
    # INTEL的VT-d、AMD的AMD-V、ARM的SMMU；uio_hv_generic是微软hyper-v虚拟机中的uio驱动。
    kmod_list = ["uio_hv_generic"]
    #需要绑定的设备，两层list，内层list每个节点有两个参数：网卡名、网卡的PCI地址。在PCI环境中，
    # 网卡的PCI地址是必须的；在VMBUS环境中，网卡名是必须的。
    dev_lst = [["eth2", "04:00.3"]]


    #解析参数
    if "optimsys"==sys.argv[1]:
        error = Optim_system(cpu_list, page_size)
    elif "recovsys"==sys.argv[1]:
        error  = Recov_system()
    elif "initenv"==sys.argv[1]:
        error  = Init_dpdkenv(ASLR_flg, page_size, page_cnt_lst, devbind_path, \
            drvctl_path, kmod_path, kmod_list, dev_lst)
    elif "install"==sys.argv[1]:
        error  = Install_app(sys.argv[0], app_list, dllpath_list)
    elif "uninstall"==sys.argv[1]:
        error  = Uninstall_app(sys.argv[0], app_list)
    elif "monitor"==sys.argv[1]:
        error  = Monitor_dpdkapp(app_list)
    if ""!=error:
        logging.error(error)
        exit(-1)
    if "install"==sys.argv[1] or "uninstall"==sys.argv[1]:
        maker_public.do_reboot("press any key to reboot...")
    exit(0)