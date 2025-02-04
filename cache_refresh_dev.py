import requests
import time
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

username = "riddhimann"
password = os.getenv('VYAS_PASSWORD')

def send_email(subject, body):
    print("Preparing to send email...")
    sender_email = "riddhimann@navyatech.in"
    receiver_emails = ["riddhimann@navyatech.in", "kirana@navyatech.in"]
    password = os.getenv('APP_PASSWORD')
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg["To"] = ", ".join(receiver_emails)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        print("Connecting to SMTP server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_emails, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")

def token(username, password):
    print("Fetching authentication token...")
    API = "https://alpha.bestopinions.us/alphaBackend/accounts/auth/token/"
    headers = {"Content-Type": "application/json"}
    body = {
        "client_id": "bKN4Vycdhnhz8ytVwi3nbxh18MrOloSMTD8Z78Bp",
        "username": username,
        "password": password,
        "grant_type": "password",
        "endUris": "AUTHENTICATE_USER_CREDS"
    }
    response = requests.post(API, json=body, headers=headers)
    output = response.json()
    cbs_token = output['cbs_access_token']
    print("Authentication token received.")
    return cbs_token

cbs_token = token(username, password)

def trigger_cache_update():
    print("Triggering cache update...")
    url = 'https://alpha.bestopinions.us/cbsearch/api/cacheupdate/'
    headers = {
        'sec-ch-ua-platform': '"Windows"',
        'Referer': 'https://alpha.bestopinions.us/cbsearchcacherefresh',
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'x-session-id': 'undefined',
        'Cookie': f'auth_cbs_token={cbs_token}'
    }
    payload = {"cachename": "all"}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    print("Cache update triggered successfully.")
    return response.json()

def check_status(task_id):
    print(f"Checking status for task ID: {task_id}...")
    url = 'https://alpha.bestopinions.us/cbsearch/api/cacheupdatestatus/'
    headers = {
        'sec-ch-ua-platform': '"Windows"',
        'Referer': 'https://alpha.bestopinions.us/cbsearchcacherefresh',
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'x-session-id': 'undefined',
        'Cookie': f'auth_cbs_token={cbs_token}'
    }
    payload = {"task_id": task_id}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    print(f"Status for task {task_id}: {response.json()}")
    return response.json()

def main():
    t1 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Script started at {t1}")
    
    try:
        cache_update_response = trigger_cache_update()
    except Exception as e:
        print(f"Error occurred while triggering cache update: {e}")
        return
    
    task_id_list = [item['task_id'] for item in cache_update_response]
    print(f"Task IDs received: {task_id_list}")
    
    print("Waiting for 30 seconds before checking task status...")
    time.sleep(30)
    
    failed_tasks = []
    for task_id in task_id_list:
        try:
            status_response = check_status(task_id)
            if status_response.get("status") != "SUCCESS":
                failed_tasks.append(task_id)
        except Exception as e:
            print(f"Error checking status for task_id {task_id}: {e}")
            failed_tasks.append(task_id)
    
    if not failed_tasks:
        subject = "CBsearch Cache Update Task Completed Successfully"
        body = f"CBsearch cache update task initiated at {t1}\nAll tasks have passed."
        print("All tasks completed successfully.")
    else:
        subject = "CBsearch Cache Update Task Failed"
        failed_tasks_str = ", ".join(failed_tasks)
        body = f"CBsearch cache update task initiated at {t1}\nFailed tasks: {failed_tasks_str}"
        print(f"Failed tasks: {failed_tasks_str}")
    
    send_email(subject, body)
    print("Script execution completed.")

if __name__ == "__main__":
    main()
