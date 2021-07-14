# vscode_project_maker
## 概述
工作n年了，工作环境一直是台式机，所以整了个双硬盘分别装了windows和linux，平时的开发就在linux下，普通工作就在windows下，虽然经常切换系统感觉比较麻烦，但是凑合下也就算了。不过，在2019年12月，爱折腾的我终于给自己换了一个工作。新公司给我配了一台装好了win10专业版的笔记本，这家伙，就像刘姥姥进大观园，头一遭啊！怎么安装linux？怎么安装开发环境？没办法，经过两个月的折腾，终于使用win10+hyper-v+vscode整合出了一个开发环境，该方法在win10中开启HYPER-V，然后安装CentOS和Ubuntu虚拟机，最后安装vscode，这一切完成后，使用该工程提供的脚本初始化虚拟机，创建C/C++，GO,PYTHON,JAVA工程供主机上的vscode开发。
接下来从**安装**，**配置网络**，**配置DPDK**，**新建工程**，**编译调试工程**这三个角度来进行说明。

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

第2步，解压缩vscode_project_maker，把**vscode_project_maker\\.ssh**目录拷贝到当前用户的主目录下，进入.ssh目录后选中**inithyper-v.bat**脚本，单击右键以管理员权限运行，如果执行权限不对或者不是windows10专业版，脚本会报错。

第三步，如果正确开启了hyper-v，则会要求重启，重新启动后进入**vscode_project_maker\\.ssh**目录，以管理员权限再次运行**inithyper-v.bat**脚本，会创建虚拟网卡供后续安装的虚拟机进行通信，同时也会在桌面创建一个**hyper-v管理器快捷方式**。

第四步，双击桌面**hyper-v管理器快捷方式**，在弹出的界面中选中**Hyper-V设置**，修改虚拟硬盘，虚拟机配置文件的存储位置，最好不要存储在C盘，因为会占用大量的存储空间。![set_hyper-v](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/set_hyper-v.jpg) 

第五步，虚拟机管理界面中选中**快速创建...**：在弹出的对话框中点击**更改安装源(I)...**，选择centos7_x86-64、ubuntu18.04_x86-64/ubuntu20.04_x86-64镜像；取消**此虚拟机将运行Windows(启用Windows Secure Boot)**；点击**更多选项(R)**修改虚拟机的名称。上面三步做好后就可以点击**创建虚拟机(V)**按钮来创建虚拟机。这里需要说明一下，因为网络的原因，可能出现一直无法点击**创建虚拟机(V)**的情况，此时只需要断开windows 10的网络，重新创建虚拟机即可。

第六步，创建成功的页面上点击**编辑设置(S)**。在弹出的界面中依次点击**添加硬件**->**网络适配器**->**添加(D)**，为虚拟机新建一个网卡，网卡的虚拟交换机设置为**HYPER-V-NAT-Network**；点击**检查点**，取消**启用检查点(E)**；点击**处理器**，设置处理器为物理CPU的一半(推荐)，点击**内存**，将**RAM(R)**设置为2048MB，动态内存区间设置为512M~2048M(推荐)；最后点击**确定**完成虚拟机的配置。

最后就可以在界面上看见新建的虚拟机了，此时可以选中虚拟机，然后点击**连接**进入虚拟机界面，再点击**启动**开始安装linux。![create_vm](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/create_vm.jpg) ![set_vm](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/set_vm.jpg) ![start_vm](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/start_vm.jpg)

### 安装virtual box
第一步，从( https://www.virtualbox.org/wiki/Downloads )下载virtu box 6.1及以上版本。

第二步，双击安装包进入安装界面，需要自己选择一下安装路径!，在安装过程中会提示新增通用串行总线，此时要点击**安装**。**注意：安装过程可能会暂时断网**！ 
![virtualbox_path_select](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/virtualbox_path_select.jpg) ![virtualbox_install_bus](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/virtualbox_install_bus.jpg)

第三步，双击桌面**Oracle VM VirtualBox**，在弹出的界面中点击**新建**，此时会再次弹出界面，点击**专家模式**，依次设置虚拟机的类型、内存大小、硬盘(硬盘要设置为**动态分配**，且不低于**40G**)，然后创建虚拟机。**注意：虚拟机的存储路径最好不要放置在C盘，容易把分区占满**！！！**可以在创建虚拟机时选择存储路径，或者通过全局配置修改默认存储路径**。

第四步，选中界面上新创建的虚拟机，右键进入设置界面，依次修改虚拟机的可用CPU(**如果要使用DPDK，则核心数不能小于2**)，开启第二网卡，并且网络类型设置为**host only**)，在**存储**分界面中设置接下来要安装的操作系统的ISO镜像，然后保存设置。

最后就可以可以选中虚拟机，然后点击**启动**开始安装linux。 ![virtualbox_create_vm](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/virtualbox_create_vm.jpg) ![virtualbox_create_vm_hd](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/virtualbox_create_vm_hd.jpg) ![virtualbox_set_vm_cpu](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/virtualbox_set_vm_cpu.jpg) ![virtualbox_set_vm_net](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/virtualbox_set_vm_net.jpg) ![virtualbox_set_vm_iso](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/virtualbox_set_vm_iso.jpg)

注意：如果需要在后台启动virtualbox虚拟机，则需要选中虚拟机，点击右键，选中**启动**->**无界面启动**。

## 安装linux
目前支持的linux系统为centos和ubuntu，详细安装步骤请自行百度，不在本文讨论范围。
### Centos安装注意事项
1 安装centos7时要关闭内核调试，选择GNOME桌面版。
2 安装完毕第一次进入系统时，会有一个初始化界面，此时需要将网络连接中设置的网卡全部打开，虚拟机软件会自动给它们配置固定IP，否则后续就没法联网。
3 初始化完毕后，注销当前用户，重新登录到root用户，然后进入**系统设置**-**网络设置**，将所有网卡都设置为**自动连接**
![VirtualBox_centos7_17_05_2021_16_58_43](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/VirtualBox_centos7_17_05_2021_16_58_43.jpg) ![VirtualBox_centos7_17_05_2021_16_59_12](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/VirtualBox_centos7_17_05_2021_16_59_12.jpg) ![VirtualBox_centos7_17_05_2021_21_27_50](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/VirtualBox_centos7_17_05_2021_21_27_50.jpg) ![VirtualBox_centos7_17_05_2021_21_28_17](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/VirtualBox_centos7_17_05_2021_21_28_17.jpg)

### Ubuntu安装注意事项
1 安装ubuntu18.04、ubuntu20.04时**强烈建议**关闭主机的网络连接，否则在下载deb包时会卡死。

### 设置centos开发环境
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

### 设置ubuntu开发环境
ubuntu安装时默认不开启root账号，所以只能已普通账号进入系统，打开终端，运行一下命令：

    sudo bash
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

安装脚本会自动升级系统到最新版；系统安装配置GCC，PYTHON，JAVA，GO，GIT，SSHD等软件；配置网络；关闭图形界面；还会给ubuntu系统开启root账号并设置密码。**注意：因为网络原因，在安装GO和GIT时可能会因为网络问题而失败，此时只需要多试几次即可**。安装完毕重启系统后即可用字符界面登录。![init_linux](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/init_linux.jpg)

## 安装vscode
从( https://code.visualstudio.com )中下载最新的vscode进行安装，安装完毕后，打开vscode，在**Extensions**(扩展插件市场)中检索并安装Remote-SSH插件(Microsoft)。接着进入windows 10当前用户主目录下的.ssh目录，以管理员权限运行**initssh.bat**，输入前面安装的虚拟机的IP地址(192.168.137.00/24网段)、root账号、root密码后会初始化虚拟机的ssh免密连接，以后vscode就可以打开**Remote Explorer**->**Configure**->**用户主目录\\.ssh\\config**，编辑连接信息，然后右键点击**虚拟机图标**，选择**Connect to Host in Current Windows**或**Connect to Host in New Windows**即可免密连接操作虚拟机了。其中**IdentityFile**为前面的initssh.bat脚本生成的ssh连接私钥，连接上去后就可以在vscode的TERMINAL中执行各种shell命令。**注意：有些情况下，会因为IP复用的情况连接不上虚拟机，此时只需要删除用户主目录\\.ssh\\hosts文件即可**。

连接上虚拟机后，就可以在**Extensions**中安装**C/C++(Microsoft)**，**Python(Microsoft)**，**Go(Microsoft)**，**Java Extension Pack(Microsoft)**，**PlantUML(Microsoft)**。**注意：这些扩展插件会安装在虚拟机中**。![vscode_config_1](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/vscode_config_1.jpg) ![vscode_config_2](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/vscode_config_2.jpg)

## 设置虚拟机自启动
hyper-v可以在管理界面设置开机自启动；virtualbox需要修改**vscode_project_maker/.ssh/autostarts-vm.bat**脚本的**虚拟机安装目录**和**自启动虚拟机名称**，然后放置到**C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp**目录下。
![hyper-v_set_start](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/hyper-v_set_start.jpg) ![virtualbox_set_start](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/virtualbox_set_start.jpg)

# 配置网络
在hyper-v环境下，可能需要对第二块内部网卡独立配置IP，此时可以在vscode_project_maker目录下运行如下命令：

        python3 osenv_maker.py config_IP 192.168.137.xx/24
        
其中的IP地址为和windows 10主机通信的地址，必须是192.168.137.0/24网段。

# 配置DPDK
在virtualbox环境下，如果网卡支持DPDK，则可以安装DPDK开发环境。此时可以在vscode_project_maker目录下运行如下命令：

        python3 osenv_maker.py config_DPDK install/uninstall

其中的install为安装DPDK环境到/usr/local/dpdk中去，uninstall为卸载/usr/local/dpdk目录。默认会配置256个2M大小的巨页；驱动放置在/usr/local/dpdk/kernel下。

# 新建工程
目前可以通过vscode_project_maker创建c、c++、python、java、golang开发工程。可以在vscode_project_maker目录下运行如下命令创建：

        python3 __init__.py language[c|c++|python|java|golang] output[app|static|shared] workspace

c、c++、golang可以创建可执行程序、动态库、静态库工程，python、java只能创建可执行程序工程。

工程创建完毕后，使用vscode连接上虚拟机，依次点击"File"->"Open Folder"，然后远程打开该工程目录，进行相应的开发。
![vscode_open_folder_1](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/vscode_open_folder_1.jpg) ![vscode_open_folder_2](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/vscode_open_folder_2.jpg)

# 编译调试工程
