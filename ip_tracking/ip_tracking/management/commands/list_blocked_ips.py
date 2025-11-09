"""
Management command to list all blocked IP addresses.

Usage:
    python manage.py list_blocked_ips
    python manage.py list_blocked_ips --all  # Include inactive blocks
"""

from django.core.management.base import BaseCommand
from ip_tracking.ip_tracking.models import BlockedIP


class Command(BaseCommand):
    """
    Django management command to list all blocked IP addresses.
    """

    help = 'List all blocked IP addresses'

    def add_arguments(self, parser):
        """Define command-line arguments."""
        parser.add_argument(
            '--all',
            action='store_true',
            help='Show all blocked IPs including inactive ones'
        )

    def handle(self, *args, **options):
        """Execute the list command."""
        show_all = options['all']

        # Get blocked IPs
        if show_all:
            blocked_ips = BlockedIP.objects.all()
            title = 'All Blocked IPs (Active and Inactive)'
        else:
            blocked_ips = BlockedIP.objects.filter(is_active=True)
            title = 'Currently Blocked IPs'

        # Display results
        self.stdout.write(self.style.SUCCESS(f'\n{title}'))
        self.stdout.write('=' * 70)

        if not blocked_ips.exists():
            self.stdout.write(self.style.WARNING('No blocked IPs found.'))
            return

        for blocked_ip in blocked_ips:
            status = '🔴 Active' if blocked_ip.is_active else '⚪ Inactive'

            self.stdout.write(f'\n{status} - {blocked_ip.ip_address}')
            self.stdout.write(f'  Blocked at: {blocked_ip.blocked_at}')

            if blocked_ip.blocked_by:
                self.stdout.write(f'  Blocked by: {blocked_ip.blocked_by}')

            if blocked_ip.reason:
                self.stdout.write(f'  Reason: {blocked_ip.reason}')

            self.stdout.write('-' * 70)

        # Summary
        total = blocked_ips.count()
        active = blocked_ips.filter(is_active=True).count()

        self.stdout.write(
            self.style.SUCCESS(f'\nTotal: {total} | Active: {active}')
        )