import socket
import json
import joblib
import numpy as np
#import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation
# from matplotlib.dates import DateFormatter
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
jamming_db = db['jamming']

# 서버의 호스트와 포트 설정
HOST = 'localhost'
PORT = 49152

# 수신한 데이터를 저장할 리스트 (고정 길이로 유지)
#window_size = 100  # 그래프에 표시할 데이터 포인트 개수
#timestamps = [np.nan] * window_size  # 시간값 저장
#frequencies = [np.nan] * window_size  # 주파수 데이터 저장
#signal_strengths = [np.nan] * window_size  # 신호 강도 데이터 저장
#noise_levels = [np.nan] * window_size  # 잡음 레벨 데이터 저장
#jamming_points = [np.nan] * window_size  # jamming 공격 점을 표시하기 위한 리스트 (비정상 데이터에만 값이 입력됨)

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
            # 기존 데이터를 한 칸씩 왼쪽으로 이동
            #timestamps.pop(0)
            #frequencies.pop(0)
            #signal_strengths.pop(0)
            #noise_levels.pop(0)
            #jamming_points.pop(0)

            # 새 데이터를 추가
            #timestamps.append(datetime.strptime(packet['timestamp'], '%Y-%m-%d %H:%M:%S'))  # timestamp 추가
            #frequencies.append(handle_data[0])
            #signal_strengths.append(handle_data[1])
            #noise_levels.append(handle_data[2])
            timestamp = datetime.strptime(packet['timestamp'], '%Y-%m-%d %H:%M:%S')
            
            data = {
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'frequency': float(handle_data[0]),
                'signal_strength': float(handle_data[1]),
                'noise_level': float(handle_data[2]),
                'prediction': prediction.item() # 1,-1
            }
            print("저장할 데이터:", data)
            jamming_db.insert_one(data)

    except Exception as e:
        print(f"패킷 평가 중 오류 발생: {e}")

# 실시간 그래프 업데이트 함수
# def update_graph(frame):
#     plt.clf()  # 이전 그래프 프레임을 지움

#     # Lock을 사용하여 쓰레드 동기화
#     with lock:
#         valid_timestamps = [t for t in timestamps if not pd.isna(t)]
#         valid_noise_levels = [n for n in noise_levels if not pd.isna(n)]
#         valid_signal_strengths = [s for s in signal_strengths if not pd.isna(s)]
#         valid_jamming_points = [jp for jp, ts in zip(jamming_points, timestamps) if not pd.isna(jp) and not pd.isna(ts)]
#         valid_jamming_timestamps = [ts for jp, ts in zip(jamming_points, timestamps) if not pd.isna(jp) and not pd.isna(ts)]

#     if len(valid_timestamps) > 0:
#         # 파란색 선 그래프 (잡음 레벨 데이터)
#         plt.plot(valid_timestamps, valid_noise_levels, color='blue', label='Noise Level')
#         plt.scatter(valid_jamming_timestamps, valid_jamming_points, color='red', label='Jamming Attack', zorder=5)  # 빨간색 점으로 jamming 공격 표시
#         plt.xlabel('Time (min:sec)')
#         plt.ylabel('Noise Level (dB)')
#         plt.title('Real-Time VSAT Noise Level Monitoring')
#         plt.xlim(min(valid_timestamps), max(valid_timestamps))
#         plt.ylim(min(valid_noise_levels) - 5, max(valid_noise_levels) + 5)

#         # X축 시간 포맷 설정 (분:초)
#         plt.gca().xaxis.set_major_formatter(DateFormatter('%M:%S'))  # "분:초" 형식으로 설정

#         plt.xticks(rotation=45)  # X축 시간값 회전
#         plt.legend(loc='upper right')
#         plt.grid(True)

#         # 추가 정보 출력 (신호 강도)
#         plt.twinx()  # 두 번째 Y축 생성
#         plt.plot(valid_timestamps, valid_signal_strengths, color='green', label='Signal Strength')
#         plt.ylabel('Signal Strength')

#     else:
#         # 아직 데이터가 없는 경우 메시지 출력
#         plt.text(0.5, 0.5, 'No data received yet', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)

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

#실시간 트래픽 수신 및 평가 시작
if __name__ == "__main__":
    # 실시간 플롯 설정
    #fig, ax = plt.subplots(figsize=(10, 6))

    # 그래프를 주기적으로 갱신하는 함수 (애니메이션)
    #anim = FuncAnimation(fig, update_graph, interval=1000, blit=False)  # 애니메이션 객체를 anim 변수에 할당

    # 데이터 수신 및 평가 시작
    receive_thread = threading.Thread(target=receive_and_evaluate)
    receive_thread.start()

    # 실시간 그래프 유지
    # plt.show()
