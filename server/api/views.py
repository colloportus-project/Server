from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from db_connect import db
from .myAI import  traffic_gen, jamming, traffic_rate
# from .jamming import *
# from .traffic_gen import *
# from .traffic_rate import *
from .models import *
from bson.json_util import dumps
import json
import pymongo
import datetime
import threading

# Create your views here.
def main(request):
    traffic_gen.start_server()

    return HttpResponse("<h1>Hello~</h1>")

class JammingAPI(APIView):
    def get(self, request):
        if request.headers.get('Accept') == 'application/json':
            documents = jamming_db.find()
            data_list = []
            for doc in documents:
                data_list.append({
                    '_id': str(doc.get('_id')),  # ObjectId를 문자열로 변환
                    'timestamp':doc.get('timestamp'),
                    'frequency': doc.get('frequency'),
                    'signal_strength': doc.get('signal_strength'),
                    'noise_level': doc.get('noise_level'),
                    'prediction': doc.get('prediction') # 1,-1
                })
            data = data_list
            return JsonResponse(data, safe=False, status=200)
        else:
            return JsonResponse({'error': 'Invalid request'}, status=400)
    
class TrafficAPI(APIView):
    def get(self, request):
        if request.headers.get('Accept') == 'application/json':
            true_documents = traffic_true_db.find()
            false_documents = traffic_false_db.find()
            data_list = []
            for doc in true_documents:
                data_list.append({
                    '_id': str(doc.get('_id')),  # ObjectId를 문자열로 변환
                    'ip': doc.get('ip'),
                    'TF': doc.get('tf'),
                    'time': doc.get('time'),
                    'size': doc.get('packet_size'),
                })
            
            for doc in false_documents:
                data_list.append({
                    '_id': str(doc.get('_id')),  # ObjectId를 문자열로 변환
                    'ip': doc.get('ip'),
                    'TF': doc.get('tf'),
                    'time': doc.get('time'),
                    'size': doc.get('packet_size'),
                })
            
            sorted_list = sorted(data_list, key=lambda x: datetime.fromisoformat(x['timestamp']))
            return JsonResponse(sorted_list, safe=False, status=200)
        else:
            return JsonResponse({'error': 'Invalid request'}, status=400)
    
# class WarningAPI(APIView):
#     def get(self, requset):

#     def post(self, request):


    

    