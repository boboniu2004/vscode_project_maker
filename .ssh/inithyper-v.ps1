#check windows version
$IsArm64 = systeminfo | where{$_ -match "ARM64-based"}
$OsInfo = systeminfo | where{$_ -match "OS.+Microsoft Windows"}
$OsInfo
if ([String]::IsNullOrEmpty($OsInfo) -or ($OsInfo -notmatch "OS.+Microsoft Windows 10" -and $OsInfo -notmatch "OS.+Microsoft Windows 11"))
{
    "This script must run in win10 or win11"
    pause
    exit
}
"Check windows version finish"

#start hyper-v
$Features = dism /online  /Get-Features /Format:Table | where{$_ -match "Microsoft-Hyper-V-All.+"}
$Features
if ([String]::IsNullOrEmpty($Features))
{
    "Can not find Hyper-V,if you windows is ""win10/win11 home"",you can run this cmd(have no testing): pushd ""%~dp0"" dir /b %SystemRoot%\servicing\Packages\*Hyper-V*.mum >hyper-v.txt for /f %%i in ('findstr /i . hyper-v.txt 2^>nul') do dism /online /norestart /add-package:""%SystemRoot%\servicing\Packages\%%i"" del hyper-v.txt Dism /online /enable-feature /featurename:Microsoft-Hyper-V-All /LimitAccess /ALL"
    pause
    exit
}
if ($Features -match "Microsoft-Hyper-V-All.+已禁用")
{
    Dism /Online /Enable-Feature /FeatureName:Microsoft-Hyper-V-All /All
}
#start Microsoft-Windows-Subsystem-Linux
if (![String]::IsNullOrEmpty($IsArm64))
{
    if ($Features -match "Microsoft-Windows-Subsystem-Linux.+已禁用")
    {
        Dism /Online /Enable-Feature /FeatureName:Microsoft-Windows-Subsystem-Linux /All
    }
}
"Open hyper-v finish"

#create Hyper-V Manager.lnk
$Shell = New-Object -ComObject WScript.Shell
$Desktop = [System.Environment]::GetFolderPath('Desktop')
$HaveShortcut = Test-Path "$Desktop\Hyper-V Manager.lnk"
if ($HaveShortcut -like "False")
{
    $Shortcut = $Shell.CreateShortcut("$Desktop\Hyper-V Manager.lnk")
    $Shortcut.TargetPath = "%windir%\System32\mmc.exe"
    $Shortcut.Arguments = "%windir%\System32\virtmgmt.msc"
    $Shortcut.Description = "Manager your virtual machine"
    $Shortcut.IconLocation = "%ProgramFiles%\Hyper-V\SnapInAbout.dll"
    $Shortcut.WorkingDirectory = "%ProgramFiles%\Hyper-V\"
    $Shortcut.Save()
    "Create $Desktop\Hyper-V Manager.lnk"
}
"Create Hyper-V $Desktop\Hyper-V Manager.lnk finish"

#create NAT network
#stop all virtual machines
Get-VM | where{$_.State -eq "Running"} | foreach{Stop-VM $_.Name}
if ([String]::IsNullOrEmpty($IsArm64))
{
    Get-NetNat | Remove-NetNat
}
$VMSwitchInfo = Get-NetAdapter -Name "*HYPER-V-NAT-Network*"
if ([String]::IsNullOrEmpty($VMSwitchInfo))
{
    New-VMSwitch -SwitchName "HYPER-V-NAT-Network" -SwitchType Internal -Notes "Internal network,use 192.168,137.0/24"
}
$VMSwitchInfo = Get-NetAdapter -Name "*HYPER-V-NAT-Network*"
if ($VMSwitchInfo)
{
    Remove-NetIPAddress -InterfaceIndex $VMSwitchInfo.ifIndex
    New-NetIPAddress -InterfaceIndex $VMSwitchInfo.ifIndex -IpAddress 192.168.137.1 -PrefixLength 24
}
if ([String]::IsNullOrEmpty($IsArm64))
{
    New-NetNat -Name "HYPER-V-NAT-Network" -InternalIPInterfaceAddressPrefix "192.168.137.0/24"
}
"Create NAT network finish"

#Set wsl2
if (![String]::IsNullOrEmpty($IsArm64))
{
    wsl --update
    wsl --set-default-version 2
}
