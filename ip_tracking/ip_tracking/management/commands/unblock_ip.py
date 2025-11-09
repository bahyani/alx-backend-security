"""
Management command to unblock IP addresses.

Usage:
    python manage.py unblock_ip 192.168.1.100
"""

from django.core.management.base import BaseCommand, CommandError
from ip_tracking.ip_tracking.models import BlockedIP


class Command(BaseCommand):
    """
    Django management command to remove IP addresses from the blacklist.
    """

    help = 'Unblock an IP address to allow it to access the site'

    def add_arguments(self, parser):
        """Define command-line arguments."""
        parser.add_argument(
            'ip_address',
            type=str,
            help='IP address to unblock'
        )

    def handle(self, *args, **options):
        """Execute the unblock command."""
        ip_address = options['ip_address']

        try:
            # Find the blocked IP
            blocked_ip = BlockedIP.objects.filter(
                ip_address=ip_address,
                is_active=True
            ).first()

            if not blocked_ip:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  IP {ip_address} is not currently blocked.'
                    )
                )
                return

            # Unblock the IP
            blocked_ip.unblock()

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ IP {ip_address} has been unblocked successfully!'
                )
            )

        except Exception as e:
            raise CommandError(f'❌ Error unblocking IP: {str(e)}')