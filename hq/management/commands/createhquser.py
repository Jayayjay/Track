import getpass
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = 'Create an HQ portal user account'

    def add_arguments(self, parser):
        parser.add_argument('--email',      help='Email address (used as username)')
        parser.add_argument('--first-name', dest='first_name', help='First name')
        parser.add_argument('--last-name',  dest='last_name',  help='Last name')
        parser.add_argument('--staff',      action='store_true', default=False, help='Grant staff/admin access')
        parser.add_argument('--superuser',  action='store_true', default=False, help='Grant superuser access')

    def handle(self, *args, **options):
        self.stdout.write('\n  HQ Portal — Create User Account\n')
        self.stdout.write('  ' + '─' * 36 + '\n')

        # ── Email ────────────────────────────────────────────────
        email = options.get('email') or self._prompt('  Email address: ').strip().lower()
        if not email or '@' not in email:
            self.stderr.write(self.style.ERROR('  Invalid email address.'))
            return

        if User.objects.filter(username=email).exists():
            self.stderr.write(self.style.ERROR(f'  An account with email "{email}" already exists.'))
            return

        # ── Name ─────────────────────────────────────────────────
        first_name = options.get('first_name') or self._prompt('  First name: ').strip()
        last_name  = options.get('last_name')  or self._prompt('  Last name:  ').strip()

        if not first_name or not last_name:
            self.stderr.write(self.style.ERROR('  First and last name are required.'))
            return

        # ── Password ─────────────────────────────────────────────
        while True:
            password = getpass.getpass('  Password (8+ chars): ')
            confirm  = getpass.getpass('  Confirm password:    ')
            if password != confirm:
                self.stderr.write(self.style.WARNING('  Passwords do not match. Try again.\n'))
                continue
            try:
                validate_password(password)
                break
            except ValidationError as e:
                for msg in e.messages:
                    self.stderr.write(self.style.WARNING(f'  {msg}'))
                self.stderr.write('')

        # ── Role ─────────────────────────────────────────────────
        is_staff     = options['staff'] or options['superuser']
        is_superuser = options['superuser']

        if not options['staff'] and not options['superuser']:
            role_input = self._prompt('  Role  [member/staff/superuser] (default: member): ').strip().lower()
            if role_input in ('staff', 's'):
                is_staff = True
            elif role_input in ('superuser', 'su', 'super'):
                is_staff = is_superuser = True

        # ── Create ───────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write(f'  Email:     {email}')
        self.stdout.write(f'  Name:      {first_name} {last_name}')
        role_label = 'Superuser' if is_superuser else 'Staff' if is_staff else 'Member'
        self.stdout.write(f'  Role:      {role_label}')
        self.stdout.write('')

        confirm = self._prompt('  Create this account? [Y/n]: ').strip().lower()
        if confirm and confirm not in ('y', 'yes'):
            self.stdout.write('  Cancelled.')
            return

        user = User.objects.create_user(
            username     = email,
            email        = email,
            password     = password,
            first_name   = first_name,
            last_name    = last_name,
            is_staff     = is_staff,
            is_superuser = is_superuser,
        )
        token, _ = Token.objects.get_or_create(user=user)

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'  Account created successfully.'))
        self.stdout.write(f'  User ID:   {user.id}')
        self.stdout.write(f'  API Token: {token.key}')
        self.stdout.write('')

    def _prompt(self, label):
        return input(label)
