import requests,json
import os
import sys
sys.path.insert(0, '..')          # import local sppclient, not global under user site package
import time

from optparse import OptionParser
import spplib.sdk.client as client
import spplib.cli.util as spputil


from spp_cleanup import cleanup_log
import traceback

def set_configuration():
    spp_username = None
    spp_password = None
    spp_url= None
    if(options.username is not None):
        spp_username = options.username
    else:
        if(spp_username is None):
            try:
                spp_username = os.environ.get("SPPUSER")
            except:
                print('Missing Username for Spectrum Protect Plus')
                print("Invalid input, use -h switch for help")
                sys.exit(1)

    if(options.password is not None):
        spp_password = options.password
    else:
        if(spp_password is None):
            try:
                spp_password = os.environ.get("SPPPASS")
            except:
                print('Missing Password for Spectrum Protect Plus')
                print("Invalid input, use -h switch for help")
                sys.exit(1)

    if(options.host is not None):
        spp_host = options.host
        spp_url = 'https://' + spp_host
    else:
        if(spp_url is None):
            try:
                spp_host = os.environ.get("SPPHOST")
                spp_url = 'https://' + spp_host
            except:
                print('Missing valid URL to Spectrum Protect Plus')
                print("Invalid input, use -h switch for help")
                sys.exit(1)

    return(spp_url,spp_host,spp_username,spp_password)

def session_start(spp_url, spp_username, spp_password):
    print(spp_url)
    try:
        session = client.SppSession(spp_url, spp_username, spp_password)
        session.login()
    except requests.exceptions.HTTPError as err:
        print("HTTP Error: {0}".format(err))
        print("exiting ...")
        sys.exit(1)
    except:
        print("unknown ERROR: ", sys.exc_info()[0])
        print("exiting ...")
        sys.exit(1)

    return session

def get_alerts(session):
    try:
        ''' the dictionary qsp contains the filters, sort statements and others like pageSize'''
        qsp = {}
        if options.sort is not None:
            if options.sort.upper() == "DESC":
                qsp['sort'] = '[{"property": "last", "direction": "DESC"}]'
            else:
                qsp['sort'] = '[{"property": "last", "direction": "ASC"}]'
        else:
            qsp['sort'] = '[{"property": "last", "direction": "ASC"}]'


        qsp['pageSize'] = 10000       # if set too small the number of returned results is incorrect and does not match the timeframe

        queryResult = client.SppAPI(session, '').get(path='/api/endeavour/alert/message', params=qsp)
        #queryResult = client.SppAPI(session, '').get(path='/api/endeavour/alert/message')
    except requests.exceptions.HTTPError as err:
        print("HTTP Error: {0}".format(err))
        spputil.get_error_details(err)
        print("exiting ...")
        sys.exit(1)
    except:
        print("other ERROR: ", traceback.print_exc())
        print("exiting ...")
        sys.exit(1)

    return queryResult

def format_alert_list(myQueryResult):
    #spputil.remove_links(myQueryResult)
    print()
    alert_fmt = "  {:<19.19s} | {:<6.6s} | {:<5s} | {:s}"
    print(alert_fmt.format("   last occurance", "Type", "ackn", "description"))
    print("  " + "-" * 120)
    for alert in myQueryResult['alerts']:
        msg=alert['message']
        acknowledged=str(alert['acknowledged'])
        type=alert['type']
        displayMsg = True

        lastOccurance=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(alert['last']/1000))

        if options.type is not None:
            if options.type.upper() != type:
                displayMsg = False

        if options.ack is not None:
            if options.ack.upper() != acknowledged.upper():
                displayMsg = False

        if options.timeframe is not None:
            timeframems = int(options.timeframe) * 60 * 60 * 1000
            starttime = int(round(time.time() * 1000)) - timeframems
            if alert['last'] < starttime:
                displayMsg = False

        if options.search is not None:
            if options.search.upper() not in msg.upper():
                displayMsg = False

        if displayMsg == True:
            print(alert_fmt.format(lastOccurance, type, acknowledged, msg))

def save_to_file(spp_host, data):
    try:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = "spp_log_{}_{}.log".format(spp_host, timestamp)
        path = "./logs"
        fullname = path + '/' + filename
        print('Write output to file: ' + fullname)
        f = open(fullname, "w+")
        f.write(str(data))
        f.close()
        return (fullname)
    except IOError as e:
        print('Could write the data to file...')
        print('Error: ' + str(e))

def s3_upload(filename):
    # Here are we uploading data to IBM Cloud Object Storage.
    import s3
    import subprocess
    subprocess.call('python s3.py --upload --filename {filename}'.format(**locals()), shell=True)

def add_time(t):
    global last_time
    t_delta=t
    #print(type(t))
    t_delta= t-last_time
    #t_delta = (last_time-t).astype('timedelta64[m]')
    last_time = t
    print(t_delta)
    return t_delta

def format_output(myQueryResult):
    import pandas as pd
    from pandas.io.json import json_normalize
    import json
    #the_mess1 = 'Log backup failed for database [WideWorldImporters] on instance [SQL2016]. An exception occurred while executing a Transact-SQL statement or batch.. Error: 0x80131501'
    the_mess1 = 'Log backup failed for database [AdventureWorks2014] on instance [SQL2016]. An exception occurred while executing a Transact-SQL statement or batch.. Error: 0x80131501'
    dataset = json_normalize(myQueryResult['alerts'])
    dataset['_unitLevel'] = dataset['initMessageParams'].apply(lambda x: 'Foo' if x == None else x[0])
    dataset['_lastSeen'] = dataset.apply(lambda row: add_time(row['alertTime']) if row['message'] == the_mess1 else 0, axis=1)
    dataset_filter = dataset[['acknowledged', 'alertTime', 'category', 'categoryDisplayName', 'count', 'dataSource', 'expired', 'expiresAt', 'first', 'initMessageParams', 'initialMessage', 'jobSessionId', 'last', 'message', 'messageName', 'messageParams', 'name', 'retention', 'status', 'statusDisplayName', 'storageId', 'unique', '_unitLevel', '_lastSeen']]
    #json_dataset = dataset_filter.to_json()

    dataset_filter_last_line = dataset_filter[-3:]
    #dataset_header = dataset.cloumns[['acknowledged', 'alertTime', 'category', 'categoryDisplayName', 'count', 'dataSource', 'expired', 'expiresAt', 'first', 'initMessageParams', 'initialMessage', 'jobSessionId', 'last', 'message', 'messageName', 'messageParams', 'name', 'retention', 'status', 'statusDisplayName', 'storageId', 'unique', '_unitLevel', '_lastSeen']]
    json_dataset = dataset_filter_last_line.to_json(r'./data.csv', orient='split')
    print('#' * 100)
    print(json_dataset)
    print('#' * 100)

def main():
    if(options.uploadOnly and options.filename):
        s3_upload(options.filename)

    else:
        spp_url, spp_host, spp_username, spp_password = set_configuration()
        session = session_start(spp_url, spp_username, spp_password)
        myQueryResult = get_alerts(session)
        if(options.test):
            format_alert_list(myQueryResult)

        if(options.lastLine):
            if len(myQueryResult) > 0:
                format_output(myQueryResult)
            else:
                Print('No Data')

        else:
            saved_file = save_to_file(spp_host, myQueryResult)
            cleanup_log(saved_file)
            if options.upload:
                s3_upload(saved_file)


        session.logout()

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--user", dest="username", help="SPP Username")
    parser.add_option("--pass", dest="password", help="SPP Password")
    parser.add_option("--host", dest="host", help="SPP Host, (ex. 172.20.49.49)")
    parser.add_option("--sort",  dest="sort", help="sort order: DESC or ASC ")
    parser.add_option("--test", dest="test", help="Use --test yes to print data in your screen instead of saving data to file")
    parser.add_option("--upload", dest="upload", help="Upload the file direct to S3 Storage")
    parser.add_option("--upload-only", dest="uploadOnly", help="Use this to only upload all logs")
    parser.add_option("--filename", dest="filename", help="Upload a dedicated file")
    parser.add_option("--last-line", dest="lastLine", help="Only collect the latest line from the log")
    (options, args) = parser.parse_args()
    main()
