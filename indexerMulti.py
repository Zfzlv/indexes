# -*- coding: utf-8 -*-

import pprint
import logging
import urllib
import sys, os
import re
import copy
import json, requests
import MySQLdb
import MySQLdb.cursors
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import elasticsearch
import parse_args
import rules
import loop
import indexer
from es_helper import Es
from multiprocessing import Pool
from multiprocessing import Process


def f(args):
     indexer.index(args)


if __name__ == '__main__':

    # multiprocessing
    args = parse_args.parse()
    workerCnt = args['worker_count']
    if workerCnt <= 0:
        print "worker processes can not be negative!"
    elif workerCnt == 1:
        args['mod'] = None
        Process(target=f, args=(args,)).start()
    else:
        for num in range(workerCnt):
            args['mod'] = [workerCnt, num]
            Process(target=f, args=(args,)).start()
