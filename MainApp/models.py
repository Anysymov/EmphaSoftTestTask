from django.db import models

class Room(models.Model):
    name = models.TextField()
    price = models.IntegerField()
    spots = models.IntegerField()

    def __str__(self):
        return self.name


class User(models.Model):
    username = models.TextField()
    password = models.TextField()
    full_name = models.TextField()

    def __str__(self):
        return self.username


class Reservation(models.Model):
    room = models.TextField()
    reserved_for = models.TextField()
    reservation_date = models.DateField()

    def __str__(self):
        return self.room
