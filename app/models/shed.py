from django.db import models
from app.models.account import *

class Shed(models.Model):
    class Meta:
        app_label = 'app'

    owner = models.ForeignKey(User)
    name = models.CharField(max_length=100)
    # address = models.ForeignKey(Address)
    #to check whether the shed is active
    isActive = models.BooleanField(default=True)
    #to check whether shed is visible to ppl outside community
    isPrivate = models.BooleanField(default=False)
    dateCreated = models.DateTimeField(auto_now_add=True)
    #tools to be pre approved while added
    toolModeration = models.BooleanField(default=True)


    def __str__(self):
        return self.name


class Membership(models.Model):
    class Meta:
        app_label = 'app'

    MEMBER = 0
    ADMIN = 1
    ROLE_CHOICES = (
        (MEMBER, 'Member'),
        (ADMIN, 'Admin'),
    )

    location = models.ForeignKey(Shed)
    role = models.IntegerField(choices=ROLE_CHOICES, default=MEMBER)
    user = models.ForeignKey(User)

    def role_toString(self):
        return self.ROLE_CHOICES[self.role][1]

    def __str__(self):
        return self.user.first_name