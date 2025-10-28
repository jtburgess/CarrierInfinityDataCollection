#!python3
import argparse
import io
import json
import logging
import re
import requests
from sys import exit, stdout
from typing import Dict, IO
from parseArduinoToDict import parseArduinoToDict

"""
  get data from an arduino temp_sensor that looks like this:
    NAME,MIN,MAX,AVG,LAST,COUNT
    Inside,67.7,69.3,68.8,69.3,48
    Outside,53.2,56.4,54.8,54.6,48
    %Humidity,45.9,46.1,46.0,46.0,48
    Barometer,29.8,29.8,29.8,29.8,48

  extract temp and humidity data and return it reformatted as in CarrierDataSchema.txt:

"""
def getWebFileObj(url, params=None, headers=None, timeout=10) -> IO[str]:
  r = requests.get(url, params=params, headers=headers, timeout=timeout)
  r.raise_for_status()         # raises on HTTP error codes
  return io.TextIOWrapper(io.BytesIO(r.content), encoding="utf-8", newline="")

pattern = re.compile(r'^(?:(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d).){3}(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)$')
def isIPaddr(arg):
  if pattern.match(arg):
    return arg
  else:
    raise ValueError

# these are the field-name mappings from each arduino to the combined output dictionary
# note each map represents a row on the input -- and always selects the LAST value
map98 = [
  [ 'test2', 'TItemp' ],
  [ '%Humidity', 'Thumidity' ],
]
map100 = [
  [ 'Inside', 'LItemp' ],
  [ 'Outside', 'LOtemp' ],
  [ '%Humidity', 'Lhumidity' ],
]

def main():
    import argparse
    parser = argparse.ArgumentParser( prog='PROG',
        description="Collect data from Arduino temp sensor(s)."
    )

    parser.add_argument( "-d", "--debug", action="store_true", help="Enable debug output" )
    parser.add_argument('file', nargs='?', help="name of CSV data file to use")
    parser.add_argument("-i", "--ipaddr", nargs=1, type=isIPaddr)
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("Debug mode enabled.")
    else:
        logging.basicConfig(level=logging.INFO)

    logging.debug ("Args=[ %s ]" % args)
    if args.file and len(args.file) > 1:
        parser.error("Only one file argument accepted")

    if args.file and len(args.file) == 1:
        logging.debug("reading CSV data from: %s" % args.file[0])
        infile = open(args.file[0], newline="")
        sensor_dict = parseArduinoToDict (infile)
    else:
        # no file means read the live data from arduino
        logging.debug("reading CSV data from the sensors on the netqork")
        if args.ipaddr:
          sensor_ips = args.ipaddr # its a list of one
        else:
          sensor_ips = [ '192.168.0.98', '192.168.0.100' ]

        collected_data = {}
        for ip in sensor_ips:
          url = 'http://' + ip + '/getRawData'
          logging.debug (url)
          sensor_dict = parseArduinoToDict (getWebFileObj(url))
          # logging.debug("got sensor_dict: %s a (%s)" % (sensor_dict, type(sensor_dict)))

          # now extract the current (LAST) values for selected NAMEs
          if ip == '192.168.0.98':
            map = map98
          elif ip == '192.168.0.100':
            map = map100
          else:
            log.error( "no field map exists for %" % ip)
            map = []
          for field in map:
            # logging.debug("field = %s a (%s)" % (field, type(field)))
            try:
              logging.debug ("Map field %s to %s = %s" % (field[0], field[1], sensor_dict[field[0]]['LAST']))
              collected_data.__setitem__(field[1], sensor_dict[field[0]]['LAST'])
            except:
              logging.warning("device %s is missing %s" % (ip, field[0]))

    json.dump (sensor_dict, stdout, indent=2, ensure_ascii=False)
    print("\nresulted in\n")
    json.dump (collected_data, stdout, indent=2, ensure_ascii=False)
    exit(0)


if __name__ == '__main__' :
  main()
