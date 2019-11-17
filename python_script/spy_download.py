import urllib.request #获取URL文本
import re,os #正则表达式匹配URL及.zip文件
import Global_Basedir
import Path_Name_Format

def download(url):
    print(url)
    baseDir = Global_Basedir.SPEC_BASE_DIR
    download_path = Path_Name_Format.SPEC_ZIP_PATH.format(basedir=baseDir)
    zip = download_path + url.split("/")[-1]
    if os.path.exists(zip):
        print(zip + " already exist!!!")
    else:
        urllib.request.urlretrieve(url, zip)

def spy_new_ver(url):
    print(url)
    with urllib.request.urlopen(url) as f:
        contentNet = f.read().decode('utf-8')
    speclist = re.findall(r'>[0-9]{5}-....zip<', contentNet)
    specNew = speclist[-1].replace(">", "").replace("<", "")
    download_url = url + specNew
    download(download_url)
    ver = specNew[6:9]
    return ver

def spy_series():
    url = "https://www.3gpp.org/ftp/specs/archive/29_series/"

    #爬取网页内容保存到conentNet字符串中.
    with urllib.request.urlopen(url) as f:
        contentNet = f.read().decode('utf-8')

    #解析29系列所有num and ver
    list_num = re.findall(r'>[0-9]{2}.[0-9]{3}<',contentNet)
    for num in list_num:
        url = url + num.replace(">", "").replace("<", "") + "/"
        spy_new_ver()

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(current_dir)
    baseDir = os.path.dirname(current_dir)
    print(baseDir)
    Global_Basedir.init(baseDir)
    # 下载29系列所有最新版本
    spy_series()
