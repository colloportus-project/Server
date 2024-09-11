from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from db_connect import db
from .myAI import traffic_gen, ip_block
from .models import *
from bson.json_util import dumps
import json
import pymongo
from datetime import datetime

# Create your views here.
def main(request):
    traffic_gen.start_server()

class JammingAPI(APIView):
    def get(self, request):
        if request.headers.get('Accept') == 'application/json':
            true_documents = jamming_true_db.find()
            false_documents = jamming_false_db.find()
            data_list = []
            for doc in true_documents:
                data_list.append({
                    '_id': str(doc.get('_id')),  # ObjectId를 문자열로 변환
                    'timestamp':doc.get('timestamp'),
                    'frequency': doc.get('frequency'),
                    'signal_strength': doc.get('signal_strength'),
                    'noise_level': doc.get('noise_level'),
                    'prediction': doc.get('prediction') # 1,-1
                })
            
            for doc in false_documents:
                data_list.append({
                    '_id': str(doc.get('_id')),  # ObjectId를 문자열로 변환
                    'timestamp':doc.get('timestamp'),
                    'frequency': doc.get('frequency'),
                    'signal_strength': doc.get('signal_strength'),
                    'noise_level': doc.get('noise_level'),
                    'prediction': doc.get('prediction') # 1,-1
                })
            
            sorted_list = sorted(data_list, key=lambda x: datetime.fromisoformat(x['timestamp']))
        
            data = sorted_list
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
                    'judge': doc.get('judge'),
                    'time': doc.get('time'),
                    'size': doc.get('packet_size'),
                    'protocol': doc.get('protocol')
                })
            
            for doc in false_documents:
                data_list.append({
                    '_id': str(doc.get('_id')),  # ObjectId를 문자열로 변환
                    'ip': doc.get('ip'),
                    'judge': doc.get('judge'),
                    'time': doc.get('time'),
                    'size': doc.get('packet_size'),
                    'protocol': doc.get('protocol')
                })
            
            sorted_list = sorted(data_list, key=lambda x: datetime.fromisoformat(x['time']))
            return JsonResponse(sorted_list, safe=False, status=200)
        else:
            return JsonResponse({'error': 'Invalid request'}, status=400)
    
class WarningAPI(APIView):
    def get(self, requset):
        data = traffic_false_db.find()
        return JsonResponse(data, safe=False, status=200)
    
    # post에서는 각 동작에 대한 판단을 해줘야 함.
    def post(self, request):
        result = 0
        try:
            # 요청 본문을 JSON으로 파싱
            data = json.loads(request.body)
            if data["action"] == "accept":
                result = ip_block.accept_ip(data["ip"])
            else:
                result = ip_block.block_ip(data["ip"])

        except json.JSONDecodeError:
            # JSON 파싱 실패 시 에러 응답 반환
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)

        # JSON 데이터에서 'ip' 키로 값을 가져옴
        ip = data.get('ip')
    
        # IP가 없을 경우 에러 반환
        if not ip:
            return JsonResponse({'error': 'IP address not provided'}, status=400)

        
        # result에 따라 적절한 응답 반환
        if result == 0:
            return JsonResponse({'message': 'No abnormal IP found', 'result': result}, status=200) # 이걸 프론트에서 받아올 수 있음.
        elif result == 2:
            return JsonResponse({'message': 'IP access successfully', 'result': result}, status=200)
        else:
            return JsonResponse({'message': 'IP block successfully', 'result':result}, status=200)

class HandleAPI(APIView):
    def get(self, request):
        cursor = jamming_handle_db.find()  # 모든 문서 조회

        # Cursor 객체에서 데이터를 리스트로 변환
        documents = list(cursor)

        # 데이터를 JSON으로 직렬화
        data = json.dumps(documents, default=str)  # ObjectId 같은 비직렬화 가능한 데이터 처리

        return JsonResponse(data, safe=False, status=200)

    