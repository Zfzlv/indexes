# -*- coding: utf-8 -*-

import pprint
import logging
import urllib
import argparse
import sys, os
import re
import copy
import json, requests
import getpass
import MySQLdb
import MySQLdb.cursors
from lxml import html
from lxml.html.clean import Cleaner
from HTMLParser import HTMLParser
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import elasticsearch
import phoneticSymbol
import esIndexer


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        if len(self.fed) == 0:
            pass
        # if re.match("[A-Za-z0-9]", d[0]):
        #     d = ' ' + d
        # if re.match("[A-Za-z0-9]", d[-1]):
        #     d += ' '
        else:
            last = self.fed[-1]
            if (re.match("[A-Za-z]", last[-1]) and re.match("[A-Za-z]", d[0]) or
                (re.match("[0-9]", last[-1]) and re.match("[0-9]", d[0]))):
                d = ' ' + d
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)


def strip_tags(htmlData):
    s = MLStripper()
    s.feed(htmlData)
    return s.get_data()


def processDoc(row, **kwargs):
    verbose = kwargs['verbose']
    stemInnerUnicode = row['stem_inner'].decode('utf8')
    stemInnerUnicode = esIndexer.removeScriptAndStyle(stemInnerUnicode)
    stemInnerUnicode = esIndexer.removeTags(stemInnerUnicode)
    stemInnerUnicode = esIndexer.removePhoneticSymbol(stemInnerUnicode)
    stemRemovePlusAndMinus = esIndexer.removePlusAndMinus(stemInnerUnicode)
    if stemRemovePlusAndMinus == stemInnerUnicode:
        return None
    else:
        return stemRemovePlusAndMinus


if __name__ == '__main__':

    esIndexer.index(processDoc)
