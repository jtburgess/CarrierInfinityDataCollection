#!/usr/bin/env python3
"""
parse_sensor_to_dict.py

Read a sensor-style CSV and return a mapping from NAME -> row-by-column-name
so you can do things like:

    rows = parse_sensor_csv_to_map(open("input.csv"))
    print(rows["Inside"]["LAST"])

sample data:
NAME,MIN,MAX,AVG,LAST,COUNT
Inside,65.3,68.8,67.2,68.8,2095
Outside,36.8,56.9,45.6,50.2,2095
%Humidity,41.7,43.3,42.4,42.7,2095
Barometer,30.0,30.1,30.1,30.1,2095

Behavior:
- Header names are UPPERCASE for lookup
- The NAME column is used as the key for the top-level mapping. It should be the first column.
- If there are multiple rows with the same NAME, the mapping value becomes a list of row dicts (in encountered order).
- all rows must have the same number of columns
- Numeric-looking values are converted to int or float when possible.
- Can read from a filename or stdin when used as a script; prints JSON output.

Usage (as library):
    from parse_sensor_to_dict import parse_sensor_csv_to_map
    with open("input.csv", newline="") as f:
        rows_map = parse_sensor_csv_to_map(f)
    print(rows_map["Inside"]["LAST"])

Usage (CLI):
    python3 parse_sensor_to_dict.py input.csv
    cat input.csv | python3 parse_sensor_to_dict.py
"""

from __future__ import annotations
import sys
import csv
import json
from typing import Dict, Any, IO, Union

import logging
logger = logging.getLogger(__name__)


def _to_number_if_possible(s: str) -> Union[int, float, str]:
    s = s.strip()
    if s == "":
        return s

    try:
        # Allow floats with decimal point
        if "." in s:
            return float(s)
        else:
            return int(s)

    except Exception:
        # float and/or int conversion failed
        return s


def parse_sensor_csv_to_map( fileobj: IO[str] ) -> Dict[str, Any]:
    """
    Parse a CSV from fileobj and return a mapping: NAME -> row-dict (keys uppercase).
    ASSUME Name is first column, first row is UPPER_CASE field names
    If multiple rows share the same NAME, the value will be a list of dicts.
    """
    reader = csv.reader(fileobj)
    try:
        header_row = next(reader)
    except StopIteration:
        return {}

    header = [h.strip() for h in header_row]

    # Find NAME column (case-insensitive). If not present, assume first column is NAME.
    name_idx = None
    for i, h in enumerate(header):
        if h == "NAME":
            name_idx = i
            break
    if name_idx is None:
        name_idx = 0
        # Prepend NAME to header so mapping keys remain consistent
        # but we will keep the original header columns as-is (we assume first column is name).
        # Build a synthetic header list for mapping.
        if header:
            # ensure header[0] is NAME for mapping
            header[0] = "NAME"

    # Ensure header length reflects columns we expect for mapping; we'll map by index.
    # Process each row: pad with "" if short, truncate if long.
    result: Dict[str, Any] = {}

    for row in reader:
        row = [c.strip() for c in row]
        # pad or truncate to header length
        if len(row) < len(header):
            row += [""] * (len(header) - len(row))
        elif len(row) > len(header):
            # If row longer, keep extras and create synthetic header names for them
            # (e.g., "EXTRA_0", "EXTRA_1")
            extra_count = len(row) - len(header)
            for i in range(extra_count):
                header.append(f"EXTRA_{i}")
        # Build row dict keyed by uppercase header names
        row_dict: Dict[str, Any] = {}
        for i, val in enumerate(row[: len(header)]):
            key = header[i]
            row_dict[key] = _to_number_if_possible(val)

        # Determine name key (preserve the actual NAME cell value as the lookup key)
        name_value = row[name_idx].strip() if name_idx < len(row) else ""
        if name_value == "":
            # fallback: try to use a generated name if empty
            name_value = f"<unnamed_row_{len(result)+1}>"

        # Insert into result, handling duplicates
        existing = result.get(name_value)
        if existing is None:
            result[name_value] = row_dict
        else:
            # If existing is single dict, convert it to list
            if isinstance(existing, list):
                existing.append(row_dict)
            else:
                result[name_value] = [existing, row_dict]

    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Collect data from Arduino temp sensor(s)."
    )
    # Example argument; add more as needed
    parser.add_argument( "-d", "--debug", action="store_true", help="Enable debug output" )
    parser.add_argument('file', nargs='*', help="name of CSV data file to use")
    args = parser.parse_args()

    if args.debug:
        print("Debug mode enabled.")
        logger.setLevel(logging.DEBUG)

    if len(args.file) == 1:
        logger.debug("reading CSV data from: %s" % args.file[0])
        infile = open(args.file[0], newline="")
    elif len(args.file) == 0:
        logger.debug("reading CSV data from stdin")
        infile = sys.stdin
    else:
        print ("Only one file arg accepted")

    rows_map = parse_sensor_csv_to_map(infile)
    # Write JSON to stdout for easy inspection
    print (json.dump(rows_map, sys.stdout, indent=2, ensure_ascii=False))
    sys.stdout.write("\n")

    if infile is not sys.stdin:
        infile.close()
    return 0

if __name__ == "__main__":
    main()
