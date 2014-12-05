from time import time
from optparse import make_option
from datetime import datetime
from django.db.models import Q
from django.core.management.base import BaseCommand, CommandError

from app.models import *


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--today',
                    dest='today',
                    default=date.today(),
                    help='If specified, the command will be run with the specified date as today\'s date.'),
        make_option('--verbose',
                    dest='verbose',
                    action='store_true',
                    default=False,
                    help='Produce verbose output.'),
    )
    help = 'Command that performs daily tasks such as sending notifications, changing status of reservations.'

    def handle(self, *args, **options):
        # Option: Today's date
        today = options['today']
        if not isinstance(today, datetime.date):
            today = datetime.datetime.strptime(options['today'], '%Y-%m-%d').date()

        # Option: Verbosity
        if not isinstance(options['verbose'], bool):
            self.is_verbose = bool(options['verbose'])
        else:
            self.is_verbose = options['verbose']

        tomorrow = today + datetime.timedelta(days=1)

        start = time()
        self.vwrite('#' * 40)
        self.stdout.write('ToolShare Batch Started')
        self.vwrite('#' * 40)
        self.vwrite('')

        self.stdout.write('Today is %s' % today.isoformat())
        self.vwrite('')

        # Send email notifications to borrowers
        # TODO : AGGREGATE RESERVATIONS TO SEND A SINGLE EMAIL TO THE BORROWER
        self.vwrite('Sending Email Notifications ' + '-' * 10, 1)
        self.vwrite('Reservations Ending %s ' % tomorrow.isoformat() + '-' * 10, 2)
        active_reservations = Reservation.objects \
            .filter(status='AC', user__send_reminders=True, to_date=tomorrow).order_by('user__email')

        if active_reservations:
            self.vwrite('Processing %d Reservations ' % active_reservations.count(), 3)
            self.vwrite('%s%s' % ('Tool'.ljust(30), 'Borrower Email'), 4)
            self.vwrite('%s%s' % ('----'.ljust(30), '--------------'), 4)
            for r in active_reservations:
                self.vwrite('%s%s' % (r.tool.name.ljust(30), r.user.email.ljust(50)), 4)
        else:
            self.vwrite('No Reservations To Process', 3)

        self.vwrite('')

        self.vwrite('Overdue Reservations ' + '-' * 10, 2)
        overdue_reservations = Reservation.objects.filter(status='O').order_by('user__email')

        if overdue_reservations:
            self.vwrite('Processing %d Reservations' % overdue_reservations.count(), 3)
            self.vwrite('%s%s' % ('Tool'.ljust(30), 'Borrower Email'), 4)
            self.vwrite('%s%s' % ('----'.ljust(30), '--------------'), 4)
            for r in overdue_reservations:
                self.vwrite('%s%s' % (r.tool.name.ljust(30), r.user.email.ljust(50)), 4)
        else:
            self.vwrite('No Reservations To Process', 3)

        self.vwrite('')

        # Change Status of Reservations
        self.vwrite('Changing Status of Reservations ' + '-' * 10, 1)

        self.vwrite('Approved > Active ' + '-' * 10, 2)
        approved_reservations = Reservation.objects.filter(status='A', from_date=today)

        if approved_reservations.count():
            self.vwrite('Processing %d Reservations' % approved_reservations.count(), 3)
            if self.is_verbose:
                self.vwrite('%s%s' % ('Tool'.ljust(30), 'Borrower'.ljust(30)), 4)
                self.vwrite('%s%s' % ('----'.ljust(30), '--------'), 4)
                for r in approved_reservations:
                    self.vwrite('%s%s' % (r.tool.name.ljust(30), r.user.first_name.ljust(30)), 4)
            approved_reservations.update(status='AC')
        else:
            self.vwrite('No Reservations To Process', 3)

        self.vwrite('Active > Overdue ' + '-' * 10, 2)
        active_reservations = Reservation.objects.filter(status='AC', to_date=today)

        if active_reservations:
            self.vwrite('Processing %d Reservations' % active_reservations.count(), 3)
            if self.is_verbose:
                self.vwrite('%s%s' % ('Tool'.ljust(30), 'Borrower'.ljust(30)), 4)
                self.vwrite('%s%s' % ('----'.ljust(30), '--------'), 4)
                for r in active_reservations:
                    self.vwrite('%s%s' % (r.tool.name.ljust(30), r.user.first_name.ljust(30)), 4)
            active_reservations.update(status='O')
        else:
            self.vwrite('No Reservations To Process', 3)

        self.vwrite('')
        self.vwrite('#' * 40)
        self.stdout.write('Completed In %.4f mins.' % (time() - start))
        self.vwrite('#' * 40)

    def vwrite(self, message, offset=0):
        if self.is_verbose:
            self.stdout.write(' ' * offset + str(message))