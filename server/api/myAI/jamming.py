import socket
import json
import joblib
import numpy as np
from datetime import datetime
import pandas as pd
import threading
from sklearn.impute import SimpleImputer
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# 모델과 스케일러 로드
iso_forest, scaler = joblib.load(r'C:\Users\dngur\Desktop\공모전\사이버 시큐리티 해커톤\Server\server\api\myAI\isolation_forest_model_jamming.pkl')

uri = "mongodb+srv://user1:!spwksgo@colloportus.wf3wq.mongodb.net/"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

db = client['database']
jamming_true_db = db['jamming_true']
jamming_false_db = db['jamming_false']
jamming_handle_db = db['jamming_handle']

# 서버의 호스트와 포트 설정
HOST = 'localhost'
PORT = 49152

# Lock 객체를 생성하여 쓰레드 간 동시 접근 방지
lock = threading.Lock()

def handle_missing_values(data):
    # NaN 값을 0으로 대체 (기본값을 다른 값으로 설정할 수도 있습니다)
    imputer = SimpleImputer(strategy='mean')  # 또는 strategy='constant', fill_value=0.0
    data = np.array(data).reshape(-1, 1)  # 2D 배열로 변환
    data_imputed = imputer.fit_transform(data)
    return data_imputed.flatten() # 2D 배열을 다시 1D배열로 형변환하여 반환

# 트래픽을 평가하는 함수
def evaluate_packet(packet):
    try:
        # 패킷에서 데이터 추출 및 결측값 처리
        frequency = packet.get('frequency', np.nan)
        signal_strength = packet.get('signal_strength', np.nan)
        noise_level = packet.get('noise_level', np.nan)

        # 결측값 처리
        handle_data = handle_missing_values([frequency, signal_strength, noise_level])

        # 데이터 전처리
        X = np.array([handle_data])
        #print(f"수신된 패킷: {packet}")  # 디버깅: 패킷 수신 여부 확인
        
        # 데이터 스케일링
        X_scaled = scaler.transform(X)

        # Isolation Forest 모델로 예측
        prediction = iso_forest.predict(X_scaled)[0]  # 예측 결과 (1: 정상, -1: jamming)

        # Lock을 사용하여 쓰레드 동기화
        with lock:
            timestamp = datetime.strptime(packet['timestamp'], '%Y-%m-%d %H:%M:%S')
            
            data = {
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'frequency': float(handle_data[0]),
                'signal_strength': float(handle_data[1]),
                'noise_level': float(handle_data[2]),
                'prediction': prediction.item() # 1,-1
            }

            if prediction == 1:
                jamming_true_db.insert_one(data)
            else:
                handle_jamming_attack(data)
                jamming_false_db.insert_one(data)

            print(f"{data['timestamp']} - 정상 통신 중")
            print("저장할 데이터:", data)

    except Exception as e:
        print(f"패킷 평가 중 오류 발생: {e}")

# 소켓을 통해 서버로부터 주파수를 수신하고 평가하는 함수
def receive_and_evaluate():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))  # 서버에 연결
            print(f"서버에 연결되었습니다: {HOST}:{PORT}")

            buffer = b''  # 데이터 수신 버퍼

            while True:
                data = s.recv(4096)  # 데이터 수신
                if not data:
                    print("서버와의 연결이 종료되었습니다.")
                    break

                buffer += data

                # 완전한 JSON 객체가 들어올 때까지 대기
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)  # '\n' 기준으로 분할
                    try:
                        packet = json.loads(line.decode('utf-8'))
                        evaluate_packet(packet)  # 데이터를 평가하여 DB에 추가
                    except json.JSONDecodeError:
                        print("JSON 디코딩 중 오류 발생, 데이터 손상 가능성.")
                        continue

        except ConnectionRefusedError:
            print(f"서버에 연결할 수 없습니다: {HOST}:{PORT}")
        except Exception as e:
            print(f"오류 발생: {e}")

# jamming attack handle
def handle_jamming_attack(data):
    noise_threshold = 3.0  # 노이즈 임계값
    signal_threshold = 40.0  # 신호 강도 임계값
    new_noise = 0
    new_signal_power = 0
    new_backup = 0

    print(f"{data['timestamp']} - 재밍 공격 감지: 노이즈 {data['noise_level']} dB")
    # 노이즈 변경 - 10 나누기
    new_noise = change_frequency(data['noise_level'])
    print(f"새 주파수: {new_noise} MHz로 변경")
            
    # 신호 강도 조정 - 20 더하기
    if data['signal_strength'] < signal_threshold:
        new_signal_power = adjust_signal_power(data['signal_strength'])
        print(f"신호 강도 증가: {new_signal_power} dBm")
    else:
        print("신호 강도 정상")

    # 백업 경로 활성화 조건
    if data['noise_level'] > noise_threshold and data['signal_strength'] < signal_threshold:
        print("지속적인 재밍 공격! 백업 경로 활성화.")
        new_backup = activate_backup_route() # 1이면 백업 됨
    insert_data = {
        'noise': new_noise,
        'signal_power': new_signal_power,
        'backup': new_backup 
    }
    jamming_handle_db.insert_one(insert_data)

def activate_backup_route():
    print("백업 경로가 활성화되었습니다.")
    return 1

def change_frequency(data):
    return float(data/10)

def adjust_signal_power(data):
    return float(data+20)


#실시간 트래픽 수신 및 평가 시작
if __name__ == "__main__":
    # 데이터 수신 및 평가 시작
    receive_thread = threading.Thread(target=receive_and_evaluate)
    receive_thread.start()