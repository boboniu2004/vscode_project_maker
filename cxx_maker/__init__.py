#!/usr/python/bin
# -*- coding: utf-8 -*-


import os
import sys
import re
import maker_public


#函数功能：制作c语言的makefile文件
#函数参数：工程类型，工程路径，编译器，源文件后缀，语言标准
#函数返回：错误描述
def makeMakefile(szAppType, szProjPath, szComplier, szSuffix, szStd):
    #检测
    if "app"!=szAppType and "shared"!=szAppType and "static"!=szAppType:
        return ("Invalid output(%s)" %(szAppType))
    #读取基础的makefile文件
    szMakeCont,szErr = maker_public.readTxtFile( os.path.dirname(os.path.realpath(sys.argv[0]))+"/cxx_maker/makefile.conf" )
    if 0 < len(szErr):
        return szErr
    #替换编译器
    szMakeCont = re.sub("\\n[ \\t]*CXX[ \\t]*:=.*", ("\nCXX := %s" %(szComplier)), szMakeCont)
    #替换后缀
    szMakeCont = re.sub("\\n[ \\t]*SUFFIX[ \\t]*:=.*", ("\nSUFFIX := %s" %(szSuffix)), szMakeCont)
    #替换编译选项
    if "app"==szAppType:
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS[ \\t]*:=.*", \
            ("\nCXXFLAGS := -std=%s -Wall -m64 -O2 -fPIC -fmessage-length=0" %(szStd)), szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS_DBG[ \\t]*:=.*", \
            ("\nCXXFLAGS_DBG := -std=%s -Wall -m64 -O0 -g3 -fPIC -fmessage-length=0" %(szStd)), szMakeCont)
    elif "shared"==szAppType:
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS[ \\t]*:=.*", \
            ("\nCXXFLAGS := -std=%s -Wall -m64 -O2 -fPIC -fmessage-length=0 -fvisibility=hidden" %(szStd)), szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS_DBG[ \\t]*:=.*", \
            ("\nCXXFLAGS_DBG := -std=%s -Wall -m64 -O0 -g3 -fPIC -fmessage-length=0 -fvisibility=hidden" %(szStd)), szMakeCont)
    else:
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS[ \\t]*:=.*", \
            ("\nCXXFLAGS := -std=%s -Wall -m64 -O2 -fPIC -fmessage-length=0" %(szStd)), szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS_DBG[ \\t]*:=.*", \
            ("\nCXXFLAGS_DBG := -std=%s -Wall -m64 -O0 -g3 -fPIC -fmessage-length=0" %(szStd)), szMakeCont)
    #替换链接器
    if "app"==szAppType or "shared"==szAppType:
        szMakeCont = re.sub("\\n[ \\t]*LD[ \\t]*:=.*", "\nLD := gcc", szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*LDOUTFLG[ \\t]*:=.*", "\nLDOUTFLG := -o", szMakeCont)
    else:
        szMakeCont = re.sub("\\n[ \\t]*LD[ \\t]*:=.*", "\nLD := ar", szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*LDOUTFLG[ \\t]*:=.*", "\nLDOUTFLG := ", szMakeCont)
    #替换链接选项
    if "app" == szAppType:
        szMakeCont = re.sub("\\n[ \\t]*LDFLAGS[ \\t]*:=.*", "\nLDFLAGS := -Wl,-rpath,./", szMakeCont)
    elif "shared" == szAppType:
        szMakeCont = re.sub("\\n[ \\t]*LDFLAGS[ \\t]*:=.*", "\nLDFLAGS := -Wl,-rpath,./ -shared", szMakeCont)
    else:
        szMakeCont = re.sub("\\n[ \\t]*LDFLAGS[ \\t]*:=.*", "\nLDFLAGS := -crv", szMakeCont)
    #替换最终目标
    szTarget = os.path.basename(szProjPath)
    if "app" == szAppType:
        szMakeCont = re.sub("\\n[ \\t]*TARGET[ \\t]*:=.*", ("\nTARGET := $(BIN_DIR)/%s" %(szTarget)), szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*TARGET_DBG[ \\t]*:=.*", ("\nTARGET_DBG := $(BIN_DIR_DBG)/%s" %(szTarget)), szMakeCont)
    elif "shared" == szAppType:
        szMakeCont = re.sub("\\n[ \\t]*TARGET[ \\t]*:=.*", ("\nTARGET := $(BIN_DIR)/lib%s.so" %(szTarget)), szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*TARGET_DBG[ \\t]*:=.*", ("\nTARGET_DBG := $(BIN_DIR_DBG)/lib%s.so" %(szTarget)), szMakeCont)
    else:
        szMakeCont = re.sub("\\n[ \\t]*TARGET[ \\t]*:=.*", ("\nTARGET := $(BIN_DIR)/lib%s.a" %(szTarget)), szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*TARGET_DBG[ \\t]*:=.*", ("\nTARGET_DBG := $(BIN_DIR_DBG)/lib%s.a" %(szTarget)), szMakeCont)
    #写入makefile文件
    szErr = maker_public.writeTxtFile(szProjPath+"/makefile", szMakeCont)
    return szErr


#函数功能：制作索引文件
#函数参数：工程路径
#函数返回：错误描述
def makePropertiesfile(szProjPath):
    gccVersion = maker_public.execCmdAndGetOutput("gcc -dumpversion").replace('\n', '')
    szConfig = \
        "{\n"\
        "    \"configurations\": [\n"\
        "        {\n"\
        "            \"name\": \"Linux\",\n"\
        "            \"includePath\": [\n"\
        "                \"${workspaceFolder}/**\",\n"\
        "                \"/usr/include\",\n"\
        "                \"/usr/local/include\",\n"\
        "                \"/usr/lib/gcc/x86_64-redhat-linux/%s/include\",\n"\
        "                \"/usr/include/c++/%s/x86_64-redhat-linux\"\n"\
        "            ],\n"\
        "            \"defines\": [],\n"\
        "            \"compilerPath\": \"/usr/bin/gcc\",\n"\
        "            \"cStandard\": \"c11\",\n"\
        "            \"cppStandard\": \"c++11\",\n"\
        "            \"intelliSenseMode\": \"gcc-x64\"\n"\
        "        }\n"\
        "    ],\n"\
        "    \"version\": 4\n"\
        "}" %(gccVersion, gccVersion)
    return maker_public.writeTxtFile(szProjPath+"/.vscode/c_cpp_properties.json", szConfig)


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
        "            \"label\": \"gcc build active file\",\n"\
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
        "            \"label\": \"gcc clean active file\",\n"\
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
        "{\n"\
        "    // Use IntelliSense to learn about possible attributes.\n"\
        "    // Hover to view descriptions of existing attributes.\n"\
        "    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387\n"\
        "    \"version\": \"0.2.0\",\n"\
        "    \"configurations\": [\n"\
        "        {\n"\
        "            \"name\": \"gcc build and debug active file\",\n"\
        "            \"type\": \"cppdbg\",\n"\
        "            \"request\": \"launch\",\n"\
        "            \"program\": \"${workspaceFolder}/debug/"+os.path.basename(szProjPath)+"\",\n"\
        "            \"args\": [],\n"\
        "            \"stopAtEntry\": false,\n"\
        "            \"cwd\": \"${workspaceFolder}\",\n"\
        "            \"environment\": [],\n"\
        "            \"externalConsole\": false,\n"\
        "            \"MIMode\": \"gdb\",\n"\
        "            \"setupCommands\": [\n"\
        "                {\n"\
        "                    \"description\": \"Enable pretty-printing for gdb\",\n"\
        "                    \"text\": \"-enable-pretty-printing\",\n"\
        "                    \"ignoreFailures\": true\n"\
        "                }\n"\
        "            ],\n"\
        "            \"preLaunchTask\": \"gcc build active file\",\n"\
        "            \"miDebuggerPath\": \"/usr/bin/gdb\"\n"\
        "        }\n"\
        "    ]\n"\
        "}\n"
    return maker_public.writeTxtFile(szProjPath+"/.vscode/launch.json", szConfig)


#函数功能：创建C/C++类型的工程
#函数参数：开发语言，工程类型，工程路径
#函数返回：错误描述
def MakeProject(szLangType, szAppType, szProjPath):
    #建立include目录
    szErr = maker_public.makeDirs(szProjPath+"/include")
    if 0 < len(szErr):
        return szErr
    #建立src目录
    szErr = maker_public.makeDirs(szProjPath+"/src")
    if 0 < len(szErr):
        return szErr
    #建立.vscode目录
    szErr = maker_public.makeDirs(szProjPath+"/.vscode")
    if 0 < len(szErr):
        return szErr
    #建立makefile
    if "c" == szLangType:
        szErr = makeMakefile(szAppType, szProjPath, "gcc", ".c", "c11")
    else: 
        szErr = makeMakefile(szAppType, szProjPath, "g++", ".cpp", "c++11")
    if 0 < len(szErr):
        return szErr
    #建立配置索引配置目录
    szErr = makePropertiesfile(szProjPath)
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
        "//函数功能：主函数\n"\
        "//函数参数：可执行文件全路径，启动时加入的参数\n"\
        "//函数返回：执行成功返回0，否则返回负值的错误码\n"
    if "c" == szLangType:
        szData += \
            "int main(void){\n"\
            "    return 0;\n"\
            "}\n"
        szErr = maker_public.writeTxtFile(szProjPath+"/src/main.c", szData)
    else:
        szData += \
            "int main(){\n"\
            "    return 0;\n"\
            "}\n"
        szErr = maker_public.writeTxtFile(szProjPath+"/src/main.cpp", szData)
    if 0 < len(szErr):
        return szErr
    #
    return ""
    