import json
import joblib
import numpy as np
from sklearn.metrics import mean_squared_error
import socket
import pandas as pd
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# 모델 로드
autoencoder = joblib.load(r'C:\Users\dngur\Desktop\공모전\사이버 시큐리티 해커톤\Server\server\api\myAI\autoencoder_model_real.pkl')
isolation_forest = joblib.load(r'C:\Users\dngur\Desktop\공모전\사이버 시큐리티 해커톤\Server\server\api\myAI\isolation_forest_model_real.pkl')
scaler = joblib.load(r'C:\Users\dngur\Desktop\공모전\사이버 시큐리티 해커톤\Server\server\api\myAI\scaler_real.pkl')

uri = "mongodb+srv://user1:!spwksgo@colloportus.wf3wq.mongodb.net/"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

db = client['database']
traffic_true_db = db['traffic_true']
traffic_false_db = db['traffic_false']

# 소켓 설정
HOST = 'localhost'
PORT = 49152  

# 트래픽을 평가하는 함수
def evaluate_packet(packet):
    try:
        #print(f"수신된 패킷: {packet}")  # 패킷 수신 확인

        features = ['source_port', 'destination_port', 'packet_size', 'duration', 'data_volume']
        X = pd.DataFrame([packet])[features]
        
        # 데이터 전처리
        X_scaled = scaler.transform(X)

        # Autoencoder로 재구성 오류 계산
        X_pred = autoencoder.predict(X_scaled)
        mse = mean_squared_error(X_scaled, X_pred)

        # Isolation Forest로 예측
        if_score = isolation_forest.decision_function(X_scaled)
        if_pred = isolation_forest.predict(X_scaled)

        # 결과 출력 (source_ip 추가)
        source_ip = packet.get('source_ip', '알 수 없음')  # source_ip를 packet에서 추출
        
        # MongoDB에 데이터 삽입
        if if_pred[0] == 1:
            data = {
                'ip':source_ip, 
                'packet_size':packet.get('packet_size'), 
                'time': packet.get('timestamp'),
                'protocol': packet.get('protocol'),
                'judge':"정상"
            }
            traffic_true_db.insert_one(data)
        else:
            data = {
                'ip':source_ip, 
                'packet_size':packet.get('packet_size'), 
                'time': packet.get('timestamp'),
                'protocol': packet.get('protocol'),
                'judge':"비정상"
            }
            traffic_false_db.insert_one(data)

        print(f"Source IP: {source_ip}, Autoencoder MSE: {mse}, Isolation Forest Score: {if_score[0]}, Prediction: {'정상' if if_pred[0] == 1 else '비정상'}")
        return data
    except Exception as e:
        print(f"패킷 평가 중 오류 발생: {e}")

# 소켓을 통해 수신한 트래픽을 평가하는 함수
def receive_and_evaluate():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print('서버와 연결되었습니다.')

        buffer = b''  # 데이터 수신 버퍼
        while True:
            data = s.recv(1024)
            if not data:
                break

            buffer += data

            # 완전한 JSON 객체가 들어올 때까지 대기 (버퍼에 '\n'이 포함되면)
            while b'\n' in buffer:
                line, buffer = buffer.split(b'\n', 1)  # '\n'을 기준으로 분할
                if line:
                    try:
                        packet = json.loads(line.decode('utf-8'))
                        evaluate_packet(packet)
                    except json.JSONDecodeError:
                        print("JSON 디코딩 중 오류 발생")
                        continue

# 실시간 트래픽 수신 및 평가 시작
if __name__ == "__main__":
    receive_and_evaluate()