import requests
import time
import json
from datetime import datetime
import schedule
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

API_URL = "https://ttdevasthanams.ap.gov.in/cms/api/universal-latest-updates"

# File to store the latest known data
DATA_FILE = "ttd_latest_update_saved_data.json"

# File to log all JSON responses
LOG_FILE = "ttd_api_response_data_log.json"

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


def log_response(data, status):
    try:
        with open(LOG_FILE, "r") as file:
            log = json.load(file)
    except FileNotFoundError:
        log = []

    timestamped_data = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "data": data
    }

    log.append(timestamped_data)
    with open(LOG_FILE, "w") as file:
        json.dump(log, file, indent=4)


def check_for_updates():
    print(f"[{datetime.now().isoformat()}]")
    print("Checking for updates...")
    latest_data = load_latest_data()
    new_data = fetch_data()
    status = "Data feched"

    if new_data is None:
        print("No data fetched. Skipping this check.\n")
        return

    try:
        new_entries = [entry for entry in new_data if entry not in latest_data]

        if new_entries:
            save_latest_data(new_data)
            status = "New updates found"
            print("[*] New updates found! :")

            for entry in new_entries:
                data = entry['attributes']['data']
                updated_at = entry['attributes']['updatedAt']
                created_at = entry['attributes']['createdAt']

                # print(f"{data}")
                # print(f"  updatedAt: {updated_at}")
                # print(f"  createdAt: {created_at}")
                # print('\n')

                # Send email for each new update
                subject = "TTD API - New Update Found - " + datetime.now().isoformat() 
                body = f"\n{data}\n- Updated At: {updated_at}\n- Created At: {created_at}"
                print(body)
                send_email(subject, body, "runal.banarse@gmail.com")

        else:
            status = "No new updates found"
            print(status)

    except Exception as e:
        status = "Exception Occurs: " + str(e)
        print("Failed to process new data.")
        print("Error:\n",e)

    finally:
        # Log the fetched data
        log_response(new_data, status)
        print()
    


# def main():
#     # while True:
#         check_for_updates()
#         time.sleep(CHECK_INTERVAL)


# START - Schedule
def job():
    try:
        check_for_updates()
        check_for_updates()
        print("Sleep...\n")

    except Exception as e:
        print("Exception Occurs:\n" + str(e))
        # Send email
        subject = "TTD API - Error - " + datetime.now().isoformat() 
        body = "Exception Occurs:\n\n" + str(e)
        send_email(subject, body, "hello@runalb.com")


def main():
    print("Script Runing...\n")
    job()

    # Schedule the job to run at specified time
    schedule.every().day.at("11:00").do(job)  # 11AM
    schedule.every().day.at("19:00").do(job)  # 07PM
    # schedule.every().day.at("22:55").do(job) #test

    while True:
        schedule.run_pending()
        time.sleep(600)  # wait 10 minute
# END - Schedule


def send_email(subject, body, to_address):
    from_address = "sender email"
    password = "sender password"

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the server and send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Update with your SMTP server and port
        server.starttls()
        server.login(from_address, password)
        text = msg.as_string()
        server.sendmail(from_address, to_address, text)
        server.quit()
        print(f"- Email sent to: {to_address}")
    except Exception as e:
        print(f"Failed to send email: {e}")


if __name__ == "__main__":
    main()
 
