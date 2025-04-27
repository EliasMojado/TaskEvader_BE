# node/management/commands/update_node_statuses.py

from django.core.management.base import BaseCommand
from node.models import Node

class Command(BaseCommand):
    help = "Mark overdue ONGOING nodes as MISSED"

    def handle(self, *args, **options):
        updated = Node.objects.update_missed_nodes()
        self.stdout.write(self.style.SUCCESS(
            f"✓ Updated {updated} node(s) to MISSED."
        ))
