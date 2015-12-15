#! /usr/bin/env python
#
#   Dome9 AWS Security Groups reporter, locker and unlocker
#   Use it to report on your multi-account, multi-regions AWS setups (in CSV / json format) 
#   and to lock (=move to 'Full Protection') or unlock (move to 'Read-only' mode) them.
#   See README file for instructions.
#      
#   Roy Feintuch <roy@dome9.com>
#   Copyright (c) 2015, Dome9 Security, Ltd. See LICENSE file
#
import argparse, json, requests, csv, sys, os
from requests.auth import HTTPBasicAuth

# Fix Python 2.x. vs 3 raw_input compatability
try: input = raw_input
except NameError: pass

def reporter(args):
    # Fetch data from Dome9 api
    resp = requests.get(api_end_point + 'cloudsecuritygroups?format=json', auth=HTTPBasicAuth(email, key))
    data = json.loads(resp.text)
    
    # Filter data according to user filter
    filtered = filter_data(args, data)
    
    # Output data as CSV 
    if(args.action == 'report'):    
        output = csv.writer(sys.stdout)
        output.writerow(data[0].keys())
        for entry in filtered:
            output.writerow(entry.values())
    
    if(args.action == 'report_json'):    
        print(json.dumps(filtered))
        
    if args.verbose:
        print('--- Stats ----')
        import datetime
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        print(args)
        print('Original data set: %d' % len(data))
        print('Filtered data set: %d' % len(filtered))
    
    return filtered
    
def filter_data(filter_args, data):
    filters = []
    if filter_args.vpc!=None:
        filters.append(lambda x: x['Vpc'] in filter_args.vpc)
    if filter_args.sgname != None:
        filters.append(lambda x: x['Name'] in filter_args.sgname)
    if filter_args.accid != None:
        filters.append(lambda x: x['CloudAccountExternalNumber'] in filter_args.accid)
    if filter_args.region != None:
        filters.append(lambda x: x['Region'] in filter_args.region)
    if filter_args.sgid != None:
        filters.append(lambda x: x['ExternalId'] in filter_args.sgid)
    
    pred = lambda x: all( f(x) for f in filters )    
    return [x for x in data if pred(x)]
    
if __name__ == "__main__":
    # --- Command line argument parsing ---
    parser = argparse.ArgumentParser(description='Query for security groups given some filter criteria')
    parser.add_argument('--sgname', nargs='+', help='Filter given list of security groups names (space delimited)', required=False)
    parser.add_argument('--sgid', nargs='+', help='Filter given list of security groups (aws) ids (space delimited)', required=False)
    parser.add_argument('--vpc', nargs='+', help='Filter given list of VPC ids. Will match all security groups in these VPCs', required=False)
    parser.add_argument('--accid', nargs='+', help='Filter given list of AWS account ids. Will match all security groups in these accounts', required=False)
    parser.add_argument('--region', nargs='+', help='Filter given list of regions. Will match all security groups in these regions', required=False)
    parser.add_argument('-v','--verbose', help='Prints additional statistics', action="store_true") 
    parser.add_argument('-a','--action',help='[report|report_json|lock|unlock]', required=True)
    parser.add_argument('-u','--user', help='Dome9 user name (your email)')
    parser.add_argument('-p','--apisecret', help='Your Dome9 api key. Found under settings.')
    parser.add_argument('--ack', help='Supress acknowledgement message before perfroming changes (recommended only for automated use-cases)',  action="store_true")
    args = parser.parse_args()
    
    email = args.user or os.getenv('d9_user')
    if not email:
        print("either provide --user parameter or d9_user environement variable")
        sys.exit() 
    key = args.apisecret or os.getenv('d9_api_sec')
    if not key:
        print("either provide --apisecret parameter or d9_api_sec environement variable")
        sys.exit()     
    
    api_end_point = 'https://api.dome9.com/v1/'
    # fetch security groups from Dome9 api
    sgs = reporter(args)
        
    if(args.action == 'lock' or args.action == 'unlock'):
        ack = args.ack or input('You are about to update (%s) %d security groups. Continue (y/n)?' % (args.action,len(sgs)))=='y'
        if not ack:
            print('Exiting without updating security groups.')
            sys.exit() 
        for sg in sgs:
            print('Updating sg: %s>%s>%s>%s (%s) ' % (sg['CloudAccountExternalNumber'], sg['Region'], sg['Vpc'] ,sg['Name'], sg['ExternalId']))
            url = api_end_point + 'cloudsecuritygroups/' +  sg['Id']
            isProtected = str(args.action == 'lock').lower()
            r = requests.put(url, data = "IsProtected=%s" % isProtected, auth=HTTPBasicAuth(email, key), headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"})
            
   