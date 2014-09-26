from django.db import models


class User(AbstractUser):
    middle_name = models.CharField(max_length=25)
    pickup_arrangements = models.CharField(max_length=100)
    phone_num = models.CharField(max_length=11)
    reputation = models.PositiveIntegerField(default=0)

    def UpdateUserInfo(self):
        pass

    def UpdatePreferences(self):
        pass

        # TODO : DEFINE METHOD AS SOON AS TOOL IS DEFINED
        # def Register(self, Tool):
        #    pass


class Address(models.Model):
    apartment_number = models.CharField(max_length=10)
    street = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    county = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    country = models.CharField(max_length=50)

    User = models.ForeignKey(User)
    
    
class BlackoutDate(models.Model):
    blackoutStart = models.DateField()
    blackoutEnd = models.DateField()


class Tool(models.Model):
    name = models.CharField(max_length=20)
    pictureURL = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    # location = Address()
    status = models.CharField(max_length = 10)
    blackoutDates = models.ForeignKey(BlackoutDate)


