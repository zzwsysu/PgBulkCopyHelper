#! /usr/bin/python3
# coding: utf-8

"""
该文件用来对 SysuNM 中所有项目进行nuget打包，并推送到nuget仓库
"""

import os, subprocess, shutil

projects = ['PgBulkCopyHelper']
            
local_path = r'D:\Projects\ZZW_NugetFeed'
remote_path = r'http://172.18.190.172:8081/api/v2/package'
temp_path = 'temp_path'

push_to_local = True
push_to_remote = True
delete_temp_path = True

apikey = 'its408nugetserver'
pack_mode = 'Release'

            
projs_path = dict()
projs_nuspec = dict()
            
def get_projs_path():
    for proj in projects:
        proj_name = proj + '.csproj'
        proj_path = os.path.join(proj, proj_name)
        projs_path[proj] = proj_path
    
def get_projs_nuspec():
    for proj in projects:
        nuspec_name = proj + '.nuspec'
        nuspec_path = os.path.join(proj, nuspec_name)
        projs_nuspec[proj] = nuspec_path
    
def pack_to_temp(proj_name):
    print('packing project %s...\n' % proj_name)
    if proj_name not in projects:
        print('%s not found.' % proj_name)
        return
    if not os.path.isfile(projs_nuspec[proj_name]):
        print('the .nuspec file of the project "%s" not found.' % proj_name)
        return
    proj_path = projs_path[proj_name]
    if not os.path.isdir(temp_path):
        os.mkdir(temp_path)
    args = ['nuget', 'pack', proj_path, '-properties', 'Configuration=%s' % pack_mode, 
            '-outputdirectory', temp_path]
    subprocess.call(args)
    print('\npacked %s successfully!\n' % proj_name)
    print('*****************************************************************\n')
    
def pack_all():
    for proj in projects:
        pack_to_temp(proj)
    
    print('\n')
    print('\n')
    if push_to_local:
        print('start to push the packages to the local path.\n')
        if not os.path.isdir(local_path):
            print('making the directory: %s...\n' % local_path)
            os.mkdir(local_path)
        for nuspecfile in os.listdir(temp_path):
            nuspecfile_path = os.path.join(temp_path, nuspecfile)
            print('copy file: %s --> %s' % (nuspecfile_path, local_path))
            shutil.copy2(nuspecfile_path, local_path)
            print('    done!\n')
    
    print('\n')
    print('\n')
    if push_to_remote:
        print('start to push the packages to the remote server.\n')
        args = ['nuget', 'push', os.path.join(temp_path, '*.nupkg'), 
                apikey, '-Source', remote_path]
        subprocess.call(args)
        print('push all the packages to the remote server successfully!\n')
        
    if delete_temp_path:
        shutil.rmtree(temp_path)
    
if __name__ == '__main__':
    get_projs_path()
    get_projs_nuspec()
    # pack('SysuNM.Core.Data')
    pack_all()
    input()