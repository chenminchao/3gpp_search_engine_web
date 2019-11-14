import re
import os

def create_folder(out_path, dir):
    if not os.path.exists(os.path.join(out_path, dir)):
        os.makedirs(os.path.join(out_path, dir))
        print("create folder ", os.path.join(out_path, dir))

def parse_file(infile, outfile):
    print(infile)
    create_folder(outfile, os.path.basename(infile).split(".")[0])
    outfile = outfile + "\\" + os.path.basename(infile).split(".")[0]
    print("outfile is ", outfile)
    with open(infile, errors='ignore') as f:
        content = f.read()

    html_header = content.split('<body')[0]
    html_header = html_header + "<body lang=EN-US link=blue vlink=purple style='tab-interval:14.2pt'>\n"
    body_end = '</body>\n';
    mark_script = '<script type="text/javascript" src="https://ajax.microsoft.com/ajax/jQuery/jquery-1.4.2.min.js"></script>\n' +  \
                  '<script src="https://cdnjs.cloudflare.com/ajax/libs/mark.js/7.0.0/mark.min.js"></script>\n' + \
                  '<script type="text/javascript">\n' +\
                  '$(document).ready(function(){\n' + \
                  'var instance = new Mark(document.querySelector("body"));\n' + \
                  'instance.unmark({done: function(){\n' + \
                  'var url = document.URL;\n' +\
                  'var key = decodeURIComponent(url.split("=")[1]);\n' +\
                  'console.log(key);\n' + \
                  'instance.mark(key) }})\n' +\
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
    print(len(paragraph_list_sorted))
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
            fname = outfile + '\\' + fname + '.html'
            print(fname, current_index)
            with open(fname, "w") as f:
                f.write(html_header)
                f.write(''.join(htmls))
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
                print(os.path.join(root, file))
                if("_files" not in str(root)):
                    parse_file(os.path.join(root, file), out_path)
    #input_files = [f for f in os.listdir(in_path) if os.path.isfile(os.path.join(in_path, f)) and f.endswith(".htm")]
    #for input_file in input_files:
    #    parse_file(os.path.join(in_path, input_file), out_path)

if __name__ == "__main__":
    rootpath = "C:\\3gpp_search_engine\\3gpp_search_engine_web"  # 获取上级路径
    in_Path = rootpath + "\\specs\\spec_htms"
    out_Path = rootpath + "\\parsed_htmls"
    main(in_Path, out_Path)