# aegismail/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from pymongo import MongoClient
from aegismailapp.notifications import notify_user_of_security_event

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aegismail.settings')

# Initialize Celery app with Redis as the broker
app = Celery('aegismail', broker='redis://localhost:6379/0')

# Using a string here means the worker doesn't have to serialize the configuration
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps
app.autodiscover_tasks()

# MongoDB client and log collection setup
client = MongoClient("mongodb://localhost:27017/")
db = client['Clusters']
logs_collection = db['logs']

# Task to monitor security events (login attempts) in MongoDB
@app.task
def monitor_security_events():
    # Example logic for detecting suspicious events
    logs = logs_collection.find({"action": "login_attempt"})
    suspicious_ips = ["192.168.0.1", "10.0.0.1"]  # Example suspicious IPs
    for log in logs:
        if log['details'].get('ip_address') in suspicious_ips:  # Example logic
            # Notify user about suspicious login attempt
            notify_user_of_security_event(
                user_token=log['details']['user_token'],
                event_details="Suspicious login attempt detected"
            )

# Task to debug and print request details
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
