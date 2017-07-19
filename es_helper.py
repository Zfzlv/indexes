# -*- coding: utf-8 -*-

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from elasticsearch.client import IndicesClient
import elasticsearch
import logging
import sys, os


class Es(object):
    def __init__(self, esHost, verbose):
        # init es
        self.esBulkTimeout = 60

        """
        self.es = Elasticsearch(
            esHost,
            # sniff before doing anything
            sniff_on_start=True,
            # refresh nodes after a node fails to respond
            sniff_on_connection_fail=True,
            # and also every 60 seconds
            sniffer_timeout=60,
            # urlopen timeout
            timeout=self.esBulkTimeout
        )
        """

        #self.es = Elasticsearch([{'host': '10.10.3.236', 'port': 9200}],timeout=60, sniff_on_start=False)
        self.es = Elasticsearch([{'host': '10.10.42.201', 'port': 9200}])
        """
        10.10.3.236

10.10.18.249

10.10.194.162
10.10.49.91

10.10.26.16

10.10.42.201
        """
        # config logger
        if verbose >= 2:
            logLevel = logging.DEBUG
        else:
            logLevel = logging.ERROR
        # logging.basicConfig(filename = os.path.join(os.getcwd(), 'es.log'))
        logger = logging.getLogger('elasticsearch')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        esLog = logging.FileHandler(os.path.join(os.getcwd(), 'es.log'))
        esLog.setLevel(logLevel)
        esLog.setFormatter(formatter)
        logger.addHandler(esLog)

        esLogger = logging.getLogger('elasticsearch.trace')
        esTraceLog = logging.FileHandler(os.path.join(os.getcwd(), 'es-trace.log'))
        esTraceLog.setFormatter(formatter)
        esLogger.addHandler(esTraceLog)
        # logging.basicConfig(filename = os.path.join(os.getcwd(), 'es-trace.log'))
        # logger = logging.getLogger('elasticsearch.trace')


    def getEs(self):
        return self.es


    def getEsAction(self, esIndex, esType, id):
        esActionTemplate = {
            '_op_type': 'index',
            '_index': esIndex,
            '_type': esType,
            # '_analyzer': 'ik',
            '_id': id,
            # 'stem_search': str,
            'id': id
        }
        return esActionTemplate
        # esAction = copy.deepcopy(esActionTemplate)
        # source = {
        #     '_id': id,
        #     'stem_search': stripStr,
        #     'id': id
        # }
        # esAction.update(source)

    def bulk(self, batchData):
        #elasticsearch.helpers.bulk(self.es, batchData, timeout=self.esBulkTimeout)
        elasticsearch.helpers.bulk(self.es, batchData)

    def analyze(self, index, body, analyzer):
        
        esIndexClient = IndicesClient(self.es)
        analysisResult = esIndexClient.analyze(index=index, body=body, analyzer=analyzer)
        return analysisResult


if __name__ == '__main__':
    esHelper = Es('wl-test1', 1)
    body = u"""
    """
    # body = u"min～10min只改变了某一条件"
    analysisResult = esHelper.analyze('question_bank', body, 'ik_smart')
    print analysisResult
