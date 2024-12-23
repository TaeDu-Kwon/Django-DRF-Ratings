from django.test import TestCase

# Create your tests here.
# from .models import Channel, BroadcastDay, Broadcast

# CHANNEL_LIST = [
#     "SBS", "MBC", "KBS1", "KBS2", "tvN", "MBN", "채널A", "MBC M",
#     "JTBC", "iHQ", "tvN SHOW", "MBC evey1", "KBS joy", "ENA", "E채널",
#     "TV CHOSUN", "K-STAR", "SBS플러스", "Mnet", "EBS1", "채널S"
# ]

# DAY = ["월","화","수","목","금","토","일"]

# class BroadcastTestCase(TestCase):
#     def setUp(self):
#         super().setUp()

#         for channel in CHANNEL_LIST:
#             Channel.objects.create(channel_name = channel)
        
#         for day in DAY:
#             BroadcastDay.objects.create(day = day)

#     def test_채널이름_가져오기(self):
#         channel_list = Channel.objects.all()

#         # 채널 값을 비교 
#         self.assertEqual(channel_list.count(), len(CHANNEL_LIST), f"채널 개수가 {len(CHANNEL_LIST)}개가 아닙니다.")
        

        

