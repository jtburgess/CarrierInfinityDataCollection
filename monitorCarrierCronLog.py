#!/usr/bin/env python3
# this runs in Indigo every 6 hours as a Condition in a Schedule. 
# the Carrier_cron runs every 30 minutes, 
# so to get a full set with NO errors, I need to look at the last 12 lines
# if I look at 20, there might be overlap, but not if there are errors
# save the errors in a temp file, to be used by the email Action in the indigo Schedule
import subprocess
result = subprocess.run(
    "tail -20 /Users/jburgess/Dropbox/CarrierDataCollection/carrier_cron.log | grep ERROR > /private/tmp/CarrierCronLogErrors.txt; wc -l < /private/tmp/CarrierCronLogErrors.txt",
    shell=True,
    capture_output=True,
    text=True
)

num_err = int(result.stdout.strip())
# print (num_err)
return (num_err != 0)
