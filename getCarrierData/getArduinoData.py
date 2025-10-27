import requests
from sys import exit
import argparse

"""
  get data from an arduino temp_sensor that looks like this:
    NAME,MIN,MAX,AVG,LAST,COUNT
    test2,69.5,69.6,69.5,69.6,27
    %Humidity,46.9,47.6,47.2,46.9,27
    Barometer,29.8,29.8,29.8,29.8,27
  OR
    NAME,MIN,MAX,AVG,LAST,COUNT
    Inside,67.7,69.3,68.8,69.3,48
    Outside,53.2,56.4,54.8,54.6,48
    %Humidity,45.9,46.1,46.0,46.0,48
    Barometer,29.8,29.8,29.8,29.8,48

  extract temp and humidity data and return it reformatted like this:
    DATE,TIME,CurrentInside,CurrentOutside,CurrentHumidity  where Current <=> LAST
"""
def curl_get(url, params=None, headers=None, timeout=10):
  resp = requests.get(url, params=params, headers=headers, timeout=timeout)
  resp.raise_for_status()         # raises on HTTP error codes
  return resp.text

def main():
  sensor_ips = [ '192.168.0.98', '192.168.0.100' ]
  for ip in sensor_ips:
    url = 'http://' + ip + '/getRawData'
    print (url)
    sensor_data = curl_get (url)
    print (sensor_data)

  exit(0)


if __name__ == '__main__' :
  main()
