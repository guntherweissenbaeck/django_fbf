from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User


class Command(BaseCommand):
    help = 'Verwaltet die data-export Gruppe und weist Benutzern diese Gruppe zu'

    def add_arguments(self, parser):
        parser.add_argument(
            '--add-user',
            type=str,
            help='Füge einen Benutzer zur data-export Gruppe hinzu (Username)'
        )
        parser.add_argument(
            '--remove-user',
            type=str,
            help='Entferne einen Benutzer aus der data-export Gruppe (Username)'
        )
        parser.add_argument(
            '--list-users',
            action='store_true',
            help='Liste alle Benutzer in der data-export Gruppe auf'
        )
        parser.add_argument(
            '--create-group',
            action='store_true',
            help='Erstelle die data-export Gruppe falls sie nicht existiert'
        )

    def handle(self, *args, **options):
        # Stelle sicher, dass die Gruppe existiert
        group, created = Group.objects.get_or_create(name='data-export')
        if created:
            self.stdout.write(
                self.style.SUCCESS('Gruppe "data-export" wurde erstellt')
            )

        if options['create_group']:
            self.stdout.write(
                self.style.SUCCESS('Gruppe "data-export" ist verfügbar')
            )
            return

        if options['add_user']:
            username = options['add_user']
            try:
                user = User.objects.get(username=username)
                user.groups.add(group)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Benutzer "{username}" wurde zur data-export Gruppe hinzugefügt'
                    )
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Benutzer "{username}" existiert nicht')
                )

        if options['remove_user']:
            username = options['remove_user']
            try:
                user = User.objects.get(username=username)
                user.groups.remove(group)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Benutzer "{username}" wurde aus der data-export Gruppe entfernt'
                    )
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Benutzer "{username}" existiert nicht')
                )

        if options['list_users']:
            users_in_group = group.user_set.all()
            if users_in_group:
                self.stdout.write('Benutzer in der data-export Gruppe:')
                for user in users_in_group:
                    self.stdout.write(f'  - {user.username} ({user.email})')
            else:
                self.stdout.write('Keine Benutzer in der data-export Gruppe')

        # Zeige Hilfe wenn keine Argumente gegeben wurden
        if not any([options['add_user'], options['remove_user'], 
                   options['list_users'], options['create_group']]):
            self.stdout.write('\n=== Data-Export Gruppenverwaltung ===')
            self.stdout.write('Verfügbare Befehle:')
            self.stdout.write('  --create-group: Erstelle die data-export Gruppe')
            self.stdout.write('  --add-user USERNAME: Füge Benutzer zur Gruppe hinzu')
            self.stdout.write('  --remove-user USERNAME: Entferne Benutzer aus Gruppe')
            self.stdout.write('  --list-users: Liste alle Benutzer in der Gruppe')
            self.stdout.write('\nBeispiele:')
            self.stdout.write('  python manage.py manage_data_export --add-user admin')
            self.stdout.write('  python manage.py manage_data_export --list-users')
