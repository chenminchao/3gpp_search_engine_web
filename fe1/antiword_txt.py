# -*- coding: utf-8 -*-

import shutil
import os
import sys
import tempfile
import re
import glob
import subprocess
import json

import Config
import Constant
from util import unzip, anti2txt

def convert(series, num, ver):
    basedir = Config.SPEC_STORE_DIR
    zipPath = Constant.ZIP_PATH.format(basedir = basedir, series = series, ver = ver, num = num)
    anti_txt_name = Constant.ANTI_TXT_NAME.format(basedir=basedir, series=series, ver=ver, num=num)
    try:
        zipBasename = os.path.basename(zipPath)
        with tempfile.TemporaryDirectory() as tmpdir:
            pathToZip = os.path.join(tmpdir, zipBasename)
            shutil.copyfile(zipPath, pathToZip)
            # Unzip
            unzipDir = os.path.splitext(pathToZip)[0] + '.unzip'
            unzip(pathToZip, unzipDir)
            # Convert
            docs = glob.glob(os.path.join(unzipDir, "*.doc"))
            anti2txt(docs[0], anti_txt_name)
        return anti_txt_name
    except Exception as e:
        # Cleanup
        shutil.rmtree(anti_txt_name)
        raise e
    except KeyboardInterrupt as e:
        # Cleanup
        shutil.rmtree(anti_txt_name)
        raise e

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(sys.argv[0], "basedir", "series", "num", "spec_ver")
        sys.exit(1)
    Config.init(sys.argv[1])
    for arg in sys.argv[2:]:
        if not re.fullmatch(r'[-0-9a-zA-Z]+', arg):
            print("Malformed argument", arg)
            sys.exit(1)
    series, num, ver = sys.argv[2:]
    print(convert(series, num, ver))
