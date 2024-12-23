from django.test import TestCase

# Create your tests here.
from broadcast.models import Channel, BroadcastDay, Broadcast
from broadcast_ratings.models import BroadcastRatings,AudienceSampleSize
from rest_framework.test import APITestCase, APIClient
import json

JSON_PATH = r"C:\Users\Eon-PC050\Desktop\BroadCasting_Data\BroadCasting_Data\sample_data.json"


class BroadcastTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls): 
        # setUP은 테스트 함수 실행할 때 마다 실행을 하고 setUPTestData는 총 한번만 실행을 해준다고 한다
        # APIClient는 DRF에서 사용되는 간편한 방법으로 데이터를 자동으로 json으로 직렬화한다고 한다 
        # 그래서 기존 post할 때 content_type="application/json" 방식 말고 format='json' 해당 형식으로 한다.
        cls.client = APIClient()

        # --------------------------------- 초기 json 데이터 저장 --------------------------------- #
        with open(JSON_PATH, encoding="utf-8") as jn:
            cls.json_object = json.load(jn)

        cls.BROADCAST = cls.json_object["BROADCAST"]
        cls.CHANNEL_LIST = cls.json_object["CHANNEL_LIST"]
        cls.DAY = cls.json_object["DAY"]
        cls.AUDIENCESAMPLESIZE = cls.json_object["AUDIENCESAMPLESIZE"]

        # bulk_create => DB에 여러 객체를 한번에 삽입한다
        Channel.objects.bulk_create([Channel(channel_name = channel) for channel in cls.CHANNEL_LIST])
        BroadcastDay.objects.bulk_create([BroadcastDay(day = day) for day in cls.DAY])
        AudienceSampleSize.objects.bulk_create([AudienceSampleSize(audience_type = audience["audience_type"], sample_size = audience["sample_size"]) for audience in cls.AUDIENCESAMPLESIZE])
        
        # --------------------------------- 초기 Broadcast 데이터 저장 --------------------------------- #
        
        # in_bulk => 여러 레코드를 한 번에 가져오는 메서드 (반환값은 딕셔너리 형식 field_name을 지정하면 지정된 필드 값을 키로 하는 딕셔너리를 반환한다.)
        days = BroadcastDay.objects.in_bulk(field_name="day") 
        channels = Channel.objects.in_bulk(field_name="channel_name")
        cls.broadcast_data = []
        cls.broadcast_create_failed_data = []

        for broadcast in cls.BROADCAST:
            day_list = []
            channel = channels[broadcast["channel"]]

            if len(broadcast["day"]) > 3:
                days_split = broadcast["day"].split(",")

                for day in days_split:
                    day_list.append(days[day].day)
            else:
                day_list.append(days[broadcast["day"]].day)

            res = cls.client.post(
                path = "/broadcast",
                data = {
                    "program" : broadcast["program"],
                    "channel" : channel.channel_name,
                    "broadcast_day" : day_list
                },
                format = "json"
            )
            if res.status_code == 201:
                cls.broadcast_data.append(res.json())
            else:
                cls.broadcast_create_failed_data.append(broadcast)
                print("Broadcast Create Error : " + str(broadcast))
        # --------------------------------- 초기 Broadcast 시청률 구하기기 저장 --------------------------------- #
        cls.broadcast_rating_data = []

        for broadcast in cls.broadcast_data:
            for day, audience_data in cls.json_object[broadcast["program"]].items():
                for audience_type, viewers in audience_data.items():
                    res = cls.client.post(
                        path = "/broadcast-ratings/",
                        data = {
                            "broadcast_pk" : broadcast["id"],
                            "month" : day,
                            "ratings_type" : audience_type,
                            "viewers" : viewers
                        },
                        format= "json"
                    )
                    cls.broadcast_rating_data.append(res.json())
    
    def test_채널_저장_내역_확인(self):
        channel_list = Channel.objects.all()
        self.assertEqual(channel_list.count(), len(self.CHANNEL_LIST), f"채널 개수가 {len(self.CHANNEL_LIST)}개가 아닙니다.")
        
    def test_day_저장_내역_확인(self):
        day_list = BroadcastDay.objects.all()
        self.assertEqual(day_list.count(), len(self.DAY), f"요일 개수가 {len(self.DAY)}개가 아닙니다.")

    def test_프로그램_생성하기(self):

        channel = Channel.objects.get(channel_name = "MBC")

        토요일 = BroadcastDay.objects.get(day = "토요일")
        일요일 = BroadcastDay.objects.get(day = "일요일")

        res = self.client.post(
            path = "/broadcast",
            data = {
                "program" : "명곡의 불후",
                "channel" : channel.channel_name,
                "broadcast_day" : [토요일.day,일요일.day]
            },
            #content_type="application/json"
            format='json'
        )
        
        self.assertEqual(res.status_code,201)
        
        data = res.json()

        self.assertIsNotNone(data["id"])

        broadcast = Broadcast.objects.get(pk = data["id"])
        self.assertEqual(data["id"], broadcast.id)
        self.assertEqual(data["channel"],broadcast.channel.channel_name)

        # many to many field는 .all을 해야 결과 값이 나온다
        self.assertEqual(len(data["broadcast_day"]),len(broadcast.broadcast_day.all()))

        return broadcast
    
    def test_프로그램_수정하기(self):
        broadcast = self.test_프로그램_생성하기()

        토요일 = BroadcastDay.objects.get(day = "토요일")

        res = self.client.patch(
            path = f"/broadcast/{broadcast.id}",
            data = {
                "program" : "불후의 명곡",
                "broadcast_day" : [토요일.day]
            },
            #content_type="application/json"
            format='json'
        )

        data = res.json()
        self.assertIsNotNone(data["id"])

        broadcast = Broadcast.objects.get(pk = data["id"])
        self.assertEqual(broadcast.program,data["program"])

        return broadcast

    def test_프로그램_삭제하기(self):
        broadcast = self.test_프로그램_수정하기()

        res = self.client.delete(path = f"/broadcast/{broadcast.id}")
        self.assertEqual(res.status_code, 204) # destory는 작업이 성공하면 204로 반환한다.

    def test_가구_월간_시청률_구하기(self):
        broadcast = self.test_프로그램_생성하기()

        가구 = AudienceSampleSize.objects.get(audience_type = "가구")
        가구_시청자_수 = 1711341

        res = self.client.post(
            path = "/broadcast-ratings/",
            data = {
                "broadcast_pk" : broadcast.id,
                "month" : "2023-01",
                "ratings_type": 가구.audience_type,
                "viewers" : 가구_시청자_수,
            },
            #content_type="application/json"
            format='json'
        )
        data = res.json()

        self.assertEqual(res.status_code, 201)
        self.assertIsNotNone(data["id"])

        ratings = (가구_시청자_수 / 가구.sample_size) * 100
        ratings = round(ratings,2)

        self.assertEqual(data["ratings"],ratings)   

    
    def test_타입별_최대_최소_시청률_조회(self):
        #self.test_여러_프로그램_시청률_구하기()
       
        #------------------- ratings type --------------------------- #
        res = self.client.get(path = "/broadcast-ratings/stats/?ratings_type=10대" )
        self.assertEqual(res.status_code, 200)

        #{'Filter': '10대', 'Max Ratings': {'Program': '일타 스캔들', 'Month': '2023-03', 'Ratings': 7.34}, 'Min Ratings': {'Program': '맛있는 녀석들', 'Month': '2023-09', 'Ratings': 0.01}}
        data = res.json()
        self.assertIn("Max Ratings", data)
        self.assertIn("Min Ratings", data)
        self.assertIsNotNone(data["Max Ratings"]["Program"])
        self.assertIsNotNone(data["Min Ratings"]["Program"])
        self.assertNotEqual(data["Max Ratings"]["Month"],data["Min Ratings"]["Month"])

        # ------------------------ program ----------------------------- #
        res = self.client.get(path = "/broadcast-ratings/stats/?program=놀라운 토요일" )
        self.assertEqual(res.status_code, 200)

        #{'Filter': '놀라운 토요일', 'Max Ratings': {'Program': '놀라운 토요일', 'Month': '2023-02', 'Ratings': 3.22}, 'Min Ratings': {'Program': '놀라운 토요일', 'Month': '2023-11', 'Ratings': 0.75}}
        data = res.json()
        self.assertIn("Max Ratings", data)
        self.assertIn("Min Ratings", data)
        self.assertIsNotNone(data["Max Ratings"]["Program"])
        self.assertIsNotNone(data["Min Ratings"]["Program"])
        self.assertNotEqual(data["Max Ratings"]["Month"],data["Min Ratings"]["Month"])

        # ------------------------ month ----------------------------- #
        res = self.client.get(path = "/broadcast-ratings/stats/?month=2023-07" )
        self.assertEqual(res.status_code, 200)

        #{'Filter': '2023-07', 'Max Ratings': {'Program': '미운 우리 새끼', 'Month': '2023-07', 'Ratings': 9.39}, 'Min Ratings': {'Program': '고딩엄빠3', 'Month': '2023-07', 'Ratings': 0.02}}
        data = res.json()
        self.assertIn("Max Ratings", data)
        self.assertIn("Min Ratings", data)
        self.assertIsNotNone(data["Max Ratings"]["Program"])
        self.assertIsNotNone(data["Min Ratings"]["Program"])
        # month 기준으로 하기 때문에 equal
        self.assertEqual(data["Max Ratings"]["Month"],data["Min Ratings"]["Month"])

        # ---------------------- program ratings_type ------------------ #
        res = self.client.get(path = "/broadcast-ratings/stats/?program=1박 2일 시즌4&ratings_type=30대")
        self.assertEqual(res.status_code, 200)

        # {'Filter': '1박 2일 시즌4 - 30대', 'Max Ratings': {'Program': '1박 2일 시즌4', 'Month': '2023-11', 'Ratings': 4.5}, 'Min Ratings': {'Program': '1박 2일 시즌4', 'Month': '2023-09', 'Ratings': 3.04}}
        data = res.json()
        
        self.assertIn("Max Ratings", data)
        self.assertIn("Min Ratings", data)
        self.assertIsNotNone(data["Max Ratings"]["Program"])
        self.assertIsNotNone(data["Min Ratings"]["Program"])
        self.assertNotEqual(data["Max Ratings"]["Month"],data["Min Ratings"]["Month"])

        # ---------------------- broadcast day ------------------ #
        res = self.client.get(path = "/broadcast-ratings/stats/?broadcast_day=수요일")
        self.assertEqual(res.status_code, 200)

        #{'Filter': '수요일', 'Max Ratings': {'Program': '라디오스타', 'Month': '2023-01', 'Ratings': 4.4}, 'Min Ratings': {'Program': '고딩엄빠3', 'Month': '2023-07', 'Ratings': 0.02}}
        data = res.json()
        self.assertIn("Max Ratings", data)
        self.assertIn("Min Ratings", data)
        self.assertIsNotNone(data["Max Ratings"]["Program"])
        self.assertIsNotNone(data["Min Ratings"]["Program"])
        self.assertNotEqual(data["Max Ratings"]["Month"],data["Min Ratings"]["Month"])

        # ---------------------- channel ------------------------- #
        res = self.client.get(path = "/broadcast-ratings/stats/?channel=MBC")
        self.assertEqual(res.status_code, 200)

        #{'Filter': 'iHQ', 'Max Ratings': {'Program': '맛있는 녀석들', 'Month': '2023-02', 'Ratings': 0.56}, 'Min Ratings': {'Program': '맛있는 녀석들', 'Month': '2023-10', 'Ratings': 0.0}}
        data = res.json()
        self.assertIn("Max Ratings", data)
        self.assertIn("Min Ratings", data)
        self.assertIsNotNone(data["Max Ratings"]["Program"])
        self.assertIsNotNone(data["Min Ratings"]["Program"])
        self.assertNotEqual(data["Max Ratings"]["Month"],data["Min Ratings"]["Month"])

    def test_프로그램_평균_시청률(self):
        res = self.client.get(path = "/broadcast-ratings/average/라디오스타")
        self.assertEqual(res.status_code, 200)

        #{'program': '라디오스타', 'average_ratings': 2.03}
        data = res.json()
        self.assertIsNotNone(data["average_ratings"])        

    def test_시청자_타입별_최고_시청률_조회(self):
        # ex) 10대 rank 1 oooo / rank 2 oooo ... rank 5 oooo
        res = self.client.get(path = "/broadcast-ratings/ranking/ratings_type/30대")
        #res = self.client.get(path = "/broadcast-ratings/ranking/month/2023-05")
        #res = self.client.get(path = "/broadcast-ratings/ranking/program/미운 우리 새끼")
        self.assertEqual(res.status_code, 200)

        #{'Filter': 'ratings_type', 
        # 'Filter Value': '30대', 
        # 'Top 5 Programs': [
        # {'Rank': 1, 'Program': '모범택시2', 'Month': '2023-04', 'Ratings': 6.9}, 
        # {'Rank': 2, 'Program': '일타 스캔들', 'Month': '2023-03', 'Ratings': 6.12}, 
        # {'Rank': 3, 'Program': '미운 우리 새끼', 'Month': '2023-02', 'Ratings': 5.5}, 
        # {'Rank': 4, 'Program': '미운 우리 새끼', 'Month': '2023-01', 'Ratings': 5.3}, 
        # {'Rank': 5, 'Program': '미운 우리 새끼', 'Month': '2023-03', 'Ratings': 5.18} ]}
        data = res.json()
        self.assertEqual(len(data["Top 5 Programs"]),5)
    
    # def test_여러_프로그램_생성하기(self): # 제작 후 실행 시간이 오래 걸리는 이슈로 setUPTestData에서 제작하기로 변경
    #     days = BroadcastDay.objects.in_bulk(field_name = "day")
    #     channels = Channel.objects.in_bulk(field_name = "channel_name")
    
    #     for broadcast in self.BROADCAST:
    #         day_list = []
    #         channel = channels[broadcast["channel"]]

    #         if len(broadcast["day"]) > 3:
    #             days_split = broadcast["day"].split(",")
                
    #             for day in days_split:
    #                 day_list.append(days[day].day)

    #         else:
    #             day_list.append(days[broadcast["day"]].day)

    #         res = self.client.post(
    #             path = "/broadcast",
    #             data = {
    #                 "program" : broadcast["program"],
    #                 "channel" : channel.channel_name,
    #                 "broadcast_day" : day_list
    #             },
    #             content_type="application/json"
    #         )

    #         self.assertEqual(res.status_code,201)
            
    #         data = res.json()
    #         self.assertIsNotNone(data["id"])

    #         broadcast = Broadcast.objects.get(pk = data["id"])
    #         self.assertEqual(data["id"], broadcast.id)
    #         self.assertEqual(data["channel"],broadcast.channel.channel_name)

    #         # many to many field는 .all을 해야 결과 값이 나온다
    #         self.assertEqual(len(data["broadcast_day"]),len(broadcast.broadcast_day.all()))
        
    # def test_여러_프로그램_시청률_구하기(self): # 제작 후 실행 시간이 오래 걸리는 이슈로 setUPTestData에서 제작하기로 변경
    #     #self.test_여러_프로그램_생성하기()
    #     broadcasts = self.broadcast_data #Broadcast.objects.all()
        
    #     for broadcast in broadcasts:
    #         for day, audience_data in self.json_object[broadcast["program"]].items():
    #             for audience_type, viewers in audience_data.items():
    #                 res = self.client.post(
    #                     path = "/broadcast-ratings/",
    #                     data = {
    #                         "broadcast_pk" : broadcast["id"],
    #                         "month" : day,
    #                         "ratings_type" : audience_type,
    #                         "viewers" : viewers
    #                     },
    #                     #content_type='application/json'
    #                     format= "json"
    #                 )

    #                 self.assertEqual(res.status_code, 201)
    #                 data = res.json()
                    
    #                 self.assertIsNotNone(data["id"])
    #                 self.assertEqual(data["broadcast"],  broadcast["id"])
    #                 self.assertEqual(data["month"], day)
    #                 self.assertEqual(data["ratings_type"], audience_type)
    #                 self.assertEqual(data["viewers"], viewers)
                    
    #                 # ratings 값 검증
    #                 audience = AudienceSampleSize.objects.get(audience_type=audience_type)
    #                 expected_ratings = round((viewers / audience.sample_size) * 100, 2)
    #                 self.assertAlmostEqual(data["ratings"], expected_ratings, places=2)

    #                 # 데이터베이스 검증
    #                 broadcast_ratings = BroadcastRatings.objects.get(pk=data["id"])
    #                 self.assertEqual(broadcast_ratings.ratings, expected_ratings)
                