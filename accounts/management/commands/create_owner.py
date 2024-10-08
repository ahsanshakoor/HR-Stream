from django.core.management.base import BaseCommand
from accounts.bulk_create import create_objects


class Command(BaseCommand):
    help = 'Create Role Owner and All Permissions'

    def handle(self, *args, **kwargs):
        create_objects()
        self.stdout.write("Role and Permissions are created")