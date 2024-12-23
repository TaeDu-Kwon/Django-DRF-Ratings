from django.db import models

# Create your models here.

class Channel(models.Model):
    channel_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.channel_name
    
class BroadcastDay(models.Model):
    day = models.CharField(max_length=20, unique= True)

    def __str__(self):
        return self.day

class Broadcast(models.Model):
    program = models.CharField(max_length=100,blank=False)
    channel = models.ForeignKey(Channel, on_delete= models.CASCADE)
    broadcast_day = models.ManyToManyField(BroadcastDay)

    def __str__(self):
        return self.program    
