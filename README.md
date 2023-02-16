# vscode_project_maker
## 概述
工作n年了，工作环境一直是台式机，所以整了个双硬盘分别装了windows和linux，平时的开发就在linux下，普通工作就在windows下，虽然经常切换系统感觉比较麻烦，但是凑合下也就算了。不过，在2019年12月，爱折腾的我终于给自己换了一个工作。新公司给我配了一台装好了win10专业版的笔记本，这家伙，就像刘姥姥进大观园，头一遭啊！怎么安装linux？怎么安装开发环境？没办法，经过两个月的折腾，终于使用win10+hyper-v+vscode整合出了一个开发环境，该方法在win10中开启HYPER-V，然后安装CentOS和Ubuntu虚拟机，最后安装vscode，这一切完成后，使用该工程提供的脚本初始化虚拟机，创建C/C++，GO,PYTHON,JAVA工程供主机上的vscode开发。
接下来从**安装**，**备份**，**配置网络**，**配置DPDK和hyperscan**，**新建工程**，**编译调试工程**，**创建f-stack开发环境**，**创建vpp开发环境**，**安装gperftools**,**DPDK管理脚本**这九个角度来进行说明。

# 安装
## 硬件要求
硬件平台为x86_64/arm64，需要开启硬件虚拟化技术，如intel vt-x/amd-v，具体的开启方法根据BIOS厂商而异，请自行百度。

## 系统要求
宿主操作系统目前支持windows 10专业版(据说windows 10家庭版也可以，但是未进行测试)。

## 网络要求
需要连接互联网。

## 安装虚拟机软件
目前支持hyper-v和virtual box 6.1以上版本。

### 安装hyper-v
对于满足硬件、OS、网络要求的机器：
第一步，下载vscode_project_maker( https://github.com/boboniu2004/vscode_project_maker )。

第二步，解压缩vscode_project_maker，把**vscode_project_maker\\.ssh**目录拷贝到当前用户的主目录下，进入.ssh目录后选中**inithyper-v.bat**脚本，单击右键以管理员权限运行，如果执行权限不对或者不是windows10/windows11专业版，脚本会报错。因为目前在windows10 arm64/windows11 arm64下没有可以运行在hyper-v中的的linux发行版，所以windows10 arm64/windows11 arm64下**inithyper-v.bat**会同时开启hyper-v和WSL(Windows Subsystem for Linux)。**后续如果不特别说明，则hyper-v默认包含了WSL**。

第三步，如果正确开启了hyper-v，则会要求重启，重新启动后进入**vscode_project_maker\\.ssh**目录，以管理员权限再次运行**inithyper-v.bat**脚本，会创建虚拟网卡供后续安装的虚拟机进行通信，同时也会在桌面创建一个**hyper-v管理器快捷方式**。

第四步，双击桌面**hyper-v管理器快捷方式**，在弹出的界面中选中**Hyper-V设置**，修改虚拟硬盘，虚拟机配置文件的存储位置，最好不要存储在C盘，因为会占用大量的存储空间。![set_hyper-v](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/set_hyper-v.jpg) 

#### 快速创建hyper-v虚拟机
第一步，虚拟机管理界面中选中**快速创建...**：在弹出的对话框中点击**更改安装源(I)...**，选择centos7_x86-64、centos8_x86-64、ubuntu18.04_x86-64/ubuntu20.04_x86-64镜像；取消**此虚拟机将运行Windows(启用Windows Secure Boot)**；点击**更多选项(R)**修改虚拟机的名称。上面三步做好后就可以点击**创建虚拟机(V)**按钮来创建虚拟机。这里需要说明一下，因为网络的原因，可能出现一直无法点击**创建虚拟机(V)**的情况，此时只需要断开windows 10的网络，重新创建虚拟机即可。

第二步，创建成功的页面上点击**编辑设置(S)**。在弹出的界面中依次点击**添加硬件**->**网络适配器**->**添加(D)**，为虚拟机新建一个网卡，网卡的虚拟交换机设置为**HYPER-V-NAT-Network**；点击**检查点**，取消**启用检查点(E)**；点击**处理器**，设置处理器为物理CPU的一半(推荐)，点击**内存**，将**RAM(R)**设置为4096MB，动态内存区间设置为512M~4096M(推荐，编译vpp的虚拟机内存不能低于6144M)；将**自动停止操作**设置为**强行关闭虚拟机**；最后点击**确定**完成虚拟机的配置。

第三步，如果需要使用DPDK、F-STACK或者VPP，需要添加额外的虚拟网卡。此时需要在hyper-v主界面上点击虚拟机，单机右键选中**设置(E)**。在弹出的界面中依次点击**添加硬件**->**网络适配器**->**添加(D)**，添加新的虚拟网卡，网卡的虚拟交换机设置为**HYPER-V-NAT-Network**；最后点击**确定**完成虚拟机的配置。

最后就可以在界面上看见新建的虚拟机了，此时可以选中虚拟机，然后点击**连接**进入虚拟机界面，再点击**启动**开始安装linux。![create_vm](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/create_vm.jpg) ![set_vm](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/set_vm.jpg) ![start_vm](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/start_vm.jpg)

#### 标准创建hyper-v虚拟机
快速创建的虚拟机的硬盘是动态扩展并且最大为128GB，后续在使用时虚拟硬盘会越来越大，如果要限制虚拟硬盘的大小，则需要按照标准步骤创建虚拟机。

第一步，虚拟机管理界面中选中**新建**-**虚拟机(M)**，在弹出的对话框中依次设置**虚拟机名称**，**虚拟机类型**，**虚拟机内存(要勾选动态内存)**，**虚拟机网络(选择Default Switch)**，**虚拟机硬盘(限制在50GB)**，**虚拟操作系统安装路径**。

第二步，创建成功的页面上点击**编辑设置(S)**。在弹出的界面中依次点击**添加硬件**->**网络适配器**->**添加(D)**，为虚拟机新建一个网卡，网卡的虚拟交换机设置为**HYPER-V-NAT-Network**；取消**安全**-**启用安全启动(E)**；点击**检查点**，取消**启用检查点(E)**；点击**处理器**，设置处理器为物理CPU的一半(推荐)，点击**内存**，将**RAM(R)**设置为4096MB，动态内存区间设置为512M~4096M(推荐，编译vpp的虚拟机内存不能低于6144M)；将**自动停止操作**设置为**强行关闭虚拟机**；最后点击**确定**完成虚拟机的配置。

第三步，如果需要使用DPDK、F-STACK或者VPP，需要添加额外的虚拟网卡。此时需要在hyper-v主界面上点击虚拟机，单机右键选中**设置(E)**。在弹出的界面中依次点击**添加硬件**->**网络适配器**->**添加(D)**，添加新的虚拟网卡，网卡的虚拟交换机设置为**HYPER-V-NAT-Network**；最后点击**确定**完成虚拟机的配置。

最后就可以在界面上看见新建的虚拟机了，此时可以选中虚拟机，然后点击**连接**进入虚拟机界面，再点击**启动**开始安装linux。![create_vm_stand1](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/create_vm_stand1.jpg) ![create_vm_stand2](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/create_vm_stand2.jpg) ![create_vm_stand3](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/create_vm_stand3.jpg) ![create_vm_stand4](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/create_vm_stand4.jpg) ![create_vm_stand5](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/create_vm_stand5.jpg) ![create_vm_stand6](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/create_vm_stand6.jpg) ![create_vm_stand7](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/create_vm_stand7.jpg) ![create_vm_stand8](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/create_vm_stand8.jpg) 

#### 创建安装WSL虚拟机
在windows10 arm64/windows11 arm64下，因为没有可以运行在hyper-v的linux发行版，所以需要安装WSL虚拟机。

第一步，打开**Microsoft Store**即windows应用商店，搜索linux发行版。常用的是ubuntu，可能同时有好几个版本，可以选择最新的安装。

第二步，安装完毕后，打开windows终端(windows徽标+x)，输入命令wsl --list，就可以看到已经安装的WSL虚拟机，然后将虚拟机导出到非系统盘，否则虚拟机越用越大，可能会把系统盘撑爆了，在windows终端输入以下命令：

        mkdir -P D:\bark
        mkdir -P D:\WSL\ubuntu[1804|2004]
        wsl -t Ubuntu[18.04|20.04]
        wsl --export Ubuntu[18.04|20.04] D:\bark\ubuntu[1804|2004].tar
        wsl --unregister Ubuntu[18.04|20.04]
        wsl --import Ubuntu[18.04|20.04] D:\WSL\ubuntu[1804|2004] D:\bark\ubuntu[1804|2004].tar
        ubuntu[1804|2004].exe config --default-user root

上述命令第一第二行在D盘下创建了bark目录和WSL/ubuntu[1804|2004]目录，分别用于存储备份出来的虚拟机和重新安装的位置；第三行是关闭已经安装的ubuntu虚拟机，虚拟机名称来源自wsl --list；第四行是将虚拟机导出到D:\bark中，文件名为ubuntu[1804|2004].tar；第五行是注销已备份的虚拟机；第六行是从D:\bark\ubuntu[1804|2004].tar中重新安装虚拟机到D:\WSL\ubuntu[1804|2004]，并且命名为Ubuntu[18.04|20.04]；第七行是将虚拟机的默认登录账号设置为root，其中ubuntu[1804|2004].exe是虚拟机的配置程序，输入命令时可以按tab键选择。

第三步，在重新安装了wsl虚拟机后，在windows终端输入命令wsl，即可进入虚拟机。首次登录时会要求设置密码。目前wsl虚拟机下可以编译DPDk，HYPERSCAN，F-STACK，VPP。但是只有一张网卡，所以如果要运行DPDK程序，并且绑定了该网卡，会导致虚拟机无法上网。

![install_wsl_ubuntu](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/install_wsl_ubuntu.jpg)

### 安装virtual box
第一步，从( https://www.virtualbox.org/wiki/Downloads )下载virtu box 6.1及以上版本。

第二步，双击安装包进入安装界面，需要自己选择一下安装路径!，在安装过程中会提示新增通用串行总线，此时要点击**安装**。**注意：安装过程可能会暂时断网**！ 
![virtualbox_path_select](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/virtualbox_path_select.jpg) ![virtualbox_install_bus](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/virtualbox_install_bus.jpg)

第三步，双击桌面**Oracle VM VirtualBox**，在弹出的界面中点击**新建**，此时会再次弹出界面，点击**专家模式**，依次设置虚拟机的类型、内存大小(编译vpp的虚拟机内存不能低于6144M)、硬盘(硬盘要设置为**动态分配**，且不低于**40G**)，然后创建虚拟机。**注意：虚拟机的存储路径最好不要放置在C盘，容易把分区占满**！！！**可以在创建虚拟机时选择存储路径，或者通过全局配置修改默认存储路径**。

第四步，选中界面上新创建的虚拟机，右键进入设置界面，依次修改虚拟机的可用CPU(**如果要使用DPDK，则核心数不能小于2**)，开启第二网卡，并且网络类型设置为**host only**)，在**存储**分界面中设置接下来要安装的操作系统的ISO镜像，然后保存设置。

第五步，如果需要使用DPDK、f-stack或者vpp，需要添加额外的虚拟网卡。此时单机界面上的虚拟机，右键进入设置界面，添加新的虚拟网卡，然后保存设置。

最后就可以可以选中虚拟机，然后点击**启动**开始安装linux。 ![virtualbox_create_vm](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/virtualbox_create_vm.jpg) ![virtualbox_create_vm_hd](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/virtualbox_create_vm_hd.jpg) ![virtualbox_set_vm_cpu](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/virtualbox_set_vm_cpu.jpg) ![virtualbox_set_vm_net](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/virtualbox_set_vm_net.jpg) ![virtualbox_set_vm_iso](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/virtualbox_set_vm_iso.jpg)

注意：如果需要在后台启动virtualbox虚拟机，则需要选中虚拟机，点击右键，选中**启动**->**无界面启动**。

## 安装linux
目前支持的linux系统为centos和ubuntu，详细安装步骤请自行百度，不在本文讨论范围。
### Centos安装注意事项
1 安装centos7、centos8时要关闭内核调试，选择GNOME桌面版。
2 安装完毕第一次进入系统时，会有一个初始化界面，此时需要将网络连接中设置的网卡全部打开，虚拟机软件会自动给它们配置固定IP，否则后续就没法联网。
3 初始化完毕后，注销当前用户，重新登录到root用户，然后进入**系统设置**-**网络设置**，将所有网卡都设置为**自动连接**
![VirtualBox_centos7_17_05_2021_16_58_43](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/VirtualBox_centos7_17_05_2021_16_58_43.jpg) ![VirtualBox_centos7_17_05_2021_16_59_12](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/VirtualBox_centos7_17_05_2021_16_59_12.jpg) ![VirtualBox_centos7_17_05_2021_21_27_50](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/VirtualBox_centos7_17_05_2021_21_27_50.jpg) ![VirtualBox_centos7_17_05_2021_21_28_17](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/VirtualBox_centos7_17_05_2021_21_28_17.jpg)

### Ubuntu安装注意事项
1 安装ubuntu18.04、ubuntu20.04时**强烈建议**关闭主机的网络连接，否则在下载deb包时会卡死。

2 osenv_maker.py脚本可以帮助初始化centos或者ubuntu，其参数命令如下：

        osenv_maker:    [--work_mod|--deb_src|--go_proxy|--git_proxy]
            --work_mod [mod]        工作模式，online|offline|config_IP。默认是online。
            --ip [192.168.137.xx]   在线模式下第二块网卡的IP地址，hyper-v默认为192.168.137.xx；virtualbox默认为192.168.56.xx网段。
            --deb_src [url]         deb源，默认为http://mirrors.aliyun.com/ubuntu
            --rpm_src [url]         rpm源，centos7下默认为http://mirrors.163.com/.help/CentOS%s-Base-163.repo；centos8下默认为http://mirrors.aliyun.com/repo/Centos-vault-8.5.2111.repo。
            --epel_src [url]        epel源，只在centos7生效，默认http://mirrors.aliyun.com/repo/epel-7.repo。
            --go_proxy [url]        go的代理，默认为https://proxy.golang.com.cn。
            --git_proxy [url]       github的代理(如ghproxy.com)，默认为空。

### 设置centos7开发环境
以root账号进入系统，打开终端，运行一下命令：

        cd /root/
        wget https://github.com/boboniu2004/vscode_project_maker/archive/refs/heads/master.zip -O ./vscode_project_maker.zip
        unzip ./vscode_project_maker.zip
        cd ./vscode_project_maker-master
        python osenv_maker.py --ip [192.168.137.xx|192.168.56.xx]。

其中192.168.137.xx为和windows宿主机通信的地址，hyper-v下是192.168.137.0/24网段；virtualbox下是192.168.137.0/24网段。WSL虚拟机环境下 **--ip** 字段不生效。

### 设置centos8开发环境
以root账号进入系统，打开终端，运行一下命令：

        cd /root/
        wget https://github.com/boboniu2004/vscode_project_maker/archive/refs/heads/master.zip -O ./vscode_project_maker.zip
        unzip ./vscode_project_maker.zip
        cd ./vscode_project_maker-master
        python3 osenv_maker.py --ip [192.168.137.xx|192.168.56.xx]。

其中192.168.137.xx为和windows宿主机通信的地址，hyper-v下是192.168.137.0/24网段；virtualbox下是192.168.137.0/24网段。WSL虚拟机环境下 **--ip** 字段不生效。

**注意：WSL不支持centos7和centos8**。

### 设置ubuntu开发环境
ubuntu安装时默认不开启root账号，所以只能已普通账号进入系统，打开终端，运行一下命令：

        sudo bash
        cd /root/
        wget https://github.com/boboniu2004/vscode_project_maker/archive/refs/heads/master.zip -O ./vscode_project_maker.zip
        unzip ./vscode_project_maker.zip
        cd ./vscode_project_maker-master
        python3 osenv_maker.py --ip [192.168.137.xx|192.168.56.xx]。

其中192.168.137.xx为和windows宿主机通信的地址，hyper-v下是192.168.137.0/24网段；virtualbox下是192.168.137.0/24网段。WSL虚拟机环境下 **--ip** 字段不生效。

安装脚本会自动升级系统到最新版；系统安装配置GCC，PYTHON，JAVA，GO，GIT，SSHD等软件；配置网络；关闭图形界面；还会给ubuntu系统开启root账号并设置密码。**注意：因为网络原因，在安装GO和GIT时可能会因为网络问题而失败，此时只需要多试几次即可**。安装完毕重启系统后即可用字符界面登录(**注意：hyper-v环境下ubuntu20.04系统在重启时可能会停顿在hyper-v界面，此时只需要等待一端时间，然后按组合键Ctrl+Alt+F1就可以进入登录界面**)。![init_linux](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/init_linux.jpg)

## 安装vscode
从( https://code.visualstudio.com )中下载最新的vscode进行安装，安装完毕后，打开vscode，在**Extensions**(扩展插件市场)中检索并安装Remote-SSH插件(Microsoft)。接着进入windows 10当前用户主目录下的.ssh目录，以管理员权限运行**initssh.bat**，输入前面安装的虚拟机的IP地址(192.168.137.00/24网段)、root账号、root密码后会初始化虚拟机的ssh免密连接，以后vscode就可以打开**Remote Explorer**->**Configure**->**用户主目录\\.ssh\\config**，编辑连接信息，然后右键点击**虚拟机图标**，选择**Connect to Host in Current Windows**或**Connect to Host in New Windows**即可免密连接操作虚拟机了。其中**IdentityFile**为前面的initssh.bat脚本生成的ssh连接私钥，连接上去后就可以在vscode的TERMINAL中执行各种shell命令。**注意：有些情况下，会因为IP复用的情况连接不上虚拟机，此时只需要删除用户主目录\\.ssh\\hosts文件即可**。

连接上虚拟机后，就可以在**Extensions**中安装**C/C++(Microsoft)**，**Python(Microsoft)**，**Go(Microsoft)**，**Java Extension Pack(Microsoft)**，**PlantUML(Microsoft)**。**注意：这些扩展插件会安装在虚拟机中**。![vscode_config_1](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/vscode_config_1.jpg) ![vscode_config_2](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/vscode_config_2.jpg)

## 设置虚拟机自启动
hyper-v可以在管理界面设置开机自启动；virtualbox需要修改**vscode_project_maker/.ssh/autostarts-vm.bat**脚本的**虚拟机安装目录**和**自启动虚拟机名称**，然后放置到**C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp**目录下。
![hyper-v_set_start](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/hyper-v_set_start.jpg) ![virtualbox_set_start](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/virtualbox_set_start.jpg)

# 备份
及时的备份虚拟机，可以在虚拟机损坏时及时的还原过来。

## 备份还原hyper-v虚拟机

一，在hyper-v下，需要在控制台选中相应的虚拟机，首先关闭该虚拟机，然后右键选中**导出(X)**，在谈出的对话框中选择导出路径，点击确定，等待导出完毕。导出完毕的虚拟机会存储在**导出路径-虚拟机名称目录**

二，如果要恢复虚拟机，则在控制台右侧点击**导入虚拟机**，在弹出的对话框中依次设置**备份路径**-**要导入的虚拟机**-**导入类型**-**虚拟机存储位置**。切记**导入类型**要选择**复制虚拟机(创建新的唯一ID)**，否则会把原先备份的虚拟机替换掉。

## 备份还原WSL虚拟机

一，在WSL下，可以运行如下命令导出虚拟机：

        mkdir -P D:\bark
        wsl -t Ubuntu[18.04|20.04]
        wsl --export Ubuntu[18.04|20.04] D:\bark\ubuntu[1804|2004].tar

wsl虚拟机Ubuntu[18.04|20.04]就会被备份到D:\bark\ubuntu[1804|2004].tar中。

二，如果要恢复虚拟机，则运行如下命令：

        mkdir -P D:\WSL\ubuntu[1804|2004]
        wsl --import Ubuntu[18.04|20.04] D:\WSL\ubuntu[1804|2004] D:\bark\ubuntu[1804|2004].tar

会将虚拟机Ubuntu[18.04|20.04]还原到D:\WSL\ubuntu[1804|2004]中。

# 配置网络
在hyper-v和virtualbox环境下，可能需要对第二块内部网卡独立配置IP，此时可以在vscode_project_maker目录下运行如下命令：

        python3|python osenv_maker.py --work_mod config_IP --ip [192.168.137.xx|192.168.56.xx]
        
其中192.168.137.xx为和windows宿主机通信的地址，hyper-v下是192.168.137.0/24网段；virtualbox下是192.168.137.0/24网段。

# 新建工程
目前可以通过vscode_project_maker创建c、c++、python、java、golang开发工程。可以在vscode_project_maker目录下运行如下命令创建：

        python3 __init__.py language[c|c++|python|java|golang] output[app|static|shared|app-dpdk|static-dpdk|shared-dpdk] workspace

c、c++、golang可以创建可执行程序、动态库、静态库工程，python、java只能创建可执行程序工程。-dpdk后缀的意思是创建DPDK工程，只在c、c++下有效。

工程创建完毕后，使用vscode连接上虚拟机，依次点击"File"->"Open Folder"，然后远程打开该工程目录，进行相应的开发。
![vscode_open_folder_1](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/vscode_open_folder_1.jpg) ![vscode_open_folder_2](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/vscode_open_folder_2.jpg)

# 编译调试工程

# 配置开源框架
在virtualbox环境下、或者hyper-v环境下，可以使用opensrc_maker.py来配置开源框架，目前支持dpdk、hyperscan、gperftools、fstack、vpp。

        osenv_maker:    [--dpdk|--hyperscan|--gperftools|--fstack|--vpp|--ins_path|--wor_mod]
            --dpdk        [normal|meson]         安装dpdk，可选传统编译模式，或者meson编译模式。默认normal
            --hyperscan                          安装hyperscan。
            --gperftools                         安装google的性能分析工具，包括tcmalloc内存池。
            --fstack      [dpdk_path] [hs_path]  安装f-stack用户态协议栈，需要设置dpdk路径和hyperscan路径。
            --vpp                                安装VPP框架。
            --ins_path    [path]                 安装目录，必须指明，如/usr/local。
            --git_proxy   [url]                  github的代理(如ghproxy.com)，默认为空。

# 配置DPDK-hyperscan
在virtualbox环境下、或者hyper-v环境下的centos8/Ubuntu[18.04|20.04]系统，可以安装DPDK、hyperscan开发环境。在vscode_project_maker目录下运行如下命令：

        python3 osenv_maker.py --dpdk [normal|meson] --ins_path [path]
        python3 osenv_maker.py --hyperscan --ins_path [path]

其中的install为安装DPDK环境到/usr/local/dpdk中去，uninstall为卸载/usr/local/dpdk目录。默认会配置256个2M大小的巨页；驱动放置在/usr/local/dpdk/kernel下。该命令同时还会安装/卸载hyperscan。

# 创建f-stack开发环境
在virtualbox环境下、或者hyper-v环境下的centos8/Ubuntu[18.04|20.04]系统，如果网卡支持DPDK，且已经正确安装了DPDK到/usr/local/dpdk下，则可以配置f-stack开发环境。首先需要参见hyper-v虚拟机安装步骤的**第七步**、或者virtual box虚拟机安装步骤的**第四步**给虚拟机增加网卡，然后可以在vscode_project_maker目录下运行如下命令：

        python3 opensrc_maker.py --fstack [dpdk path] [hyperscan path] --ins_path [path]

安装完毕后，需要重启虚拟机，然后就可以使用vscode打开f-stack开发目录，首先运行**gcc clean active file**任务重新配置，后续只需要运行**gcc build active file**任务就可以进行编译了，该任务会自动生成debug调试目录，该目录中可以修改f-stack和nginx的配置，非常方便。开机后第一次调试前需要运行**gcc init active file**任务初始化dpdk环境，在hyper-v下可以使用veth结合DPDK的虚拟设备来进行收发包，virtualbox建议使用系统自带的VFIO来绑定设备。

# 创建vpp开发环境
在virtualbox环境下、或者hyper-v环境下的centos8/Ubuntu[18.04|20.04]系统，如果网卡支持DPDK，则可以配置vpp开发环境。首先需要参见hyper-v虚拟机安装步骤的**第七步**、或者virtual box虚拟机安装步骤的**第四步**给虚拟机增加网卡，然后可以在vscode_project_maker目录下运行如下命令：

        python3 opensrc_maker.py --vpp --ins_path [path]

安装完毕后，然后就可以使用vscode打开vpp开发目录，该目录中的build-root/install-vpp_debug-native/vpp/etc/startup.conf中可以修改vpp配置。后续就可以使用vscode进行集成开发和调试了，非常方便。开机后第一次调试前需要运行**gcc init active file**任务初始化dpdk环境，在hyper-v下可以使用veth结合DPDK的虚拟设备来进行收发包，virtualbox建议使用系统自带的VFIO来绑定设备。

2 每次调试开始后，网卡处于非激活状态，此时需要运行build-root/install-vpp_debug-native/vpp/bin/vppctl，输入命令：

        show hardware-interfaces
        set interface state  [卡名称] up

其中卡名称从show hardw-interface命令中获取。

3 在编译vpp依赖的组件IPSec_MB时，虚拟机需要的内存会超过4GB，所以需要将虚拟机内存调整为至少6GB才能顺利编译完成，否则会出现编译任务被杀死的错误。其中hyper-v虚拟机是在**设置E**-**内存**-**动态内存**-**最大RAM(A)**中进行调整，记得在创建虚拟机时需要勾选同一界面上的**启用动态内存(E)**选项；virtualbox虚拟机是在**设置**-**系统**-**主板(M)**-**内存大小(M)**中进行调整。对hyper-v虚拟机的内存调整可以直接生效，而virtualbox需要先关闭虚拟机才能进行调整生效。
![set_vpp_memory](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/set_vpp_memory.jpg) ![virtualbox_set_vpp_memory](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/virtualbox_set_vpp_memory.jpg)

# 安装gperftools
gperftools是Google开源的一款非常使用的性能分析工具集。由tcmalloc(高性能内存池)、heap-profiler(内存使用监控器)、heap-checker(内存泄漏检查工具)、cpu-profiler(程序cpu时间统计和分析)四大块构成。利用gperftools可以优化程序的内存分配性能，检查内存泄漏情况，分析程序性能瓶颈。如果需要使用gperftools，可以在vscode_project_maker目录下运行如下命令安装：

        python3 opensrc_maker.py --gperftools --ins_path [path]

安装时会检测上次安装情况，输入'y'会覆盖原先的安装。在gperftools的安装目录下会有libunwind和gperftools两个子目录，其中libunwind是一个堆栈跟踪回溯工具，gperftools的cpu-profiler会用到它。libunwind/lib和gperftools/lib和目录中存放了需要用到的动态库和静态库。

## 使用tcmalloc
在有大量malloc/free、new/delete操作的程序中使用tcmalloc来代替linux自身的ptmalloc来分配内存，会显著提高程序的整体性能。有两种使用方法：

        静态链接法：在编译阶段直接链接gperftools/lib/libtcmalloc_minimal.a或者gperftools/lib/libtcmalloc_minimal_debug.a。
        二者主要的区别是debug库在牺牲性能的前提下带上了更多的调试信息。注意：因为tcmalloc使用了c++代码，所以在链接时需要使用g++作为链接器，否则会出现大量的c++符号找不到的错误。

        动态加载法：在程序运行前设置环境变量LD_PRELOAD，然后运行程序：LD_PRELOAD=gperftools/lib/[libtcmalloc_minimal|libtcmalloc_minimal_debug].so [app path]

tcmalloc利用hook技术在底层替换malloc/free、new/delete。所以无论是静态链接，还是动态加载都不需要改写程序原先的代码。

## 使用heap-profiler
heap-profiler会监控堆(heap)的使用情况，找出哪些函数申请了较多的内存，哪些地方可能发生了内存泄漏。使用方法为静态链接法和动态加载法：

        静态链接法：在编译阶段直接链接/usr/local/gperftools/lib/libtcmalloc_and_profiler.a和/usr/local/libunwind/lib/libunwind.a,同时增加链接选项-lpthread(arm64体系下还要添加-lz)。该使用方法适合对特定代码段进行检测：
        #include <gperftools/heap-profiler.h>
        ...
        HeapProfilerStart(out_path);
        do_somthine{}
        HeapProfilerDump(out_reason);
        HeapProfilerStop();
        编译完毕后，运行程序，就会输出一个名为out_path.001.heap的文件。

        动态加载法：在程序运行前设置环境变量LD_PRELOAD、HEAPCHECK、HEAPPROFILE三个环境变量，然后运行程序：LD_PRELOAD=perftools/lib/libtcmalloc_and_profiler.so HEAPCHECK=[minimal|normal|strict] HEAPPROFILE=[profile path] [app path]
        此外，还可以通过设置环境变量HEAP_PROFILE_ALLOCATION_INTERVAL=[bytes]或者HEAP_PROFILE_TIME_INTERVAL=[seconds]来控制heap的输出间隔，这两个变量分别表示内存每增加多少字节输出一次，或者间隔多少时间输出一次。

        运行完毕后会在HEAPPROFILE指明的地方或者out_path处会生成一系列的heap文件，可以使用pprof工具查看。
        
**注意：在arm64体系下使用动态加载法时，当程序退出后会触发bus error，但是不影响使用**

## 使用heap-checker
heap-checker是一个堆(heap)内存泄漏检测工具。可以理解为heap-profiler的子功能，运行heap-profiler时也会检查内存泄漏，所以不做详细介绍。

## 使用cpu-profiler
cpu-profiler会监控程序的CPU消耗，找出哪些函数调用消耗CPU资源。使用方法为静态链接法和动态加载法：

        静态链接法：在编译阶段直接链接/usr/local/gperftools/lib/libtcmalloc_and_profiler.a和/usr/local/libunwind/lib/libunwind.a,同时增加链接选项-lpthread。该使用方法适合对特定代码段进行检测：
        #include <gperftools/profiler.h>
        ...
        ProfilerStart(out_path);
        do_somthine{}
        ProfilerStop();
        编译完毕后，运行程序即可。

        动态加载法：在程序运行前设置环境变量LD_PRELOAD、CPUPROFILE环境变量，然后运行程序：LD_PRELOAD=perftools/lib/libtcmalloc_and_profiler.so CPUPROFILE=[out_path] [app path]

        运行完毕后会将分析结果输出到out_path中去，可以使用pprof工具查看。

# DPDK管理脚本
DPDK应用运行在linux系统中时，为了保证CPU尽可能的运行应用代码，需要对宿主linux做一系列的优化。同时还要设置巨页，绑定网卡，监控进程等一系列操作。为了降低DPDK使用的复杂度，开发了一众脚本来自动化完成上述工作，目前已经在ubuntu和centos下通过了测试。这是它的参数说明。![dpdk_opt](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/dpdk_opt.jpg)

## 脚本生成
DPDK脚本目前是vscode_project_maker的一部分，体量较大。如果想把这部分代码单独抽取出来，嵌入到自己的DPDK应用目录中去使用，可以在vscode_project_maker目录下运行如下命令：

        python3 dpdk_scrits.py make [scrits path]

该命令会将DPDK脚本的代码从vscode_project_maker中抽取出来，然后存储在[scrits path]/dpdk_scrits目录中，该目录下的__init__.py为脚本主入口。

## 系统优化
针对宿主linux系统的优化主要有五点：关闭消耗CPU的服务、关闭图形界面，设置默认的巨页尺寸，开启iommu，隔离CPU核心。其中关闭消耗CPU的服务和图形界面是为了降低CPU开销；iommu/smmu是x86/arm64体系下的设备虚拟化功能，它允许虚拟设备进行DMA操作；隔离CPU是为了保证这些CPU核心在运行DPDK应用时不会被中断和调度。可以在vscode_project_maker|dpdk_scrits目录下运行如下命令：

        python3 [dpdk_scrits|__init__].py optimsys [log file]

运行前需要配置cpu_list、page_size参数。cpu_list参数为需要隔离的CPU核心清单，从0开始，格式为1,4,5,6,2-3，不能大于等于系统CPU数目，不需要时可以配置为空串。page_size参数为需要开启的巨页的尺寸，有2048kb和1048576kb两种。[log file]为脚本可选参数，表示将运行时发生的错误记录到参数指明的日志文件中去，不设置的话会将错误打印到shell终端。

可以在vscode_project_maker|dpdk_scrits目录下运行如下命令来停止上述优化：

        python3 [dpdk_scrits|__init__].py recovsys [log file]

**注意：优化和恢复操作都需要重启操作系统后才能生效**

## 环境设置
在运行dpdk应用前，需要设置宿主linux中的巨页数量、绑定网卡。可以在vscode_project_maker|dpdk_scrits目录下运行如下命令：

        python3 [dpdk_scrits|__init__].py initenv [log file]

运行前需要配置ASLR_flg、page_size、page_cnt_lst、devbind_path、drvctl_path、kmod_path、kmod_list、 dev_lst参数。

ASLR_flg参数为linux地址随机化开启标志：1表示开启、0表示关闭。只能配置为0或者1。默认情况下是开启的，但是f-stack需要关闭该功能。

page_cnt_lst参数为需要设置的巨页的数量，按照NUMA节点进行分配，在非NUMA结构下，只能配置node0。

devbind_path参数为PCI设备的DPDK绑定脚本所在的路径，一般在DPDK安装路径的usertools下。如果配置为相对目录，则最后的绝对目录为：脚本所在目录的上一级/配置的路径。不需要时可以配置为None。
    
drvctl_path参数为VMBUS设备的DPDK绑定脚本所在的路径，该设备是微软hyper-v虚拟机的绑定程序，可以从 https://gitlab.com/driverctl/driverctl 下载。如果配置为相对目录，则最后的绝对目录为：脚本所在目录的上一级/配置的路径。devbind_path和drvctl_path不能同时生效，如果drvctl_path是有效的目录，则devbind_path会被忽略。不需要时可以配置为None。
    
kmod_path参数为DPDK内核模块所在的路径，主要是igb_uio.ko和rte_kni.ko所在的路径，在编译DPDK时获取。注意：在DPDK20以后版本中默认是不打开igb_uio的，需要额外下载igb_uio源代码并且构建编译脚本，具体可以参见本工程中对VPP的DPDK的编译方法。如果配置为相对目录，则最后的绝对目录为：脚本所在目录的上一级/配置的路径。不需要时可以配置为None。
    
kmod_list参数为需要加载的内核模块，可以是igb_uio、rte_kni、uio_pci_generic、vfio_pci、uio_hv_generic。其中uio_pci_generic是linux提供的uio驱动，大部分场景可以替代igb_uio，只有一些比较老的设备才会需要igb_uio驱动；vfio_pci是3.6之后的内核提供的一种uio驱动，可以支持IO虚拟化技术，如INTEL的VT-d、AMD的AMD-V、ARM的SMMU；uio_hv_generic是微软hyper-v虚拟机中的uio驱动。
    
dev_lst参数为需要绑定的设备，两层list，内层list每个节点有两个参数：网卡名、网卡的PCI地址。在PCI环境中，
网卡的PCI地址是必须的；在VMBUS环境中，网卡名是必须的。
    
## 进程监控
可以把vscode_project_maker拷贝到dpdk程序的安装目录下，然后dpdk_scrits下运行如下命令来初始化dpdk应用：

        python3 [dpdk_scrits|__init__].py install [log file]

运行前需要配置app_list和dllpath_list参数。

app_list参数为需要初始化的程序的信息，两层list，内层list每个节点有三个参数：程序路径、工作路径、启动参数。如果程序路径、工作路径配置为相对目录，则最后的绝对目录为：脚本所在目录的上一级/配置的路径。脚本会将这些程序加入计划任务，保证开机后将其全部加载起来，后续还会每隔一分钟检查一下进程是否存在，不存在就重新拉起来。

dllpath_list程序依赖的动态库路径清单，每个元素代表一个应用需要的动态库路径，他们会被添加到系统中，供启动时查找。如果配置为相对目录，则最后的绝对目录为：dpdk程序的安装目录/配置的路径。

如果不再需要运行dpdk应用，则可以在安装目录下的dpdk_scrits中运行如下命令来卸载dpdk应用：

        python3 [dpdk_scrits|__init__].py uninstall [log file]
