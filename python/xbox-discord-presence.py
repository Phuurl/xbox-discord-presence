import os
import sys
import time

import requests
import yaml
from pypresence import Presence

with open(os.path.join(os.path.dirname(__file__), "config.yaml"), "r") as config_file:
    config = yaml.safe_load(config_file)

RPC = Presence(config["discord_client_id"])
RPC.connect()

presence_url = "https://xapi.us/v2/" + config["xbox_target_profile"] + "/presence"
headers = {"X-AUTH": config["xbox_api_key"]}
current_status = ""

while True:  # The presence will stay on as long as the program is running
    r = requests.get(presence_url, headers=headers)
    json_response = r.json()

    active_game = ""
    try:
        for i in json_response["devices"]:
            if i["type"] == "XboxOne":
                for t in i["titles"]:
                    if t["placement"] == "Full":
                        active_game = t["name"]
                        break
    except Exception as e:
        print(e)
        print(json_response)
        sys.exit(1)

    if active_game == "":
        if current_status != "":
            RPC.clear()
            current_status = ""
            print("Status cleared")
    else:
        if current_status != active_game:
            RPC.update(state=config["xbox_type"], details=active_game,
                       large_image="big-logo-1", large_text="Gamertag: " + config["xbox_profile_name"])
            current_status = active_game
            print("Status set to " + active_game)

    time.sleep(300)  # Xbox API is limited to 60 requests/hour, so only refresh every 5 minutes
