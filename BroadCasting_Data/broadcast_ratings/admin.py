from django.contrib import admin

# Register your models here.
from .models import BroadcastRatings, AudienceSampleSize
# Register your models here.
# admin 0000

admin.site.register(BroadcastRatings)
admin.site.register(AudienceSampleSize)