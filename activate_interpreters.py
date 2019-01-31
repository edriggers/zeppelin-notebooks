#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Activates all Interpreters for the Notebooks on the running Zeppelin instance.

The initial creation was done with the Standalone Zeppelin Docker project in
mind.  This would be run as follows inside the running container:

docker exec -it spliceserver /bin/bash
cd /opt/zeppelin/notebook
python activate_interpreters.py -z 'http://localhost:8090'
'''

import requests
import argparse
import os
import json
import mmap


__author__ = "Christopher Maahs"
__copyright__ = "Copyright 2019, Splice Machine"
__credits__ = ["Erin Driggers"]
__version__ = '0.0.1'

current_file_directory = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser(description="This script will activate interpreters on all Notebooks in the running Zeppelin instance")
parser.add_argument('-z', '--zeppelinUrl', dest='zeppelinUrl',
                    default='http://localhost:8080', help='Zeppelin url for example: http://localhost:8080')

parser.add_argument('-u', '--user', dest='user',
                    default="",
                    help='Zeppelin user if authentication enabled')

parser.add_argument('-p', '--password', dest='password',
                    default="",
                    help='Zeppelin password if authentication enabled')

args = parser.parse_args()

ZEPPELIN_URL=args.zeppelinUrl
USER=args.user
PASSWORD=args.password
authentication=True

if USER is None or USER == "":
    authentication=False

login_url = ZEPPELIN_URL + '/api/login'
list_url = ZEPPELIN_URL + '/api/notebook'
bind_url = ZEPPELIN_URL + '/api/notebook/interpreter/bind'

# These are the notebooks that are currently installed on Zeppelin
currentNotebookIds = {}
currentNotebookNames = {}
cookies=None

#
# Authenticate if necessary
#
if authentication is True:
    r = requests.post(login_url, data='userName=' + USER + "&password=" + PASSWORD)
    if r.status_code == 200:
        loginResponse = json.loads(r.text)
        cookies = r.cookies
        if cookies is None:
            print ('******* Unable to retrieve cookie ********')
            exit()
    else:
        print ('******* Authentication failed ********')
        exit()

if authentication is True and cookies is None:
    exit()


#
# Get the current notebooks on the Zeppelin cluster
#
totalNotes = 0
r = requests.get(list_url, cookies=cookies)
if r.status_code == 200:
    notebooks = json.loads(r.text)
    for note in notebooks['body']:
        totalNotes += 1
        currentNotebookIds[note['id']] = note['name']

        if note['name'] not in currentNotebookNames:
            currentNotebookNames[note['name']] = []

        currentNotebookNames[note['name']].append(note['id'])
print ('**** Currently there are ' + str(totalNotes) + ' notebooks in Zeppelin ****')

#
# Read the interpreter binding for each Notebook loaded in Zeppelin, and test
# to see if they are 'selected', if not add those that aren't selected into a
# json array:
#
# [
#  "splicemachine",
#  "spark",
#  "md",
#  "angular",
#  "python"
# ]
#
# and PUT to /api/notebook/interpreter/bind/{notebookid}

for notekey in currentNotebookIds:
    unselected_interpreters = []
    r = requests.get(bind_url + '/' + notekey, cookies=cookies)
    if r.status_code == 200:
        bound_interpreters = json.loads(r.text)
        for interpreter in bound_interpreters['body']:
            if interpreter['selected'] == False:
                unselected_interpreters.append(interpreter['id'])
        if unselected_interpreters.count > 0:
            body = json.dumps(unselected_interpreters)
            r = requests.put(bind_url + '/' + notekey, data=body, cookies=cookies)
            if r.status_code == 200:
                print ('**** Activated Interpreters on Notebook: ' + notekey + ' ****')
            else:
                print ('**** FAILED to Activate Interpreters on Notebook: ' + notekey + ' ****')
