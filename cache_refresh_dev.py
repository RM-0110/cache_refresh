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
    # Set up email credentials and server
    sender_email = "riddhimann@navyatech.in"  # Your email address
    receiver_emails = ["riddhimann@navyatech.in", "kirana@navyatech.in"]  # Receiver email address (can be the same as sender)
    password = os.getenv('APP_PASSWORD')  # Get password from environment variables

    # Set up the MIME structure for the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg["To"] = ", ".join(receiver_emails)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Establish connection to Gmail SMTP server and send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure the connection
        server.login(sender_email, password)  # Log in using the email credentials
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)  # Send email
        server.quit()  # Close the connection
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")

def token(username, password):
    API = "https://alpha.bestopinions.us/alphaBackend/accounts/auth/token/"
    headers = {
    "Content-Type": "application/json"
    }
    body = {"client_id":"bKN4Vycdhnhz8ytVwi3nbxh18MrOloSMTD8Z78Bp","username":username,"password":password,"grant_type":"password","endUris":"AUTHENTICATE_USER_CREDS"}
    response = requests.post(API, json = body, headers= headers)
    output = response.json()
    cbs_token = output['cbs_access_token']
    print(cbs_token)
    return cbs_token

cbs_token = token(username, password)

def trigger_cache_update():
    url = 'https://alpha.bestopinions.us/cbsearch/api/cacheupdate/'
    headers = {
        'sec-ch-ua-platform': '"Windows"',
        'Referer': 'https://alpha.bestopinions.us/cbsearchcacherefresh',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, /',
        'Content-Type': 'application/json',
        'x-session-id': 'undefined',
        'Cookie': f'auth_cbs_token={cbs_token}'
    }
    payload = {"cachename": "all"}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def check_status(task_id):
    url = 'https://alpha.bestopinions.us/cbsearch/api/cacheupdatestatus/'
    headers = {
        'sec-ch-ua-platform': '"Windows"',
        'Referer': 'https://alpha.bestopinions.us/cbsearchcacherefresh',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, /',
        'Content-Type': 'application/json',
        'x-session-id': 'undefined',
        'Cookie': f'auth_cbs_token={cbs_token}'
    }
    payload = {"task_id": task_id}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def main():
    t1 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
    try:
        cache_update_response = trigger_cache_update()
    except Exception as e:
        print(f"Error occurred while triggering cache update: {e}")
        return

    task_id_list = [item['task_id'] for item in cache_update_response]

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

    # Step 5: Send email based on the results
    if not failed_tasks:
        subject = "CBsearch Cache Update Task Completed Successfully"
        body = f"CBsearch cache update task has been initiated at {t1}\nAll the tasks have passed."
    else:
        subject = "CBsearch Cache Update Task Failed"
        if len(failed_tasks) == 1:
            body = f"CBsearch cache update task has been initiated at {t1}\n{failed_tasks[0]} has failed."
        else:
            failed_tasks_str = ", ".join(failed_tasks)
            body = f"CBsearch cache update task has been initiated at {t1}\nThe following tasks have failed: {failed_tasks_str}"

    send_email(subject, body)

if __name__ == "__main__":
    main()
