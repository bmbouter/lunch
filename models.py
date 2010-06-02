from django.db import models

class Order(models.Model):
    date = models.DateField(auto_now_add=True)
    username = models.CharField(max_length=64,editable=False)
    guests = models.IntegerField(default=0)

    def __str__(self):
        return '%s on %s with %s guests' % (self.username, self.date, self.guests)

    def __repr__(self):
        return '%s on %s with %s guests' % (self.username, self.date, self.guests)
