import os
import sys
import glob
import json
import shutil
from elasticsearch import Elasticsearch
import Global_Basedir
import Path_Name_Format
from util import get_spec_list,get_new_ver,get_ver_list,unzip,copy_image,chang_html_lang
import platform
if not platform.system() == 'Linux':
    from doc2html_converter import elasticsearch_convert_doc2html
from jsonGeneration import txt2json
from parse_html import parse_file
from spy_download import spy_new_ver
from libreoffice_convert import libre_convert_doc_to_html,slice_html

def move_zip():
    baseDir = Global_Basedir.SPEC_BASE_DIR
    zip_Path = Path_Name_Format.SPEC_ZIP_PATH.format(basedir=baseDir)
    if not os.path.exists(zip_Path):
        print(zip_Path + " path not exist!!!")
    else:
        inputFileNames = os.listdir(zip_Path)
        for i, fileName in enumerate(inputFileNames):
            if fileName.endswith('ZIP'):
                fname = zip_Path + fileName
                fname1 = fname.replace("ZIP", "zip")
                os.rename(fname, fname1)
                fileName = fileName.replace("ZIP", "zip")
            if fileName.endswith('zip'):
                series = fileName[0:2]
                num = fileName[2:5]
                ver = fileName[6:9]
                print(series + num + ver)

def get_del_spec(series, num, ver):
    baseDir = Global_Basedir.SPEC_BASE_DIR
    html_name = Path_Name_Format.HTML_NAME.format(basedir=baseDir, series=series, num=num, ver=ver)
    slice_html_name = Path_Name_Format.SLICE_HTML_PATH.format(basedir=baseDir, series=series, num=num, ver=ver)
    json_name = Path_Name_Format.JSON_NAME.format(basedir=baseDir, series=series, num=num, ver=ver)
    specName = series + num + '-' + ver
    if not os.path.exists(html_name):
        print(specName + 'has no html!!!')
        cmd = 'rm -rf ' + os.path.dirname(html_name)
        os.system(cmd)
        return 'true'
    elif not os.path.exists(slice_html_name):
        print(specName + ' has no slice_html!!!')
        return 'true'
    elif not os.path.exists(json_name):
        print(specName + ' has no json!!!')
        return 'true'
    else:
        html_list = glob.glob(slice_html_name + "*.html", recursive=True)
        if len(html_list) == 0:
            print(specName + ' only has picture!!!')
            cmd = 'rm -rf ' + os.path.dirname(slice_html_name)
            os.system(cmd)
            return 'true'
    return 'false'

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
        if not os.path.exists(docName) and not os.path.exists(docxName):
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
                    if len(doclist) > 0:
                        if os.path.basename(doclist[0]) != os.path.basename(docName):
                            shutil.move(doclist[0], docName)
                            print(" rename " + os.path.basename(doclist[0]) + "->" + os.path.basename(docName))
                        else:
                            print("unzip" + zip_file + " failed!!!")
                            os.rmdir(docPath)
                    elif len(docxlist) > 0:
                        if os.path.basename(docxlist[0]) != os.path.basename(docxName):
                            shutil.move(docxlist[0], docxName)
                            print(" rename " + os.path.basename(docxlist[0]) + "->" + os.path.basename(docxName))
                        else:
                            print("unzip" + zip_file + " failed!!!")
                            os.rmdir(docPath)
                    else:
                        print("unzip" + zip_file + " but no doc/docx file!!!")
            except Exception as e:
                print("unzip " + zip_file + " failed !!!")
                os.rmdir(docPath)
                print(e)

def convert_doc_to_html(series, num, ver):
    # only for windows
    baseDir = Global_Basedir.SPEC_BASE_DIR
    output_html_name = Path_Name_Format.HTML_NAME.format(basedir=baseDir, series=series, num=num, ver=ver)
    if not os.path.exists(output_html_name):
        docName = Path_Name_Format.DOC_NAME.format(basedir=baseDir, series=series, num=num, ver=ver)
        docxName = Path_Name_Format.DOCX_NAME.format(basedir=baseDir, series=series, num=num, ver=ver)
        if os.path.exists(docName):
            elasticsearch_convert_doc2html(docName)
        elif os.path.exists(docxName):
            elasticsearch_convert_doc2html(docxName)
        else:
            print(series + num + '-' + ver + " does not exist doc or docx")
        if not os.path.exists(output_html_name):
            print("convert html failed for spec " + series + num + '-' + ver)

def convert_doc_to_html2(series, num, ver):
    # only for linux
    baseDir = Global_Basedir.SPEC_BASE_DIR
    output_html_name = Path_Name_Format.HTML_NAME.format(basedir=baseDir, series=series, num=num, ver=ver)
    docName = Path_Name_Format.DOC_NAME.format(basedir=baseDir, series=series, num=num, ver=ver)
    docxName = Path_Name_Format.DOCX_NAME.format(basedir=baseDir, series=series, num=num, ver=ver)
    if not os.path.exists(output_html_name):
        if os.path.exists(docName):
            libre_convert_doc_to_html(docName)
            if os.path.exists(output_html_name):
                #change html lang
                chang_html_lang(output_html_name)
        elif os.path.exists(docxName):
            libre_convert_doc_to_html(docxName)
            if os.path.exists(output_html_name):
                #change html lang
                chang_html_lang(output_html_name)
        else:
            print(series + num + '-' + ver + " does not exist doc or docx")
        if not os.path.exists(output_html_name):
            print("convert html failed for spec " + series + num + '-' + ver)

def convert_doc_to_txt(series, num, ver):
    baseDir = Global_Basedir.SPEC_BASE_DIR
    output_txt_name = Path_Name_Format.TXT_NAME.format(basedir=baseDir, series=series, num=num, ver=ver)
    if os.path.exists(output_txt_name):
        print(output_txt_name  + " already exist!!!")
    else:
        txt_path = os.path.dirname(output_txt_name)
        if not os.path.exists(os.path.dirname(output_txt_name)):
            os.makedirs(txt_path)
        docName = Path_Name_Format.DOC_NAME.format(basedir=baseDir, series=series, num=num, ver=ver)
        docxName = Path_Name_Format.DOCX_NAME.format(basedir=baseDir, series=series, num=num, ver=ver)
        if os.path.exists(docName):
            cmd = "antiword -t " + docName + " > " + output_txt_name
            os.system(cmd)
        elif os.path.exists(docxName):
            cmd = "docx2txt < " + docxName + " > " + output_txt_name
            os.system(cmd)
        else:
            print(series + num + '-' + ver + " does not exist doc or docx")
        if not os.path.exists(output_txt_name):
            print("convert txt failed for spec " + series + num + '-' + ver)

def convert_txt_to_json(series, num, ver):
    baseDir = Global_Basedir.SPEC_BASE_DIR
    out_json = Path_Name_Format.JSON_NAME.format(basedir=baseDir, series=series, ver=ver, num=num)
    txt_name = Path_Name_Format.TXT_NAME.format(basedir=baseDir, series=series, ver=ver, num=num)
    if not os.path.exists(txt_name):
        specName = series + num + "-" + ver
        print("no txt for spec: " + specName)
    elif not os.path.exists(out_json):
        json_path = os.path.dirname(out_json)
        if not os.path.exists(json_path):
            os.makedirs(json_path)
        try:
            txt2json(txt_name, out_json)
            if not os.path.exists(out_json):
                print("txt2json converts fails for " + out_json)
        except Exception as e:
            print("txt2json converts fails for " + out_json)

def Convert_html_to_slice_html(series, num, ver):
    baseDir = Global_Basedir.SPEC_BASE_DIR
    html_name = Path_Name_Format.HTML_NAME.format(basedir=baseDir, series=series, ver=ver, num=num)
    slice_html_path = Path_Name_Format.SLICE_HTML_PATH.format(basedir=baseDir, series=series, ver=ver, num=num)
    if not os.path.exists(html_name):
        specName = series + num + "-" + ver
        print("no html for spec: " + specName)
    elif not os.path.exists(slice_html_path):
        os.mkdir(slice_html_path)
        try:
            parse_file(html_name, slice_html_path)
            copy_image(os.path.dirname(html_name), slice_html_path)
        except Exception as e:
            print(html_name + " slice fails!!!")

def Convert_html_to_slice_html2(series, num, ver):
    baseDir = Global_Basedir.SPEC_BASE_DIR
    html_name = Path_Name_Format.HTML_NAME.format(basedir=baseDir, series=series, ver=ver, num=num)
    slice_html_path = Path_Name_Format.SLICE_HTML_PATH.format(basedir=baseDir, series=series, ver=ver, num=num)
    if not os.path.exists(html_name):
        specName = series + num + "-" + ver
        print("no html for spec: " + specName)
    elif not os.path.exists(slice_html_path):
        os.mkdir(slice_html_path)
        try:
            slice_html(html_name)

            if os.path.exists(slice_html_path):
                cmd = 'cp -rp ' + html_name.replace(".html", "_*") + ' ' + slice_html_path
                os.system(cmd)
        except Exception as e:
            print(html_name + " slice fails!!!")

def Update_index_for_elasticsearch(series, num, ver):
    baseDir = Global_Basedir.SPEC_BASE_DIR
    specName = series + num + "-" + ver
    out_json = Path_Name_Format.JSON_NAME.format(basedir=baseDir, series=series, ver=ver, num=num)

    es = Elasticsearch(['localhost'], port=9200, timeout=50)
    spec_in_elasticsearch = series + num + "*"
    result = es.indices.get(index=spec_in_elasticsearch)

    spec_need_del = get_del_spec(series, num, ver)
    if spec_need_del == 'true':
        if result:
            print(str(*result) + " need to be deleted form elasticsearch!!!")
            es.indices.delete(index=spec_in_elasticsearch)
    else:
        if result:
            # print(str(*result) + " exists in elasticsearch")
            current_ver = (str(*result)).split("-")[1]
            if (current_ver < ver):
                print(str(*result) + "is not the latest one, update it")
                es.indices.delete(index=spec_in_elasticsearch)
                data = json.load(open(out_json, "r"))
                # print("starting to upload " + specName);
                try:
                    for i, line in enumerate(data):
                        if len(line['desc']) < 1000000:
                            es.index(index=specName, doc_type='doc', id=i, body=line)
                        else:
                            print("======================================")
                            print(line['key'])
                except Exception as e:
                    print("failed upload " + specName);
                    print(e)
        else:
            data = json.load(open(out_json, "r"))
            # print("starting to upload " + specName);
            try:
                for i, line in enumerate(data):
                    if len(line['desc']) < 1000000:
                        es.index(index=specName, doc_type='doc', id=i, body=line)
                    else:
                        print("======================================")
                        print(line['key'])
            except Exception as e:
                print("failed upload " + specName);
                print(e)

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(current_dir)
    baseDir = os.path.dirname(current_dir)
    print(baseDir)
    Global_Basedir.init(baseDir)

    # get spec in speclist.txt and convert it: zip->doc/docx->html->slice_html doc/docx->txt->json->upload
    spec_list = get_spec_list()
    print("get spec in speclist.txt and convert it: zip->doc/docx->html->slice_html")
    i = 0
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

        i = i + 1
        print(str(i) + ':' + str(len(spec_list)) + ' ' + specName)

        # unzip zip to doc/docx
        print("1. unzip " + specName + ".zip to " + specName + ".doc !!!")
        unzip_zip_to_doc(series, num, ver)

        # convert doc/docx to html
        print("2. convert " + specName + ".doc to " + specName + ".html !!!")
        convert_doc_to_html2(series, num, ver)

        # convert doc/docx to html
        print("2. convert " + specName + ".html to " + specName + "CLA*.html !!!")
        Convert_html_to_slice_html2(series, num, ver)
    
        # convert doc/docx to txt
        print("3. convert " + specName + ".doc to " + specName + ".txt !!!")
        convert_doc_to_txt(series, num, ver)
    
        # convert txt to json
        print("4. convert " + specName + ".txt to " + specName + ".json !!!")
        convert_txt_to_json(series, num, ver)

        # Update index for elasticsearch
        print("5. Update spec " + specName + " index for elasticsearch!!!")
        Update_index_for_elasticsearch(series, num, ver)

