#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Updates the Zeppelin spark interpreter to work on a cloudera or hortonworks cluster.  This script must be run on the hadoop cluster.

Run for the details about the parameters: python configure-spark-interpreter.py --help

Example for running it for a zeppelin instance hitting a Cloudera Hadoop Cluster: 
    python configure-spark-interpreter.py -z "http://srv132:8180" -a "CDH" -s "/tmp/zeppelin" -r "http://stl-colo-srv131.splicemachine.colo:8088"

Example for running it for a zeppelin instance hitting a Hortonworks Hadoop Cluster: 
    python configure-spark-interpreter.py -z "http://srv036:9995" -a "HDP" -s "/tmp/zeppelin" -v "0.7.3" -u admin -p admin

{License_info}
'''

import requests
import argparse
import os
import json
from os import listdir
import subprocess


_author__ = "Erin Driggers"
__copyright__ = "Copyright 2018, Splice Machine"
__credits__ = ["Erin Driggers"]
__version__ = '0.0.1'

current_file_directory = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser(description="This script will update the spark interpreter settings with values compatible with CDH")

parser.add_argument('-z', '--zeppelinUrl', dest='zeppelinUrl',
                    default='http://localhost:8080', help='Zeppelin url for example: http://localhost:8080')

parser.add_argument('-a', '--hadoopVendor', dest='hadoopVendor',
                    default='CDH', help='The hadoop vendor.  Valid values are CDH for Cloudera or HDP for Hortonworks')

parser.add_argument('-c', '--hadoopVendorRootDir', dest='hadoopVendorRootDir',
                    help='The root directory for hadoop.  If the vendor is CDH then it defaults to /opt/cloudera/parcels if it is HDP it defaults to /usr/hdp/2.6.3.0-235')

parser.add_argument('-r', '--resourceUrl', dest='resourceUrl',
                    default='http://localhost:8088', help='Yarn resource url for example: http://localhost:8088')

parser.add_argument('-s', '--spliceAdditionalJarDir', dest='spliceAdditionalJarDir',
                    default='/tmp/splicemachine/', help='Path where additional splice machine jars are place')

parser.add_argument('-u', '--user', dest='user',
                    help='Zeppelin user if authentication enabled')

parser.add_argument('-p', '--password', dest='password',
                    help='Zeppelin password if authentication enabled')

parser.add_argument('-v', '--zeppelinVersion', dest='zeppelinVersion', default="0.8.0",
                    help='Zeppelin version.')

args = parser.parse_args()

ZEPPELIN_URL=args.zeppelinUrl
HADOOP_VENDOR=args.hadoopVendor
HADOOP_ROOT_DIR=args.hadoopVendorRootDir
RESOURCE_URL=args.resourceUrl
SPLICE_ADDITIONAL_JARS_DIR=args.spliceAdditionalJarDir
USER=args.user
PASSWORD=args.password
ZEPPELIN_VERSION=args.zeppelinVersion


if HADOOP_ROOT_DIR is None:
    if HADOOP_VENDOR == 'CDH':
        HADOOP_ROOT_DIR = '/opt/cloudera/parcels'
    elif HADOOP_VENDOR == 'HDP':
        HADOOP_ROOT_DIR = '/usr/hdp/2.6.3.0-235'
    else:
        print('Invalid value for hadoopVendor');
        exit();

SPLICE_SPECIAL_JAR="splicemachine-cdh5.14.0-2.2.0.cloudera2_2.11-2.7.0.1828.jar"
if HADOOP_VENDOR == 'CDH':
    HADOOP_VENDOR_DIR=HADOOP_ROOT_DIR + "/CDH/lib"
    HBASE_LIB_DIR=HADOOP_VENDOR_DIR + '/hbase'
    SPARK_ROOT_DIR=HADOOP_ROOT_DIR + "/SPARK2/lib/spark2"
    SPLICE_ROOT_DIR=HADOOP_ROOT_DIR + "/SPLICEMACHINE"
elif HADOOP_VENDOR == 'HDP':
    HADOOP_VENDOR_DIR=HADOOP_ROOT_DIR
    HBASE_LIB_DIR=HADOOP_VENDOR_DIR + '/hbase/lib'
    SPARK_ROOT_DIR=HADOOP_ROOT_DIR + "/spark2"
    SPLICE_ROOT_DIR="/opt/splice/default/"
else:
    print('Invalid value for hadoopVendor');
    exit();

currentSparkProperties={}
cookies=None
interpreterId=None
authentication=True
if USER is None or USER == "":
    authentication=False

#
# Function to build the list of properties to update
#
def addProperty(propList, name, value, type):
    if ZEPPELIN_VERSION == "0.7.3":
        propList[name] = value
    else:
        prop = {}
        prop['name'] = name
        prop['value'] = value
        prop['type'] = type
        propList[name] = prop
    return propList


#
# Authenticate if necessary
#
if authentication is True:
    r = requests.post(ZEPPELIN_URL + '/api/login', data='userName=' + USER + "&password=" + PASSWORD)
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
# Get the spark interpreter setting id
#
print('***** Getting spark interpreter id *****')
r = requests.get(ZEPPELIN_URL + '/api/interpreter/setting', cookies=cookies)
if r.status_code == 200:
    data = json.loads(r.text)
    interpreters = data['body']
    for interpreter in interpreters:
        if interpreter['name'] == 'spark':
            interpreterId = interpreter['id']

if interpreterId is None:
    print ('Interpreter not found - exiting')
    exit()

#
# Get the spark interpreter
#
print('***** Getting interpreter settings *****')
r = requests.get(ZEPPELIN_URL + '/api/interpreter/setting/' + interpreterId, cookies=cookies)
if r.status_code == 200:
    data = json.loads(r.text)
    sparkDetails = data['body']
    for property in sparkDetails['properties']:
        propertyDetails = sparkDetails['properties'][property]
        if ZEPPELIN_VERSION == "0.7.3":
            currentSparkProperties = addProperty(currentSparkProperties,property,sparkDetails['properties'][property], None)
        else:
            currentSparkProperties = addProperty(currentSparkProperties,propertyDetails['name'], propertyDetails['value'], propertyDetails['type'])
else:
    print('There was an error getting the current interpreter settings - exiting')
    exit()

hadoop_classpath = subprocess.Popen([HADOOP_VENDOR_DIR + "/hadoop/bin/hadoop", "classpath"],
                          stdout=subprocess.PIPE).communicate()[0]
hadoop_classpath = hadoop_classpath.rstrip()

sparkJars = []

sparkJars.append(HBASE_LIB_DIR + '/hbase-protocol.jar')
sparkJars.append('/etc/hbase/conf/hbase-site.xml')
sparkJars.append('/etc/hadoop/conf/core-site.xml')
sparkJars.append('/etc/hadoop/conf/hdfs-site.xml')
sparkJars.append('/etc/hadoop/conf/yarn-site.xml')
sparkJars.append(SPLICE_ADDITIONAL_JARS_DIR + '/' + SPLICE_SPECIAL_JAR)
for file in listdir(SPLICE_ROOT_DIR + "/lib"):
    sparkJars.append(SPLICE_ROOT_DIR + "/lib/" + file)
sparkJars.append(HBASE_LIB_DIR + '/hbase-client.jar')
sparkJars.append(HBASE_LIB_DIR + '/hbase-common.jar')
sparkJars.append(HBASE_LIB_DIR + '/hbase-server.jar')

if HADOOP_VENDOR == 'CDH':
    sparkJars.append(HBASE_LIB_DIR + '/lib/htrace-core.jar')
elif HADOOP_VENDOR == 'HDP':
    sparkJars.append(HBASE_LIB_DIR + '/htrace-core-3.1.0-incubating.jar')


sparkClassPath = []
sparkClassPath.append('/etc/hbase/conf')
sparkClassPath.append(SPLICE_ROOT_DIR + '/lib/*')
sparkClassPath.append(SPARK_ROOT_DIR + '/jars/*')
sparkClassPath.append(HBASE_LIB_DIR + '/*')
if HADOOP_VENDOR == 'CDH':
    sparkClassPath.append(HBASE_LIB_DIR + '/lib/*')
sparkClassPath.append(SPLICE_ADDITIONAL_JARS_DIR + "/*")


#
# Generate the list of properties that should be set for the spark interpreter
#
updatedSparkProperties = {}

updatedSparkProperties = addProperty(updatedSparkProperties,'master', 'yarn', 'string')
updatedSparkProperties = addProperty(updatedSparkProperties,'zeppelin.spark.uiWebUrl', RESOURCE_URL, 'string')

updatedSparkProperties = addProperty(updatedSparkProperties,'zeppelin.spark.useHiveContext', False, 'checkbox')
updatedSparkProperties = addProperty(updatedSparkProperties,'spark.submit.deployMode', 'cluster', 'string')
updatedSparkProperties = addProperty(updatedSparkProperties,'spark.kryo.referenceTracking', False, 'checkbox')
updatedSparkProperties = addProperty(updatedSparkProperties,'spark.kryo.registrator', "com.splicemachine.derby.impl.SpliceSparkKryoRegistrator", 'string')
updatedSparkProperties = addProperty(updatedSparkProperties,'HADOOP_CONFIG_DIR', '/etc/hadoop/conf', 'string')
updatedSparkProperties = addProperty(updatedSparkProperties,'HADOOP_HOME', HADOOP_VENDOR_DIR + '/lib/hadoop', 'string')
updatedSparkProperties = addProperty(updatedSparkProperties,'SPARK_HOME', SPARK_ROOT_DIR, 'string')
updatedSparkProperties = addProperty(updatedSparkProperties,'SPARK_CONF_DIR', '/etc/spark2/conf', 'string')
updatedSparkProperties = addProperty(updatedSparkProperties,'SPARK_DIST_CLASSPATH', hadoop_classpath, 'textarea')
updatedSparkProperties = addProperty(updatedSparkProperties,'spark.executor.extraClassPath', ":".join(sparkClassPath), 'textarea')
updatedSparkProperties = addProperty(updatedSparkProperties,'spark.driver.extraClassPath', ":".join(sparkClassPath), 'textarea')
updatedSparkProperties = addProperty(updatedSparkProperties,'spark.jars', ",".join(sparkJars), 'textarea')

print('****** Properties that are going to change *******')
mergedSparkProperties=currentSparkProperties
for property in updatedSparkProperties:
    propDetails = updatedSparkProperties[property]
    mergedSparkProperties[property]=propDetails 
    if property in currentSparkProperties:
        currentPropDetails = currentSparkProperties[property]
    else:
        currentPropDetails = None

    if ZEPPELIN_VERSION == "0.7.3":
        if currentPropDetails is None:
            print('Adding property: name=' + property + " value=" + propDetails)
        else:
            if propDetails != currentPropDetails:
                print('Updating property:' + property)
                print ("CURRENT:   value=" + currentPropDetails)
                print ("NEW:       value=" + propDetails)
    else:
        if currentPropDetails is None:
            print('Adding property')
            print ("name=" + str(propDetails['name']) + " value=" + str(propDetails['value']))
        else:
            if propDetails['value'] != currentPropDetails['value']:
                print('Updating property:' + propDetails['name'])
                print ("CURRENT:   value=" + str(currentPropDetails['value']))
                print ("NEW:       value=" + str(propDetails['value']))

#
# Update the spark interpreter
#
print('***** Update interpreter settings *****')
sparkSettings={}
sparkSettings['name']="spark"
sparkSettings['properties']=mergedSparkProperties
r = requests.put(ZEPPELIN_URL + '/api/interpreter/setting/' + interpreterId, data=json.dumps(sparkSettings), cookies=cookies)
if r.status_code == 200:
    print('success')
else:
    print('There was an error processing the request')
    print(r.status_code)
    print(r.text)
