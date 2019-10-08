import lxml.etree as etree
import argparse
import re

def get_keys(content):
    key_list = []
    dom = etree.HTML(content)
    h1_keys = dom.xpath('/html/body//h1')
    h2_keys = dom.xpath('/html/body//h2')
    h3_keys = dom.xpath('/html/body//h3')
    for h1_key in h1_keys:
        key = ''.join(h1_key.itertext()).replace("\n", " ").replace("\xa0", " ")
        keys = key.split()
        if len(keys) > 1:
            key = (keys[0], re.sub(keys[0], '', key).strip())
        else:
            key = (0, key)
        key_list.append(key)
    for h2_key in h2_keys:
        key = ''.join(h2_key.itertext()).replace("\n", " ").replace("\xa0", " ")
        keys = key.split()
        if len(keys) > 1:
            key = (keys[0], re.sub(keys[0], '', key).strip())
        else:
            key = (0, key)
        key_list.append(key)
    for h3_key in h3_keys:
        key = ''.join(h3_key.itertext()).replace("\n", " ").replace("\xa0", " ")
        keys = key.split()
        if len(keys) > 1:
            key = (keys[0], re.sub(keys[0], '', key).strip())
        else:
            key = (0, key)
        key_list.append(key)
    print(key_list)
    return key_list

def sort_key_list(paragraph_list_sorted, key_list):
    print("sort_key_list\n")
    print(len(paragraph_list_sorted), len(key_list))
    key_list_sorted = []
    for paragraph in paragraph_list_sorted:
        for key in key_list:
            if str(key[0]) in paragraph and str(key[1].split("(")[0].split('"')[0]) in paragraph:
                key_list_sorted.append(key)
            elif key[0] == 0 and str(key[1]) in paragraph:
                key_list_sorted.append(key)
            # ('5.4.2.1', 'PDN GW initiated bearer modification with bearer QoS update')
            elif len(str(key[0]).split('.')) == 4:
                if str(key[0])[:-2] in paragraph and str(key[1].split("(")[0].split('"')[0]) in paragraph:
                    key_list_sorted.append(key)
    print(key_list_sorted)
    for key in key_list:
        if key not in key_list_sorted:
            print(key)
    return key_list_sorted

def main(infile, outfile):
    print(infile)
    with open(infile) as f:
        content = f.read()

    key_list = get_keys(content)
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

    key_list_sorted = sort_key_list(paragraph_list_sorted, key_list)

    current_index = 0
    htmls = []
    print(len(key_list_sorted))
    print(key_list_sorted)
    print(len(paragraph_list_sorted))
    print(paragraph_list_sorted)
    print(len(paragraphs))
    for paragraph in paragraphs:
        if current_index == len(paragraph_list_sorted) -1:
            break
        elif paragraph.replace("\n", " ") == paragraph_list_sorted[current_index]:
            htmls.clear()
            htmls.append(paragraph)
        elif paragraph.replace("\n", " ") == paragraph_list_sorted[current_index+1]:
            #fname = str(key_list_sorted[current_index][0]) + "-" + str(key_list_sorted[current_index][1].replace(" ", "_"))
            fname = str(key_list_sorted[current_index][0])
            fname = outfile + '/' + fname + '.html'
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="extract paragraph htmls")
    parser.add_argument("--input", required="true")
    parser.add_argument("--output", required="true")
    args = parser.parse_args()
    main(args.input, args.output)