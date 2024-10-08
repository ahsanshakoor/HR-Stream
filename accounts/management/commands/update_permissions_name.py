from django.core.management.base import BaseCommand
from accounts.bulk_create import update_permission_names


class Command(BaseCommand):
    help = 'Update All Permission Name'

    def handle(self, *args, **kwargs):
        update_permission_names()
        self.stdout.write("Permission Names are updated")