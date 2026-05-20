import paho.mqtt.client as mqtt # MQTT 통신을 위한 라이브러리 가져오기
import requests # 인터넷(OpenWeatherMap)에서 날씨 데이터를 가져오기 위한 라이브러리

# OpenWeatherMap API 설정
API_KEY = "API KEY--" # 날씨 데이터를 요청할 때 필요한 인증 키
url = f"https://api.openweathermap.org/data/2.5/weather?q=Seoul&appid={API_KEY}&units=metric" # 서울 날씨(섭씨 단위) 요청 주소

# 구독(Subscribe) 중인 토픽에서 새로운 메시지가 들어왔을 때 실행되는 콜백 함
def on_message(client, userdata, msg):
    text = msg.payload.decode('utf-8') # 들어온 바이트 형태의 메시지를 문자열(텍스트)로 변환
    print("\n수신된 명령: " + text) # 화면에 수신된 명령 텍스트 출력

    # 수신된 명령(텍스트) 안에 "날씨"라는 단어가 포함되어 있는지 확인
    if "날씨" in text:
        print("OpenWeatherMap API 정보를 불러옵니다...")
        try:
            response = requests.get(url) # 설정한 URL 주소로 날씨 데이터 요청
            data = response.json() # 받아온 날씨 데이터를 파이썬 딕셔너리 형태로 변환
           
            temp = data["main"]["temp"] # 데이터에서 현재 기온 추출
            humi = data["main"]["humidity"] # 데이터에서 현재 습도 추출
           
            # 노트북으로 보낼 문장 생성
            msg_text = f"현재 서울의 기온은 {int(temp)}도, 습도는 {humi}퍼센트 입니다."
            print("전송할 내용:", msg_text) # 서버 콘솔에 전송할 내용 미리 출력
           
            # 노트북으로 결과 텍스트 다시 발행(Publish)
            client.publish("weather_info", msg_text)
            print("-> 노트북으로 날씨 데이터를 전송했습니다.")

        # 인터넷 연결이 끊기거나 API 구조가 바뀌는 등 에러 발생 시 프로그램이 안 꺼지도록 예외 처리
        except Exception as e:
            print("API 요청 또는 데이터 처리 중 에러 발생:", e)

client = mqtt.Client(client_id="PiWeatherServer") # MQTT 클라이언트 객체 생성 (이름을 "PiWeatherServer"로 지정)
client.on_message = on_message # 메시지가 수신되었을 때 위에서 만든 'on_message' 함수가 실행되도록 연결
client.connect("127.0.0.1") # 로컬(내 컴퓨터/라즈베리파이 자체)에 설치된 MQTT 브로커(서버)에 연결
client.subscribe("voice_weather", 1) # "voice_weather"라는 토픽을 구독하여, 이 주소로 들어오는 명령을 감시 (QoS 레벨은 1로 설정)

print("날씨 요청 대기 중...")
try:
    # 프로그램이 종료되지 않고 계속 켜져 있으면서 MQTT 메시지를 실시간으로 수신 대기
    client.loop_forever() 
    # 사용자가 키보드로 Ctrl + C를 누르면 오류 메시지 없이 깔끔하게 대기 루프를 종료
except KeyboardInterrupt:
    pass
