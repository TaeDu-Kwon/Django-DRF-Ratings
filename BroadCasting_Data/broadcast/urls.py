from django.urls import path

from . import views

urlpatterns = [
    path("broadcast",views.BroadcastViewset.as_view({
        "get" : "list", 
        "post": "create",
    })),

    path("broadcast/<int:pk>",views.BroadcastViewset.as_view({
        "get" : "list",
        "patch" : "partial_update",
        "delete" : "destroy"
    })),

    # path("channel",views.ChannelViewset.as_view({
    #     "get" : "list", 
    #     "post": "create",
    # })),
    # path("broadcast-day",views.BroadcastDayViewset.as_view({
    #     "get" : "list", 
    #     "post": "create",
    # })),

]