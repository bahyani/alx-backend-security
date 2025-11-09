# ALX Backend Security: IP Tracking System

This repository contains a Django-based IP tracking system for the ALX Backend Security project. It implements request logging, rate limiting, IP geolocation analytics, and anomaly detection to enhance web application security and analytics while ensuring compliance with privacy standards.

## Project Overview

The `ip_tracking` Django app provides tools to:
- Log IP addresses and request metadata using middleware.
- Apply rate limiting to prevent abuse (Task 1).
- Enhance logs with geolocation data (country, city) using a third-party API (Task 2).
- Detect anomalies (e.g., high request volumes or access to sensitive paths) and flag suspicious IPs (Task 4).

The system uses Django middleware, Celery for asynchronous tasks, Redis for caching and task queuing, and integrates with `ipinfo.io` for geolocation.

## Features

- **Request Logging**: Logs IP addresses, request paths, methods, timestamps, and geolocation data (country, city).
- **Rate Limiting**: Limits authenticated users to 10 requests/minute and anonymous users to 5 requests/minute on sensitive endpoints (e.g., `/login`).
- **IP Geolocation**: Enhances logs with country and city data, cached for 24 hours to optimize performance.
- **Anomaly Detection**: Flags IPs exceeding 100 requests/hour or accessing sensitive paths (`/admin`, `/login`) using an hourly Celery task.
- **Privacy Compliance**: Supports GDPR/CCPA through anonymization and transparent data policies.

## Requirements

- Python 3.8+
- Django 4.2+
- Redis (for caching and Celery)
- Dependencies (see `requirements.txt`):
  - `django-ratelimit`
  - `django-ipgeolocation`
  - `django-redis`
  - `celery`
  - `django-celery-beat`
  - `python-decouple`

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/<your-username>/alx-backend-security.git
   cd alx-backend-security
