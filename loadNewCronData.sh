#!/bin/bash
# copy recent data from the Mac Mini
# load it into Excel
# append the data to the archive, and empty the new data files
# and copy it back to the Mac Mini

# function to import data from json to excel, and then copy that data to the archive
# one parapmeter: $1 = Daily or RealTime

# shell debug options
# e exit on any error
# u unset variables is an error 
# v print lines as read
# x print as executed
set -eux #v

Mini='/Volumes/jburgess/Dropbox/CarrierDataCollection'
Me='/Users/jburgess/Library/CloudStorage/Dropbox/CarrierDataCollection'

if [ ! -d $Mini ]
then
    echo Mount the Mac Mini, first
    exit 1
fi
if [ ! -d $Me ]
then
    echo EEK! $Me is missing
    exit 2
fi

# first copy the lastest data from Mac Mini
cp -p $Mini/Carrier*.json $Me

# load it into Excel
cd $Me
python3 getCarrierData/loadJSONtoExcel.py "$@" --RealTime
python3 getCarrierData/loadJSONtoExcel.py "$@" --Daily

echo continue? ; read x

cd $Me
# append the data to the archive, and empty the new data files
for type in Daily RealTime
do
    file=Carrier${type}Data.json
    cat $file >> Old$file
    > $file
done

echo continue? ; read x

# and copy it back to the Mac Mini
cp -p Carrier*.json OldCarrier*.json $Mini
exit 0
