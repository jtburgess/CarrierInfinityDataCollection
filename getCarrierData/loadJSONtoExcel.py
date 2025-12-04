import argparse
import datetime
import json
import logging
from openpyxl import load_workbook
from sys import exit, stdout, exc_info

# DataDir = '/Users/jburgess/Library/CloudStorage/Dropbox/CarrierDataCollection/'
DataDir = "../"
ExcelFile = 'carrier infinity usage stats.xlsx'

# fast efficient way to turn numbers as strings into int or float as needed
def str2num(s):
  try:
      return int(s)
  except:
    try:
      return float(s)
    except:
      return s

def loadJsonToExcel (jsonFile: str, sheet_name: str):
  logging.debug (f"Read Json file {DataDir}{jsonFile}")

  wb = load_workbook(DataDir + ExcelFile)
  logging.debug (f"worksheets in {ExcelFile} are: {wb.sheetnames}")

  ws = wb[sheet_name]
  logging.info (f"sheet {ws.title} has {ws.max_row} rows to start")

  # the list of fields we want to collect from the JSON is in row 1
  field_list = list(next(ws.iter_rows(values_only=True, max_row=1)))
  num_fields = len(field_list)
  logging.debug(f"{num_fields} field names in row 1: {field_list}")

  # now load all the saved data into excel, one row at a time, arranged by the field_list columns
  with open(DataDir + jsonFile, 'r') as jf:
    new_line_count = 0
    for line in jf:
      new_row = [None] * num_fields
      input_dict = json.loads(line)
      new_line_count +=1
      i=0
      for field in field_list:
        if field in input_dict:
          new_row[i] = str2num ( input_dict[field] )
        else:
          logging.error(f"line {new_line_count} in the input is missing field {field}")
        i+=1
      logging.debug(f"new row #{new_line_count}: {new_row}")
      ws.append(new_row)

  wb.save(DataDir + ExcelFile)
  logging.info (f"appended {new_line_count} rows")

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
