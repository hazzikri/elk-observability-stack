"""
Log Generator — simulates realistic application log streams for the ELK stack demo.
Writes JSON-structured application logs and Nginx-style access logs continuously.
"""
import json
import os
import random
import time
from datetime import datetime, timezone

LOG_DIR = "/var/log/app"
APP_LOG = os.path.join(LOG_DIR, "application.log")
ACCESS_LOG = os.path.join(LOG_DIR, "access.log")

ENDPOINTS = ["/api/orders", "/api/users", "/api/products", "/health", "/login", "/dashboard", "/api/metrics"]
METHODS = ["GET", "POST", "PUT", "DELETE"]
STATUS_WEIGHTS = [200, 200, 200, 201, 301, 400, 401, 403, 404, 500, 503]
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "curl/7.88.1",
    "PostmanRuntime/7.36.3",
    "python-requests/2.31.0",
]
IPS = ["103.12.45.67", "192.168.1.10", "10.0.0.25", "172.16.8.99", "203.0.113.42"]
SERVICES = ["auth-service", "order-service", "product-catalog", "notification-service", "api-gateway"]
LOG_LEVELS = ["INFO", "INFO", "INFO", "WARN", "ERROR"]

os.makedirs(LOG_DIR, exist_ok=True)

def write_access_log():
    now = datetime.now(timezone.utc).strftime("%d/%b/%Y:%H:%M:%S +0000")
    ip = random.choice(IPS)
    method = random.choice(METHODS)
    endpoint = random.choice(ENDPOINTS)
    status = random.choice(STATUS_WEIGHTS)
    size = random.randint(200, 15000)
    ua = random.choice(USER_AGENTS)
    line = f'{ip} - - [{now}] "{method} {endpoint} HTTP/1.1" {status} {size} "-" "{ua}"\n'
    with open(ACCESS_LOG, "a") as f:
        f.write(line)

def write_app_log():
    level = random.choice(LOG_LEVELS)
    service = random.choice(SERVICES)
    messages = {
        "INFO": [
            "Request processed successfully",
            "Cache hit for key user:session:{uid}".format(uid=random.randint(1000, 9999)),
            "Database connection pool: {used}/20 connections in use".format(used=random.randint(1, 18)),
            "Scheduled job completed in {ms}ms".format(ms=random.randint(10, 500)),
        ],
        "WARN": [
            "Response time exceeded threshold: {ms}ms".format(ms=random.randint(800, 2000)),
            "Retry attempt {n}/3 for upstream service".format(n=random.randint(1, 3)),
            "Cache miss — falling back to database",
        ],
        "ERROR": [
            "Database connection timeout after 30s",
            "Unhandled exception in request handler",
            "Downstream service returned 503 — circuit breaker OPEN",
        ]
    }
    msg = random.choice(messages[level])
    log = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "service": service,
        "message": msg,
        "trace_id": f"trace-{random.randint(100000, 999999)}",
        "duration_ms": random.randint(5, 3000)
    }
    with open(APP_LOG, "a") as f:
        f.write(json.dumps(log) + "\n")

print("Log generator started. Writing logs to", LOG_DIR)
while True:
    write_access_log()
    write_app_log()
    time.sleep(random.uniform(0.5, 2.0))
