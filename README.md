# vscode_project_maker
## 概述
工作n年了，工作环境一直是台式机，所以整了个双硬盘分别装了windows和linux，平时的开发就在linux下，普通工作就在windows下，虽然经常切换系统感觉比较麻烦，但是凑合下也就算了。不过，在2019年12月，爱折腾的我终于给自己换了一个工作。新公司给我配了一台装好了win10专业版的笔记本，这家伙，就像刘姥姥进大观园，头一遭啊！怎么安装linux？怎么安装开发环境？没办法，经过两个月的折腾，终于使用win10+hyper-v+vscode整合出了一个开发环境，该方法在win10中开启HYPER-V，然后安装CentOS和Ubuntu虚拟机，最后安装vscode，这一切完成后，使用该工程提供的脚本初始化虚拟机，创建C/C++，GO,PYTHON,JAVA工程供主机上的vscode开发。
接下来从**安装**，**备份**，**配置网络**，**配置DPDK和hyperscan**，**新建工程**，**编译调试工程**，**创建f-stack开发环境**，**创建vpp开发环境**，**DPDK管理脚本**这九个角度来进行说明。

# 安装
## 硬件要求
硬件平台为intel x86_64，需要开启硬件虚拟化技术vt-x，具体的开启方法根据BIOS厂商而异，请自行百度。

## 系统要求
宿主操作系统目前支持windows 10专业版(据说windows 10家庭版也可以，但是未进行测试)。

## 网络要求
需要连接互联网。

## 安装虚拟机软件
目前支持hyper-v和virtual box 6.1以上版本。

### 安装hyper-v
对于满足硬件、OS、网络要求的机器：
第一步，下载vscode_project_maker( https://github.com/boboniu2004/vscode_project_maker )。

第二步，解压缩vscode_project_maker，把**vscode_project_maker\\.ssh**目录拷贝到当前用户的主目录下，进入.ssh目录后选中**inithyper-v.bat**脚本，单击右键以管理员权限运行，如果执行权限不对或者不是windows10/windows11专业版，脚本会报错。因为目前在windows10 arm64/windows11 arm64下没有可以运行在hyper-v中的的linux发行版，所以windows10 arm64/windows11 arm64下**inithyper-v.bat**会同时开启hyper-v和WSL(Windows Subsystem for Linux)。

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
    mkdir -P D:\WSL\ubuntu2004
    wsl -t Ubuntu20.04
    wsl --export Ubuntu20.04 D:\bark\ubuntu2004.tar
    wsl --unregister Ubuntu20.04
    wsl --import Ubuntu20.04 D:\WSL\ubuntu2004 D:\bark\ubuntu2004.tar
    ubuntu2004.exe config --default-user root

上述命令第一第二行在D盘下创建了bark目录和WSL/ubuntu2004目录，分别用于存储备份出来的虚拟机和重新安装的位置；第三行是关闭已经安装的ubuntu虚拟机，虚拟机名称来源自wsl --list；第四行是将虚拟机导出到D:\bark中，文件名为ubuntu2004.tar；第五行是注销已备份的虚拟机；第六行是从D:\bark\ubuntu2004.tar中重新安装虚拟机到D:\WSL\ubuntu2004，并且命名为Ubuntu20.04；第七行是将虚拟机的默认登录账号设置为root，其中ubuntu2004.exe是虚拟机的配置程序，输入命令时可以按tab键选择。

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

### 设置centos7开发环境
以root账号进入系统，打开终端，运行一下命令：

    cd /root/
    wget https://github.com/boboniu2004/vscode_project_maker/archive/refs/heads/master.zip -O ./vscode_project_maker.zip
    unzip ./vscode_project_maker.zip
    cd ./vscode_project_maker-master

    在hyper-v环境下：
        python osenv_maker.py 192.168.137.xx/24
    其中的IP地址为和windows 10主机通信的地址，必须是192.168.137.0/24网段。
    在virtualbox环境下：
        python osenv_maker.py
    系统会自动将第一张网卡设置为10.0.2.15/24，第二张网卡设置为192.168.56.xx/24。

### 设置centos8开发环境
以root账号进入系统，打开终端，运行一下命令：

    cd /root/
    wget https://github.com/boboniu2004/vscode_project_maker/archive/refs/heads/master.zip -O ./vscode_project_maker.zip
    unzip ./vscode_project_maker.zip
    cd ./vscode_project_maker-master

    在hyper-v环境下：
        python3 osenv_maker.py 192.168.137.xx/24
    其中的IP地址为和windows 10主机通信的地址，必须是192.168.137.0/24网段。
    在virtualbox环境下：
        python3 osenv_maker.py
    系统会自动将第一张网卡设置为10.0.2.15/24，第二张网卡设置为192.168.56.xx/24。

**注意：WSL不支持centos7和centos8**。

### 设置ubuntu开发环境
ubuntu安装时默认不开启root账号，所以只能已普通账号进入系统，打开终端，运行一下命令：

    sudo bash
    cd /root/
    wget https://github.com/boboniu2004/vscode_project_maker/archive/refs/heads/master.zip -O ./vscode_project_maker.zip
    unzip ./vscode_project_maker.zip
    cd ./vscode_project_maker-master

    在hyper-v/wsl环境下：
        python3 osenv_maker.py 192.168.137.xx/24
    其中的IP地址为和windows 10主机通信的地址，必须是192.168.137.0/24网段。在wsl模式下，运行完脚本后不会重启，此时需要在windows10 arm64/windows11 arm64下已管理员权限运行.ssh中的restartwsl2.bat来使设置生效。
    在virtualbox环境下：
        python3 osenv_maker.py
    系统会自动将第一张网卡设置为10.0.2.15/24，第二张网卡设置为192.168.56.xx/24。

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
    wsl -t Ubuntu20.04
    wsl --export Ubuntu20.04 D:\bark\ubuntu2004.tar

wsl虚拟机Ubuntu20.04就会被备份到D:\bark\ubuntu2004.tar中。

二，如果要恢复虚拟机，则运行如下命令：

    mkdir -P D:\WSL\ubuntu2004
    wsl --import Ubuntu20.04 D:\WSL\ubuntu2004 D:\bark\ubuntu2004.tar

会将虚拟机Ubuntu20.04还原到D:\WSL\ubuntu2004中。

# 配置网络
在hyper-v环境下，可能需要对第二块内部网卡独立配置IP，此时可以在vscode_project_maker目录下运行如下命令：

        python3 osenv_maker.py config_IP 192.168.137.xx/24
        
其中的IP地址为和windows 10主机通信的地址，必须是192.168.137.0/24网段。

# 配置DPDK和hyperscan
在virtualbox环境下、或者hyper-v环境下的centos8/ubuntu20.04系统，如果网卡支持DPDK，则可以安装DPDK开发环境。首先需要参见hyper-v虚拟机安装步骤的**第七步**、或者virtual box虚拟机安装步骤的**第四步**给虚拟机增加网卡，然后可以在vscode_project_maker目录下运行如下命令：

        python3 osenv_maker.py config_DPDK install/uninstall

其中的install为安装DPDK环境到/usr/local/dpdk中去，uninstall为卸载/usr/local/dpdk目录。默认会配置256个2M大小的巨页；驱动放置在/usr/local/dpdk/kernel下。该命令同时还会安装/卸载hyperscan。

# 新建工程
目前可以通过vscode_project_maker创建c、c++、python、java、golang开发工程。可以在vscode_project_maker目录下运行如下命令创建：

        python3 __init__.py language[c|c++|python|java|golang] output[app|static|shared] workspace

c、c++、golang可以创建可执行程序、动态库、静态库工程，python、java只能创建可执行程序工程。

工程创建完毕后，使用vscode连接上虚拟机，依次点击"File"->"Open Folder"，然后远程打开该工程目录，进行相应的开发。
![vscode_open_folder_1](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/vscode_open_folder_1.jpg) ![vscode_open_folder_2](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/vscode_open_folder_2.jpg)

# 编译调试工程

# 创建f-stack开发环境
在virtualbox环境下、或者hyper-v环境下的centos8/ubuntu20.04系统，如果网卡支持DPDK，且已经正确安装了DPDK到/usr/local/dpdk下，则可以配置f-stack开发环境。首先需要参见hyper-v虚拟机安装步骤的**第七步**、或者virtual box虚拟机安装步骤的**第四步**给虚拟机增加网卡，然后可以在vscode_project_maker目录下运行如下命令：

        python3 opensrc_maker.py f-stack [f-stack_project_path]

安装完毕后，需要重启虚拟机，然后就可以使用vscode打开f-stack开发目录，首先运行**gcc clean active file**任务重新配置，然后运行**gcc install active file**任务生成debug调试目录，该目录中可以修改f-stack和nginx的配置。后续就可以使用vscode进行集成开发和调试了，非常方便。开机后第一次调试前需要运行**gcc init active file**任务初始化dpdk环境，如果在hyper-v环境下的centos8/ubuntu20.04系统下想查看已经绑定的设备，可以运行命令：

        /usr/local/dpdk/sbin/driverctl/driverctl -b vmbus list-overrides

如果没有绑定任何设备，那么可能是LINUX内核进行了升级导致DPDK的内核模块失效了，此时需要重新安装DPDK，可以参见章节**配置DPDK**。

# 创建vpp开发环境
在virtualbox环境下、或者hyper-v环境下的centos8/ubuntu20.04系统，如果网卡支持DPDK，则可以配置vpp开发环境。首先需要参见hyper-v虚拟机安装步骤的**第七步**、或者virtual box虚拟机安装步骤的**第四步**给虚拟机增加网卡，然后可以在vscode_project_maker目录下运行如下命令：

        python3 opensrc_maker.py vpp [f-stack_project_path]

安装完毕后，然后就可以使用vscode打开vpp开发目录，该目录中的build-root/install-vpp_debug-native/vpp/etc/startup.conf中可以修改vpp配置。后续就可以使用vscode进行集成开发和调试了，非常方便。开机后第一次调试前需要运行**gcc init active file**任务初始化dpdk环境，如果在hyper-v环境下的centos8/ubuntu20.04系统下想查看已经绑定的设备，可以运行命令：

        driverctl/driverctl -b vmbus list-overrides

注意：

1 如果driverctl/driverctl命令没有绑定任何设备，那么可能是LINUX内核进行了升级导致DPDK的内核模块失效了，此时需要重新安装vpp的依赖，可以运行**gcc clean active file**任务清理vpp环境，然后运行**gcc build active file**任务重新编译vpp。

2 每次调试开始后，网卡处于非激活状态，此时需要运行build-root/install-vpp_debug-native/vpp/bin/vppctl，输入命令：

        show hardware-interfaces
        set interface state  [卡名称] up

其中卡名称从show hardw-interface命令中获取。

3 在编译vpp依赖的组件IPSec_MB时，虚拟机需要的内存会超过4GB，所以需要将虚拟机内存调整为至少6GB才能顺利编译完成，否则会出现编译任务被杀死的错误。其中hyper-v虚拟机是在**设置E**-**内存**-**动态内存**-**最大RAM(A)**中进行调整，记得在创建虚拟机时需要勾选同一界面上的**启用动态内存(E)**选项；virtualbox虚拟机是在**设置**-**系统**-**主板(M)**-**内存大小(M)**中进行调整。对hyper-v虚拟机的内存调整可以直接生效，而virtualbox需要先关闭虚拟机才能进行调整生效。
![set_vpp_memory](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/set_vpp_memory.jpg) ![virtualbox_set_vpp_memory](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/virtualbox_set_vpp_memory.jpg)

# DPDK管理脚本
DPDK应用运行在linux系统中时，为了保证CPU尽可能的运行应用代码，需要对宿主linux做一系列的优化。同时还要进行设置巨页，绑定网卡，监控进程等一系列操作。为了降低DPDK使用的复杂度，开发了一众脚本来自动化完成上述工作，目前已经在ubuntu和centos下通过了测试。这是它的参数说明。![dpdk_opt](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/dpdk_opt.jpg)

## 系统优化

## 环境设置

## 进程监控