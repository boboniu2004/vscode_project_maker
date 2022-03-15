#!/usr/python/bin
# -*- coding: utf-8 -*-


import os
import sys
import re
import maker_public


#make_nomal_makefile 制作c语言的makefile文件；
# 参数：工程类型，工程路径，编译器，源文件后缀，语言标准；
# 返回：错误描述
def make_nomal_makefile(szAppType, szProjPath, szComplier, szSuffix, szStd):
    #读取基础的makefile文件
    szMakeCont,szErr = maker_public.readTxtFile( 
        os.path.dirname(os.path.abspath(sys.argv[0]))+"/cxx_maker/makefile.conf" )
    if 0 < len(szErr):
        return szErr
    #替换编译器
    szMakeCont = re.sub("\\n[ \\t]*CC[ \\t]*:=.*", 
        ("\nCC := %s" %(szComplier)), szMakeCont)
    #替换后缀
    szMakeCont = re.sub("\\n[ \\t]*SUFFIX[ \\t]*:=.*", 
        ("\nSUFFIX := %s" %(szSuffix)), szMakeCont)
    #替换编译选项
    if -1!=str(szAppType).find("app"):
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS[ \\t]*:=.*", \
            ("\nCXXFLAGS := -std=%s $(WERROR_FLAGS) -O3 -fmessage-length=0" %(szStd)), szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS_DBG[ \\t]*:=.*", \
            ("\nCXXFLAGS_DBG := -std=%s $(WERROR_FLAGS) -O0 -g3 -fmessage-length=0" 
            %(szStd)), szMakeCont)
    elif -1!=str(szAppType).find("shared"):
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS[ \\t]*:=.*", \
            ("\nCXXFLAGS := -std=%s $(WERROR_FLAGS) -O3 -fPIC -fmessage-length=0 "\
            "-fvisibility=hidden" %(szStd)), szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS_DBG[ \\t]*:=.*", \
            ("\nCXXFLAGS_DBG := -std=%s $(WERROR_FLAGS) -O0 -g3 -fPIC "\
            "-fmessage-length=0 -fvisibility=hidden" %(szStd)), szMakeCont)
    else:
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS[ \\t]*:=.*", \
            ("\nCXXFLAGS := -std=%s $(WERROR_FLAGS) -O3 -fPIC -fmessage-length=0" 
            %(szStd)), szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS_DBG[ \\t]*:=.*", \
            ("\nCXXFLAGS_DBG := -std=%s $(WERROR_FLAGS) -O0 -g3 -fPIC -fmessage-length=0" 
            %(szStd)), szMakeCont)
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
        szMakeCont = re.sub("\\n[ \\t]*LDXXFLAGS[ \\t]*:=.*", 
            "\nLDXXFLAGS := -Wl,-rpath,./", szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*LDXXFLAGS_DBG[ \\t]*:=.*", 
            "\nLDXXFLAGS_DBG := -Wl,-rpath,./", szMakeCont)
    elif -1!=str(szAppType).find("shared"):
        szMakeCont = re.sub("\\n[ \\t]*LDXXFLAGS[ \\t]*:=.*", 
            "\nLDXXFLAGS := -Wl,-rpath,./ -shared", szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*LDXXFLAGS_DBG[ \\t]*:=.*", 
            "\nLDXXFLAGS_DBG := -Wl,-rpath,./ -shared", szMakeCont)
    else:
        szMakeCont = re.sub("\\n[ \\t]*LDXXFLAGS[ \\t]*:=.*", 
            "\nLDXXFLAGS := -crv", szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*LDXXFLAGS_DBG[ \\t]*:=.*", 
            "\nLDXXFLAGS_DBG := -crv", szMakeCont)
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


#make_nomal_makefile 制作c语言的makefile文件；
# 参数：工程类型，工程路径，编译器，源文件后缀，语言标准；
# 返回：错误描述
def make_dpdk_makefile(szAppType, szProjPath, szComplier, szSuffix, szStd):
    #读取基础的makefile文件
    szMakeCont,szErr = maker_public.readTxtFile( 
        os.path.dirname(os.path.abspath(sys.argv[0]))+"/cxx_maker/makefile-dpdk.conf" )
    if 0 < len(szErr):
        return szErr
    #替换编译器
    szMakeCont = re.sub("\\n[ \\t]*CC[ \\t]*:=.*", 
        ("\nCC := %s" %(szComplier)), szMakeCont)
    #替换后缀
    szMakeCont = re.sub("\\n[ \\t]*SUFFIX[ \\t]*:=.*", 
        ("\nSUFFIX := %s" %(szSuffix)), szMakeCont)
    #替换编译选项
    if -1!=str(szAppType).find("app"):
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS[ \\t]*:=.*", \
            ("\nCXXFLAGS := -std=%s -O3 -fmessage-length=0 "\
            "$(shell $(PKGCONF) --cflags libdpdk)" %(szStd)), szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS_DBG[ \\t]*:=.*", \
            ("\nCXXFLAGS_DBG := -std=%s -O0 -g3 -fmessage-length=0 "\
            "$(shell $(PKGCONF) --cflags libdpdk)" %(szStd)), szMakeCont)
    elif -1!=str(szAppType).find("shared"):
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS[ \\t]*:=.*", \
            ("\nCXXFLAGS := -std=%s -O3 -fPIC -fmessage-length=0 -fvisibility=hidden "\
            "$(shell $(PKGCONF) --cflags libdpdk)" %(szStd)), szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS_DBG[ \\t]*:=.*", \
            ("\nCXXFLAGS_DBG := -std=%s -O0 -g3 -fPIC -fmessage-length=0 "\
            "-fvisibility=hidden $(shell $(PKGCONF) --cflags libdpdk)" 
            %(szStd)), szMakeCont)
    else:
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS[ \\t]*:=.*", \
            ("\nCXXFLAGS := -std=%s -O3 -fPIC -fmessage-length=0 "\
            "$(shell $(PKGCONF) --cflags libdpdk)" %(szStd)), szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*CXXFLAGS_DBG[ \\t]*:=.*", \
            ("\nCXXFLAGS_DBG := -std=%s -O0 -g3 -fPIC -fmessage-length=0 "\
            "$(shell $(PKGCONF) --cflags libdpdk)" %(szStd)), szMakeCont)
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
        szMakeCont = re.sub("\\n[ \\t]*LDXXFLAGS[ \\t]*:=.*", 
            "\nLDXXFLAGS := -Wl,-rpath,./", szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*LDXXFLAGS_DBG[ \\t]*:=.*", 
            "\nLDXXFLAGS_DBG := -Wl,-rpath,./", szMakeCont)
    elif -1!=str(szAppType).find("shared"):
        szMakeCont = re.sub("\\n[ \\t]*LDXXFLAGS[ \\t]*:=.*", 
            "\nLDXXFLAGS := -Wl,-rpath,./ -shared", szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*LDXXFLAGS_DBG[ \\t]*:=.*", 
            "\nLDXXFLAGS_DBG := -Wl,-rpath,./ -shared", szMakeCont)
    else:
        szMakeCont = re.sub("\\n[ \\t]*LDXXFLAGS[ \\t]*:=.*", 
            "\nLDXXFLAGS := -crv", szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*LDXXFLAGS_DBG[ \\t]*:=.*", 
            "\nLDXXFLAGS_DBG := -crv", szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*STATIC_LIBS[ \\t]*:=.*", 
            "\nSTATIC_LIBS := ", szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*STATIC_LIBS_DBG[ \\t]*:=.*", 
            "\nSTATIC_LIBS_DBG := ", szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*SHARE_LIBS[ \\t]*:=.*", 
            "\nSHARE_LIBS := ", szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*SHARE_LIBS_DBG[ \\t]*:=.*", 
            "\nSHARE_LIBS_DBG := ", szMakeCont)
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
    #替换没有pkg-config下的编译项目
    #替换APP
    if -1!=str(szAppType).find("app"):
        szMakeCont = re.sub("\\n[ \\t]*APP[ \\t]*=.*", 
            ("\nAPP = %s" %(szTarget)), szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*TARGET_NAME[ \\t]*:=.*", 
            "\nTARGET_NAME = $(APP)", szMakeCont)
    elif -1!=str(szAppType).find("shared"):
        szMakeCont = re.sub("\\n[ \\t]*SHARED[ \\t]*=.*", 
            ("\nSHARED = lib%s.so" %(szTarget)), szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*TARGET_NAME[ \\t]*:=.*", 
            "\nTARGET_NAME = $(SHARED)", szMakeCont)
    else:
        szMakeCont = re.sub("\\n[ \\t]*LIB[ \\t]*=.*", 
            ("\nLIB = lib%s.a" %(szTarget)), szMakeCont)
        szMakeCont = re.sub("\\n[ \\t]*TARGET_NAME[ \\t]*:=.*", 
            "\nTARGET_NAME = $(LIB)", szMakeCont)
    #替换CFLAGS
    szMakeCont = re.sub("\\n[ \\t]*CFLAGS[ \\t]*\\+=[ \\t]*-O0.*", 
        ("\nCFLAGS += -std=%s -O0 -g3 -fmessage-length=0 $(WERROR_FLAGS) $(MACROS_DBG) " %(szStd)), szMakeCont)
    szMakeCont = re.sub("\\n[ \\t]*CFLAGS[ \\t]*\\+=[ \\t]*-O3.*", 
        ("\nCFLAGS += -std=%s -O3 -fmessage-length=0 $(WERROR_FLAGS) $(MACROS) " %(szStd)), szMakeCont)
    #替换rte.extapp.mk
    if -1 != str(szAppType).find("shared"):
        szMakeCont = re.sub("rte\\.extapp\\.mk", "rte.extshared.mk", szMakeCont)
    elif -1 != str(szAppType).find("static"):
        szMakeCont = re.sub("rte\\.extapp\\.mk", "rte.extlib.mk", szMakeCont)
    #写入makefile文件
    szErr = maker_public.writeTxtFile(szProjPath+"/makefile", szMakeCont)
    return szErr


#makeMakefile 制作c语言的makefile文件；参数：工程类型，工程路径，编译器，源文件后缀，语言标准；
# 返回：错误描述
def makeMakefile(szAppType, szProjPath, szComplier, szSuffix, szStd):
    #检测
    if "app"!=szAppType and "shared"!=szAppType and "static"!=szAppType and \
        "app-dpdk"!=szAppType and "shared-dpdk"!=szAppType and "static-dpdk"!=szAppType:
        return ("Invalid output(%s)" %(szAppType))
    sz_err = ""
    if -1 == str(szAppType).find("-dpdk"):
        sz_err = make_nomal_makefile(szAppType, szProjPath, szComplier, szSuffix, szStd)
    else:
        sz_err = make_dpdk_makefile(szAppType, szProjPath, szComplier, szSuffix, szStd)
    return sz_err


#makePropertiesfile 制作索引文件；参数：项目类型、工程路径和开发语言；返回：错误描述
def makePropertiesfile(szAppType, szProjPath, szComplier):
    other_inc_path = "\n"
    if -1!=str(szAppType).find("-dpdk"):
        other_inc_path = ",\n                \"/usr/local/dpdk/include\"\n"
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
        "                \"/usr/local/include\""\
        +other_inc_path+\
        "            ],\n"\
        "            \"defines\": [],\n"\
        "            \"compilerPath\": \"/usr/bin/"+szComplier+"\",\n"\
        "            \"cStandard\": \"c11\",\n"\
        "            \"cppStandard\": \"c++11\",\n"\
        "            \"intelliSenseMode\": \"${default}\"\n"\
        "        }\n"\
        "    ],\n"\
        "    \"version\": "+maker_public.getVer("prop")+"\n"\
        "}"
    return maker_public.writeTxtFile(szProjPath+"/.vscode/c_cpp_properties.json", szConfig)


#makeBuildfile 制作编译文件；参数：应用类型、工程路径和编译器；返回：错误描述
def makeBuildfile(szAppType, szProjPath, szComplier):
    build_cmd = "                \"debug\"\n"
    clean_cmd = "                \"clean\"\n"
    if -1 != str(szAppType).find("-dpdk"):
        build_cmd = "                \"O=debug\"\n"
        clean_cmd = "                \"O=clean\"\n"
    szConfig = \
        "{\n"\
        "    // See https://go.microsoft.com/fwlink/?LinkId=733558\n"\
        "    // for the documentation about the tasks.json format\n"\
        "    \"version\": \""+maker_public.getVer("task")+"\",\n"\
        "    \"tasks\": [\n"\
        "        {\n"\
        "            \"type\": \"shell\",\n"\
        "            \"label\": \""+szComplier+" build active file\",\n"\
        "            \"command\": \"/usr/bin/make\",\n"\
        "            \"args\": [\n"\
        "                \"-f\",\n"\
        "                \"${workspaceFolder}/makefile\",\n"+\
        build_cmd+\
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
        "                \"${workspaceFolder}/makefile\",\n"+\
        clean_cmd+\
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
        "    \"version\": \""+maker_public.getVer("launch")+"\",\n"\
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
    szErr = makePropertiesfile(szAppType, szProjPath, szComplier)
    if 0 < len(szErr):
        return szErr
    #建立编译任务
    szErr = makeBuildfile(szAppType, szProjPath, szComplier)
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
    