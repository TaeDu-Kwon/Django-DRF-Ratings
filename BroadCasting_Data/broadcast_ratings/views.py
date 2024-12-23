from django.shortcuts import render

# Create your views here.
from .models import BroadcastRatings, AudienceSampleSize
from broadcast.models import Broadcast
from .serialziers import BroadcastRatingsSerializers, AudienceSampleSizeSerializers
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework import viewsets, status
from rest_framework.response import Response
import re

class BroadcastRatingsViewset(viewsets.ModelViewSet):
    queryset = BroadcastRatings.objects.all()
    serializer_class = BroadcastRatingsSerializers

    filter_fields = {
        "program" : "broadcast__program",
        "month" : "month",
        "ratings_type" : "ratings_type",
        "channel" : "broadcast__channel__channel_name",
        "broadcast_day" : "broadcast__broadcast_day",
    }

    def average(self, request, *args, **kwargs):
        program = kwargs.get("program")
        queryset = self.queryset.filter(broadcast__program = program)

        # aggregate => Django에서 필드 전체의 합 평균 개수등을 계산할 때 사용을 한다.
        #  Avg => queryset 결과에서 특정 컬럼기준 평균값을 구할 때 사용하는 매개변수 ==> 결과 {'average': 2.0326851851851853}
        average_rating = queryset.aggregate(average = Avg("ratings"))["average"] 
                
        response_data = {
            "program": program,
            "average_ratings": round(average_rating, 2) if average_rating else None
        }
        return Response(response_data, status=200)
    
    def ranking(self,request, *args, **kwargs):
        filter_conditions = {}
        ranking_list = []
        
        filter = kwargs.get("filter")
        value = kwargs.get("value")

        if not filter in self.filter_fields:
            return Response({"error":"Filter 값에 문제가 있습니다."},status=status.HTTP_400_BAD_REQUEST)
        
        filter_conditions[self.filter_fields[filter]] = value
        queryset = self.queryset.filter(**filter_conditions)
        

        ranking_queryset_list= queryset.order_by("-ratings")[:5]
        ranking_count = 1
        for i in ranking_queryset_list:
            ranking_list.append({
                "Rank" : ranking_count, 
                "Program" : i.broadcast.program, 
                "Month" : i.month, 
                "Ratings" : i.ratings
                })
            ranking_count += 1

        response_data = {
            "Filter" : filter,
            "Filter Value" : value,
            "Top 5 Programs" : ranking_list
        }

        return Response(response_data, status=200)
        

    def stats(self,request,*args, **kwargs):
        queryset = self.queryset
        filter_conditions = {}
        filter_display = []

        broadcast_day = {"월요일" : 1, "화요일" : 2, "수요일" : 3, "목요일" : 4, "금요일" : 5, "토요일" : 6, "일요일" : 7}

        for parm, db_field in self.filter_fields.items():
            value = request.query_params.get(parm,None)
            if value:
                if parm == "broadcast_day":
                    filter_display.append(value)
                    value = broadcast_day[value]
                else:
                    filter_display.append(value)
                filter_conditions[db_field] = value
                

        queryset = queryset.filter(**filter_conditions)

        max_rating_object = queryset.order_by("-ratings").first() # -ratings : 내림차순으로 정렬
        min_rating_object = queryset.order_by("ratings").first()

        response_data = {
            "Filter" : " - ".join(filter_display) if filter_display else None,
            "Max Ratings": {
                "Program" : max_rating_object.broadcast.program if max_rating_object else None,
                "Month" : max_rating_object.month if max_rating_object else None,  
                "Ratings" : max_rating_object.ratings if max_rating_object else None
            },
            "Min Ratings" : {
                "Program" : min_rating_object.broadcast.program if min_rating_object else None,
                "Month" : min_rating_object.month if min_rating_object else None,
                "Ratings" : min_rating_object.ratings if min_rating_object else None
            }
        }
        
        return Response(response_data,status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data

        broadcast = Broadcast.objects.get(pk = data["broadcast_pk"])
        viewers = data["viewers"]
        month = data["month"]
        
        try:
            audience_sample_size = AudienceSampleSize.objects.get(audience_type = data["ratings_type"])
        except:
            return Response({"error":"There isn't audience sample size please make sample size."},status=status.HTTP_400_BAD_REQUEST)
        
        # 추가 - 같은 날짜에 값이 있는 경우

        pattern = r'^\d{4}-(0[1-9]|1[0-2])$'
        is_month_pattern = re.match(pattern,month)

        if is_month_pattern == None:
            return Response({"error":"There isn't month pattern"},status=status.HTTP_400_BAD_REQUEST)
        
        ratings = (viewers / audience_sample_size.sample_size) * 100
        ratings = round(ratings,2)

        broadcast_ratings = BroadcastRatings.objects.create(
            broadcast = broadcast,
            month = month,
            ratings_type = data["ratings_type"],
            viewers = viewers,
            ratings = ratings
        )
        serializer = self.get_serializer(broadcast_ratings)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,status=status.HTTP_201_CREATED,headers=headers)