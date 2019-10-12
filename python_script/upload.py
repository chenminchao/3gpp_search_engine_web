import json
import sys
from pprint import pprint
from elasticsearch import Elasticsearch
import argparse
import ntpath
import os

def main(file):
    name = ntpath.basename(file).split('.')[0]
    print(name)
    es = Elasticsearch(['localhost'], port=9200, timeout=50)
    data = json.load(open(file, "r"))

    for i, line in enumerate(data):
        if len(line['desc']) < 1000000:
            check_file = file + str(i)
            es.index(index=name, doc_type='doc', id=i, body=line)
        else:
            print("======================================")
            print(line['key'])

if __name__ == "__main__":
    rootpath = os.path.abspath('..')  # 获取上级路径
    filePath = rootpath + "\\specs\\spec_jsons"
    fileNames = os.listdir(filePath)
    for fileName in fileNames:
        if fileName.endswith('json'):
            input = filePath + "\\" + fileName
            main(input)