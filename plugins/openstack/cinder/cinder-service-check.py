#!/usr/bin/python
#
# Created By Bruce Martins
# email: bmartins At gmail Dot com
# Cinder Agent Status check, doesn't require the cinder python client 
# and can be run remotely
#
# loosely  based on neutron-agent-status.py by
# Brian Clark <brian.clark@cloudapt.com>
#
# Released under the same terms as Sensu (the MIT license);
# see LICENSE for details.
#
import sys
import json
import logging
import argparse
import requests

STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3

#logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(description='Check OpenStack Cinder Service status')
parser.add_argument('--auth-url', metavar='URL', type=str, default='http://localhost',
                    required=False,
                    help='Keystone URL')
parser.add_argument('--username', metavar='username', type=str, default='admin',
                    required=False,
                    help='username for authentication')
parser.add_argument('--password', metavar='password', type=str, default='admin',
                    required=False,
                    help='password for authentication')
parser.add_argument('--tenant', metavar='tenant', type=str, default='admin',
                    required=False,
                    help='tenant name for authentication')
parser.add_argument('--region_name', metavar='region', type=str,
                    help='Region to select for authentication')
parser.add_argument('--bypass', metavar='bybass', type=str,
                    required=False,
                    help='bypass the service catalog and use this URL for Cinder API')

args = parser.parse_args()

def getAuthToken():
        header = {'content-type': 'application/json'}
        payload = {"auth": {"tenantName": args.tenant,"passwordCredentials": {"username": args.username,"password": args.password}}}
        request = requests.post(args.auth_url + ':5000/v2.0/tokens', data=json.dumps(payload), headers=header)
        response = json.loads(request.text)
        token = response.get("access").get("token").get("id")
        endpoint = response.get("access").get("token").get("tenant").get("id")
        return [token,endpoint] 

def getNeutronAgentState(token):
    tenantID = token[1]
    auth_token = token [0]
    url = args.auth_url + ':8776/v1/' + tenantID + '/os-services'
    header = {'content-type': 'application/json','X-Auth-Token': auth_token}
    request = requests.get(url, data=None, headers=header)
    response = json.loads(request.text)
    #print json.dumps(response, sort_keys = False, indent=4)
    arr = response['services']     
    outer_dict = arr[0]
    inner_dict_state = outer_dict["state"]
    inner_dict_status = outer_dict["status"]
    for item in arr:
        if item['state'] == 'down' and item['status'] == 'disabled':
              exit_state = STATE_OK
              state_string = "OK"
              print "Cinder status: {state_str}.".format(state_str=state_string)
              sys.exit(exit_state)
              return 0
        
        elif item['state'] == 'up' and item['status'] == 'disabled':
              exit_state = STATE_WARNING
              state_string = "WARNING"
              print "Cinder status: {state_str}.".format(state_str=state_string)
              sys.exit(exit_state)
              return 1
        
        elif item['state'] == 'down' and item['status'] == 'enabled':
              exit_state = STATE_CRITICAL
              state_string = "CRITICAL"
              print "Cinder status: {state_str}.".format(state_str=state_string)
              sys.exit(exit_state)
              return 2
        
        else:
              exit_state = STATE_OK
              state_string = "OK"
    print "Cinder status: {state_str}.".format(state_str=state_string)
    sys.exit(exit_state)


getNeutronAgentState(getAuthToken())
