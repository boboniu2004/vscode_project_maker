#!/usr/python/bin
# -*- coding: utf-8 -*-


import maker_public
import os
import sys
import re


#函数功能：制作gp语言的makefile文件
#函数参数：工程类型，工程路径
#函数返回：错误描述
def makeMakefile(szAppType, szProjPath):
    #检测
    if "app"!=szAppType and "shared"!=szAppType and "static"!=szAppType:
        return ("Invalid output(%s)" %(szAppType))
    #读取基础的makefile文件
    szMakeCont,szErr = maker_public.readTxtFile( os.path.dirname(os.path.abspath(sys.argv[0]))+"/golang_maker/makefile.conf" )
    if 0 < len(szErr):
        return szErr
    #替换编译选项
    if "app" == szAppType:
        szMakeCont = re.sub("\\n[ \\t]*GOFLAGS[ \\t]*:=.*", \
            "\nGOFLAGS := -a -v -gcflags \"-N -l\" -ldflags \"-w -s\"", szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*GOFLAGS_DBG[ \\t]*:=.*", \
            "\nGOFLAGS_DBG := -v -gcflags \"-N -l\"", szMakeCont)
    elif "shared" == szAppType:
        szMakeCont = re.sub("\\n[ \\t]*GOFLAGS[ \\t]*:=.*", \
            "\nGOFLAGS := -a -v -gcflags \"-N -l\" -ldflags \"-w -s\" -buildmode=plugin", szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*GOFLAGS_DBG[ \\t]*:=.*", \
            "\nGOFLAGS_DBG := -v -gcflags \"-N -l\" -buildmode=plugin", szMakeCont)
    else:
        szMakeCont = re.sub("\\n[ \\t]*GOFLAGS[ \\t]*:=.*", \
            "\nGOFLAGS := -a -v -gcflags \"-N -l\" -ldflags \"-w -s\" -buildmode=archive", szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*GOFLAGS_DBG[ \\t]*:=.*", \
            "\nGOFLAGS_DBG := -i -v -gcflags \"-N -l\" -buildmode=archive", szMakeCont)
    #替换编译命令
    #获取模块名称
    szModName = os.path.basename(os.path.abspath(szProjPath))
    szSuffix = ""
    szSrc = szModName+"/src/main"
    if "shared" == szAppType:
         szSuffix = ".so"
    elif "static" == szAppType:
        szSuffix = ".a"
        szSrc = "./..."
    szMakeCont = re.sub("\\n\\t\\$\\(GO\\)[ \\t]*.+[ \\t]*\\$\\(GOFLAGS\\)[ \\t]*\\$\\(LIBS\\).*", \
        "\n\t$(GO) -o $(TOP_DIR)/bin/"+szModName+szSuffix+" $(GOFLAGS) $(LIBS) "+szSrc,\
        szMakeCont)
    szMakeCont = re.sub("\\n\\t\\$\\(GO\\)[ \\t]*.+[ \\t]*\\$\\(GOFLAGS_DBG\\)[ \\t]*\\$\\(LIBS\\).*", \
        "\n\t$(GO) -o $(TOP_DIR)/bin/"+szModName+".debug"+szSuffix+" $(GOFLAGS_DBG) $(LIBS) "+szSrc, \
        szMakeCont)   
    #替换GOPATH(该功能在go1.8以上不需要了)
    #szMakeCont = re.sub("\\n[ \\t]*GOPATH[ \\t]*:=.*", ("\nGOPATH := %s:%s" %(szProjPath, os.environ["HOME"]+"/go")), szMakeCont)
    #写入makefile文件
    szErr = maker_public.writeTxtFile(szProjPath+"/makefile", szMakeCont)
    return szErr



#函数功能：制作编译文件
#函数参数：工程路径
#函数返回：错误描述
def makeBuildfile(szProjPath):
    szConfig = \
        "{\n"\
        "    // See https://go.microsoft.com/fwlink/?LinkId=733558\n"\
        "    // for the documentation about the tasks.json format\n"\
        "    \"version\": \"2.0.0\",\n"\
        "    \"tasks\": [\n"\
        "        {\n"\
        "            \"type\": \"shell\",\n"\
        "            \"label\": \"go build active file\",\n"\
        "            \"command\": \"/usr/bin/make\",\n"\
        "            \"args\": [\n"\
        "                \"-f\",\n"\
        "                \"${workspaceFolder}/makefile\",\n"\
        "                \"debug\"\n"\
        "            ],\n"\
        "            \"options\": {\n"\
        "                \"cwd\": \"${workspaceFolder}\"\n"\
        "            },\n"\
        "            \"problemMatcher\": [\n"\
        "                \"$gcc\"\n"\
        "            ],\n"\
        "            \"group\": {\n"\
        "                \"kind\": \"build\",\n"\
        "                \"isDefault\": true\n"\
        "            }\n"\
        "        },\n"\
        "        {\n"\
        "            \"type\": \"shell\",\n"\
        "            \"label\": \"go clean active file\",\n"\
        "            \"command\": \"/usr/bin/make\",\n"\
        "            \"args\": [\n"\
        "                \"-f\",\n"\
        "                \"${workspaceFolder}/makefile\",\n"\
        "                \"clean\"\n"\
        "            ],\n"\
        "            \"options\": {\n"\
        "                \"cwd\": \"${workspaceFolder}\"\n"\
        "            },\n"\
        "            \"problemMatcher\": [\n"\
        "                \"$gcc\"\n"\
        "            ],\n"\
        "            \"group\": {\n"\
        "                \"kind\": \"build\",\n"\
        "                \"isDefault\": true\n"\
        "            }\n"\
        "        }\n"\
        "    ]\n"\
        "}\n"
    return maker_public.writeTxtFile(szProjPath+"/.vscode/tasks.json", szConfig)


#函数功能：制作调试文件
#函数参数：工程路径
#函数返回：错误描述
def makeDebugfile(szProjPath):
    szConfig = \
    "    {\n"\
    "        // Use IntelliSense to learn about possible attributes.\n"\
    "        // Hover to view descriptions of existing attributes.\n"\
    "        // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387\n"\
    "        \"version\": \"0.2.0\",\n"\
    "        \"configurations\": [\n"\
    "            {\n"\
    "                \"name\": \"Launch\",\n"\
    "                \"type\": \"go\",\n"\
    "                \"request\": \"launch\",\n"\
    "                \"mode\": \"debug\",\n"\
    "                \"program\": \"${workspaceFolder}/src/main/main.go\",\n"\
    "                \"env\": {\n"\
    "                },\n"\
    "                \"args\": []\n"\
    "            }\n"\
    "        ]\n"\
    "    }\n"
    return maker_public.writeTxtFile(szProjPath+"/.vscode/launch.json", szConfig)


#函数功能：给golang工程创建mod文件
#函数参数：工程路径
#函数返回：错误描述
def makeGomod(szProjPath):
    #获取模块名称
    szModName = os.path.basename(os.path.abspath(szProjPath))
    if True==os.path.exists(szProjPath+"/go.mod") and False==os.path.isfile(szProjPath+"/go.mod"):
        return "Can not create go.mod"
    if False == os.path.exists(szProjPath+"/go.mod"):
        szPwd = os.getcwd()
        os.chdir(szProjPath)
        if 0 != os.system("go mod init "+szModName):
            os.chdir(szPwd)
            return "Can not create go.mod"
        os.chdir(szPwd)
    #
    return ""



#函数功能：创建golang类型的工程
#函数参数：开发语言，工程类型，工程路径
#函数返回：错误描述
def MakeProject(szLangType, szAppType, szProjPath):
    #建立bin目录
    szErr = maker_public.makeDirs(szProjPath+"/bin")
    if 0 < len(szErr):
        return szErr
    #建立src目录
    szErr = maker_public.makeDirs(szProjPath+"/src")
    if 0 < len(szErr):
        return szErr
    #建立pkg目录
    szErr = maker_public.makeDirs(szProjPath+"/pkg")
    if 0 < len(szErr):
        return szErr
    #建立main目录
    szErr = maker_public.makeDirs(szProjPath+"/src/main")
    if 0 < len(szErr):
        return szErr
    #建立.vscode目录
    szErr = maker_public.makeDirs(szProjPath+"/.vscode")
    if 0 < len(szErr):
        return szErr
    #建立makefile
    szErr = makeMakefile(szAppType, szProjPath)
    if 0 < len(szErr):
        return szErr
    #建立编译任务
    szErr = makeBuildfile(szProjPath)
    if 0 < len(szErr):
        return szErr   
    #建立调试任务
    szErr = makeDebugfile(szProjPath)
    if 0 < len(szErr):
        return szErr
    #建立主文件
    szData = \
        "package main\n\n\n"\
        "import (\n"\
	    "    \"fmt\"\n"\
        ")\n\n\n"\
        "//函数功能：主函数\n"\
        "//函数参数：无\n"\
        "//函数返回：进程退出码\n"\
        "func main()  {\n"\
        "	fmt.Print(\"hello world\")\n"\
        "}"
    szErr = maker_public.writeTxtFile(szProjPath+"/src/main/main.go", szData)
    if 0 < len(szErr):
        return szErr
    #创建MOD
    szErr = makeGomod(szProjPath)
    if 0 < len(szErr):
        return szErr
    #
    return ""
    