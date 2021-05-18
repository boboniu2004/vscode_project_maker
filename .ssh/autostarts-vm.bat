echo off

echo 该脚本只针对VirtualBox虚拟机，请将脚本放置在C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp目录下
echo virtual默认的安装路径是C:\Program Files\Oracle\VirtualBox，如果未安装在该目录下，则需要修改
echo [name] 需要替换成真实的虚拟机名称

"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" startvm [name] --type headless

exit