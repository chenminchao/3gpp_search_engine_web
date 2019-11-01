# -*- coding: utf-8 -*-

import re
import zipfile
import magic
import mimetypes
import subprocess
from enum import IntEnum,auto,unique

import bs4.element

from Tokenizer import RE_NUMBERING,W_CLAUSE,W_FIGURE,W_TABLE

def unzip(f, d):
    with zipfile.ZipFile(f, 'r') as ref:
        ref.extractall(d)

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
    if RE_NUMBERING.fullmatch(l[0]):
        return (TocType.Clause, l[0], l[-1])
    if l[0] in W_CLAUSE:
        guessedType = TocType.Clause
    elif l[0] in W_FIGURE:
        guessedType = TocType.Figure
    elif l[0] in W_TABLE:
        guessedType = TocType.Table
    else:
        return None
    l = l[1].split(maxsplit=1)
    l[0] = l[0].replace(':', '')
    if RE_NUMBERING.fullmatch(l[0]):
        return (guessedType, l[0], l[-1])
    return None

def buildTagStr(t, num):
    num = num.lower()
    # Stringify
    if t == TocType.Clause:
        t = "CLA"
    elif t == TocType.Figure:
        t = "FIG"
    elif t == TocType.Table:
        t = "TAB"
    return '__'.join(["__REF" , t, num])

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
        if type(obj) is not bs4.element.Tag:
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
    prv=bs4.element.Tag.find_previous_sibling
    nxt=bs4.element.Tag.find_next_sibling
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

def anti2txt(src, dst):
    # use antiword to convert doc to txt
    p = subprocess.Popen(['antiword', '-t', src, '>', dst])
    _,stderr = p.communicate()
    if p.returncode:
        return stderr
    return None
