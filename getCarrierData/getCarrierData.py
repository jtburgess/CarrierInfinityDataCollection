#!/usr/bin/env python3
# use https://github.com/dahlb/carrier_api to write a simple program to collect system data
import asyncio
import argparse
import datetime
import json
import logging
from sys import exit, stdout, exc_info
from PRIVATE import UserName, PassWord
from typing import Any, Dict

from carrier_api.api_connection_graphql import ApiConnectionGraphql
from carrier_api.api_websocket_data_updater import WebsocketDataUpdater
from carrier_api.const import FanModes

def traceBack():
    import traceback
    """return a traceback in a variable"""
    # from sys import exc_info
    excType, excValue, excTraceback = exc_info()
    logging.error ("EXCEPTION: excType=%s, excValue=%s, excTraceback=%s" % (excType, excValue, excTraceback))
    lines = traceback.format_exception(excType, excValue, excTraceback)
    logging.debug( "".join( lines ))

async def getCarrierData(args) -> Dict[str, Any]:
    username = UserName
    password = PassWord
    api_connection = None
    systems = {}

    logger = logging.getLogger("gql.transport.aiohttp")
    logger.setLevel("WARNING") # the gql.transport.aiohttp logs a lot at INFO
    #logger.setLevel("DEBUG") # the gql.transport.aiohttp logs a lot at INFO

    try:
        api_connection = ApiConnectionGraphql(username=username, password=password)
        systems = await api_connection.load_data()
        logging.debug("API connected. %d systems\n" % (len(systems)))
        if args.debug:
            for system in systems:
                logging.debug( json.dumps(system.__repr__(), sort_keys=True, indent=2, separators=(',', ': ')) )
    except:
        # ApiConnection just fails silently when it gets an error, so I added this.
        traceBack()
    finally:
        logging.debug ("Finally!")
        if api_connection is not None:
            await api_connection.cleanup()
        return systems

# select the fields we want to record on an hourly (RealTime) basis from the larger carrier dictionary
status_fields = [
  [ 'outdoor_temperature', 'out_temp' ],
  [ 'airflow_cfm', 'airflow_cfm' ],
  [ 'blower_rpm', 'blower_rpm' ],
  [ 'humidifier_on', 'humidifier_on' ],
  [ 'outdoor_unit_operational_status', 'outdoor_status' ],
  [ 'indoor_unit_operational_status', 'indoor_status' ],
]
zone_fields = [
  [ 'current_activity', 'hp_profile' ],
  [ 'conditioning', 'conditioning' ],
  [ 'temperature', 'in_temp' ],
  [ 'humidity', 'humidity' ],
  [ 'fan', 'fan' ],
]

def selectRealTimeData(collected_data : Dict[str, Any]) -> Dict[str, Any]:
    selected_data = {}
    today = str(datetime.date.today())
    selected_data.__setitem__ ("DATE", today)
    now = datetime.datetime.now().strftime('%H:%M:%S')
    selected_data.__setitem__ ("TIME", now)

    status = collected_data['status']
    for field in status_fields:
        try:
          selected_data.__setitem__ (field[1], status[field[0]])
        except:
          logging.warning("carrier status is missing %s" % (field[0]))

    zone = status['zones'][0]
    for field in zone_fields:
        try:
          selected_data.__setitem__ (field[1], zone[field[0]])
        except:
          logging.warning("carrier status-zone is missing %s" % (field[0]))

    return selected_data

# select the data that only is available on a Daily basis
daily_status_fields = [
  [ 'filter_used', 'hp_filter%' ],
  [ 'humidity_level', 'humid_filter%' ],
]
# ['energy']['periods'][0]
daily_energy_fields = [
  [ 'id', 'id' ],
  [ 'cooling', 'cool_btu' ],
  [ 'hp_heat', 'heat_btu' ],
  [ 'fan', 'hp_fan' ],
  [ 'gas', 'furnace_btu' ],
  [ 'fan_gas', 'furnace_fan' ],
  [ 'loop_pump', 'loop_pump' ],
]
def selectDailyData(collected_data : Dict[str, Any]) -> Dict[str, Any]:
    selected_data = {}
    today = str(datetime.date.today())
    selected_data.__setitem__ ("DATE", today)
    now = datetime.datetime.now().strftime('%H:%M:%S')
    selected_data.__setitem__ ("TIME", "Daily")

    status = collected_data['status']
    for field in daily_status_fields:
        try:
          selected_data.__setitem__ (field[1], status[field[0]])
        except:
          logging.warning("carrier status is missing %s" % (field))

    energy = collected_data['energy']['periods'][0]
    for field in daily_energy_fields:
        try:
          selected_data.__setitem__ (field[1], energy[field[0]])
        except:
          logging.warning("carrier energy is missing %s" % (field))

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
    parser.add_argument( "-R", "--realtime", action="store_true", help="get the realtime fields" )
    parser.add_argument( "-D", "--daily", action="store_true", help="get the Daily Fields" )
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

    if args.debug:
        # write the raw collected data to a file for comparison
        f = open("carrier_collected_data", "w")
        f.write (str(collected_data) + '\n')
        f.close ()

    if args.raw:
        #print (str(collected_data) + '\n')
        selected_data = collected_data
    elif args.realtime:
        selected_data = selectRealTimeData(collected_data.__repr__())
    elif args.daily:
        selected_data = selectDailyData(collected_data.__repr__())
    else:
        logging.error ("You must specify either --raw, --realtime or --daily")
        exit(1)

    json.dump (selected_data, stdout, indent=2, ensure_ascii=False)
    print ("\n")
    exit(0)

if __name__ == "__main__":
    asyncio.run(main())
    #await main()
