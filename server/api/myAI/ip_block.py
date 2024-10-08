from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://user1:!spwksgo@colloportus.wf3wq.mongodb.net/"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

db = client['database']
traffic_false_db = db['traffic_false']
blocked_ip_db = db['blocked_ip']

# 비정상 IP 차단 함수
def block(ip):
    print(f"비정상 IP {ip} 차단 중...")
    # 여기에서 실제 IP 차단 명령을 구현할 수 있습니다.
    # 예시: 리눅스의 iptables 명령으로 IP 차단
    # subprocess.run(['sudo', 'iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'])
    # 테스트 환경에서는 실제 차단 대신 메시지만 출력하도록 설정합니다.
    print(f"IP {ip} 차단 완료.")
    

# DB에서 IP 가져와 허용, 차단 
def accept_ip(data):
    abnormal_data = traffic_false_db.find_one({'ip':data})
    if abnormal_data:
        traffic_false_db.delete_one({'_id': abnormal_data['_id']})
        print(f"IP {data} 허용...")
        return 2

def block_ip(data):
    block_data = traffic_false_db.find_one({'ip':data})
    if block_data:
        traffic_false_db.delete_one({'_id': block_data['_id']})
        blocked_ip_db.insert_one(block_data)
        block(block_data)
        return 1
