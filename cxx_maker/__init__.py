#!/usr/python/bin
# -*- coding: utf-8 -*-


import os
import sys
import re
import maker_public


#makeMakefile 制作c语言的makefile文件；参数：工程类型，工程路径，编译器，源文件后缀，语言标准；
# 返回：错误描述
def makeMakefile(szAppType, szProjPath, szComplier, szSuffix, szStd):
    #检测
    if "app"!=szAppType and "shared"!=szAppType and "static"!=szAppType and \
        "app-dpdk"!=szAppType and "shared-dpdk"!=szAppType and "static-dpdk"!=szAppType:
        return ("Invalid output(%s)" %(szAppType))
    #读取基础的makefile文件
    szMakeCont,szErr = maker_public.readTxtFile( 
        os.path.dirname(os.path.realpath(sys.argv[0]))+"/cxx_maker/makefile.conf" )
    if 0 < len(szErr):
        return szErr
    #替换编译器
    szMakeCont = re.sub("\\n[ \\t]*CXX[ \\t]*:=.*", 
        ("\nCXX := %s" %(szComplier)), szMakeCont)
    #替换后缀
    szMakeCont = re.sub("\\n[ \\t]*SUFFIX[ \\t]*:=.*", 
        ("\nSUFFIX := %s" %(szSuffix)), szMakeCont)
    #替换编译选项
    if -1!=str(szAppType).find("app"):
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS[ \\t]*:=.*", \
            ("\nCXXFLAGS := -std=%s -Wall -m64 -O2 -fmessage-length=0" %(szStd)), szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS_DBG[ \\t]*:=.*", \
            ("\nCXXFLAGS_DBG := -std=%s -Wall -m64 -O0 -g3 -fmessage-length=0" 
            %(szStd)), szMakeCont)
    elif -1!=str(szAppType).find("shared"):
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS[ \\t]*:=.*", \
            ("\nCXXFLAGS := -std=%s -Wall -m64 -O2 -fPIC -fmessage-length=0 "\
            "-fvisibility=hidden" %(szStd)), szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS_DBG[ \\t]*:=.*", \
            ("\nCXXFLAGS_DBG := -std=%s -Wall -m64 -O0 -g3 -fPIC "\
            "-fmessage-length=0 -fvisibility=hidden" %(szStd)), szMakeCont)
    else:
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS[ \\t]*:=.*", \
            ("\nCXXFLAGS := -std=%s -Wall -m64 -O2 -fPIC -fmessage-length=0" 
            %(szStd)), szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS_DBG[ \\t]*:=.*", \
            ("\nCXXFLAGS_DBG := -std=%s -Wall -m64 -O0 -g3 -fPIC -fmessage-length=0" 
            %(szStd)), szMakeCont)
    if -1!=str(szAppType).find("-dpdk"):
        rep_str = "$(shell $(PKGCONF) --cflags libdpdk)"
        #if "test_libhs\n"==maker_public.execCmdAndGetOutput(
        #    "pkg-config --exists libhs && echo test_libhs"):
        #    rep_str += " $(shell $(PKGCONF) --cflags libhs)"
        szMakeCont = "ifeq ($(shell pkg-config --exists libdpdk && echo 0),)\n"+\
            "$(error \"Please define RTE_SDK environment variable\")\nendif\n\n"+\
            szMakeCont
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS[ \\t]*:=[ \\t]*", \
            "\nCXXFLAGS := "+rep_str+" ", szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS_DBG[ \\t]*:=[ \\t]*", \
            ("\nCXXFLAGS_DBG := "+rep_str+" "), szMakeCont)
    #替换链接器
    if -1!=str(szAppType).find("app") or -1!=str(szAppType).find("shared"):
        szMakeCont = re.sub("\\n[ \\t]*LD[ \\t]*:=.*", "\nLD := "+szComplier, 
            szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*LDOUTFLG[ \\t]*:=.*", 
            "\nLDOUTFLG := -o", szMakeCont)
    else:
        szMakeCont = re.sub("\\n[ \\t]*LD[ \\t]*:=.*", "\nLD := ar", szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*LDOUTFLG[ \\t]*:=.*", 
            "\nLDOUTFLG := ", szMakeCont)
    #替换链接选项
    if -1!=str(szAppType).find("app"):
        szMakeCont = re.sub("\\n[ \\t]*LDFLAGS[ \\t]*:=.*", 
            "\nLDFLAGS := -Wl,-rpath,./", szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*LDFLAGS_DBG[ \\t]*:=.*", 
            "\nLDFLAGS_DBG := -Wl,-rpath,./", szMakeCont)
    elif -1!=str(szAppType).find("shared"):
        szMakeCont = re.sub("\\n[ \\t]*LDFLAGS[ \\t]*:=.*", 
            "\nLDFLAGS := -Wl,-rpath,./ -shared", szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*LDFLAGS_DBG[ \\t]*:=.*", 
            "\nLDFLAGS_DBG := -Wl,-rpath,./ -shared", szMakeCont)
    else:
        szMakeCont = re.sub("\\n[ \\t]*LDFLAGS[ \\t]*:=.*", 
            "\nLDFLAGS := -crv", szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*LDFLAGS_DBG[ \\t]*:=.*", 
            "\nLDFLAGS_DBG := -crv", szMakeCont)
    if "app-dpdk"==szAppType or "shared-dpdk"==szAppType:
        rep_str = "$(shell $(PKGCONF) --static --libs libdpdk)"
        #if "test_libhs\n"==maker_public.execCmdAndGetOutput(
        #    "pkg-config --exists libhs && echo test_libhs"):
        #    rep_str += " $(shell $(PKGCONF) --static --libs libhs)"
        szMakeCont = re.sub("\\n[ \\t]*LDFLAGS[ \\t]*:=[ \\t]*", 
            "\nLDFLAGS := "+rep_str+" ", szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*LDFLAGS_DBG[ \\t]*:=[ \\t]*", 
            "\nLDFLAGS_DBG := "+rep_str+" ", szMakeCont)
    #替换最终目标
    szTarget = os.path.basename(szProjPath)
    if -1!=str(szAppType).find("app"):
        szMakeCont = re.sub("\\n[ \\t]*TARGET[ \\t]*:=.*", 
            ("\nTARGET := $(BIN_DIR)/%s" %(szTarget)), szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*TARGET_DBG[ \\t]*:=.*", 
            ("\nTARGET_DBG := $(BIN_DIR_DBG)/%s" %(szTarget)), szMakeCont)
    elif -1!=str(szAppType).find("shared"):
        szMakeCont = re.sub("\\n[ \\t]*TARGET[ \\t]*:=.*", 
            ("\nTARGET := $(BIN_DIR)/lib%s.so" %(szTarget)), szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*TARGET_DBG[ \\t]*:=.*", 
            ("\nTARGET_DBG := $(BIN_DIR_DBG)/lib%s.so" %(szTarget)), szMakeCont)
    else:
        szMakeCont = re.sub("\\n[ \\t]*TARGET[ \\t]*:=.*", 
            ("\nTARGET := $(BIN_DIR)/lib%s.a" %(szTarget)), szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*TARGET_DBG[ \\t]*:=.*", 
            ("\nTARGET_DBG := $(BIN_DIR_DBG)/lib%s.a" %(szTarget)), szMakeCont)
    #写入makefile文件
    szErr = maker_public.writeTxtFile(szProjPath+"/makefile", szMakeCont)
    return szErr


#makePropertiesfile 制作索引文件；参数：项目类型、工程路径和开发语言；返回：错误描述
def makePropertiesfile(szAppType, szProjPath, szLangType):
    #获取GCC
    GccVersion = maker_public.execCmdAndGetOutput("gcc -dumpversion").replace('\n', '')
    CppVersion = maker_public.execCmdAndGetOutput("g++ -dumpversion").replace('\n', '')
    #获取GCC的include路径
    GccIncPath = ""
    other_inc_path = "\n"
    if "centos" == maker_public.getOSName():
        GccIncPath = "x86_64-redhat-linux/"+GccVersion+"/include"
        if "c++" == szLangType:
            other_inc_path = ",\n                \"/usr/include/c++/"+\
                CppVersion+"/x86_64-redhat-linux\"\n"
    else:
        GccIncPath = "x86_64-linux-gnu/"+GccVersion+"/include"
        if "c++" == szLangType:
            other_inc_path = ",\n                \"/usr/include/c++/"+CppVersion+"\"\n"
    if -1!=str(szAppType).find("-dpdk"):
        other_inc_path = other_inc_path[:len(other_inc_path)-1]
        #if "test_libhs\n"!=maker_public.execCmdAndGetOutput(
        #    "pkg-config --exists libhs && echo test_libhs"):
        other_inc_path += ",\n                \"/usr/local/dpdk/include\"\n"
        #else:
        #    other_inc_path += ",\n                \"/usr/local/dpdk/include\""\
        #       ",\n                \"/usr/local/hyperscan/include/hs\"\n"
    szConfig = \
        "{\n"\
        "    \"configurations\": [\n"\
        "        {\n"\
        "            \"name\": \"Linux\",\n"\
        "            \"includePath\": [\n"\
        "                \"${workspaceFolder}/**\",\n"\
        "                \"/usr/include\",\n"\
        "                \"/usr/local/include\",\n"\
        "                \"/usr/lib/gcc/"+GccIncPath+"\""+other_inc_path+\
        "            ],\n"\
        "            \"defines\": [],\n"\
        "            \"compilerPath\": \"/usr/bin/gcc\",\n"\
        "            \"cStandard\": \"c11\",\n"\
        "            \"cppStandard\": \"c++11\",\n"\
        "            \"intelliSenseMode\": \"gcc-x64\"\n"\
        "        }\n"\
        "    ],\n"\
        "    \"version\": 4\n"\
        "}"
    return maker_public.writeTxtFile(szProjPath+"/.vscode/c_cpp_properties.json", szConfig)


#makeBuildfile 制作编译文件；参数：工程路径和编译器；返回：错误描述
def makeBuildfile(szProjPath, szComplier):
    szConfig = \
        "{\n"\
        "    // See https://go.microsoft.com/fwlink/?LinkId=733558\n"\
        "    // for the documentation about the tasks.json format\n"\
        "    \"version\": \"2.0.0\",\n"\
        "    \"tasks\": [\n"\
        "        {\n"\
        "            \"type\": \"shell\",\n"\
        "            \"label\": \""+szComplier+" build active file\",\n"\
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
        "            \"label\": \""+szComplier+" clean active file\",\n"\
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


#makeDebugfile 制作编译文件；参数：工程路径和编译器；返回：错误描述
def makeDebugfile(szProjPath, szComplier):
    szConfig = \
        "{\n"\
        "    // Use IntelliSense to learn about possible attributes.\n"\
        "    // Hover to view descriptions of existing attributes.\n"\
        "    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387\n"\
        "    \"version\": \"0.2.0\",\n"\
        "    \"configurations\": [\n"\
        "        {\n"\
        "            \"name\": \""+szComplier+" build and debug active file\",\n"\
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
        "            \"preLaunchTask\": \""+szComplier+" build active file\",\n"\
        "            \"miDebuggerPath\": \"/usr/bin/gdb\"\n"\
        "        }\n"\
        "    ]\n"\
        "}\n"
    return maker_public.writeTxtFile(szProjPath+"/.vscode/launch.json", szConfig)


#MakeProject 创建C/C++类型的工程；参数：开发语言，工程类型，工程路径；返回：错误描述
def MakeProject(szLangType, szAppType, szProjPath):
    #获取开发语言
    if "c" == szLangType:
        szComplier = "gcc"
    else:
        szComplier = "g++"
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
        szErr = makeMakefile(szAppType, szProjPath, szComplier, ".c", "gnu11")
    else: 
        szErr = makeMakefile(szAppType, szProjPath, szComplier, ".cpp", "gnu++11")
    if 0 < len(szErr):
        return szErr
    #建立配置索引配置目录
    szErr = makePropertiesfile(szAppType, szProjPath, szLangType)
    if 0 < len(szErr):
        return szErr
    #建立编译任务
    szErr = makeBuildfile(szProjPath, szComplier)
    if 0 < len(szErr):
        return szErr
    #建立调试任务
    szErr = makeDebugfile(szProjPath, szComplier)
    if 0 < len(szErr):
        return szErr
    #建立主文件
    szData = \
        "//函数功能：主函数\n"\
        "//函数参数：可执行文件全路径，启动时加入的参数\n"\
        "//函数返回：执行成功返回0，否则返回负值的错误码\n"
    if "c" == szLangType:
        if False==os.path.exists(szProjPath+"/src/main.c"):
            szData += \
                "int main(void){\n"\
                "    return 0;\n"\
                "}\n"
            szErr = maker_public.writeTxtFile(szProjPath+"/src/main.c", szData)
    else:
        if False==os.path.exists(szProjPath+"/src/main.cpp"):
            szData += \
                "int main(){\n"\
                "    return 0;\n"\
                "}\n"
            szErr = maker_public.writeTxtFile(szProjPath+"/src/main.cpp", szData)
    if 0 < len(szErr):
        return szErr
    #
    return ""
    