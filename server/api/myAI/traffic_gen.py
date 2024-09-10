import socket
import threading
import json
import random
import time
from datetime import datetime

# 프로토콜 목록
protocols = ['TCP', 'UDP', 'IP', 'DVB-S2', 'MPLS', 'MDNS']

# 정상 트래픽을 생성하는 함수
def generate_normal_packet_data():
    packet = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'source_ip': f"192.168.{random.randint(0, 255)}.{random.randint(1, 255)}",
        'destination_ip': f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}",
        'source_port': random.randint(1024, 65535),
        'destination_port': random.randint(1024, 65535),
        'protocol': random.choice(protocols),
        'packet_size': random.randint(100, 1400),
        'duration': round(random.uniform(0.01, 2.0), 2),
        'data_volume': round(random.uniform(0.1, 50.0), 2),
        'is_normal': True
    }
    return packet

# 비정상 트래픽을 생성하는 함수
def generate_abnormal_packet_data():
    packet = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'source_ip': f"192.168.{random.randint(0, 255)}.{random.randint(1, 255)}",
        'destination_ip': f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}",
        'source_port': random.randint(1024, 65535),
        'destination_port': random.randint(1024, 65535),
        'protocol': random.choice(protocols),
        'packet_size': random.choice([random.randint(20, 50), random.randint(2000, 5000)]),
        'duration': round(random.choice([random.uniform(0.001, 0.05), random.uniform(4.0, 5.0)]), 2),
        'data_volume': round(random.choice([random.uniform(0.1, 0.5), random.uniform(80.0, 100.0)]), 2),
        'is_normal': False
    }
    return packet

# VSAT 네트워크의 정상 주파수 데이터를 생성하는 함수
def generate_normal_vsat_frequency():
    packet = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'frequency': random.uniform(11.7, 12.2),  # GHz 대역, VSAT 네트워크에서 주로 사용되는 범위
        'signal_strength': round(random.uniform(30.0, 50.0), 2),  # dB
        'noise_level': round(random.uniform(1.0, 5.0), 2),  # 정상적인 노이즈 레벨
        'is_jamming': False
    }
    return packet

# VSAT 네트워크의 jamming 공격 데이터를 생성하는 함수
def generate_jamming_vsat_frequency():
    packet = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'frequency': random.uniform(11.7, 12.2),  # GHz 대역
        'signal_strength': round(random.uniform(10.0, 20.0), 2),  # 낮은 신호 세기
        'noise_level': round(random.uniform(20.0, 40.0), 2),  # 높은 노이즈, jamming 공격
        'is_jamming': True
    }
    return packet

# 소켓 설정
HOST = 'localhost'
PORT = 49152  # 서버 포트

# 클라이언트1(네트워크 트래픽)을 처리하는 함수
def handle_client1(conn, addr):
    print(f"클라이언트1: {addr}에 연결되었습니다.")
    
    try:
        while True:
            # 트래픽 유형 선택 (90% 확률로 정상, 10% 확률로 비정상)
            if random.random() < 0.9:
                packet = generate_normal_packet_data()
            else:
                packet = generate_abnormal_packet_data()

            # 트래픽을 JSON으로 변환하여 클라이언트로 전송 (끝에 \n 추가)
            packet_json = json.dumps(packet).encode('utf-8') + b'\n'
            conn.sendall(packet_json)
            
            print(f"클라이언트1로 네트워크 트래픽이 전송되었습니다: {packet['source_ip']}")

            # 1초 대기
            time.sleep(1)
    except ConnectionResetError:
        print(f"클라이언트1: {addr}와의 연결이 종료되었습니다.")
    finally:
        conn.close()

# 클라이언트2(VSAT 주파수)를 처리하는 함수
def handle_client2(conn, addr):
    print(f"클라이언트2: {addr}에 연결되었습니다.")
    
    try:
        while True:
            # 주파수 유형 선택 (95% 확률로 정상, 5% 확률로 jamming)
            if random.random() < 0.95:
                packet = generate_normal_vsat_frequency()
            else:
                packet = generate_jamming_vsat_frequency()

            # 주파수 데이터를 JSON으로 변환하여 클라이언트로 전송 (끝에 \n 추가)
            packet_json = json.dumps(packet).encode('utf-8') + b'\n'
            conn.sendall(packet_json)
            
            print(f"클라이언트2로 VSAT 주파수가 전송되었습니다: {packet['frequency']} GHz")

            # 1초 대기
            time.sleep(1)
    except ConnectionResetError:
        print(f"클라이언트2: {addr}와의 연결이 종료되었습니다.")
    finally:
        conn.close()

# 서버 시작
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"서버가 {PORT} 포트에서 수신 대기 중입니다...")

        client_count = 0  # 클라이언트 카운트 초기화

        while True:
            # 클라이언트 연결을 허용
            conn, addr = server_socket.accept()
            client_count += 1  # 클라이언트 카운트 증가

            # 클라이언트1과 클라이언트2로 자동 분류하여 트래픽 전송
            if client_count % 2 == 1:
                # 클라이언트1에 대한 트래픽 전송을 새로운 스레드에서 처리
                client_thread = threading.Thread(target=handle_client1, args=(conn, addr))
            else:
                # 클라이언트2에 대한 주파수 전송을 새로운 스레드에서 처리
                client_thread = threading.Thread(target=handle_client2, args=(conn, addr))

            client_thread.start()

