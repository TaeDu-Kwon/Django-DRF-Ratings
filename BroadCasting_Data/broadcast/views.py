from django.shortcuts import render

# Create your views here.
from .models import Channel,Broadcast,BroadcastDay
from .serialziers import BroadcastSerializers, ChannelSerializers, BroadcastDaySerializers
from rest_framework import viewsets

class BroadcastViewset(viewsets.ModelViewSet):
    queryset = Broadcast.objects.all()
    serializer_class = BroadcastSerializers

    def partial_update(self,request,*args,**kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return response

class ChannelViewset(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializers

class BroadcastDayViewset(viewsets.ModelViewSet):
    queryset = BroadcastDay.objects.all()
    serializer_class = BroadcastDaySerializers    