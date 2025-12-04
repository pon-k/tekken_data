import requests
import json
import logging
import traceback
import logging

logging.basicConfig(level=logging.INFO,
                    filename="t8data.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

replays_url = "https://wank.wavu.wiki/api/replays"

# HTTP request func that returns JSON from wavu API
 
def get_data(before_par=1764825684):
    try:
        response = requests.get(replays_url, params={"before": before_par})
        if response.ok:
            replay_data_raw = response.json()
            #replay_data_clean = json.dumps(replay_data_raw, indent=4)
            logging.info(f"{response.status_code}. Logging replays from {before_par}... ")
            return replay_data_raw
            
        else:            
            logging.error(response.status_code)
            return False

    except Exception as e:
        logging.error(traceback.format_exc())
        return False

# Loop that collects replays from specified period

def loop_func(limit_par, before):
    loop_limit = 0
    while before >= limit_par:
        data_fetch = get_data(before)
        if data_fetch:
            with open("t8data_dump", "w") as f:
                json.dump(data_fetch, f)
            before -= 700
        else:
            if loop_limit < 5:
                loop_limit += 1
                logging.error("Data fetch failed, retrying...")
            else:
                logging.error("Max retries reached, exiting loop.")
                break    
    
if __name__ == "__main__":
    loop_func(1654041600, 1764825684)
    logging.info("Data fetch complete.")