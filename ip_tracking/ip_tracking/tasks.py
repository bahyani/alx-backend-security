from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import RequestLog, SuspiciousIP


@shared_task
def detect_anomalies():
    # Define sensitive paths
    sensitive_paths = ['/admin', '/login']

    # Get time window (last 1 hour)
    one_hour_ago = timezone.now() - timedelta(hours=1)

    # Get all IPs with requests in the last hour
    recent_logs = RequestLog.objects.filter(timestamp__gte=one_hour_ago)

    # Group by IP and count requests
    ip_request_counts = recent_logs.values('ip_address').annotate(
        request_count=models.Count('id')
    )

    # Check for IPs exceeding 100 requests/hour
    for ip_data in ip_request_counts:
        ip = ip_data['ip_address']
        count = ip_data['request_count']
        if count > 100:
            # Check if IP is already flagged
            if not SuspiciousIP.objects.filter(ip_address=ip).exists():
                SuspiciousIP.objects.create(
                    ip_address=ip,
                    reason=f"Exceeded 100 requests/hour: {count} requests"
                )

    # Check for IPs accessing sensitive paths
    sensitive_logs = recent_logs.filter(path__in=sensitive_paths)
    for log in sensitive_logs:
        ip = log.ip_address
        if not SuspiciousIP.objects.filter(ip_address=ip).exists():
            SuspiciousIP.objects.create(
                ip_address=ip,
                reason=f"Accessed sensitive path: {log.path}"
            )