#!/bin/bash
#initialization with default values
SERVICE='cpu_util'
THRESHOLD='-1'

#function to print the help info
printusage()
{
        echo "This plug-in uses the OpenStack Ceilometer API to let Nagios query Ceilometer metrics of VMs."
	echo "usage:"
	echo "ceilometer-call -s metric_name -t nagios_warning_threshold -T nagios_critical_threshold"
	echo "-h: print this message"
	echo "-s service: The Ceilometer metric which you want to query"
	echo "-t threshold: Threshold value which causes Nagios to create a warning message"
	echo "-T threshold for alert: Threshold value which causes Nagios to send a critical alert message"
	echo "-c configuration file for tenants"
	echo "-r resourceid"
	exit ${EXITPROB}
}


#parse the arguments
while getopts ":hs:t:T:c:r:v:" opt
do
        case $opt in
                h )     printusage;;
                s )     SERVICE=${OPTARG};;
                t )     THRESHOLD=${OPTARG};;
                T )     CRITICAL_THRESHOLD=${OPTARG};;
		c )	CREDENTIAL=${OPTARG};;
		r )	RESOURCE=${OPTARG};;
		v )	HOST=${OPTARG};;
                ? )     printusage;;	
        esac
done

#####################################################
#####################################################
# CREDENTIAL PART REMOVED and 
# python module added for getting result from mongoDB
#####################################################
#####################################################

pythonResult=`python3.4 mongoDBhandler.py $RESOURCE $SERVICE $THRESHOLD $CRITICAL_THRESHOLD`

statusInfo=$(echo $pythonResult | awk -F '|' '{print $1 "|" $2}')
perfData=$(echo $pythonResult | awk -F '|' '{print $2}')
returnCode=$(echo $pythonResult | awk -F '|' '{print $3}')

echo "$pythonResult"
echo "$statusInfo"
echo "$perfData"
echo "$returnCode"
