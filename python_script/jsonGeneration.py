import json
import re
import argparse
import os
import logging
from logging import config

config.fileConfig('./loggingConfig.conf')


def get_title_info(catelog):
    title_level = catelog.count('.')
    title_pre = catelog.split()[0]
    key = re.sub(title_pre, '', catelog)
    key = re.sub(r'\d+', '', key).strip()
    # print(title_level, title_pre, key)
    return (key, title_pre, title_level)


def get_desc_info(title_infos, content):
    desc_infos = []
    start_num = 0
    end_num = 0
    for i, title_info in enumerate(title_infos):
        title_cur = title_info
        title_next = ()
        if (i != len(title_infos) - 1):
            title_next = title_infos[i + 1]
        else:
            # this is hard-coded, check if it is ok
            title_next = ("Annex A (informative)", "", 0)

        # get the start desc line num
        for j, line in enumerate(content[end_num:]):
            if (line.find(title_cur[0]) != -1 and line.find(title_cur[1]) != -1 and not line.split()[-1].isdigit()):
                pass
                # print(line.split(title_cur[1])[1].strip())
                # print(title_cur[0])
            if (line.find(title_cur[0]) != -1 and line.find(title_cur[1]) != -1
                    and line.split(title_cur[1])[1].strip() == title_cur[0] and not line.split()[-1].isdigit()):
                start_num = end_num + j
                break;

        # get the end desc line num
        for j, line in enumerate(content[start_num:]):
            if (line.find(title_next[0]) != -1 and line.find(title_next[1]) != -1
                    and title_next[0] != "Annex A (informative)"
                    and not line.split()[-1].isdigit()):
                pass
                # print(line.split(title_next[1])[1].strip())
                # print(title_next[0])
            if (line.find(title_next[0]) != -1 and line.find(title_next[1]) != -1
                    and title_next[0] != "Annex A (informative)" and line.split(title_next[1])[1].strip() == title_next[
                        0]
                    and not line.split()[-1].isdigit()):
                end_num = start_num + j
                break;

        # print(title_cur[1], start_num, end_num)
        desc_infos.append(''.join(content[start_num: end_num]))
    return desc_infos


def create_spec_dict_list(title_infos, desc_infos, keywords):
    spec_dict_list = []
    print(len(title_infos), len(desc_infos))
    for i, title_info in enumerate(title_infos):
        spec_dict = {}
        spec_dict['key'] = title_info[0]
        spec_dict['numbering'] = title_info[1]
        spec_dict['title_level'] = title_info[2]
        spec_dict['desc'] = desc_infos[i]
        spec_dict['Keywords'] = keywords

        spec_dict_list.append(spec_dict)
    return spec_dict_list


def save_json_file(file_name, dict_list):
    with open(file_name, 'w') as f:
        json.dump(dict_list, f)


def get_def_key(def_input):
    def_key_list = []
    for line in def_input['desc'].split('\n'):
        if (line.find(':') != -1):
            def_key_list.append(line.split(':')[0])
            print(line.split(':')[0])
    return def_key_list


def populateDefList(def_input):
    def_key_list = get_def_key(def_input)
    spec_def_list = []

    for i, def_key in enumerate(def_key_list):
        def_key_next = ''
        if (i != len(def_key_list) - 1):
            def_key_next = def_key_list[i + 1]

        start = def_input['desc'].find(def_key + ':') + len(def_key) + 1
        if def_key_next != '':
            end = def_input['desc'].find(def_key_next + ':')
        else:
            end = len(def_input['desc'])

        spec_defination = {}
        spec_defination['key'] = def_key
        spec_defination['desc'] = ''.join(def_input['desc'][start:end]).strip()
        spec_defination['numbering'] = def_input["numbering"]
        spec_defination['Keywords'] = def_input["Keywords"]
        print(spec_defination['key'])
        print(spec_defination['desc'])
        spec_def_list.append(spec_defination)
    return spec_def_list


def populateAbbrList(abbr_input):
    logging.getLogger().info("Populate Abbreviation List")
    if (len(abbr_input['desc'].split(".\n\n")) >= 2):
        abbr_input_start = abbr_input['desc'].split(".\n\n")[1]
    elif (len(abbr_input['desc'].split(":\n\n")) >= 2):
        abbr_input_start = abbr_input['desc'].split(":\n\n")[1]
    else:
        abbr_input_start = abbr_input['desc'].split(".\n")[1]
    abbr_def_list = []
    for line in abbr_input_start.split('\n'):
        line = line.strip()
        print(line)
        if (len(line.split()) > 1):
            abbr_def = {}
            abbr_def['key'] = line.split()[0]
            abbr_def['desc'] = line[len(abbr_def['key']):].strip()
            abbr_def['numbering'] = abbr_input["numbering"]
            abbr_def['Keywords'] = abbr_input["Keywords"]
            abbr_def_list.append(abbr_def)
            print(abbr_def['key'])
            print(abbr_def['desc'])
        else:
            print(len(line.split()))
    return abbr_def_list


def update_spec_list(def_index, abbr_index, def_list, abbr_list, spec_dict_list):
    del spec_dict_list[def_index]
    del spec_dict_list[abbr_index - 1]

    for def_line in def_list:
        spec_dict_list.append(def_line)

    for abbr_line in abbr_list:
        spec_dict_list.append(abbr_line)


def find_keywords_in_line(line, keywords):
    ret = False
    matchObj = re.match(r'^\b' + keywords + '$', line)
    if matchObj:
        logging.getLogger().debug("matchObj is {}".format(matchObj.group()))
        ret = True
    return ret


def main(input, output):
    spec_dict_list = []
    title_infos = []
    desc_infos = []
    title_index = []
    content = {}
    def_list = []
    abbr_list = []
    def_index = 0
    abbr_index = 0
    keywords_list = []
    keywords_index = 0

    with open(input, 'r', encoding='UTF-8') as f:
        content = f.readlines()

    findKeywords = False
    for i, line in enumerate(content):
        line = line.strip()
        if (findKeywords):
            if (line != ''):
                keywords_list.extend(line.split(","))
        if (find_keywords_in_line(line, "Keywords")):
            keywords_index = i
            findKeywords = True
        if (find_keywords_in_line(line, "3GPP")):
            findKeywords = False
            break
    if len(keywords_list) != 0 :
        keywords_list.pop()
        keywords_list = [item for item in keywords_list if (len(str(item)) != 0)]
        keywords = ','.join(keywords_list)
    else :
        keywords = "None"
    #    logging.getLogger().info("keywords_index={},keywords_list={}".format(keywords_index,keywords_list))
    logging.getLogger().info("keywords={}".format(keywords))

    for i, line in enumerate(content):
        if (line.find('Foreword') != -1 and not line[-2].isdigit()):  # 23.214?
            break

        if ((len(line) > 1 and line[0].isdigit() and line[-2].isdigit()) or
                (len(line) > 1 and line[0].isdigit() and content[i + 1][-2].isdigit())):
            title_info = get_title_info(line)
            title_infos.append(title_info)
            title_index.append(title_info[1])
            print(line)

    desc_infos = get_desc_info(title_infos, content)
    spec_dict_list = create_spec_dict_list(title_infos, desc_infos, keywords)

    for i, spec_dict in enumerate(spec_dict_list):
        if spec_dict['key'] == "Definitions":
            def_list = populateDefList(spec_dict)
            def_index = i
        if spec_dict['key'] == "Abbreviations":
            abbr_list = populateAbbrList(spec_dict)
            abbr_index = i

    update_spec_list(def_index, abbr_index, def_list, abbr_list, spec_dict_list)
    # logging.getLogger().info("def_list={}".format(def_list))
    # logging.getLogger().info("abbr_list={}".format(abbr_list))
    # logging.getLogger().info("spec_dict_list={}".format(spec_dict_list))
    save_json_file(output, spec_dict_list)


if __name__ == "__main__":
    logging.getLogger().info("jsonGeneration program is starting!")
    # abspath = os.getcwd()           # 获取当前路径
    rootpath = os.path.abspath('..')  # 获取上级路径

    in_Path = rootpath + "\\specs\\spec_txts"
    out_Path = rootpath + "\\specs\\spec_jsons"

    inputFileNames = os.listdir(in_Path)
    for i, fileName in enumerate(inputFileNames):
        if fileName.endswith('txt'):
            input = in_Path + "\\" + fileName
            output = out_Path + "\\" + fileName.split(".txt")[0] + ".json"
            logging.getLogger().info("program is dealing with {}!".format(fileName))
            main(input, output)