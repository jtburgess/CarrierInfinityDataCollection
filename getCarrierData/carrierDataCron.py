#!/usr/bin/env python3
"""
  this is the top level for collecting data from the carrier infinity and arduino sensors
  for what purpose?  Curiousity, to see how it behaves and performs, to learn ...

  Use with -R for realtime data, run every hour, or half-hour
    writes the data to CarrierRealTimeData.json (unless debugging)
  Use with -D for daily use, to capture stats that only occur daily
    writes the data to CarrierDailyData.json (unless debugging)
"""
import argparse
import asyncio
import datetime
import json
import logging
from sys import exit, stdout
import time
import datetime


from getArduinoData import getArduinoData
from getCarrierData import getCarrierData, selectRealTimeData, selectDailyData

async def main():
    parser = argparse.ArgumentParser(
        description="Collect data from Carrier Infinity system."
    )
    # Example argument; add more as needed
    parser.add_argument( "-d", "--debug", action="store_true", help="Enable debug output" )
    parser.add_argument( "-R", "--realtime", action="store_true", help="get the realtime fields" )
    parser.add_argument( "-D", "--daily", action="store_true", help="get the Daily Fields" )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, style="{",
        format="{asctime}-{levelname}-{name}: {message}",
        datefmt="%y-%m-%d %H:%M:%S",
        )
    if args.debug:
        logging.setLevel("DEBUG")
        logging.debug("Debug mode enabled.")
    logging.debug ("Args=[ %s ]" % args)

    ##### this is the business logic
    arduino_data = getArduinoData(args)

    if args.realtime:
        logging.info("running Carrier Realtime Data collection")
        output_file = "../CarrierRealTimeData.json"
        # since the Carrier login is async, I can do the arduino collection while waiting
        getDataTask = asyncio.create_task (getCarrierData(args))
        carrier_data = await getDataTask
        if len(carrier_data) != 1:
            logging.error("Carrier returned %d systems\n" % len(carrier_data))
            exit(1)

        carrier_data = selectRealTimeData(carrier_data[0].__repr__())
    elif args.daily:
        logging.info("running Carrier Daily Data collection")
        output_file = "../CarrierDailyData.json"

        # wait until just past midnight
        now = datetime.datetime.now()
        midnight = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        secs = (midnight - now).total_seconds()
        if args.debug or secs > 600:
          logging.info ("would have slept %d seconds" % secs)
        else:
          time.sleep(max(0, secs+5))   # sleep 5 extra seconds, just for goot measure

        getDataTask = asyncio.create_task (getCarrierData(args))
        carrier_data = await getDataTask
        if len(carrier_data) != 1:
            logging.error("Carrier returned %d systems\n" % len(carrier_data))
            exit(1)

        carrier_data = selectDailyData(carrier_data[0].__repr__())
        del carrier_data['DATE'] #we want yesterday's date!
    else:
        logging.error ("You must specify either --realtime or --daily")
        exit(1)

    if args.debug:
        logging.debug ("arduino data: " + str(arduino_data))
        logging.debug ("selected carrier data: " + str(carrier_data[0].__repr__()))

    collected_data = {**arduino_data, **carrier_data}
    logging.debug ("combined data: " + str(collected_data))

    # write the collected data to a file for comparison
    f = open(output_file, "a")
    f.write (str(collected_data) + '\n')
    f.close ()

    exit(0)


if __name__ == "__main__":
  asyncio.run(main())
