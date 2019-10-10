import lxml.etree as etree
import argparse
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
    html_header = html_header + "<body lang=EN-US link=blue vlink=purple style='tab-interval:14.2pt'>"
    html_end = "</body>"

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
                f.write(html_end)
                f.close()
            htmls.clear()
            htmls.append(paragraph)
            current_index = current_index + 1
        else:
            htmls.append(paragraph)

def main(in_path, out_path):
    input_files = [f for f in os.listdir(in_path) if os.path.isfile(os.path.join(in_path, f)) and f.endswith(".htm")]
    for input_file in input_files:
        parse_file(os.path.join(in_path, input_file), out_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="extract paragraph htmls")
    parser.add_argument("--input", required="true")
    parser.add_argument("--output", required="true")
    args = parser.parse_args()
    main(args.input, args.output)