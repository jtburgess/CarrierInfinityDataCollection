import argparse
import datetime
import json
import logging
from openpyxl import load_workbook
from sys import exit, stdout, exc_info

# DataDir = '/Users/jburgess/Library/CloudStorage/Dropbox/CarrierDataCollection/'
DataDir = "../"
ExcelFile = 'carrier infinity usage stats.xlsx'

def loadJsonToExcel (jsonFile: str, sheet_name: str):
  logging.debug (f"Read Json file {DataDir}{jsonFile}")

  wb = load_workbook(DataDir + ExcelFile)
  logging.debug (f"worksheets in {ExcelFile} are: {wb.sheetnames}")

  ws = wb[sheet_name]
  logging.debug (f"ws {sheet_name} title: {ws.title}, has {ws.max_row} rows")

  # the list of fields we want to collect from the JSON is in row 1
  field_list = list(next(ws.iter_rows(values_only=True, max_row=1)))
  logging.debug(f"field names in row 1: {field_list}")

  with open(DataDir + jsonFile, 'r') as jf:
    for jline in jf:
      jsonData = json.loads ( jline )
  logging.debug (f"read {len(jsonData)} rows")

  wb.save()

##########
def main():
  parser = argparse.ArgumentParser(
    description="Load collected JSON into the excel spreadsheet"
  )
  # Example argument; add more as needed
  parser.add_argument( "-d", "--debug", action="store_true", help="Enable debug output" )
  parser.add_argument( "-R", "--realtime", action="store_true", help="Load JSON Realtime data" )
  parser.add_argument( "-D", "--daily", action="store_true", help="Load JSON Daily Fields" )
  args = parser.parse_args()

  if args.debug:
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Debug mode enabled.")
  else:
    logging.basicConfig(level=logging.INFO)
  logging.debug ("Args=[ %s ]" % args)

  if args.realtime and args.daily:
    logging.error ("You must specify only ONE of realtime and daily")
    exit(1)
  elif args.realtime:
    loadJsonToExcel ( 'CarrierRealTimeData.json', 'RealTime' )
  elif args.daily:
    loadJsonToExcel ( 'CarrierDailyData.json', 'Daily' )
  else:
    logging.error ("You must specify either --realtime or --daily")
    exit(1)

if __name__ == "__main__":
  main()
