#!/usr/python/bin
# -*- coding: utf-8 -*-


import sys
import os
import cxx_maker
import golang_maker
import python_maker
import java_maker


#函数功能：给工程中每个目录增加一个.gitignore防止git无法添加该目录
#函数参数：工程路径
#函数返回：错误描述
def addGitignore(szProjPath):
    PathList = os.listdir(szProjPath)
    for CurPath in PathList:
        if False == os.path.isdir(szProjPath+"/"+CurPath):
            HaveFile = True
            continue
        if "."==CurPath or ".."==CurPath:
            continue
        szErr = addGitignore(szProjPath+"/"+CurPath)
        if 0 < len(szErr):
            return szErr
    if 0 != os.system("touch "+szProjPath+"/.gitignore"):
        return "Can not add .gitignore for "+szProjPath
    return ""


#功能：给工程配置口令自动保存功能；参数：工程路径；返回：错误描述
def configGit(szProjPath):
    #配置口令自动保存
    #os.system("cd "+szProjPath+" && "+"git config  credential.helper store")
    return addGitignore(szProjPath)

#函数功能：主函数
#函数参数：可执行文件全路径，启动时加入的参数
#函数返回：执行成功返回0，否则返回负值的错误码
if __name__ == "__main__":
    #检测参数
    if 4 != len(sys.argv):
        print("vs_progject_maker: Language[c|c++|golang|python|java] "\
            "Output[app|static|shared|app-dpdk|static-dpdk|shared-dpdk] Workspace")
        exit(-1)
    #提取开发语言，工程类型，建立工程路径
    szLangType = str(sys.argv[1]).lower()
    szAppType = str(sys.argv[2]).lower()
    szProjPath = str(sys.argv[3])
    #去掉尾巴上的"/"
    if 0<len(szProjPath) and "/" == szProjPath[len(szProjPath)-1]:
        szProjPath = szProjPath[0:len(szProjPath)-1]
    if 0>=len(szProjPath) or "."==szProjPath[0]:
        print("vs_progject_maker: Invalid workspace(%s)" %(szProjPath))
        exit(-1)
    if True==os.path.exists(szProjPath) and False==os.path.isdir( os.path.realpath(szProjPath) ):
        print("vs_progject_maker: Invalid workspace(%s)" %(szProjPath))
        exit(-1)
    if False == os.path.exists(szProjPath):
        os.makedirs(szProjPath)
    #执行具体的工程创建函数
    szErrRet = ""
    if "c" == szLangType:
        szErrRet = cxx_maker.MakeProject(szLangType, szAppType, szProjPath)
    elif "c++" == szLangType:
        szErrRet = cxx_maker.MakeProject(szLangType, szAppType, szProjPath)
    elif "golang" == szLangType:
        szErrRet = golang_maker.MakeProject(szLangType, szAppType, szProjPath)
    elif "python" == szLangType:
        szErrRet = python_maker.MakeProject(szLangType, szAppType, szProjPath)
    elif "java" == szLangType:
        szErrRet = java_maker.MakeProject(szLangType, szAppType, szProjPath)
    else:
        print("vs_progject_maker: Invalid language(%s)" %(szLangType))
        exit(-1)
    #检测错误值
    if 0 < len(szErrRet):
        print("vs_progject_maker: %s" %(szErrRet))
        exit(-1)
    #配置该git工程
    szErrRet = configGit(szProjPath)
    if 0 < len(szErrRet):
        print("vs_progject_maker: %s" %(szErrRet))
        exit(-1)
    #打印生成成功信息
    print("Create %s_%s_workespace(%s) sucess\n" %(szLangType, szAppType, szProjPath))
