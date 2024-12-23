from rest_framework import serializers
from .models import BroadcastRatings, AudienceSampleSize

class BroadcastRatingsSerializers(serializers.ModelSerializer):
    class Meta:
        model = BroadcastRatings
        fields = "__all__"

class AudienceSampleSizeSerializers(serializers.ModelSerializer):
    class Meta:
        model = AudienceSampleSize
        fields = "__all__"