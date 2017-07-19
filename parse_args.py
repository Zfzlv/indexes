import sys, os
import argparse
import getpass


def parse():
    print ' '.join(sys.argv)
    print ''
    parser = argparse.ArgumentParser(description='build index from databases of question_bank', add_help=False)
    parser.add_argument('--help', action='help')
    parser.add_argument('-h', '--host', help='the host of database')
    parser.add_argument('-u', '--user', required=True, help='user of databases')
    parser.add_argument('-p', '--password', required=True, const=None, nargs='?', help='password')
    parser.add_argument('db', default=None, nargs='?', help='database name')
    # parser.add_argument('--sql', help='custom the select query in which case other sql options such as startId will be ignored')
    parser.add_argument('--start', default=0, help='start id of questions')
    parser.add_argument('--end', default=0, help='end id of questions')
    parser.add_argument('--origin', default=None, help='origin field of questions')
    # parser.add_argument('-e', '--esUrl', help='url of es index. e.g. http://es1:9200/question_bank/questions')
    parser.add_argument('-e', '--es-host', nargs='+', help='host of es, e.g. es-test1 es-test2')
    parser.add_argument('--index', required=True, help='es index name')
    parser.add_argument('--type', required=True, help='es type name')
    parser.add_argument('--index-flag', default='0,1', help='numbers separated by comma, records whose isIndexed field in those numbers will be indexed')
    parser.add_argument('-a', '--all', action='store_true', help='index or delete all the records regardless of the isIndexed field')
    parser.add_argument('-m', '--mod', action='store', type=int, default=None, nargs=2,
                        metavar=('divisor', 'remainder'), help='only questions whose id gets the right mod value specified by the two arguments will be affected')
    parser.add_argument('--force-index', action='store_true', help='this will overwrite existing document in es')
    parser.add_argument('--delete', action='store_true', help='delete mode')
    parser.add_argument('-v', '--verbose', action='count', help='print some message')
    parser.add_argument('-w', '--worker-count', default=1, type=int, help='specify the count of worker processes')
    parser.add_argument('-f', '--file', default=None, help='fetch docId from the specified file, this will ignore other settings like start and end')
    parser.add_argument('-i', '--id-isIndexed', default=None, help='table that you want to get ID-IsIndexed')

    args = parser.parse_args()
    args = vars(args)

    db = args['db']
    passwd = args['password']

    # if db or passwd is None:
    if db is None:
        if passwd is None:
            print 'db name is not found'
            sys.exit(0)
        else:
            db = passwd
            passwd = getpass.getpass('db password:')
    if passwd is None:
        passwd = getpass.getpass('db password:')
    
    args['db'] = db
    args['password'] = passwd

    return args
