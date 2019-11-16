import win32com
from win32com.client import Dispatch
import os
import glob
import Global_Basedir, Path_Name_Format

def elasticsearch_convert_doc2html(input_docs):
    w =win32com.client.Dispatch('Word.Application')
    win32com.client.gencache.EnsureDispatch('Word.Application')
    for input_doc in input_docs:
        input_doc = input_doc.replace("\\", "/")
        if (" " in input_doc) == False:
            output_html_dir = os.path.dirname(os.path.dirname(input_doc)) + "/html"
            output_html = output_html_dir + "/" + os.path.basename(input_doc).replace('doc', 'html')
            if "docx" in input_doc:
                output_html = output_html_dir + "/" + os.path.basename(input_doc).replace('docx', 'html')
            #print(output_html_dir)
            print(output_html)
            if not os.path.exists(output_html_dir):
                os.mkdir(output_html_dir)
            elif os.path.exists(output_html):
                print(output_html + " has existed")
                continue
                #shutil.rmtree(output_html_dir)
                #os.mkdir(output_html_dir)
            try:
                doc = w.Documents.Open(FileName=input_doc)
                wc = win32com.client.constants
                w.ActiveDocument.WebOptions.RelyOnCSS =1
                w.ActiveDocument.WebOptions.OptimizeForBrowser= 1
                w.ActiveDocument.WebOptions.BrowserLevel= 0 # constants.wdBrowserLevelV4
                w.ActiveDocument.WebOptions.OrganizeInFolder =0
                w.ActiveDocument.WebOptions.UseLongFileNames =1
                w.ActiveDocument.WebOptions.RelyOnVML =0
                w.ActiveDocument.WebOptions.AllowPNG = 1
                w.ActiveDocument.SaveAs(FileName=output_html, FileFormat=wc.wdFormatFilteredHTML)
                w.Documents.Close(wc.wdDoNotSaveChanges)
            except Exception as e:
                print("****************************")
                print(input_doc + " has exception")
        else:
            print("=================")
            print(input_doc + " contains spaces, ignore it")
    w.Quit()

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(current_dir)
    baseDir = os.path.dirname(current_dir)
    print(baseDir)
    Global_Basedir.init(baseDir)
    spec_path = Path_Name_Format.SPEC_PATH.format(basedir=baseDir)
    spec_path = spec_path.replace("\\", "/")
    doc_list = glob.glob(spec_path + "**/*.doc", recursive=True)
    docx_list = glob.glob(spec_path + "**/*.docx", recursive=True)
    elasticsearch_convert_doc2html(doc_list)
    elasticsearch_convert_doc2html(docx_list)
