# -*- coding: utf-8 -*-

import pprint
import logging
import sys, os
import re
import getpass
import MySQLdb
import MySQLdb.cursors
import parse_args


#sqlQueryInId = 'select * from %s where %s in (%s)'

sqlQueryInId = 'select a.*,b.length_answer,length_hint,length_remark,empty_answer,empty_hint,empty_remark,count_imgs_stem from %s as a,questions_extra_length as b where a.%s in (%s) and a.id = b.id'

sqlQueryInId_union = 'select a.*,b.isIndexed as status from %s as a,%s as b where a.%s in (%s) and a.id = b.id'


def changeSql(sql, minId, idName):
    regMinId = idName + r'\s*>=\s*[0-9]+'
    subMinId = re.compile(regMinId, re.IGNORECASE)
    sql = subMinId.sub(idName + ' >= ' + str(minId), sql)
    return sql


def fetchData(cursorQuery, sqlQuery, table, idName , is_indexed):
    sqlQueryId = sqlQuery % idName
    cursorQuery.execute(sqlQueryId)
    rows = cursorQuery.fetchall()
    ids = ','.join(map(lambda x: str(x[idName]), rows))
    return fetchDataByIds(cursorQuery, ids, table, idName, is_indexed)


def fetchDataByIds(cursorQuery, ids, table, idName, is_indexed):
    if is_indexed:
       sqlQuery = sqlQueryInId_union % (table, is_indexed, idName, ids if ids else 'null')
       #print 'sqls:--'+sqlQuery+'\n'
       cursorQuery.execute(sqlQuery)
       rows = cursorQuery.fetchall()
       return rows
    else:
       sqlQuery = sqlQueryInId % (table, idName, ids if ids else 'null')
       cursorQuery.execute(sqlQuery)
       rows = cursorQuery.fetchall()
       return rows


def fetchIds(cursorQuery, sqlQuery, table, idName):
    sqlQueryId = sqlQuery % idName
    cursorQuery.execute(sqlQueryId)
    rows = cursorQuery.fetchall()
    ids = ','.join(map(lambda x: str(x[idName]), rows))


def loop(config):
    file = config['file'] if 'file' in config else None
    if file != None:
        for row in loopFile(config):
            yield row
    else:
        for row in loopDB(config):
            yield row


def loopDB(config):
    # init arguments
    dbHost = config['host']
    user = config['user']
    passwd = config['password']
    db = config['db']
    if 'table' in config: table = config['table']
    else: table = 'questions'
    startId = config['start'] if 'start' in config else 0
    endId = config['end'] if 'end' in config else 0
    origin = config['origin'] if 'origin' in config else None
    mod = config['mod'] if 'mod' in config else None
    verbose = config['verbose']
    deleteFlag = config['delete'] if 'delete' in config else False
    indexAll = config['all'] if 'all' in config else False
    idName = config['idName']
    is_indexed = config['id_isIndexed'] if 'id_isIndexed' in config else None

    rowLimit = 1000


    # init mysql
    curClass = MySQLdb.cursors.SSDictCursor
    connQuery = MySQLdb.connect(host = dbHost, user = user, passwd = passwd, init_command = "set names utf8", cursorclass = curClass)
    connQuery.select_db(db)
    cursorQuery = connQuery.cursor()


    # construct mysql query
    sqlSelect = 'select %s from ' + table + ' '
    if is_indexed:
        sqlSelect = 'select a.%s from ' + table + ' as a,'+is_indexed + ' as b '
    sqlWhere = 'where ' + idName + ' >= ' + str(startId) + ' '
    if is_indexed:
        sqlWhere = 'where a.' + idName + ' >= ' + str(startId) + ' '
    if endId != 0:
        if is_indexed:
            sqlWhere += "and a." + idName + " <= " + str(endId) + ' '
        else:
            sqlWhere += "and " + idName + " <= " + str(endId) + ' '
    if origin != None:
        if is_indexed:
            sqlWhere += "and a.origin = '" + origin + "' "
        else:
            sqlWhere += "and origin = '" + origin + "' "
    if mod != None:
        if is_indexed:
            sqlWhere += "and mod(a.%s,%s) = %s " % (idName, mod[0], mod[1])
        else:
            sqlWhere += "and mod(%s,%s) = %s " % (idName, mod[0], mod[1])
    # if deleteFlag:
    # #    sqlWhere += "and (isIndexed <> 0 and isIndexed <> 1) "
    #     pass
    # else:
    #     if indexAll:
    #         sqlWhere += "and (isIndexed = 0 or isIndexed = 1)"
    #     else:
    #         sqlWhere += "and isIndexed = 1 "
    sqlQuery = sqlSelect + sqlWhere
    if is_indexed:
        sqlQuery += " and a.%s = b.%s" % (idName,idName)

    # sqlQueryInId = 'select * from questions where ' + idName + ' in (%s)'

    print 'sql: ' + sqlQuery % '*'

    sqlQuery = sqlQuery + ' limit ' + str(rowLimit) + ' '

    rowCount = 0
    rows = fetchData(cursorQuery, sqlQuery, table, idName,is_indexed)
    #print 'too here'+'\n'

    # mysql data loop
    while True:
        for row in rows:
            rowCount += 1
            minId = row[idName]
            yield row
        if rowCount == rowLimit:
            if config['verbose'] >= 1:
                print row[idName]
            rowCount = 0
            sqlQuery = changeSql(sqlQuery, minId + 1, idName)
            rows = fetchData(cursorQuery, sqlQuery, table, idName,is_indexed)
        else:
            print 'too '+str(rowLimit)+'--'+str(rowCount)+'\n'
            break
    #print 'too here'+'\n'
    cursorQuery.close()
    connQuery.close()


def loopFile(config):

    dbHost = config['host']
    user = config['user']
    passwd = config['password']
    db = config['db']
    if 'table' in config: table = config['table']
    else: table = 'questions'
    mod = config['mod']
    file = config['file']
    idName = config['idName']
    is_indexed = config['id_isIndexed'] if 'id_isIndexed' in config else None

    # init mysql
    curClass = MySQLdb.cursors.SSDictCursor
    connQuery = MySQLdb.connect(host = dbHost, user = user, passwd = passwd, init_command = "set names utf8", cursorclass = curClass)
    connQuery.select_db(db)
    cursorQuery = connQuery.cursor()

    rowLimit = 100
    rowCount = 0
    lineNum = 1
    idList = []
    with open(file) as f:
        for line in f:
            if mod == None or lineNum % mod[0] == mod[1]:
                idList.append(line.strip("\n"))
                rowCount += 1
            lineNum += 1
            if rowCount == rowLimit:
                # print ",".join(idList)
                rows = fetchDataByIds(cursorQuery, ",".join(idList), table, idName, is_indexed)
                for row in rows:
                    yield row
                rowCount = 0
                idList = []
    if idList:
        # print ",".join(idList)
        rows = fetchDataByIds(cursorQuery, ",".join(idList), table, idName, is_indexed)
        for row in rows:
            yield row

    cursorQuery.close()
    connQuery.close()



if __name__ == '__main__':

    config = {
        'host': '127.0.0.1',
        'user': 'timuUser',
        'db': 'question_bank',
        'startId': 0,
        'endId': 200,
        'origin': '',
        'mod': 0,
        'verbose': 1,
        'delete': False,
        'all': True,
    }

    config = parse_args.parse()

    for row in loop(config):
        print row[idName]

