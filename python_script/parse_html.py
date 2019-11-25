import argparse 
import glob 
import re 
import os 
import platform 

def create_folder(out_path, dir): 
    if not os.path.exists(os.path.join(out_path, dir)): os.makedirs(os.path.join(out_path, dir))
        #print("create folder ", os.path.join(out_path, dir))

def parse_file(infile, out_path):
    with open(infile, errors='ignore') as f:
        content = f.read()

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    spec_zip = os.path.basename(infile).replace("html", "zip")
    #spec_zip_path = os.path.dirname(os.path.dirname(infile)) + "/zip/" + spec_zip
    spec_html_path = os.path.dirname(os.path.dirname(infile)) + "/html"
    spec_html = os.path.basename(infile)

    html_header = content.split('<body')[0]
    html_header = html_header + "<body lang=EN-US link=blue vlink=purple style='tab-interval:14.2pt'>\n"
    if os.path.exists(spec_html_path):
        link_and_download = '<p align="right"> <a href=../html/' + spec_html +'>Link2doc</a> ' \
            + '<a href=../zip/' + spec_zip + '>Download</a><p>'
    else:
        link_and_download = '<p align="right"> <a href=../html/' + spec_html \
            + '>Link2doc</a> ' + '<a href=../zip/' + spec_zip + '>Download</a><p>'

    #print(link_and_download)

    body_end = '</body>\n';
    mark_script = '<script type="text/javascript" src="https://ajax.microsoft.com/ajax/jQuery/jquery-1.4.2.min.js"></script>\n' +  \
                  '<script src="https://cdnjs.cloudflare.com/ajax/libs/mark.js/7.0.0/mark.min.js"></script>\n' + \
                  '<script type="text/javascript">\n' +\
                  '$(document).ready(function(){\n' + \
                  'var instance = new Mark(document.querySelector("body"));\n' + \
		  'var options = {"separateWordSearch" : false};\n' +\
                  'instance.unmark({done: function(){\n' + \
                  'var url = document.URL;\n' +\
                  'var key = decodeURIComponent(url.split("=")[1]);\n' +\
                  'console.log(key);\n' + \
                  'instance.mark(key, options) }})\n' +\
                  '});\n' +\
                  '</script>\n'
    html_end = '</html>'

    paragraph_list_sorted = []
    paragraphs = content.split("\n\n");
    for paragraph in paragraphs:
       if("</h1>" in paragraph):
           paragraph_list_sorted.append(paragraph.replace("\n", " "))
       if("</h2>" in paragraph):
           paragraph_list_sorted.append(paragraph.replace("\n", " "))
       if("</h3>" in paragraph):
           paragraph_list_sorted.append(paragraph.replace("\n", " "))

    current_index = 0
    htmls = []
    #print(len(paragraph_list_sorted))
    for paragraph in paragraphs:
        if current_index == len(paragraph_list_sorted) -1:
            break
        elif paragraph.replace("\n", " ") == paragraph_list_sorted[current_index]:
            htmls.clear()
            htmls.append(paragraph)
        elif paragraph.replace("\n", " ") == paragraph_list_sorted[current_index+1]:
            #fname = str(key_list_sorted[current_index][0]) + "-" + str(key_list_sorted[current_index][1].replace(" ", "_"))
            content = re.sub(r'\<.*?\>', '', paragraph_list_sorted[current_index])
            fname = str(content.split(" ")[0].strip())
            fname = fname.replace("&nbsp;", "")
            if not platform.system() == 'Linux':
                fname = out_path + '\\' + fname + '.html'
            else:
                fname = out_path + '/' + fname + '.html'
            with open(fname, "w") as f:
                f.write(html_header)
                f.write(''.join(htmls))
                f.write(link_and_download)
                f.write(body_end)
                f.write(mark_script)
                f.write(html_end)
                f.close()
            htmls.clear()
            htmls.append(paragraph)
            current_index = current_index + 1
        else:
            htmls.append(paragraph)

def main(in_path, out_path):
    for root, dirs, files in os.walk(in_path):
        for file in files:
            if file.endswith(".htm"):
                input_file = os.path.join(root, file)
                if("_files" not in str(root)):
                    create_folder(out_path, os.path.basename(input_file).split(".")[0])
                    out_path = out_path + "\\" + os.path.basename(input_file).split(".")[0]
                    parse_file(input_file, out_path)

if __name__ == "__main__":
    in_file = "/home/ubuntu/3gpp_search_engine/3gpp_search_engine_web/spec/g40/23.401/html/23401-g40.html"
    out_Path = "/home/ubuntu/3gpp_search_engine/3gpp_search_engine_web/spec/g40/23.401/slice_html"
    parse_file(in_file, out_Path)
    #main(in_Path, out_Path)
