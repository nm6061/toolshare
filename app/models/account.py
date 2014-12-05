import datetime, hashlib, random, re
from datetime import date
from django.core.validators import *
from django.utils import timezone, html
from django.conf import settings
from django.db import models, transaction
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.template.loader import render_to_string

import app.constants
from app.email import send_email
from app.models.validators import *

SHA1_RE = re.compile('^[a-f0-9]{40}$')


class Address(models.Model):
    apt_num = models.CharField('apartment number', max_length=10, blank=True, validators=[AlphaNumericOnlyValidator()])
    street = models.CharField('street', max_length=50)
    city = models.CharField('city', max_length=50, validators=[AlphabetOnlyValidator()])
    county = models.CharField('county', max_length=50, default='', blank=True, validators=[AlphabetOnlyValidator()])
    state = models.CharField('state', max_length=2, default='', choices=app.constants.US_STATES)
    country = models.CharField('country', max_length=50, default='USA')
    zip = models.CharField('zip code', max_length=9, validators=[
        RegexValidator(regex='^\d{5}(\d{4})?$', message='should be 5 or 9 digits',
                       code='invalid_zip')])

    class Meta:
        app_label = 'app'

    def _get_format_string(self):
        address = self.street
        if self.apt_num:
            address = self.apt_num + ' ' + address + '{0}'
        if self.county:
            address = address + ' ' + self.county
        address = address + ' ' + self.city + '{0}' + self.state + ' ' + self.get_formatted_zip() + '{0}' + self.country

        return address

    def get_single_line(self):
        return self._get_format_string().format(', ')

    def get_multi_line(self):
        return html.mark_safe(self._get_format_string().format('<br />'))

    def get_formatted_zip(self):
        if len(self.zip) == 9:
            return self.zip[:5] + '-' + self.zip[5:]
        return self.zip

    @property
    def share_zone(self):
        return self.zip[:5]


class UserManager(BaseUserManager):
    def _create_user(self, **extra_fields):
        # Separating the user fields and address fields for simplicity
        user_fields = self._get_fields(model='user', **extra_fields)
        address_fields = self._get_fields(model='address', **extra_fields)

        user_fields['email'] = self.normalize_email(user_fields['email'])
        user = self.model(date_joined=timezone.now(), **user_fields)
        user.set_password(extra_fields['password1'])
        user.address = Address.objects.create(**address_fields)
        user.save(using=self._db)

        return user

    def create_user(self, **extra_fields):
        return self._create_user(**extra_fields)

    def _get_fields(self, model, **fields):
        _user_fields = ['date_joined', 'first_name', 'last_name', 'phone_num', 'email',
                        'pickup_arrangements', 'reputation']
        _address_fields = ['apt_num', 'street', 'city', 'county', 'state', 'country', 'zip']

        _fields = _user_fields
        if model == 'address':
            _fields = _address_fields

        sliced_fields = dict()
        for k, v in fields.items():
            if k in _fields:
                sliced_fields[k] = v

        return sliced_fields


class User(AbstractBaseUser):
    is_active = models.BooleanField('is active', default=False)
    date_joined = models.DateTimeField('Date joined', default=timezone.now)
    first_name = models.CharField('first name', max_length=30, validators=[AlphabetOnlyValidator()])
    last_name = models.CharField('last name', max_length=30, blank=True, validators=[AlphabetOnlyValidator()])
    phone_num = models.CharField('phone number', max_length=11, blank=True, validators=[
        RegexValidator(regex='^\d{10}(\d{1})?$', message='should be 10 or 11 digits', code='invalid_phone')])
    email = models.EmailField('email address', unique=True, validators=[EmailValidator()])
    pickup_arrangements = models.TextField('pickup arrangements', max_length=100, blank=True)
    reputation = models.PositiveIntegerField('reputation', default=0, blank=True)
    send_reminders = models.BooleanField('send reminders', default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']
    objects = UserManager()

    # Foreign keys
    address = models.ForeignKey(Address, unique=True)

    class Meta:
        app_label = 'app'

    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        full_name = self.first_name

        if self.last_name:
            full_name = full_name + ' ' + self.last_name

        return full_name

    def email_user(self, subject, message, from_addr):
        send_email(subject, message, [self.email], from_addr)

    def get_unresolved_future_reservations(self):
        reservations = []
        for tool in self.tool_set.all():
            reservations = reservations + list(
                tool.reservation_set.filter(from_date__gte=datetime.date.today(), status='A'))
        return reservations

    @property
    def share_zone(self):
        return self.address.share_zone


class RegistrationManager(models.Manager):
    def activate_user(self, activation_key):
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.

        if SHA1_RE.search(activation_key):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not profile.activation_key_expired():
                user = profile.user
                user.is_active = True
                user.save()
                profile.activation_key = self.model.ACTIVATED
                profile.save()
                return user
        return False

    def create_inactive_user(self, site, send_email=True, **extra_fields):
        new_user = User.objects.create_user(**extra_fields)
        new_user.is_active = False
        new_user.save()

        registration_profile = self.create_profile(new_user)

        if send_email:
            registration_profile.send_activation_email(site)

        return new_user

    create_inactive_user = transaction.commit_on_success(create_inactive_user)

    def create_profile(self, user):
        salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
        seed = salt + user.email
        activation_key = hashlib.sha1(seed.encode('utf-8')).hexdigest()
        return self.create(user=user, activation_key=activation_key)

    def delete_expired_users(self):
        for profile in self.all():
            try:
                if profile.activation_key_expired():
                    user = profile.user
                    if not user.is_active:
                        user.delete()
                        profile.delete()
            except User.DoesNotExist:
                profile.delete()


class RegistrationProfile(models.Model):
    ACTIVATED = u"already_activated"

    user = models.ForeignKey(User, unique=True)
    activation_key = models.CharField(max_length=40)

    objects = RegistrationManager()

    class Meta:
        app_label = 'app'

    def activation_key_expired(self):
        if settings.ACCOUNT_ACTIVATION_DAYS != 0:
            expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
            return self.activation_key == self.ACTIVATED or (self.user.date_joined + expiration_date <= datetime_now())

    activation_key_expired.boolean = True

    def send_activation_email(self, site):
        template_name = 'email/account_activation.html'

        context = {'activation_key': self.activation_key,
                   'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                   'site': site, 'user': self.user}

        subject = '[ToolShare] Activate your account'
        message = render_to_string(template_name, context)

        self.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)