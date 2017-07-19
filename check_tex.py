# -*- coding: utf-8 -*-

import argparse
import tex
import base64

parser = argparse.ArgumentParser()
parser.add_argument("text", help="text")
args = parser.parse_args()

text = base64.b64decode(args.text)
try:
    text = tex.parse(text)
    print 'pass'
except:
    print 'error'
    pass
