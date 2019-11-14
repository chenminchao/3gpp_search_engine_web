# -*- coding: utf-8 -*-

import os
import glob
import shutil
import zipfile
import Global_Basedir
import Path_Name_Format

def get_spec_list():
    baseDir = Global_Basedir.SPEC_BASE_DIR
    speclist_path = Path_Name_Format.SPEC_LIST_PATH.format(basedir=baseDir)
    spec_list = []
    if not os.path.exists(speclist_path):
        print(speclist_path + " does not exist")
        return spec_list
    with open(speclist_path, 'r', encoding='UTF-8') as f:
        content = f.readlines()
    for line in content:
        series = line[0:2]
        num = line[2:5]
        spec = series + "_" + num
        if num != "":
            spec_list.append(spec)
    print("spec list:")
    print(spec_list)
    return spec_list

def get_new_ver(series, num):
    basedir = Global_Basedir.SPEC_BASE_DIR
    ver_files = os.listdir(basedir + '/spec')
    ver_files.sort(key=lambda i: int(i, base=32))
    for i in range(len(ver_files) - 1, -1, -1):
        ver = ver_files[i]
        zip_path = Path_Name_Format.ZIP_PATH.format(basedir=basedir, series=series, num=num, ver=ver)
        if os.path.exists(zip_path):
            return ver
    return "none"

def get_ver_list(series, num):
    basedir = Global_Basedir.SPEC_BASE_DIR
    ver_files = os.listdir(basedir + '/spec')
    ret = []
    for ver in ver_files:
        zip_path = Path_Name_Format.ZIP_PATH.format(basedir=basedir, series=series, num=num, ver=ver)
        if os.path.exists(zip_path):
            ret.append(ver)
    return ret

def unzip(f, d):
    with zipfile.ZipFile(f, 'r') as ref:
        ref.extractall(d)

def copy_image(src, dst):
    save_dir = os.getcwd()
    print(save_dir)
    print(src)
    os.chdir(src)
    png_list = glob.glob("*.png")
    for png in png_list:
        print(os.path.join(src, png))
        shutil.copy(os.path.join(src, png), dst)
    os.chdir(save_dir)

def copy_spec(src, dst):
    save_dir = os.getcwd()
    print(save_dir)
    print(src)
    os.chdir(src)
    png_list = glob.glob("*.png")
    for png in png_list:
        print(os.path.join(src, png))
        shutil.copy(os.path.join(src, png), dst)
    os.chdir(save_dir)