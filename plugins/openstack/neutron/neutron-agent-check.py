#!/usr/bin/python
#
# Created By Bruce Martins
# email: bmartins At gmail Dot com
# Neutron Agent Status check, doesn't require the neutron python client 
# and can be run remotely
#
# loosely  based on neutron-agent-status.py by
# Brian Clark <brian.clark@cloudapt.com>
#
# Released under the same terms as Sensu (the MIT license);
# see LICENSE for details.
#
# This assumes the API endpoints for auth and Neutron are the same versus pulling the endpoints publicurl
# I may change that later
#
import sys
import base64
import json
import logging
import argparse
import requests

STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3

#logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(description='Check OpenStack Neutron Agent status')
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
    url = args.auth_url + ':9696/v2.0/agents'
    header = {'content-type': 'application/json','X-Auth-Token': auth_token}
    request = requests.get(url, data=None, headers=header)
    response = json.loads(request.text)
    #print json.dumps(response, sort_keys = False, indent=4)
    arr = response['agents']     
    outer_dict = arr[0]
    inner_dict_alive = outer_dict["alive"]
    inner_dict_state = outer_dict["admin_state_up"]
    for item in arr:
        if item['alive'] == False and item['admin_state_up'] == False:
              exit_state = STATE_OK
              state_string = "OK"
              print "Neutron Agent down/down status: {state_str}.".format(state_str=state_string)
              sys.exit(exit_state)
              return 0
        
        elif item['alive'] == True and item['admin_state_up'] == False:
              exit_state = STATE_WARNING
              state_string = "WARNING"
              print "Neutron Agent up/disabled status: {state_str}.".format(state_str=state_string)
              sys.exit(exit_state)
              return 1
        
        elif item['alive'] == False and item['admin_state_up'] == True:
              exit_state = STATE_CRITICAL
              state_string = "CRITICAL"
              print "Neutron Agent status: {state_str}.".format(state_str=state_string)
              sys.exit(exit_state)
              return 2
        
        else:
              exit_state = STATE_OK
              state_string = "OK"
    print "Neutron Agent up/up status: {state_str}.".format(state_str=state_string)
    sys.exit(exit_state)


getNeutronAgentState(getAuthToken())
