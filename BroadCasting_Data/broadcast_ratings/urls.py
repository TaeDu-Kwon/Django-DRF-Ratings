from django.urls import path

from . import views

urlpatterns = [
    
    path("broadcast-ratings/",views.BroadcastRatingsViewset.as_view({
        "post" : "create"
    })),
    path("broadcast-ratings/stats/",views.BroadcastRatingsViewset.as_view({
        "get" : "stats"
    })),
    path("broadcast-ratings/average/<str:program>",views.BroadcastRatingsViewset.as_view({
        "get" : "average",
    })),
    path("broadcast-ratings/ranking/<str:filter>/<str:value>",views.BroadcastRatingsViewset.as_view({
        "get" : "ranking",
    })),

]