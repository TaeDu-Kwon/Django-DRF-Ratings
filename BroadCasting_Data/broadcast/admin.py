from django.contrib import admin
from .models import Channel, BroadcastDay, Broadcast
# Register your models here.
# admin 0000

admin.site.register(Channel)
admin.site.register(BroadcastDay)
admin.site.register(Broadcast)