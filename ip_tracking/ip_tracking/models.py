from django.db import models

# Create your models here.

"""
Models for IP tracking and request logging.
"""

from django.db import models
from django.utils import timezone
from django.db import models




class RequestLog(models.Model):
    """
    Model to store information about incoming HTTP requests.
    Tracks IP addresses, timestamps, and request paths for security and analytics.
    """
    ip_address = models.GenericIPAddressField(
        protocol='both',  # Supports both IPv4 and IPv6
        help_text="IP address of the client making the request"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True,  # Index for faster queries by time
        help_text="When the request was made"
    )
    path = models.CharField(
        max_length=500,
        help_text="URL path that was requested"
    )
    method = models.CharField(
        max_length=10,
        default='GET',
        help_text="HTTP method used (GET, POST, etc.)"
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        help_text="User agent string from the request"
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['-timestamp']  # Most recent first
        verbose_name = "Request Log"
        verbose_name_plural = "Request Logs"
        indexes = [
            models.Index(fields=['ip_address', '-timestamp']),
            models.Index(fields=['path', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.ip_address} - {self.path} - {self.timestamp}"

    def __repr__(self):
        return f"<RequestLog: {self.ip_address} [{self.method}] {self.path}>"


class BlockedIP(models.Model):
    """
    Model to store blacklisted IP addresses.
    IPs in this table will be blocked from accessing the application.
    """
    ip_address = models.GenericIPAddressField(
        protocol='both',  # Supports both IPv4 and IPv6
        unique=True,  # Each IP can only be blocked once
        help_text="IP address to block from accessing the site"
    )
    reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason why this IP was blocked"
    )
    blocked_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this IP was added to the blacklist"
    )
    blocked_by = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Who blocked this IP (admin username or system)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this block is currently active"
    )

    class Meta:
        ordering = ['-blocked_at']
        verbose_name = "Blocked IP"
        verbose_name_plural = "Blocked IPs"
        indexes = [
            models.Index(fields=['ip_address', 'is_active']),
        ]

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"{self.ip_address} ({status})"

    def __repr__(self):
        return f"<BlockedIP: {self.ip_address}>"

    @classmethod
    def is_blocked(cls, ip_address):
        """
        Check if an IP address is currently blocked.

        Args:
            ip_address (str): IP address to check

        Returns:
            bool: True if IP is blocked, False otherwise
        """
        return cls.objects.filter(
            ip_address=ip_address,
            is_active=True
        ).exists()

    def unblock(self):
        """Mark this IP as unblocked."""
        self.is_active = False
        self.save()