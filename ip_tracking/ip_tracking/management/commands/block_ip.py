"""
Management command to block IP addresses.

Usage:
    python manage.py block_ip 192.168.1.100
    python manage.py block_ip 192.168.1.100 --reason "Spam bot"
    python manage.py block_ip 192.168.1.100 --reason "Malicious activity" --blocked-by "admin"
"""

from django.core.management.base import BaseCommand, CommandError
from ip_tracking.ip_tracking.models import BlockedIP


class Command(BaseCommand):
    """
    Django management command to add IP addresses to the blacklist.

    This command allows you to block IPs from the command line.
    """

    help = 'Block an IP address from accessing the site'

    def add_arguments(self, parser):
        """
        Define command-line arguments.

        Required:
            ip_address: The IP address to block

        Optional:
            --reason: Why this IP is being blocked
            --blocked-by: Who is blocking this IP
        """
        # Required positional argument: IP address
        parser.add_argument(
            'ip_address',
            type=str,
            help='IP address to block (e.g., 192.168.1.100 or 2001:db8::1)'
        )

        # Optional: Reason for blocking
        parser.add_argument(
            '--reason',
            type=str,
            default='',
            help='Reason for blocking this IP'
        )

        # Optional: Who blocked this IP
        parser.add_argument(
            '--blocked-by',
            type=str,
            default='CLI',
            help='Username or system that blocked this IP'
        )

    def handle(self, *args, **options):
        """
        Execute the command.

        This function runs when you execute: python manage.py block_ip <ip>
        """
        # Get the arguments
        ip_address = options['ip_address']
        reason = options['reason']
        blocked_by = options['blocked_by']

        try:
            # Check if this IP is already blocked
            existing_block = BlockedIP.objects.filter(
                ip_address=ip_address,
                is_active=True
            ).first()

            if existing_block:
                # IP is already blocked
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  IP {ip_address} is already blocked.'
                    )
                )
                self.stdout.write(
                    f'   Blocked at: {existing_block.blocked_at}'
                )
                if existing_block.reason:
                    self.stdout.write(f'   Reason: {existing_block.reason}')
                return

            # Check if IP was previously blocked but is now inactive
            inactive_block = BlockedIP.objects.filter(
                ip_address=ip_address,
                is_active=False
            ).first()

            if inactive_block:
                # Reactivate the block
                inactive_block.is_active = True
                inactive_block.reason = reason or inactive_block.reason
                inactive_block.blocked_by = blocked_by
                inactive_block.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ IP {ip_address} has been re-blocked successfully!'
                    )
                )
            else:
                # Create a new block
                blocked_ip = BlockedIP.objects.create(
                    ip_address=ip_address,
                    reason=reason,
                    blocked_by=blocked_by
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ IP {ip_address} has been blocked successfully!'
                    )
                )

            # Show details
            if reason:
                self.stdout.write(f'   Reason: {reason}')
            self.stdout.write(f'   Blocked by: {blocked_by}')

        except Exception as e:
            raise CommandError(f'❌ Error blocking IP: {str(e)}')