# vscode_project_maker
## 概述
工作n年了，工作环境一直是台式机，所以整了个双硬盘分别装了windows和linux，平时的开发就在linux下，普通工作就在windows下，虽然经常切换系统感觉比较麻烦，但是凑合下也就算了。不过，在2019年12月，爱折腾的我终于给自己换了一个工作。新公司给我配了一台装好了win10专业版的笔记本，这家伙，就像刘姥姥进大观园，头一遭啊！怎么安装linux？怎么安装开发环境？没办法，经过两个月的折腾，终于使用win10+hyper-v+vscode整合出了一个开发环境，该方法在win10中开启HYPER-V，然后安装CentOS和Ubuntu虚拟机，最后安装vscode，这一切完成后，使用该工程提供的脚本初始化虚拟机，创建C/C++，GO,PYTHON,JAVA工程供主机上的vscode开发。
接下来从**安装**，**新建工程**，**编译调试工程**这三个角度来进行说明。

# 安装
## 开启hyper-v
要开启并使用hyper-v，需要满足以下三个条件：

1 操作系统是windows 10专业版(据说windows 10家庭版也可以，但是未进行测试)。

2 CPU支持x86_64指令集和intel硬件虚拟化技术。

3 可以连接互联网。

--------------------------------------------------------------------------------------------------------------------------------------------
对于满足上述条件的机器：

第一步，重启机器，进入BIOS，开启intel硬件虚拟化支持。具体的开启方法根据BIOS厂商而异，请自行百度。

第二步，下载vscode_project_maker( https://github.com/boboniu2004/vscode_project_maker )。

第三步，解压缩vscode_project_maker，把**vscode_project_maker\\.ssh**目录拷贝到当前用户的主目录下，进入.ssh目录后选中**inithyper-v.bat**脚本，单击右键以管理员权限运行，如果执行权限不对或者不是windows10专业版，脚本会报错。

第四步，如果正确开启了hyper-v，则会要求重启，重新启动后进入**vscode_project_maker\\.ssh**目录，以管理员权限再次运行**inithyper-v.bat**脚本，会创建虚拟网卡供后续安装的虚拟机进行通信，同时也会在桌面创建一个**hyper-v管理器快捷方式**。

--------------------------------------------------------------------------------------------------------------------------------------------


## 安装linux虚拟机
首先是双击桌面**hyper-v管理器快捷方式**，在弹出的界面中选中**Hyper-V设置**，修改虚拟硬盘，虚拟机配置文件的存储位置，最好不要存储在C盘，因为会占用大量的存储空间。![set_hyper-v](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/set_hyper-v.jpg) 

在虚拟机管理界面中选中**快速创建...**：在弹出的对话框中点击**更改安装源(I)...**，选择centos7_x86-64或者ubuntu18.04_x86-64镜像；取消**此虚拟机将运行Windows(启用Windows Secure Boot)**；点击**更多选项(R)**修改虚拟机的名称。上面三步做好后就可以点击**创建虚拟机(V)**按钮来创建虚拟机。这里需要说明一下，因为网络的原因，可能出现一直无法点击**创建虚拟机(V)**的情况，此时只需要断开windows 10的网络，重新创建虚拟机即可。

接着在创建成功的页面上点击**编辑设置(S)**。在弹出的界面中依次点击**添加硬件**->**网络适配器**->**添加(D)**，为虚拟机新建一个网卡，网卡的虚拟交换机设置为**HYPER-V-NAT-Network**；点击**检查点**，取消**启用检查点(E)**；点击**处理器**，设置处理器为物理CPU的一半(推荐)，点击**内存**，将**RAM(R)**设置为2048MB，动态内存区间设置为512M~2048M(推荐)；最后点击**确定**完成虚拟机的配置。

最后就可以在界面上看见新建的虚拟机了，此时可以选中虚拟机，然后点击**连接**进入虚拟机界面，再点击**启动**开始安装linux。![create_vm](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/create_vm.jpg) ![set_vm](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/set_vm.jpg) ![start_vm](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/start_vm.jpg)

--------------------------------------------------------------------------------------------------------------------------------------------

## 初始化虚拟机
centos和ubuntu的详细安装步骤请自行百度，不在本文讨论范围。安装centos7时要关闭内核调试，选择GNOME桌面版。安装ubuntu18.04时**强烈建议**关闭主机的网络连接，否则在下载deb包时卡死。安装完毕重启后，以图形界面的方式登录进系统，使用firefox从 https://github.com/boboniu2004/vscode_project_maker 下载zip或者tar.gz格式的代码，然后解压缩：

    zip格式解压缩命令：unzip ./vscode_project_maker.zip

    tar.gz格式解压缩命令：tar -xvf ./vscode_project_maker.tar.gz
    
或可使用git下载，在终端下运行命令： git clone https://github.com/boboniu2004/vscode_project_maker 即可；

进入**vscode_project_maker/**目录后，打开终端，在其中运行命令，其中的IP地址为和windows 10主机通信的地址，必须是192.168.137.0/24网段：

    centos下：sudo python osenv_maker.py 192.168.137.xx

    ubuntu下：sudo python3 osenv_maker.py 192.168.137.xx

安装脚本会自动升级系统到最新版；系统安装配置GCC，PYTHON，JAVA，GO，GIT，SSHD等软件；配置网络；关闭图形界面；还会给ubuntu系统开启root账号并设置密码。注意：因为网络原因，在安装GO和GIT时可能会因为网络问题而失败，此时只需要多试几次即可。安装完毕重启系统后即可用字符界面登录。![init_linux](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/init_linux.jpg)

--------------------------------------------------------------------------------------------------------------------------------------------

## 安装vscode
从( https://code.visualstudio.com )中下载最新的vscode进行安装，安装完毕后，打开vscode，在**Extensions**(扩展插件市场)中检索并安装Remote-SSH插件(Microsoft)。接着进入windows 10当前用户主目录下的.ssh目录，以管理员权限运行**initssh.bat**，输入前面安装的虚拟机的IP地址(192.168.137.00/24网段)，root账号，root密码后会初始化虚拟机的ssh免密连接，以后vscode就可以打开**Remote Explorer**->**Configure**->**用户主目录\\.ssh\\config**，编辑连接信息即可使用该免密连接操作虚拟机了。其中**IdentityFile**为前面的initssh.bat脚本生成的ssh连接私钥，连接上去后就可以在vscode的TERMINAL中执行各种shell命令。注意：有些情况下，会因为IP复用的情况连接不上虚拟机，此时只需要删除用户主目录\\.ssh\\hosts文件即可。

连接上虚拟机后，就可以在**Extensions**中安装**C/C++(Microsoft)**，**Python(Microsoft)**，**Go(Microsoft)**，**Java Extension Pack(Microsoft)**，**PlantUML(Microsoft)**。注意：这些扩展插件会安装在虚拟机中。![connetc_vm](https://github.com/boboniu2004/vscode_project_maker/blob/master/picture/connetc_vm.jpg)

--------------------------------------------------------------------------------------------------------------------------------------------

# 新建工程

# 编译调试工程
