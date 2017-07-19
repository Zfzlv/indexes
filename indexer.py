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
from es_helper import Es


logging.basicConfig()
logging.getLogger().setLevel(logging.ERROR)


class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)


class bcolors:
    header = '\033[95m'
    okblue = '\033[94m'
    okgreen = '\033[92m'
    warning = '\033[93m'
    fail = '\033[91m'
    endc = '\033[0m'

    def disable(self):
        self.header = ''
        self.okblue = ''
        self.okgreen = ''
        self.warning = ''
        self.fail = ''
        self.endc = ''


def processDoc(row, **kwargs):
    verbose = kwargs['verbose']
    stemInnerUnicode = row['stem_inner'].decode('utf8')
    stemInnerUnicode = rules.clean(stemInnerUnicode)
    originUnicode = row['origin'].decode('utf8') if row['origin'] else ""
    return stemInnerUnicode, originUnicode


def index(args):

    # init arguments
    # args = parse_args.parse()
    args['idName'] = 'id'
    dbHost = args['host']
    user = args['user']
    passwd = args['password']
    db = args['db']
    startId = args['start']
    endId = args['end']
    # esUrl = args['esUrl']
    esHost = args['es_host']
    allDataFlag = args['all']
    mod = args['mod']
    forceIndex = args['force_index']
    deleteFlag = args['delete']
    verbose = args['verbose']
    esIndex = args['index']
    esType = args['type']

    indexFlagList = map(lambda x: int(x), args['index_flag'].split(','))

    # print(indexFlagList)


    # init mysql
    curClass = MySQLdb.cursors.SSDictCursor
    connUpdate = MySQLdb.connect(host = dbHost, user = user, passwd = passwd, init_command = "set names utf8", cursorclass = curClass)
    connUpdate.select_db(db)
    cursorUpdate = connUpdate.cursor()


    # init variables
    ids = []
    batchData = []
    bulkSize = 50

    print str(verbose)+"==="+"\n"
    esHelper = Es(esHost, verbose)
    es = esHelper.getEs()

    kwargs = {}
    kwargs['verbose'] = verbose
    kwargs['es'] = es
    kwargs['esIndex'] = esIndex
    kwargs['esType'] = esType

    if allDataFlag:
        promote = 'Caution! It will %s all the questions in the required scope. Press anything to continue' % \
                  ('delete' if deleteFlag else 'index')
        sys.stderr.write(bcolors.warning + promote + bcolors.endc)
        raw_input()

    # mysql data loop
    for row in loop.loop(args):
        state = ''
        id = int(row['id'])
        docExists = es.exists(id=id, index=esIndex, doc_type=esType)
        row['isIndexed'] = row['status'] if 'status' in row else row['isIndexed']
        if allDataFlag:
            if deleteFlag:
                state = 'mayDelete'
            else:
                state = 'mayIndex'
        else:
            if deleteFlag:
                # if row['isIndexed'] == 0 or row['isIndexed'] == 1:
                if row['isIndexed'] in indexFlagList:
                    continue

            if row['isIndexed'] in indexFlagList:
                state = 'mayIndex'
            else:
                state = 'mayDelete'
            # if row['isIndexed'] != 0 and row['isIndexed'] != 1:
            #     state = 'mayDelete'
            # else:
            #     state = 'mayIndex'


        if state == 'mayDelete':
            if docExists:
                if verbose >= 1:
                    print str(id) + ' will be deleted!'
                esAction = esHelper.getEsAction(esIndex, esType, id)
                esAction['stem_search'] = ""
                esAction['_op_type'] = 'delete'
                batchData.append(esAction)
            else:
                if verbose >= 1:
                    print str(id) + ' already deleted!'
        elif state == 'mayIndex':
            if verbose >= 1:
                print str(id) + ' maybe indexed!'
            stemSearch, origin = processDoc(row, **kwargs)
            if stemSearch is not False:
                if docExists == False or forceIndex:
                    state = 'index'
                else:
                    doc = es.get(id=id, index=esIndex, doc_type=esType)
                    if doc['_source']['stem_search'] != stemSearch or \
                       not 'origin' in doc['_source'] or \
                       doc['_source']['origin'] != origin:
                        state = 'index'

            if docExists and verbose >= 1:
                print str(id) + " exists!"

            if state == 'index': 
                esAction = esHelper.getEsAction(esIndex, esType, id)
                esAction['stem_search'] = stemSearch
                esAction['origin'] = origin
	        	
                esAction['length_answer'] = row['length_answer']
                esAction['length_hint'] = row['length_hint']
                esAction['length_remark'] = row['length_remark']
                esAction['empty_answer'] = row['empty_answer']
                esAction['empty_hint'] = row['empty_hint']
                esAction['empty_remark'] = row['empty_remark']
                esAction['count_imgs_stem'] = row['count_imgs_stem']
                esAction['tiku_source'] = 1
	        
                if (row['subject']):
                    if (row['subject'].find('语文') != -1):
                        # esAction['_analyzer'] = 'ik_no_formula';
                        esAction['subject'] = u'语文';
                    elif (row['subject'].find('数学') != -1):
                        esAction['subject'] = u'数学';
                    elif (row['subject'].find('物理') != -1):
                        esAction['subject'] = u'物理';
                    elif (row['subject'].find('化学') != -1):
                        esAction['subject'] = u'化学';
                    elif (row['subject'].find('英语') != -1):
                        esAction['subject'] = u'英语';
                    elif (row['subject'].find('历史') != -1):
                        esAction['subject'] = u'历史';
                    elif (row['subject'].find('地理') != -1):
                        esAction['subject'] = u'地理';
                    elif (row['subject'].find('生物') != -1):
                        esAction['subject'] = u'生物';
                    elif (row['subject'].find('政治') != -1):
                        esAction['subject'] = u'政治';
                    else:
                        esAction['subject'] = u'其他';
                else:
                    esAction['subject'] = u'其他';

                batchData.append(esAction)
                if verbose >= 1:
                    print str(id) + ' will be indexed!'

                if row['isIndexed'] == 0:
                    ids.append((id,))

        if len(batchData) == bulkSize:
            # elasticsearch.helpers.streaming_bulk(es, batchData)
            esHelper.bulk(batchData)
            batchData = []
            if verbose >= 1:
                print 'bulk action'

        # update isIndexed field
        if len(ids) == bulkSize:
            cursorUpdate.executemany("""
                UPDATE questions SET isIndexed = 1 WHERE id=%s
            """, ids)
            connUpdate.commit()
            ids = []
            if verbose >= 1:
                print 'update database'

        connUpdate.ping()

    if len(batchData) != 0:
        esHelper.bulk(batchData)
        if verbose >= 1:
            print 'bulk action'
    if not deleteFlag:
        if ids:
            if verbose >= 1:
                print 'ids size: ', len(ids)
            cursorUpdate.executemany("""
                UPDATE questions SET isIndexed = 1 WHERE id=%s
            """, ids)
            connUpdate.commit()
            if verbose >= 1:
                print 'update database'
    cursorUpdate.close()
    connUpdate.close()


if __name__ == '__main__':

    args = parse_args.parse()
    index(args)
