import os
import sys
import json
import shutil
from elasticsearch import Elasticsearch
import Global_Basedir
import Path_Name_Format
from util import get_spec_list,get_new_ver,get_ver_list,unzip,copy_image
import platform
if not platform.system() == 'Linux':
    from doc2html_converter import elasticsearch_convert_doc2html
from jsonGeneration import txt2json
from parse_html import parse_file

def move_zip():
    baseDir = Global_Basedir.SPEC_BASE_DIR
    zip_Path = Path_Name_Format.SPEC_ZIP_PATH.format(basedir=baseDir)
    if not os.path.exists(zip_Path):
        print(baseDir + " path not exist!!!")
    else:
        inputFileNames = os.listdir(zip_Path)
        for i, fileName in enumerate(inputFileNames):
            if fileName.endswith('zip'):
                series = fileName[0:2]
                num = fileName[2:5]
                ver = fileName[6:9]
                in_file = zip_Path + "\\" + fileName
                out_Path = Path_Name_Format.ZIP_PATH.format(basedir=baseDir, series=series, num=num, ver=ver)
                if not os.path.exists(out_Path):
                    saveTo = os.path.dirname(out_Path)
                    if not os.path.exists(saveTo) :
                        os.makedirs(saveTo)
                    shutil.copy(in_file, out_Path)
                    print("copy " + in_file + " to " + out_Path)
                else:
                    print(out_Path + " file already exist!!!")

def convert_doc_to_html():
    spec_list = get_spec_list()
    for spec in spec_list:
        spec_info = spec.split("_")
        series = spec_info[0]
        num = spec_info[1]
        ver = get_new_ver(series, num)
        if ver == "none":
            print("no zip for spec: " + series + num)
        else:
            zip_file = Path_Name_Format.ZIP_PATH.format(basedir=baseDir, series=series, num=num, ver=ver)
            docPath = Path_Name_Format.DOC_PATH.format(basedir=baseDir, series=series, num=num, ver=ver)
            try:
                unzip(zip_file, docPath)
                docName = Path_Name_Format.DOC_NAME.format(basedir=baseDir, series=series, num=num, ver=ver)
                docxName = Path_Name_Format.DOCX_NAME.format(basedir=baseDir, series=series, num=num, ver=ver)
                output_html_dir = Path_Name_Format.HTML_PATH.format(basedir=baseDir, series=series, num=num, ver=ver)
                if os.path.exists(output_html_dir):
                    print(output_html_dir + '/' + series + num + '-' + ver + ".html has existed ")
                else:
                    if os.path.exists(docName):
                        doc_list = []
                        doc_list.append(docName)
                        elasticsearch_convert_doc2html(doc_list)
                    if os.path.exists(docxName):
                        docx_list = []
                        docx_list.append(docxName)
                        elasticsearch_convert_doc2html(docx_list)
            except Exception as e:
                print(zip_file)
                print(e)

def convert_doc_to_txt():
    basedir = Global_Basedir.SPEC_BASE_DIR
    spec_list = get_spec_list()
    for spec in spec_list:
        spec_info = spec.split("_")
        series = spec_info[0]
        num = spec_info[1]
        ver = get_new_ver(series, num)
        if ver == "none":
            print("no zip for spec: " + series + num)
        else:
            txt_name = Path_Name_Format.TXT_NAME.format(basedir=basedir, series=series, ver=ver, num=num)
            txt_path = os.path.dirname(txt_name)
            docName = Path_Name_Format.DOC_NAME.format(basedir=basedir, series=series, ver=ver, num=num)
            docxName = Path_Name_Format.DOCX_NAME.format(basedir=basedir, series=series, ver=ver, num=num)
            if os.path.exists(txt_name):
                print(txt_name + " has already exists")
            else:
                if not os.path.exists(txt_path):
                    os.makedirs(txt_path)
                try:
                    if os.path.exists(docName):
                        cmd = "antiword -t " + docName + " > " + txt_name
                        os.system(cmd)
                    elif os.path.exists(docxName):
                        cmd = "docx2txt < " + docxName + " > " + txt_name
                        os.system(cmd)
                    else:
                        print(series + num + '-' + ver + " does not exist doc or docx")
                    return txt_name
                except Exception as e:
                    print(txt_name)
                    print(e)

def convert_txt_to_json():
    basedir = Global_Basedir.SPEC_BASE_DIR
    spec_list = get_spec_list()
    for spec in spec_list:
        spec_info = spec.split("_")
        series = spec_info[0]
        num = spec_info[1]
        ver = get_new_ver(series, num)
        if ver == "none":
            print("no zip for spec: " + series + num)
        else:
            out_json = Path_Name_Format.JSON_NAME.format(basedir=basedir, series=series, ver=ver, num=num)
            txt_name = Path_Name_Format.TXT_NAME.format(basedir=basedir, series=series, ver=ver, num=num)
            if os.path.exists(out_json):
                print("already exist elasticsearch_json for spec: " + series + num + "-" + ver)
            else:
                json_path = os.path.dirname(out_json)
                if not os.path.exists(json_path):
                    os.makedirs(json_path)
                try:
                    txt2json(txt_name, out_json)
                except Exception as e:
                    print("txt2json converts fails for " + out_json)

            if not os.path.exists(out_json):
                print(out_json + "converts fails")
                continue

def Convert_html_to_slice_html():
    basedir = Global_Basedir.SPEC_BASE_DIR
    spec_list = get_spec_list()
    for spec in spec_list:
        spec_info = spec.split("_")
        series = spec_info[0]
        num = spec_info[1]
        ver = get_new_ver(series, num)
        if ver == "none":
            print("no zip for spec: " + series + num)
        else:
            html_name = Path_Name_Format.HTML_NAME.format(basedir=baseDir, series=series, ver=ver, num=num)
            slice_html_path = Path_Name_Format.SLICE_HTML_PATH.format(basedir=baseDir, series=series, ver=ver, num=num)
            if os.path.exists(slice_html_path):
                print(slice_html_path + " has already exists")
            else:
                os.mkdir(slice_html_path)
                try:
                    parse_file(html_name, slice_html_path)
                    copy_image(os.path.dirname(html_name), slice_html_path)
                except Exception as e:
                    os.rmdir(slice_html_path)
                    print(html_name + " slice fails")
                    continue

def Update_index_for_elasticsearch():
    if platform.system() == 'Windows':
        es = Elasticsearch(['localhost'], port=9200, timeout=50)
    else:
        es = Elasticsearch(['10.0.2.2'], port=9200, timeout=50)
    spec_list = get_spec_list()
    for spec in spec_list:
        spec_info = spec.split("_")
        series = spec_info[0]
        num = spec_info[1]
        ver = get_new_ver(series, num)
        if ver == "none":
            print("no zip for spec: " + series + num)
        else:
            spec_in_elasticsearch = series + num + "*"
            result = es.indices.get(index=spec_in_elasticsearch)
            out_json = Path_Name_Format.JSON_NAME.format(basedir=baseDir, series=series, ver=ver, num=num)
            if result:
                print(str(*result) + "exists in elasticsearch")
                current_ver = (str(*result)).split("-")[1]
                if (current_ver < ver):
                    print(str(*result) + "is not the latest one, update it")
                    es.indices.delete(index=spec_in_elasticsearch)
                    name = series + num + "-" + ver
                    data = json.load(open(out_json, "r"))

                    print("starting to upload " + name);
                    for i, line in enumerate(data):
                        if len(line['desc']) < 1000000:
                            es.index(index=name, doc_type='doc', id=i, body=line)
                        else:
                            print("======================================")
                            print(line['key'])
            else:
                name = series + num + "-" + ver
                data = json.load(open(out_json, "r"))

                print("starting to upload " + name);
                for i, line in enumerate(data):
                    if len(line['desc']) < 1000000:
                        es.index(index=name, doc_type='doc', id=i, body=line)
                    else:
                        print("======================================")
                        print(line['key'])

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(current_dir)
    baseDir = os.path.dirname(current_dir)
    print(baseDir)
    Global_Basedir.init(baseDir)

    if platform.system() == 'Windows':
        if len(sys.argv) > 1:
            if sys.argv[1] == "upload":
                # Update index for elasticsearch
                print("Update index for elasticsearch!!!")
                Update_index_for_elasticsearch()
        else:
            # move spec in spec_zip to sepc/
            print("move spec in spec_zip to /spec/{ver}/{series}.{num}/zip/{series}{num}-{ver}.zip")
            move_zip()

            # convert zip to doc and html
            print("convert spec in speclist.txt to elasticseach system html !!!")
            convert_doc_to_html()

            # Convert html to slice html
            print("Convert html to slice html!!!")
            Convert_html_to_slice_html()
    else:
        # convert doc to txt
        print("convert spec in speclist.txt to txt!!!")
        convert_doc_to_txt()

        # convert txt to json
        print("convert txt to json!!!")
        convert_txt_to_json()

        # Update index for elasticsearch
        print("Update index for elasticsearch!!!")
        Update_index_for_elasticsearch()