#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Installs the splice machine notebook template to an existing Zeppelin Instance. 
Run for the details about the parameters: python load-notebooks.py --help
{License_info}
'''

import requests
import argparse
import os
import json
import mmap

__author__ = "Erin Driggers"
__copyright__ = "Copyright 2018, Splice Machine"
__credits__ = ["Erin Driggers"]
__version__ = '0.0.1'

current_file_directory = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser(description="This script will import Splice Machine's zeppelin notebooks to your zeppelin instance")
parser.add_argument('-z', '--zeppelinUrl', dest='zeppelinUrl',
                    default='http://localhost:8080', help='Zeppelin url for example: http://localhost:8080')

parser.add_argument('-n', '--notebookDir', dest='notebookDir',
                    default=current_file_directory,
                    help='Root directory containing the notebooks')

parser.add_argument('-u', '--user', dest='user',
                    default="",
                    help='Zeppelin user if authentication enabled')

parser.add_argument('-p', '--password', dest='password',
                    default="",
                    help='Zeppelin password if authentication enabled')


parser.add_argument('-d', '--delete', dest='delete', action='store_true', help='Use the -d or --delete option if you wish to delete existing matching notebooks')
args = parser.parse_args()

ZEPPELIN_URL=args.zeppelinUrl
NOTEBOOK_ROOT_DIR=args.notebookDir
DELETE_NOTEBOOKS=args.delete
USER=args.user
PASSWORD=args.password
authentication=True

if USER is None or USER == "":
    authentication=False

login_url = ZEPPELIN_URL + '/api/login'
list_url = ZEPPELIN_URL + '/api/notebook'
import_url = ZEPPELIN_URL + '/api/notebook/import'

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
# Load the notebooks in the cluster.  First check to see if they currently exist
# if they do, then delete them first.  A note can be imported and the id will change.
# Need to compare the name of the notebook
#

for subdir, dirs, files in os.walk(NOTEBOOK_ROOT_DIR):
    for file in files:
        filepath = subdir + os.sep + file

        if filepath.endswith(".json"):
            notebookId = os.path.basename(subdir)
            notebookName = ""

            if DELETE_NOTEBOOKS is True:
                with open(filepath, "r") as note_file:
                    s = mmap.mmap(note_file.fileno(), 0, access=mmap.ACCESS_READ)
                    nameLoc = s.rfind('"name"'.encode())
                    if nameLoc != -1:
                        commaLoc = s.find(",".encode(), nameLoc + 7)
                        if(commaLoc != -1):
                            notebookName = s[nameLoc:commaLoc]
                            notebookName = notebookName.replace('"name": '.encode(),''.encode())
                            notebookName = notebookName.replace('"'.encode(),''.encode())

                notebookName = notebookName.decode()
                print ('Processing notebook id: %s with name %s' % (notebookId, notebookName))
                if notebookId in currentNotebookIds:
                    print ('Notebook Id exists - deleting')
                    r = requests.delete(ZEPPELIN_URL + '/api/notebook/' + notebookId, cookies=cookies)

                if notebookName in currentNotebookNames:
                    print ('Notebook Name exists - deleting')
                    for noteId in currentNotebookNames[notebookName]:
                        print ('Deleting matching Name with notebook id:' + noteId)
                        r = requests.delete(ZEPPELIN_URL + '/api/notebook/' + noteId, cookies=cookies)

            r = requests.post(import_url, data=open(filepath, 'rb'), cookies=cookies)
            if r.status_code > 201:
                print('Status:', r.status_code)
                print ('Response:' + r.text)

