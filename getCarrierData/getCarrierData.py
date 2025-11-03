#!/usr/bin/env python3
# use https://github.com/dahlb/carrier_api to write a simple program to collect system data
import asyncio
import argparse
import datetime
import json
import logging
from sys import exit, stdout
from PRIVATE import UserName, PassWord
from typing import Any, Dict

from carrier_api.api_connection_graphql import ApiConnectionGraphql
from carrier_api.api_websocket_data_updater import WebsocketDataUpdater
from carrier_api.const import FanModes

async def getCarrierData(args) -> Dict[str, Any]:
    username = UserName
    password = PassWord
    api_connection = None
    systems = {}
    try:
        api_connection = ApiConnectionGraphql(username=username, password=password)
        systems = await api_connection.load_data()
        logging.debug("API connected. %d systems\n" % (len(systems)))
        for system in systems:
            logging.debug( json.dumps(system, sort_keys=True, indent=2, separators=(',', ': ')) )
    finally:
        logging.debug ("Finally!")
        if api_connection is not None:
            await api_connection.cleanup()
        return systems

# select the fields we want to record from the larger carrier dictionary
status_fields = [
  'outdoor_temperature',
  'airflow_cfm', 'blower_rpm', 'humidifier_on',
  'outdoor_unit_operational_status', 'indoor_unit_operational_status',
]
zone_fields = [
  'temperature', 'humidity',
  'current_activity', 'conditioning', 'fan',
]

def select_data(collected_data : Dict[str, Any]) -> Dict[str, Any]:
    selected_data = {}
    today = str(datetime.date.today())
    selected_data.__setitem__ ("DATE", today)
    now = datetime.datetime.now().strftime('%H:%M:%S')
    selected_data.__setitem__ ("TIME", now)

    status = collected_data['status']
    for field in status_fields:
        try:
          selected_data.__setitem__ (field, status[field])
        except:
          logging.warning("carrier status is missing %s" % (field))

    zone = status['zones'][0]
    for field in zone_fields:
        try:
          selected_data.__setitem__ (field, zone[field])
        except:
          logging.warning("carrier status-zone is missing %s" % (field))

    return selected_data

##########
# this is just for testing / debugging the above functions
# note IF this is NOT async, so you must call it with asyncio.run(getCarrierData)
# otherwise you can use create task ... await, as below
async def main():
    parser = argparse.ArgumentParser(
        description="Collect data from Carrier Infinity system."
    )
    # Example argument; add more as needed
    parser.add_argument( "-d", "--debug", action="store_true", help="Enable debug output" )
    parser.add_argument( "-r", "--raw", action="store_true", help="Just dump the raw data" )
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("Debug mode enabled.")
    else:
        logging.basicConfig(level=logging.WARN)

    logging.debug ("Args=[ %s ]" % args)

    getDataTask = asyncio.create_task (getCarrierData(args))
    # can do other stuff here . . .
    collected_data = await getDataTask
    if len(collected_data) != 1:
        logging.error("\nresulted in %d systems\n" % len(collected_data))
        exit(1)
    else:
        # just want the data. I only have one system
        collected_data = collected_data[0] #.__repr__()
    # write the raw collected data to a file for comparison
    f = open("carrier_collected_data", "a")
    f.write (str(collected_data) + '\n')
    f.close ()

    if args.raw:
        #print (str(collected_data) + '\n')
        json.dump (collected_data, stdout, indent=2, ensure_ascii=False)
    else:
        selected_data = select_data(collected_data.__repr__())
        json.dump (selected_data, stdout, indent=2, ensure_ascii=False)
    print ("\n")
    exit(0)

if __name__ == "__main__":
    asyncio.run(main())
    #await main()
