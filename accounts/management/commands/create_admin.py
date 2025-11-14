"""
Management command untuk membuat admin user
Usage: python manage.py create_admin
"""

from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Create an admin user'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Admin username', default='admin')
        parser.add_argument('--email', type=str, help='Admin email', default='admin@bri.co.id')
        parser.add_argument('--password', type=str, help='Admin password', default='admin123')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists!')
            )
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name='Admin',
            last_name='System',
            role='admin'
        )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created admin user: {username}')
        )
        self.stdout.write(f'  Email: {email}')
        self.stdout.write(f'  Password: {password}')
        self.stdout.write(
            self.style.WARNING('\n⚠️  Please change the password after first login!')
        )
