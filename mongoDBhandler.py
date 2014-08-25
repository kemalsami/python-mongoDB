#!/usr/bin/python
__author__ = 'kemal'

import json
import sys
from pymongo import MongoClient


from datetime import datetime

#####################################################
#####################################################
#####################################################
# ---------------------------- #
# Get DB list
# ---------------------------- #
def getDBNames(client):
    return client.database_names()

# ---------------------------- #
# Show DB list
# ---------------------------- #
def showDBNames(client):
    for dbName in getDBNames(client):
        print(dbName)



#####################################################
# ---------------------------- #
# Get COLLECTION list
# ---------------------------- #
def getCollectionNames(db):
    return db.collection_names()

# ---------------------------- #
# Show COLLECTION list
# ---------------------------- #
def showCollectionNames(db):
    for colName in getCollectionNames(db):
        print(colName)



#####################################################
# ---------------------------- #
# Check Actual Value of service in threshold
# ---------------------------- #
def serviceThresholdResult(val , th_down , th_up):
    if val > th_up:
        return 2
    elif val > th_down:
        return 1
    elif val <= th_down:
        return 0
    else:
        return -1

# ---------------------------- #
# Check that threshold are taken properly
# ---------------------------- #
def isThresholdValuesTaken():
    return thresholdDown!=None and thresholdUp!=None

# ---------------------------- #
# Check that (dateNow-10min) < (timestamp)
# ---------------------------- #
def isDataFresh(dataTime):
    dateNow = datetime.now()
    timeDiff = dateNow - dataTime
    if timeDiff.seconds <= 600:
        return True
    else:
        return False

#####################################################
#####################################################
#####################################################

"""
    GET ARGUMENTS
"""
#print('Number of arguments:', len(sys.argv), 'arguments.')
#print('Argument List:', str(sys.argv))


"""
    CONNECT TO MONGODB WITH GIVEN ARGUMENTS
"""
# For now, IP address selected as default
host            = "185.7.3.61" # mongoDB connection IP
port            = 27017        # mongoDB connection port
dbName          = 'ceilometer'
collectionName  = 'meter'
returnValue     = ""
resourceID      = None
service         = None
#thresholdDown   = None
#thresholdUp     = None

try:
    # MongoDB connection start here
    client = MongoClient(host , port)

    # Proper collection selected here
    db = client[dbName]

    try:
        resourceID  = sys.argv[1]
        service     = sys.argv[2]
        try:
            thresholdDown   = float(sys.argv[3])
            thresholdUp     = float(sys.argv[4])
        except:
            print("Threshold values was not given")

    except:
        print("DEFAULT example")
        resourceID      = "8319b081-4f08-4730-b326-db8596ace97c"
        service         = "cpu_util"
        thresholdDown   = 10
        thresholdUp     = 20


    # Find result value of service
    returnCode = -2;
    # Set time to 10min ago
    dateNow = datetime.now()
    dateNow = dateNow.replace(minute=dateNow.minute-10)
    dateNow = dateNow.replace(hour=dateNow.hour-3)

    # If result contains more than one tuples then return object will be cursor
    collection = db[collectionName]
    cursor = collection.find({"resource_id":resourceID , "counter_name":service , "timestamp":{"$gt":dateNow} }).sort([("timestamp",-1)]).limit(1)
    res = cursor.__getitem__(0)


    if service=="cpu_util":
        if isThresholdValuesTaken():
            returnCode = serviceThresholdResult( res['counter_volume'] , thresholdDown , thresholdUp )
            returnValue = "Instance="+str(resourceID)+ ", " + str(service) + "=" + str(res['counter_volume']) + ", RETURN CODE=" + str(returnCode) + " | " + str(service) + "=" + str(res['counter_volume'])

    elif service=="cpu":
        returnCode = 0
        returnValue = "Instance="+str(resourceID)+ ", " + str(service) + "=" + str(res['counter_volume']) + ", RETURN CODE=" + str(returnCode) + " | " + str(service) + "=" + str(res['counter_volume'])

    else:
        print("Selected Service is not proper")


    # GET RETURN VALUE from file
    print(returnValue + "|" + str(returnCode))

except:
    print("UNEXPECTED ERROR OCCUR")






