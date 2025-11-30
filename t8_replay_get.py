import requests
import json
import logging
import traceback

headers = {"Accept-Encoding": "gzip, deflate, br"}
replays_url = "https://wank.wavu.wiki/api/replays"

try:
    response = requests.get(replays_url)
    if response.ok:
        replay_data_raw = response.json()
        replay_data_clean = json.dumps(replay_data_raw, indent=4)
        print(replay_data_clean)
        
    else:
        print(response.status_code)

except Exception as e:
    logging.error(traceback.format_exc())