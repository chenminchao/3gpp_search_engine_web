import urllib.request #获取URL文本
import re,os #正则表达式匹配URL及.zip文件
import Global_Basedir
import Path_Name_Format

def download(url):
    #print(url)
    baseDir = Global_Basedir.SPEC_BASE_DIR
    download_path = Path_Name_Format.SPEC_ZIP_PATH.format(basedir=baseDir)
    #log_path = baseDir + "/spec_url.txt"
    zip = download_path + url.split("/")[-1]
    if os.path.exists(zip):
        print(zip + " already exist!!!")
    else:
        print(url)
        #file_handle = open(log_path, mode='a')
        #file_handle.writelines(url + "\n")
        #file_handle.close()
        urllib.request.urlretrieve(url, zip)


def spy_new_ver(url):
    #print(url)
    with urllib.request.urlopen(url) as f:
        contentNet = f.read().decode('utf-8')
    speclist = re.findall(r'>[0-9]{5}-....zip<', contentNet)
    if len(speclist) == 0:
        speclist = re.findall(r'>[0-9]{5}-....ZIP<', contentNet)
    if len(speclist) > 0:
        specNew = speclist[-1].replace(">", "").replace("<", "")
        download_url = url + specNew
        download(download_url)
        ver = specNew[6:9]
    else:
        ver = "none"
    return ver

def get_series():
    baseDir = Global_Basedir.SPEC_BASE_DIR
    serieslist_path = Path_Name_Format.SERI_LIST_PATH.format(basedir=baseDir)
    series_list = []
    if not os.path.exists(serieslist_path):
        print(serieslist_path + " does not exist")
        return series_list
    with open(serieslist_path, 'r', encoding='UTF-8') as f:
        content = f.readlines()
    for series in content:
        series = series.replace("\n", "")
        if series != "":
            series_list.append(series)
    #print("spec list:")
    #print(spec_list)
    return series_list

def spy_series():
    #获得serieslist.txt中所有系列的所有num的最新version的url
    series_list = get_series()
    for series in series_list:
        url = Path_Name_Format.URL_SER.format(series=series)

        #爬取网页内容保存到conentNet字符串中.
        with urllib.request.urlopen(url) as f:
            contentNet = f.read().decode('utf-8')

        #解析series系列所有num and ver
        list_num = re.findall(r'>[0-9]{2}.[0-9]{3}<',contentNet)
        for num in list_num:
            url_num = url + num.replace(">", "").replace("<", "") + "/"
            spy_new_ver(url_num)

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(current_dir)
    baseDir = os.path.dirname(current_dir)
    #print(baseDir)
    Global_Basedir.init(baseDir)
    spy_series()
