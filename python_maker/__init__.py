#!/usr/python/bin
# -*- coding: utf-8 -*-

import maker_public


#函数功能：创建python类型的工程
#函数参数：开发语言，工程类型，工程路径
#函数返回：错误描述
def MakeProject(szLangType, szAppType, szProjPath):
    #建立.vscode目录
    szErr = maker_public.makeDirs(szProjPath+"/.vscode")
    if 0 < len(szErr):
        return szErr
    #建立主入口文件
    szData = \
        "{\n"\
        "    // Use IntelliSense to learn about possible attributes.\n"\
        "    // Hover to view descriptions of existing attributes.\n"\
        "    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387\n"\
        "    \"version\": \"0.2.0\",\n"\
        "    \"configurations\": [\n"\
        "        {\n"\
        "            \"name\": \"Python: Current File\",\n"\
        "            \"type\": \"python\",\n"\
        "            \"request\": \"launch\",\n"\
        "            \"program\": \"${workspaceFolder}/__init__.py\",\n"\
        "            \"args\": [\n"\
        "                \"\"\n"\
        "            ],\n"\
        "            \"cwd\": \"${workspaceFolder}\",\n"\
        "            \"console\": \"integratedTerminal\"\n"\
        "        }\n"\
        "    ]\n"\
        "}\n"
    szErr = maker_public.writeTxtFile(szProjPath+"/.vscode/launch.json", szData)
    if 0 < len(szErr):
        return szErr
    #建立主文件
    szData = \
        "#!/usr/python/bin\n"\
        "# -*- coding: utf-8 -*-\n\n\n"\
        "#函数功能：主函数\n"\
        "#函数参数：可执行文件全路径，启动时加入的参数\n"\
        "#函数返回：执行成功返回0，否则返回负值的错误码\n"\
        "if __name__ == \"__main__\":\n"
    szErr = maker_public.writeTxtFile(szProjPath+"/__init__.py", szData)
    if 0 < len(szErr):
        return szErr
    #
    return ""
    