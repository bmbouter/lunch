from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    date = models.DateField(auto_now_add=True)
    ##username = models.CharField(max_length=64,editable=False)
    user = models.ForeignKey(User)
    guests = models.IntegerField(default=0)

    def __str__(self):
        return '%s on %s with %s guests' % (self.user.username, self.date, self.guests)

    def __repr__(self):
        return '%s on %s with %s guests' % (self.user.username, self.date, self.guests)
