from rest_framework import serializers
from .models import Channel,Broadcast,BroadcastDay

class ChannelSerializers(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ['id', 'channel_name'] 

class BroadcastDaySerializers(serializers.ModelSerializer):
    class Meta:
        model = BroadcastDay
        fields = ['id', 'day']

class BroadcastSerializers(serializers.ModelSerializer):
    
    # 값을 넣을 때 id말고 이름으로 넣기위해 제작
    channel = serializers.SlugRelatedField(
        queryset=Channel.objects.all(),
        slug_field="channel_name"  # 출력할 필드
    )
    broadcast_day = serializers.SlugRelatedField(
        many=True,
        queryset=BroadcastDay.objects.all(),
        slug_field="day"  # 출력할 필드
    )

    class Meta:
        model = Broadcast
        fields = ["id","program","channel","broadcast_day"]