# 🚢 CYBER SECURITY HACKATHON in BUSAN 2024
안전한 대한민국을 위한 사이버 보안 융합 기술 및 서비스 만들기 (9.10~9.12)

## ⚓️ 팀 소개
- 팀장:  [진소은](https://github.com/rosejinse) - 프론트 엔드(대시보드 구성) / 발표
- 팀원:  [동지은](https://github.com/DongjieuN) - AI 탐지 모델 학습 / 모델을 통한 탐지 코드 작성 / 데이터 셋 구현
- 팀원:  [최선민](https://github.com/ssminn) - AI 탐지 모델 학습 / 모델을 통한 탐지 코드 작성 / 데이터 셋 구현
- 팀원:  [한우혁](https://github.com/hanwoooo) - 백엔드 및 API구성 / DB연동

## 🖥️ 프로젝트 소개
AI를 활용한 해양 선박 VSAT 네트워크 통신 보안 서비스: COLLOPORTUS PROJECT

실제 데이터를 찾기에는 무리가 있어 가상 공격 시나리오 및 데이터 셋을 구성하여 구현함.

네트워크 탐지, VSAT 주파수에 대한 분석 내용과 비정상 접근 차단 등의 내용을 대시보드를 통해 한 눈에 보기 쉽게 함.

### ⚙️ 개발 환경(서버)
- `python 3.11.9`
- **Framework**: Django 4.2.5 / Django REST Framework 3.14.0
- **DataBase**: Mongo DB (use pymongo)
- **ORM**: pymongo
- **Development Tools**: ngrok (로컬 서버에 대한 외부 접근 터널링 생성)

### 📌 주요 기능
- Auto Encoder, Isolation Forest 모델을 이용한 선박 네트워크의 비정상 트래픽 탐지
- Isolation Forest 모델을 이용한 Jamming 공격 탐지
- 비정상 트래픽 IP에 대한 차단 기능(완전 구현 x)
- **주파수 조절**, **신호 세기 조절**, **백업 루트 확보**를 통한 Jamming 공격 방어 

## 📷 작동 사진
### 1. 로컬 서버 실행시

  - 서버 연결 준비
<img width="363" alt="image" src="https://github.com/user-attachments/assets/e8d4dc49-55ec-4209-8cd2-87650cb08ea4">


  - 서버와 클라이언트1(네트워크 트래픽 탐지) 연결
<img width="365" alt="image" src="https://github.com/user-attachments/assets/d069da1c-eb57-43e7-abbe-036f85a0aabf">


  - 서버와 클라이언트2(VSAT 주파수 탐지) 연결
<img width="370" alt="image" src="https://github.com/user-attachments/assets/7ec0e200-a8ee-475f-b11d-57e2a9ebe715">


### 2. 클라이언트1(네트워크 트래픽 탐지) 연결 및 패킷 분석
<img width="736" alt="image" src="https://github.com/user-attachments/assets/f14a576c-b55b-479d-a9b1-7bc22fb14853">

- 현재 나온 코드에서는 정확도, 오차율 등 평가에 대한 분석 정보가 출력되지만 이는 수정하여 패킷에 대한 정보를 출력할 수 있음.
- 마지막 prediction을 통해 정상, 비정상 패킷을 알 수 있음.
  
### 3. 클라이언트2(VSAT 주파수 탐지) 연결 및 분석
<img width="1130" alt="image" src="https://github.com/user-attachments/assets/5fd86e7c-b247-465f-ade6-a19c1df308c9">

- 주파수에 대한 정보(주파수 크기, 신호 세기, 노이즈 레벨)를 분석하고 Jamming공격이라고 판단되면 3가지 방어 기법을 통해 방어함.
- 이를 서버 로그에 띄워 제대로 작동하는지 볼 수 있음.
