# -*- coding: utf-8 -*-

import subprocess
import os
import base64
import re
import magic
import mimetypes
from enum import IntEnum,auto,unique
from bs4 import element,BeautifulSoup

fnameGenerator = None

def call_soffice(args):
    p = subprocess.Popen(["soffice"]+args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    _,stderr = p.communicate()
    if p.returncode != 0 or stderr[:7] == b'Error: ':
        return 1
    return 0

def libre_convert_doc_to_html(doc):
    output_html_dir = os.path.dirname(os.path.dirname(doc)) + "/html"
    args=['--convert-to','html','--outdir',output_html_dir,doc]
    call_soffice(args)

def resetFnameGenerator():
    global fnameGenerator
    fnameGenerator = Counter()

def extract_embed_image(embedImage, outdir):
    # Convert base64 encoded images into file.
    # Return filename
    # If the embeded image is Starview Metadata, convert it to svg
    if not (embedImage.startswith('data:image/')):
        return None
    _,rest = embedImage[11:].split(';',maxsplit=1)
    if not (rest.startswith('base64,')):
        return None
    data = base64.b64decode(rest[7:])
    path = saveFile(data, outdir, autoExt=True)
    _,ext = os.path.splitext(path)
    if ext in ['.gif', '.jpg', '.png', '.svg', '.jpe', '.ico']:
        # Common image types supported by most web browsers
        return path
    elif ext in ['bmp']:
        newPath = trimCompressImg(path) # Produces a .png file
        os.remove(path)
        return newPath
    else:
        newPath = convert_octet_stream_to_img(path, outdir) # Produces .bmp .png files
        os.remove(path)
        return newPath

def convert_octet_stream_to_img(i, outdir):
    f,ext = os.path.splitext(os.path.basename(i))
    if ext in ['bmp', 'png']:
        # Prevent overwrite
        return i
    args=['--convert-to','svg','--outdir',outdir,i]
    if not call_soffice(args):
        # Successful call
        # Find the correct Viewbox value in svg file
        return trimSvg(os.path.join(outdir, f+'.svg'))
    else:
        # Fall-back to png
        args=['--convert-to','bmp','--outdir',outdir,i]
        call_soffice(args)
        tmpBmp = os.path.join(outdir, f+'.bmp')
        path = trimCompressImg(tmpBmp)
        os.remove(tmpBmp)
        return path

def saveFile(data, outdir, autoExt = False, ext = None):
    try:
        os.makedirs(outdir)
    except FileExistsError:
        pass
    basenameNoExt = fnameGenerator.__next__()
    if ext is not None:
        basename = basenameNoExt + ext
    elif autoExt:
        basename = basenameNoExt + determineExt(data)
    path = os.path.join(outdir, basename)
    with open(path, 'wb') as f:
        f.write(data)
    return path


def trimSvg(path):
    with open(path, 'rb') as f:
        soup = BeautifulSoup(f, features='xml')
    svg = soup.find('svg', viewBox=True)
    # Fix format
    try:
        svg['xmlns'] = svg.attrs.pop('xmlns:')
    except KeyError:
        pass
    bBox = soup.find('rect', attrs={"class":"BoundingBox"})
    svg['viewBox'] = ' '.join([bBox['x'], bBox['y'], bBox['width'], bBox['height']])
    with open(path,'wb') as fo:
        fo.write(soup.encode())
    return path

def trimCompressImg(oPath):
    # Trim and convert to .png
    im = Image.open(oPath).convert('RGB')
    box = PIL.ImageOps.invert(im).getbbox()
    im = im.crop(box)
    path = os.path.splitext(oPath)[0]+'.png'
    with open(path, 'wb') as fo:
        im.save(fo, format='png')
    return path

def determineExt(data):
    # Get extension from file's type
    mag_mime = magic.from_buffer(data,mime=True)
    mag = magic.from_buffer(data)
    if mag_mime.startswith('image/'):
        guessed_ext = mimetypes.guess_extension(mag_mime)
        if guessed_ext:
            return guessed_ext
        img_fmt = mag_mime[6:]
        if img_fmt == 'x-tga':
            return '.wmf'
        return '.' + re.findall(r'[a-z]+$', img_fmt)[0]
    if mag.startswith('Windows Enhanced Metafile (EMF) image data '):
        return '.emf'
    if mag.startswith('StarView MetaFile'):
        return '.svm'
    if mag == 'ms-windows metafont .wmf':
        return '.wmf'
    return None

@unique
class TocType(IntEnum):
    Clause = auto()
    Figure = auto()
    Table = auto()

def parseHeading(s):
    # Returns (TocType, num, text) or None
    s = s.replace('\xa0',' ').strip()
    l = s.lower().split(maxsplit=1)
    if len(l) < 2:
        return None
    return (TocType.Clause, l[0], l[-1])

def buildTagStr(t, num):
    num = num.lower()
    # Stringify
    if t == TocType.Clause:
        t = "CLA"
    elif t == TocType.Figure:
        t = "FIG"
    elif t == TocType.Table:
        t = "TAB"
    return '__'.join(["_REF" , t, num])

def buildIndexRef(series, docNum, ver, t, num):
    # Stringify
    if t == TocType.Clause:
        t = "Clause"
    elif t == TocType.Figure:
        t = "Fig"
    elif t == TocType.Table:
        t = "Tab"
    spec = '.'.join([series, docNum])
    return ' '.join([spec, ver, t, num])

def Counter(start = 0):
    while True:
        yield str(start)
        start += 1

## Determine a list of elements around the given one
def lookAroundCand(obj, Range):
    def getNeighbor(obj, f):
        if type(obj) is not element.Tag:
            return None
        t=f(obj)
        while t is not None and t.getText().strip() == '':
            t=f(t)
        if t is not None:
            return t
        p=obj.parent
        if p is not None and p.name != 'body':
            return getNeighbor(p, f) # Recursive call
        return None
    prv=element.Tag.find_previous_sibling
    nxt=element.Tag.find_next_sibling
    p, n = obj, obj
    p_cnt, n_cnt = 0, 0
    loop=True
    while loop:
        loop=False
        if (p is not None) and (p_cnt < Range):
            p=getNeighbor(p, prv)
            p_cnt+=1
            if p is not None:
                yield p
                loop=True
        if (n is not None) and (n_cnt < Range):
            n=getNeighbor(n, nxt)
            n_cnt+=1
            if n is not None:
                yield n
                loop=True

def copyR(src, dst):
    # Hard to tune shutil
    # cp has the exact behavior we want
    p = subprocess.Popen(["cp", "-r", src, dst])
    _,stderr = p.communicate()
    if p.returncode:
        return stderr
    return None

def compareVer(a, b):
    a = int(a, base=32)
    b = int(b, base=32)
    if a < b:
        return -1
    elif a == b:
        return 0
    else:
        return 1

def slice_html(htmlFile):
    slice_html_path = os.path.dirname(os.path.dirname(htmlFile)) + '/slice_html'
    spec_html = './' + os.path.basename(htmlFile)
    zip_file = '../zip/' + os.path.basename(htmlFile).split('.')[0] + '.zip'
    ### Read ###
    with open(htmlFile, 'rb') as fi:
        soup = BeautifulSoup(fi, 'html.parser')
    # Sliced htmls
    body = soup.find('body')
    for i in soup.findAll(re.compile(r'^h\d+$')):
        h = parseHeading(i.getText())
        if not h:
            continue
        tocType,num,_ = h
        if tocType != TocType.Clause or 3 < len(num.split('.')):
            continue
        sSoup = BeautifulSoup(features='html.parser')
        sSoup.append(BeautifulSoup(str(soup.find('head')), 'html.parser'))
        sBody = sSoup.new_tag('body', attrs=body.attrs.copy())
        sSoup.append(sBody)
        # Link to full document
        title = sSoup.new_tag('h1')
        title.append(buildLink(os.path.basename(htmlFile).split('.')[0], spec_html, sSoup))
        sBody.append(title)
        # doload zip file
        title = sSoup.new_tag('h3')
        title.append(buildLink('Download', zip_file, sSoup))
        sBody.append(title)
        # Copy
        lst = [i]
        for n in i.nextSiblingGenerator():
            if n.name == i.name:
                break
            lst.append(n)
        lst = [str(i) for i in lst]
        sBody.append(BeautifulSoup(''.join(lst), 'html.parser'))
        sHtmlPath = os.path.join(slice_html_path, "CLA_{}.html".format(num))
        with open(sHtmlPath, 'wb') as fo:
            fo.write(sSoup.encode())

def buildLink(string, src, soup):
    a = soup.new_tag('a', href=src)
    a.string = string
    return a
