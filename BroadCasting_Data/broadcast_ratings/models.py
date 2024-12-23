from django.db import models
from django.core.validators import RegexValidator
# Create your models here.
from broadcast.models import Broadcast

class BroadcastRatings(models.Model):
    broadcast = models.ForeignKey(Broadcast, on_delete= models.CASCADE)
    month = models.CharField(max_length=7)                            
    ratings_type = models.CharField(max_length=40)
    viewers = models.IntegerField()
    ratings = models.FloatField()

    def __str__(self):
        return f"{self.broadcast} - '{self.month}' {self.ratings_type}의 시청률 : {self.ratings}"

class AudienceSampleSize(models.Model):
    audience_type = models.CharField(max_length=40)
    sample_size = models.IntegerField()

    def __str__(self):
        return self.audience_type + " - " + str(self.sample_size)