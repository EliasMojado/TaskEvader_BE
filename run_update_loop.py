#!/usr/bin/env python3
import sys, subprocess, schedule, time

PYTHON = sys.executable       # <-- absolute path to your venv’s python
MANAGE = "manage.py"

def update_statuses():
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] Running update_node_statuses…")
    subprocess.run([PYTHON, MANAGE, "update_node_statuses"])
    print(f"[{timestamp}] update_node_statuses completed.\n")

# schedule the job
schedule.every(10).minutes.do(update_statuses)

if __name__ == "__main__":
    print("Scheduler started: will run update_node_statuses every 10 minutes.")
    update_statuses()  # run once at startup
    while True:
        schedule.run_pending()
        time.sleep(1)
