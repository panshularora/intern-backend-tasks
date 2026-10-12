from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from calls.crm_client import CRMClient

User = get_user_model()


class Command(BaseCommand):
    help = 'Sync users from CRM API into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print what would be synced without saving',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        client = CRMClient()
        users = client.get_users()
        created = 0
        updated = 0

        for item in users:
            username = item.get('username') or f"user{item.get('id')}"
            email = item.get('email', '')
            self.stdout.write(f"{username} <{email}>")
            if dry_run:
                continue
            _, was_created = User.objects.update_or_create(
                username=username,
                defaults={'email': email},
            )
            if was_created:
                created += 1
            else:
                updated += 1

        if dry_run:
            self.stdout.write(self.style.WARNING(f"Dry run: {len(users)} users, nothing saved"))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Created {created} new users, updated {updated} existing users"
            ))
