import paho.mqtt.client as mqtt
import requests

# OpenWeatherMap API 설정
API_KEY = "547a0951033d1920253a706ebdad89f8"
url = f"https://api.openweathermap.org/data/2.5/weather?q=Seoul&appid={API_KEY}&units=metric"

def on_message(client, userdata, msg):
    text = msg.payload.decode('utf-8')
    print("\n수신된 명령: " + text)
   
    if "날씨" in text:
        print("OpenWeatherMap API 정보를 불러옵니다...")
        try:
            response = requests.get(url)
            data = response.json()
           
            temp = data["main"]["temp"]
            humi = data["main"]["humidity"]
           
            # 노트북으로 보낼 문장 생성
            msg_text = f"현재 서울의 기온은 {int(temp)}도, 습도는 {humi}퍼센트 입니다."
            print("전송할 내용:", msg_text)
           
            # 노트북으로 결과 텍스트 다시 발행(Publish)
            client.publish("weather_info", msg_text)
            print("-> 노트북으로 날씨 데이터를 전송했습니다.")
           
        except Exception as e:
            print("API 요청 또는 데이터 처리 중 에러 발생:", e)

client = mqtt.Client(client_id="PiWeatherServer")
client.on_message = on_message
client.connect("127.0.0.1")
client.subscribe("voice_weather", 1)

print("날씨 요청 대기 중...")
try:
    client.loop_forever()
except KeyboardInterrupt:
    pass
