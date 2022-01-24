#!/usr/python/bin
# -*- coding: utf-8 -*-


import os
import re
import psutil
import maker_public


####################################安装####################################################
#功能：获取grub-mkconfig命令；参数：无；返回：命令、错误描述
def get_mkconfcmd():
    if "" == maker_public.execCmdAndGetOutput("grub2-mkconfig --version | "\
        "grep -P\"^grub2-mkconfig[ ]+\\(GRUB\\)\""):
        return "grub2-mkconfig", ""
    elif "" == maker_public.execCmdAndGetOutput("grub-mkconfig --version | "\
        "grep -P\"^grub-mkconfig[ ]+\\(GRUB\\)\""):
        return "grub-mkconfig", ""
    return "", "Failed to find grub2-mkconfig|grub-mkconfig"

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
    all_err += disable_onesrv("NetworkManager.service")
    return all_err


#功能：隔离CPU；参数：需要隔离的CPU清单；返回：错误描述
def isolate_cpu(cpu_lst):
    #检测cpu_lst的格式
    cpu_lst = str(cpu_lst).strip()
    if None == re.search("^(\\d+,)*\\d+$", cpu_lst):
        return "The format of cpu_list is 1,2,5,7)"
    #获取grub-mkconfig命令
    mkconfig,sz_err = get_mkconfcmd()
    if "" != sz_err:
        return sz_err
    #设置启动参数，ARM下默认开启，不需要设置
    iommu_flg = ""
    if "" != maker_public.execCmdAndGetOutput("lscpu | grep -P \" vmx \""):
        iommu_flg += "iommu=pt intel_iommu=on "
    elif "" != maker_public.execCmdAndGetOutput("lscpu | grep -P \" svm \""):
        iommu_flg += "iommu=pt amd_iommu=on "
    cpu_flg = ""
    if "" != cpu_lst:
        cpu_flg = "isolCPUS="+cpu_lst+" "
    #读取grub配置文件
    grub,err = maker_public.readTxtFile("/etc/default/grub")
    if "" != err:
        return err
    #替换配置文件
    if None != re.search("\nGRUB_CMDLINE_LINUX_DEFAULT.*\nGRUB_CMDLINE_LINUX[ \\t]*=.*"):
        grub = re.sub("\nGRUB_CMDLINE_LINUX[ \\t]*=.*", \
            ("\nGRUB_CMDLINE_LINUX=\"%s%s\"" %(iommu_flg, cpu_flg) ) )
    elif None != re.search("\nGRUB_CMDLINE_LINUX[ \\t]*=.+rhgb[ \\t]+quiet[ \\t]+.*"):
        grub = re.sub("[ \\t]+rhgb[ \\t]+quiet[ \\t]+.*", \
            (" rhgb quiet %s%s\"" %(iommu_flg, cpu_flg) ) )
    else:
        return "Failed to make grub.cfg"
    #写入grub配置文件
    err = maker_public.writeTxtFile("/etc/default/grub", grub)
    if "" != err:
        return err
    #重新生成启动文件
    if 0 != os.system(mkconfig+" -o /boot/grub/grub.cfg"):
        return "Failed to make grub.cfg"
    return ""


#功能：注册计划任务；参数：脚本位置；返回：错误描述
def register_cron(monitor_scrits):
    szret = maker_public.execCmdAndGetOutput("crontab -l")
    pyregpath = monitor_scrits.replace(".", "\\.")
    if None != re.search(".+python[ \\t]+"+pyregpath+"[\\s]+monitor", szret):
        szret = re.sub(".+python[ \\t]+"+pyregpath+"[\\s]+monitor", \
            "*/1 * * * * python "+monitor_scrits+" monitor", szret)
    elif 0>=len(szret) or "\n" == szret[len(szret)-1]:
        szret += "*/1 * * * * python "+monitor_scrits+" monitor\n"
    sz_err = maker_public.writeTxtFile("/tmp/dpdk_scrits_crontab", szret)
    if 0 < len(sz_err):
        os.system("rm -Rf /tmp/dpdk_scrits_crontab")
        return sz_err
    if 0 != os.system("crontab /tmp/dpdk_scrits_crontab"):
        os.system("rm -Rf /tmp/dpdk_scrits_crontab")
        return "Failed to register cron"
    os.system("rm -Rf /tmp/dpdk_scrits_crontab")
    return ""
    

#功能：安装dpdk的环境；参数：cpu清单，格式化为1,2,5,7,8；返回：错误描述
def Install_dpdkenv(monitor_scrits, cpu_lst):
    #关闭服务
    sz_err = disable_services()
    if "" != sz_err:
        return sz_err
    #挂载定时任务  
    sz_err = register_cron(monitor_scrits)
    if "" != sz_err:
        enable_onesrv("irqbalance.service")
        return sz_err 
    #核隔离和开启iommu
    sz_err = isolate_cpu(cpu_lst)
    if "" != sz_err:
        enable_onesrv("irqbalance.service")
        unregister_cron(monitor_scrits)
        return sz_err 
    maker_public.do_reboot("press any key to reboot...")
    return ""


####################################卸载####################################################
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
    mkconfig,sz_err = get_mkconfcmd()
    if "" != sz_err:
        return sz_err
    #读取grub配置文件
    grub,err = maker_public.readTxtFile("/etc/default/grub")
    if "" != err:
        return err
    #替换配置文件
    if None != re.search("\nGRUB_CMDLINE_LINUX_DEFAULT.*\nGRUB_CMDLINE_LINUX[ \\t]*=.*"):
        grub = re.sub("\nGRUB_CMDLINE_LINUX[ \\t]*=.*", "\nGRUB_CMDLINE_LINUX=\"" )
    elif None != re.search("\nGRUB_CMDLINE_LINUX[ \\t]*=.+rhgb[ \\t]+quiet[ \\t]+.*"):
        grub = re.sub("[ \\t]+rhgb[ \\t]+quiet[ \\t]+.*", " rhgb quiet\"")
    else:
        return "Failed to make grub.cfg"
    #写入grub配置文件
    err = maker_public.writeTxtFile("/etc/default/grub", grub)
    if "" != err:
        return err
    #重新生成启动文件
    if 0 != os.system(mkconfig+" -o /boot/grub/grub.cfg"):
        return "Failed to make grub.cfg"
    return ""    


#功能：注册计划任务；参数：脚本位置；返回：错误描述
def unregister_cron(monitor_scrits):
    szret = maker_public.execCmdAndGetOutput("crontab -l")
    pyregpath = monitor_scrits.replace(".", "\\.")
    if None != re.search(".+python[ \\t]+"+pyregpath+"[^\\n]+\\n", szret):
        szret = re.sub(".+python[ \\t]+"+monitor_scrits+"[^\\n]+\\n", "", szret)
    sz_err = maker_public.writeTxtFile("/tmp/dpdk_scrits_crontab", szret)
    if 0 < len(sz_err):
        os.system("rm -Rf /tmp/dpdk_scrits_crontab")
        return sz_err
    if 0 != os.system("crontab /tmp/dpdk_scrits_crontab"):
        os.system("rm -Rf /tmp/dpdk_scrits_crontab")
        return "Failed to unregister cron"
    os.system("rm -Rf /tmp/dpdk_scrits_crontab")
    return ""


#功能：关闭一个进程；参数：进程信息；返回：已经执行了关闭操作的进程
def do_killproc(app_lst):
    kill_cmd = ""
    proc_lst = []
    for appinfo in app_lst:    
        if False == os.path.isfile(os.path.abspath(appinfo[0])):
            return []
        app_name = os.path.basename(os.path.abspath(appinfo[0]))
        kill_cmd += "killall -9 "+app_name+" || "
        proc_lst.append("app_name")
    kill_cmd = str(kill_cmd).rstrip(" || ")
    os.system(kill_cmd)
    return proc_lst


#功能：等待进程关闭；参数：进程信息；返回：错误描述
def do_waitproc(proc_lst):
    exists = True
    while exists:
        curexiste = 0
        app_stat = maker_public.execCmdAndGetOutput("ps -aux")
        app_stat = re.sub(".*grep[ \\t]+--color=auto.*($|\\n)", "", app_stat)
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

    
#功能：卸载dpdk的环境；参数：无；返回：错误描述
def Uinstall_dpdkenv(app_lst):
    #注销定时任务
    sz_err = unregister_cron()
    if "" != sz_err:
        return sz_err
    #关闭全部进程
    sz_err = close_proc(app_lst)
    if "" != sz_err:
        return sz_err
    #开启服务
    sz_err = enable_onesrv("irqbalance.service")
    if "" != sz_err:
        return sz_err
    #核隔离和关闭iommu
    sz_err = free_cpu()
    if "" != sz_err:
        return sz_err
    maker_public.do_reboot("press any key to reboot...")
    return ""


####################################初始化#################################################
#功能：设置ASLR；参数：无；返回：错误码
def set_ASLR(opt):
    if "0"!=opt or "1"!=opt:
        return "ASLR_FLG must be 0 or 1"
    if os.system("echo "+opt+" > /proc/sys/kernel/randomize_va_space"):
        return "set ASLR failed!"
    return ""


#功能：加载巨页；参数：巨页大小、巨页数量；返回：错误码
def set_one_hugepage(node_path, page_name, page_cnt):
    all_pages = os.listdir(node_path)
    sz_err = ""
    #关闭原先设置的巨页
    for page in all_pages:
        if page != page_name:
            os.system("echo 0 > "+node_path+"/"+page+"/nr_hugepages")
        else:
            if 0 != os.system("echo "+page_cnt+" > "+node_path+"/"+page+"/nr_hugepages"):
                sz_err = "Failed to set "+\
                    page_cnt+" > "+node_path+"/"+page+"/nr_hugepages"
    return sz_err  


#功能：加载巨页；参数：巨页大小、巨页数量；返回：错误码
def set_hugepage(page_size, page_cnt):
    #检测类型大小
    if 2048!=page_size and 1048576!=page_size:
        return "page_size must be 2048 or 1048576"
    #检测page_cnt是否是2的幂次方，并且修正到2的幂次方
    highest_1 = 0
    cnt_1 = 0
    cur_pos = 0
    while 0 < page_cnt:
        if page_cnt%1:
            cnt_1 = cnt_1+1
            highest_1 = cur_pos
        cur_pos = cur_pos+1
        page_cnt = page_cnt/2
    if 1 != cnt_1:
        page_cnt = pow(2*(highest_1+1))
    #检测内存是否超出
    total_mem = (psutil.virtual_memory()).total
    if page_size*page_cnt >= total_mem:
        return "hugpage limit exceeded"
    #设置巨页
    node_info = maker_public.execCmdAndGetOutput("ls /sys/devices/system/node/"
        " | grep -P \"^node\\d+$\" | sort -u").split("\n")
    if 2 >= len(node_info):#这里2的原因是最后结束行是空行
        sz_err = set_one_hugepage("/sys/kernel/mm/hugepages", \
            ("hugepages-%dkB" %page_size), ("%d" %page_cnt))
        if "" != sz_err:
            return sz_err
    else:
        for cur_nd in node_info:
            sz_err = set_one_hugepage("/sys/devices/system/node/"+cur_nd+"/hugepages", \
                ("hugepages-%dkB" %page_size), ("%d" %page_cnt))
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
            os.system(imsmod_cmd)
        if "" == maker_public.execCmdAndGetOutput("lsmod | grep "+kmod):
            return "Failed to load "+kmod
    kmod = kmod[0]
    #绑定网卡设备
    python = maker_public.get_python()
    all_err = ""
    if False == os.path.exists(drvctl_path):
        for dev in dev_lst:
            dev_name = dev[0]
            dev_addr = dev[1]
            if "" == dev_addr:
                all_err += "No PCI address\n"
                continue
            if ""!=dev_name and "" != maker_public.execCmdAndGetOutput(\
                python+" "+devbind_path+
                "/dpdk-devbind --status-dev net | grep \"if="+dev_name+"\""):
                os.system("ifconfig "+dev_name+" down")
            if "" != maker_public.execCmdAndGetOutput(\
                python+" "+devbind_path+"/dpdk-devbind --status-dev net | "\
                "grep -P \""+dev_addr+"[ \\t]+'.+'[ \\t]+drv=.+[ \\t]unused=.+\""):
                all_err = "Failed to find "+dev_addr+"\n"
                os.system(python+" "+devbind_path+"/dpdk-devbind -u "+dev_addr)
            if 0 != os.system(python+" "+devbind_path+"/dpdk-devbind --b "+kmod+" "+dev_addr):
                all_err = "Failed to bind "+dev_addr+"\n"
        os.system("python3 "+devbind_path+"/dpdk-devbind --status-dev net")
    else:
        for dev in dev_lst:
            if 0 != os.system("cd "+drvctl_path+" && "\
                "DEV_UUID=$(basename $(readlink /sys/class/net/"+dev[0]+"/device)) && "\
                "./driverctl -b vmbus set-override $DEV_UUID "+kmod):
                all_err = "Failed to bind "+dev[0]+"\n"
        os.system("cd "+drvctl_path+" && ./driverctl -b vmbus list-overrides")


#功能：设置DPDK的环境参数；参数：巨页大小、巨页数量、是否开启地址随机化；返回：错误码
def Set_dpdkenv(ASLR_flg, page_size, page_cnt, devbind_path, drvctl_path, \
    kmod_path, kmod_list, dev_lst):
    #设置地址随机化
    sz_err = set_ASLR(ASLR_flg)
    if "" != sz_err:
        return sz_err
    #设置巨页
    sz_err = set_hugepage(page_size, page_cnt)
    if "" != sz_err:
        return sz_err
    #绑定设备
    return bind_device(devbind_path, drvctl_path, kmod_path, kmod_list, dev_lst)


####################################监控进程################################################
#功能：监控一个应用；参数：app名称-app启动路径及参数；返回：错误码
def monitor_oneapp(appinfo):
    if False == os.path.isfile(os.path.abspath(appinfo[0])):
        return "Failed to find "+appinfo[0]
    app_path = os.path.abspath(appinfo[0])
    app_name = os.path.basename(os.path.abspath(appinfo[0]))
    work_dir = os.path.abspath(appinfo[1])
    app_param = appinfo[2]
    #检测进程是否存在
    app_stat = maker_public.execCmdAndGetOutput("ps -aux | grep "+app_name)
    app_stat = re.sub(".*grep[ \\t]+--color=auto.*($|\\n)", "", app_stat)
    if ""==app_stat:
        os.system("cd "+work_dir+" && "+app_path+" "+app_param)
    return ""


#功能：监控DPDK的应用；参数：app列表，包括app名称-app启动路径及参数；返回：错误码
def Monitor_dpdkapp(app_lst):
    sz_err = ""
    for appinfo in app_lst:
        sz_err += monitor_oneapp(appinfo)
    return sz_err
    

