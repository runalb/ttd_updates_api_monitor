import requests
import time
import json
from datetime import datetime
import schedule

API_URL = "https://ttdevasthanams.ap.gov.in/cms/api/universal-latest-updates"

# File to store the latest known data
DATA_FILE = "latest_update_saved_data.json"

# File to log all JSON responses
LOG_FILE = "api_response_data_log.json"

# Interval in seconds to check for updates (e.g., 60 seconds = 1 minutes)
CHECK_INTERVAL = 60


def fetch_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None


def load_latest_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_latest_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)


def log_response(data):
    try:
        with open(LOG_FILE, "r") as file:
            log = json.load(file)
    except FileNotFoundError:
        log = []

    timestamped_data = {
        "timestamp": datetime.now().isoformat(),
        "data": data
    }

    log.append(timestamped_data)
    with open(LOG_FILE, "w") as file:
        json.dump(log, file, indent=4)


def check_for_updates():
    print("\nChecking for updates...")
    latest_data = load_latest_data()
    new_data = fetch_data()

    if new_data is None:
        print("No data fetched. Skipping this check.")
        return

    log_response(new_data)

    new_entries = [entry for entry in new_data if entry not in latest_data]

    if new_entries:
        save_latest_data(new_data)
        for entry in new_entries:
            print("\n[*] New updates found! :")
            print(f"{entry['attributes']['data']}")
            print(f"updatedAt: {entry['attributes']['updatedAt']}")
            print(f"createdAt: {entry['attributes']['createdAt']}")
            # print('\n')
    else:
        print("No new updates found.")


# def main():
#     while True:
#         check_for_updates()
#         time.sleep(CHECK_INTERVAL)



# START - Schedule
def job():
    check_for_updates()

def main():
    print("Script Runing...")

    # Schedule the job to run at specified time
    schedule.every().day.at("11:00").do(job) #11AM
    schedule.every().day.at("19:00").do(job) #07PM
    # schedule.every().day.at("22:55").do(job) #test

    while True:
        schedule.run_pending()
        time.sleep(600)  # wait 10 minute
# END - Schedule


if __name__ == "__main__":
    main()
