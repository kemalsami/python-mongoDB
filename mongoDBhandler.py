#!/usr/bin/python
__author__ = 'kemal'

import json
import sys
from datetime import datetime
from pymongo import MongoClient


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

# ---------------------------- #
# That method returns EXCEPTION
# ---------------------------- #
def callException(ExceptionDesc):
    returnCode  = 2
    returnValue = "ERROR:" + str(ExceptionDesc) + " |  |" + str(returnCode)
    print(str(returnValue))

# ---------------------------- #
# MAIN Function
# ---------------------------- #
def mainFunction(db):

    try:
        # Set time to 3hours and 10mins ago
        dateNow = datetime.now()
        dateNow= dateNow.replace(minute=dateNow.minute-15)
        dateNow = dateNow.replace(hour=dateNow.hour-3)
    except:
        callException("Date problem")

    # If result contains more than one tuples then return object will be cursor
    collection = db[collectionName]
    cursor = collection.find({"resource_id": { "$regex" : regexID} , "counter_name":service , "timestamp":{"$gt":dateNow} }).sort([("timestamp",-1)]).limit(2)
    res = cursor.__getitem__(0)
    resAlternative = cursor.__getitem__(1)

    # Get values from result
    if isThresholdValuesTaken():
        returnCode = serviceThresholdResult( res['counter_volume'] , thresholdDown , thresholdUp )
        returnValue = "Instance="+str(resourceID)+ ", " + str(service) + "=" + str(res['counter_volume']) + ", RETURN CODE=" + str(returnCode) + " | " + str(service) + "=" + str(res['counter_volume'])
    else:
        # if service name finish ".rate" and its counter_type is cumulative then find rate of service
        returnCode = 0
        if runRate and "cumulative" in str(res['counter_type']):
            returnValue = "Instance="+str(resourceID)+ ", " + str(service) + ".rate=" + str(res['counter_volume']-resAlternative['counter_volume']) + ", RETURN CODE=" + str(returnCode) + " | " + str(service) + ".rate=" + str(res['counter_volume']-resAlternative['counter_volume'])
        else:
            returnValue = "Instance="+str(resourceID)+ ", " + str(service) + "=" + str(res['counter_volume']) + ", RETURN CODE=" + str(returnCode) + " | " + str(service) + "=" + str(res['counter_volume'])

    return returnValue + "|" + str(returnCode)

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
returnCode      = 2;
returnValue     = "Connection Failure"
thresholdDown   = None
thresholdUp     = None
runRate         = False

try:
    # MongoDB connection start here
    client = MongoClient(host , port)

    # Proper collection selected here
    db = client[dbName]

    try:
        resourceID  = sys.argv[1]
        regexID     = ".*"+resourceID+".*"
        service     = sys.argv[2]
        # if service name includes ".rate" then prepare to calculate rate of service
        if ".rate" in service:
            runRate = True
            service = service[:service.index('.rate')]

        # if arguments contain thresholds then take those values
        if len(sys.argv) == 5:
            thresholdDown   = float(sys.argv[3])
            thresholdUp     = float(sys.argv[4])
        else:
            thresholdDown   = None
            thresholdUp     = None

        try:
            print(mainFunction(db))
        except:
            callException("mainFunction error")

    except:
        """
        resourceID  = "8319b081-4f08-4730-b326-db8596ace97c"
        regexID     = ".*"+resourceID+".*"
        service     = "cpu.rate"
        if ".rate" in service:
            runRate = True
            service = service[:service.index('.rate')]

        print(mainFunction(db))
        """
        callException("Parameter cannot taken properly")


except:
    callException(returnValue)








