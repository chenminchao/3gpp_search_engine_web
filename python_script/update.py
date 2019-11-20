import os
import sys
import glob
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
from spy_download import spy_new_ver

def move_zip():
    baseDir = Global_Basedir.SPEC_BASE_DIR
    zip_Path = Path_Name_Format.SPEC_ZIP_PATH.format(basedir=baseDir)
    if not os.path.exists(zip_Path):
        print(zip_Path + " path not exist!!!")
    else:
        inputFileNames = os.listdir(zip_Path)
        for i, fileName in enumerate(inputFileNames):
            if fileName.endswith('zip'):
                series = fileName[0:2]
                num = fileName[2:5]
                ver = fileName[6:9]
                in_file = zip_Path + "/" + fileName
                out_zip_path = Path_Name_Format.ZIP_PATH.format(basedir=baseDir, series=series, num=num, ver=ver)
                out_zip_name = Path_Name_Format.ZIP_NAME.format(basedir=baseDir, series=series, num=num, ver=ver)
                if not os.path.exists(out_zip_name):
                    if not os.path.exists(out_zip_path) :
                        os.makedirs(out_zip_path)
                    shutil.copy(in_file, out_zip_path)
                    print("copy " + in_file + " to " + out_zip_name)
                    if not os.path.exists(out_zip_name):
                        print("move " + in_file + " failed!!!")
                        os.rmdir(out_zip_path)
                else:
                    print(out_zip_name + " file already exist!!!")

def unzip_zip_to_doc(series, num, ver):
    baseDir = Global_Basedir.SPEC_BASE_DIR
    zip_file = Path_Name_Format.ZIP_NAME.format(basedir=baseDir, series=series, num=num, ver=ver)
    if not os.path.exists(zip_file):
        specName = series + num + "-" + ver
        print("no zip for spec: " + specName)
    else:
        docPath = Path_Name_Format.DOC_PATH.format(basedir=baseDir, series=series, num=num, ver=ver)
        docName = Path_Name_Format.DOC_NAME.format(basedir=baseDir, series=series, num=num, ver=ver)
        docxName = Path_Name_Format.DOCX_NAME.format(basedir=baseDir, series=series, num=num, ver=ver)
        if os.path.exists(docName):
            print(docName + " already exist!!!")
        elif os.path.exists(docxName):
            print(docxName + " already exist!!!")
        else:
            try:
                unzip(zip_file, docPath)
                if os.path.exists(docName):
                    print(docName)
                elif os.path.exists(docxName):
                    print(docxName)
                else:
                    # spec_zip name not consist with doc name
                    doclist = glob.glob(docPath + "/*.doc", recursive=True)
                    docxlist = glob.glob(docPath + "/*.docx", recursive=True)
                    if len(doclist) == 1:
                        if os.path.basename(doclist[0]) != os.path.basename(docName):
                            shutil.move(doclist[0], docName)
                            print(" rename " + os.path.basename(doclist[0]) + "->" + os.path.basename(docName))
                        else:
                            print("unzip" + zip_file + " failed!!!")
                            os.rmdir(docPath)
                    elif len(docxlist) == 1:
                        if os.path.basename(docxlist[0]) != os.path.basename(docxName):
                            shutil.move(doclist[0], docxName)
                            print(" rename " + os.path.basename(docxlist[0]) + "->" + os.path.basename(docxName))
                        else:
                            print("unzip" + zip_file + " failed!!!")
                            os.rmdir(docPath)
                    else:
                        print("unzip" + zip_file + " failed!!!")
                        os.rmdir(docPath)
            except Exception as e:
                print("unzip " + zip_file + " failed !!!")
                os.rmdir(docPath)
                print(e)

def convert_doc_to_html(series, num, ver):
    baseDir = Global_Basedir.SPEC_BASE_DIR
    output_html_name = Path_Name_Format.HTML_NAME.format(basedir=baseDir, series=series, num=num, ver=ver)
    if os.path.exists(output_html_name):
        print(output_html_name  + " already exist!!!")
    else:
        docPath = Path_Name_Format.DOC_PATH.format(basedir=baseDir, series=series, num=num, ver=ver)
        doclist = glob.glob(docPath + "/*.doc", recursive=True)
        if len(doclist) > 0:
            elasticsearch_convert_doc2html(doclist)
        docxlist = glob.glob(docPath + "/*.docx", recursive=True)
        if len(docxlist) > 0:
            elasticsearch_convert_doc2html(docxlist)
        if len(doclist) == 0 and len(docxlist) == 0:
            print(series + num + '-' + ver + " does not exist doc or docx")
            os.rmdir(os.path.dirname(output_html_name))
        if not os.path.exists(output_html_name):
            print("convert txt failed for spec " + series + num + '-' + ver)
            os.rmdir(os.path.dirname(output_html_name))

def convert_doc_to_txt(series, num, ver):
    baseDir = Global_Basedir.SPEC_BASE_DIR
    output_txt_name = Path_Name_Format.TXT_NAME.format(basedir=baseDir, series=series, num=num, ver=ver)
    if os.path.exists(output_txt_name):
        print(output_txt_name  + " already exist!!!")
    else:
        txt_path = os.path.dirname(output_txt_name)
        if not os.path.exists(os.path.dirname(output_txt_name)):
            os.makedirs(txt_path)
        docPath = Path_Name_Format.DOC_PATH.format(basedir=baseDir, series=series, num=num, ver=ver)
        doclist = glob.glob(docPath + "/*.doc", recursive=True)
        if len(doclist) > 0:
            cmd = "antiword -t " + doclist[0] + " > " + output_txt_name
            os.system(cmd)
        docxlist = glob.glob(docPath + "/*.docx", recursive=True)
        if len(docxlist) > 0:
            cmd = "docx2txt < " + docxlist[0] + " > " + output_txt_name
            os.system(cmd)
        if len(doclist) == 0 and len(docxlist) == 0:
            print(series + num + '-' + ver + " does not exist doc or docx")
            os.rmdir(txt_path)
        if not os.path.exists(output_txt_name):
            print("convert txt failed for spec " + series + num + '-' + ver)
            os.rmdir(txt_path)
        else:
            print(output_txt_name)

def convert_txt_to_json(series, num, ver):
    baseDir = Global_Basedir.SPEC_BASE_DIR
    out_json = Path_Name_Format.JSON_NAME.format(basedir=baseDir, series=series, ver=ver, num=num)
    txt_name = Path_Name_Format.TXT_NAME.format(basedir=baseDir, series=series, ver=ver, num=num)
    if os.path.exists(out_json):
        print(out_json  + " already exist!!!")
    elif not os.path.exists(txt_name):
        specName = series + num + "-" + ver
        print("no txt for spec: " + specName)
    else:
        json_path = os.path.dirname(out_json)
        if not os.path.exists(json_path):
            os.makedirs(json_path)
        try:
            txt2json(txt_name, out_json)
            if not os.path.exists(out_json):
                print("txt2json converts fails for " + out_json)
                os.rmdir(out_json)
        except Exception as e:
            print("txt2json converts fails for " + out_json)
            os.rmdir(out_json)

def Convert_html_to_slice_html(series, num, ver):
    baseDir = Global_Basedir.SPEC_BASE_DIR
    html_name = Path_Name_Format.HTML_NAME.format(basedir=baseDir, series=series, ver=ver, num=num)
    slice_html_path = Path_Name_Format.SLICE_HTML_PATH.format(basedir=baseDir, series=series, ver=ver, num=num)
    if os.path.exists(slice_html_path):
        print(slice_html_path  + " already exist!!!")
    elif not os.path.exists(html_name):
        specName = series + num + "-" + ver
        print("no html for spec: " + specName)
    else:
        os.mkdir(slice_html_path)
        try:
            parse_file(html_name, slice_html_path)
            copy_image(os.path.dirname(html_name), slice_html_path)
        except Exception as e:
            os.rmdir(slice_html_path)
            print(html_name + " slice fails!!!")

def Update_index_for_elasticsearch(series, num, ver):
    baseDir = Global_Basedir.SPEC_BASE_DIR
    specName = series + num + "-" + ver
    out_json = Path_Name_Format.JSON_NAME.format(basedir=baseDir, series=series, ver=ver, num=num)
    if platform.system() == 'Windows':
        es = Elasticsearch(['localhost'], port=9200, timeout=50)
    else:
        es = Elasticsearch(['localhost'], port=9200, timeout=50)
    if not os.path.exists(out_json):
        print("no html for spec: " + specName)
    else:
        spec_in_elasticsearch = series + num + "*"
        result = es.indices.get(index=spec_in_elasticsearch)
        if result:
            print(str(*result) + " exists in elasticsearch")
            current_ver = (str(*result)).split("-")[1]
            if (current_ver < ver):
                print(str(*result) + "is not the latest one, update it")
                es.indices.delete(index=spec_in_elasticsearch)
        data = json.load(open(out_json, "r"))
        print("starting to upload " + specName);
        for i, line in enumerate(data):
            if len(line['desc']) < 1000000:
                es.index(index=specName, doc_type='doc', id=i, body=line)
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
                #Update_index_for_elasticsearch()
        else:
            # move spec in spec_zip to sepc/
            print("move spec in spec_zip to /spec/{ver}/{series}.{num}/zip/{series}{num}-{ver}.zip")
            move_zip()

            # get spec in speclist.txt and convert it: zip->doc/docx->html->slice_html doc/docx->txt->json->upload
            spec_list = get_spec_list()
            print("get spec in speclist.txt and convert it: zip->doc/docx->html->slice_html")
            for spec in spec_list:
                spec_info = spec.split("_")
                series = spec_info[0]
                num = spec_info[1]

                # get ver from zip
                #ver = get_new_ver(series, num)

                # get ver from network
                url_num = Path_Name_Format.URL_NUM.format(basedir=baseDir, series=series, num=num)
                ver = spy_new_ver(url_num)
                specName = series + num + "-" + ver

                print("")
                print("==============================")
                print("specs in speclist.txt")
                print(spec_list)
                print("start to deal with spec " + specName)

                #unzip zip to doc/docx
                print("1. unzip " + specName + ".zip to " + specName + ".doc !!!")
                unzip_zip_to_doc(series, num, ver)

                # convert doc/docx to html
                print("2. convert " + specName + ".doc to " + specName + ".html !!!")
                convert_doc_to_html(series, num, ver)

                # Convert html to slice html
                print("3. convert " + specName + ".html to slice htmls !!!")
                Convert_html_to_slice_html(series, num, ver)
    else:
        # get spec in speclist.txt and convert it: zip->doc/docx->html->slice_html doc/docx->txt->json->upload
        spec_list = get_spec_list()
        print("get spec in speclist.txt and convert it: doc/docx->txt->json->upload")
        for spec in spec_list:
            spec_info = spec.split("_")
            series = spec_info[0]
            num = spec_info[1]
            ver = get_new_ver(series, num) # download instead
            specName = series + num + "-" + ver

            print("")
            print("==============================")
            print("specs in speclist.txt")
            print(spec_list)
            print("start to deal with spec " + specName)

            # convert doc/docx to txt
            print("1. convert " + specName + ".doc to " + specName + ".txt !!!")
            convert_doc_to_txt(series, num, ver)

            # convert txt to json
            print("2. convert " + specName + ".txt to " + specName + ".json !!!")
            convert_txt_to_json(series, num, ver)

            # Update index for elasticsearch
            print("3. Update spec " + specName +" index for elasticsearch!!!")
            Update_index_for_elasticsearch(series, num, ver)
