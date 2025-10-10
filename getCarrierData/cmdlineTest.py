#! python3
# run with "python3 src/carrier_api/stub.py"
import logging
from asyncio import sleep, create_task
from getpass import getpass
from pathlib import Path
from PRIVATE import UserName, PassWord
import sys

import asyncio

#import os
#APIlib = os.path.dirname(__file__)+"/carrier_api"
#sys.path.append(APIlib)
#print (APIlib)

logger = logging.getLogger("carrier_api")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


from carrier_api.api_connection_graphql import ApiConnectionGraphql
from carrier_api.api_websocket_data_updater import WebsocketDataUpdater
from carrier_api.const import FanModes

async def main():
    username = UserName
    password = PassWord
    api_connection = None
    try:
        api_connection = ApiConnectionGraphql(username=username, password=password)
        systems = await api_connection.load_data()
        print([system.__repr__() for system in systems])
        async def listener():
            async def output(message):
                print([system.__repr__() for system in systems])
            ws_data_updater = WebsocketDataUpdater(systems=systems)
            api_connection.api_websocket.callback_add(ws_data_updater.message_handler)
            api_connection.api_websocket.callback_add(output)
            await api_connection.api_websocket.create_task_listener()

        listener = create_task(listener(), name="listener")

        await api_connection.set_config_manual_activity(
            system_serial=systems[0].profile.serial,
            zone_id=systems[0].config.zones[0].api_id,
            heat_set_point='73',
            cool_set_point='80',
            fan_mode=FanModes.LOW,
        )
        await sleep(500)
    finally:
        if api_connection is not None:
            await api_connection.cleanup()


asyncio.run(main())
