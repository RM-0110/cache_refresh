import requests
import time
from datetime import datetime

def send_email(subject, body):
    # Replace this function with your actual email-sending implementation.
    print(f"Subject: {subject}\nBody:\n{body}")

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
        'x-session-id': 'undefined'
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
        'x-session-id': 'undefined'
    }
    payload = {"task_id": task_id}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def main():
    # Step 1: Trigger the cache update
    t1 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get the local time in IST
    try:
        cache_update_response = trigger_cache_update()
    except Exception as e:
        # Log the error and exit the script without sending an email
        print(f"Error occurred while triggering cache update: {e}")
        return

    # Step 2: Extract task_id values
    task_id_list = [item['task_id'] for item in cache_update_response]

    # Step 3: Wait for 1 minute
    time.sleep(60)

    # Step 4: Check the status of each task_id
    failed_tasks = []
    for task_id in task_id_list:
        try:
            status_response = check_status(task_id)
            if status_response.get("status") != "SUCCESS":
                failed_tasks.append(task_id)
        except Exception as e:
            # Log the error and consider the task as failed
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