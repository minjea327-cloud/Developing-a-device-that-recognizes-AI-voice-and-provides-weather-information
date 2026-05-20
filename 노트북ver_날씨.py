import speech_recognition as sr
import paho.mqtt.client as mqtt
import pyttsx3

# TTS (음성 출력) 엔진 초기화
engine = pyttsx3.init()

# 라즈베리파이에서 보낸 날씨 데이터를 받았을 때 실행되는 함수
def on_message(client, userdata, msg):
    weather_text = msg.payload.decode('utf-8')
    print("\n[라즈베리파이 응답]: " + weather_text)
    # 노트북 스피커로 텍스트 읽기
    engine.say(weather_text)
    engine.runAndWait()

# MQTT 설정
broker_address = "10.60.7.169" 
client = mqtt.Client(client_id="Laptop_Node")
client.on_message = on_message
client.connect(broker_address)

# 라즈베리파이가 보내는 'weather_info' 토픽을 구독
client.subscribe("weather_info", 1)
# 마이크 대기와 별개로 백그라운드에서 계속 메시지를 수신하도록 설정
client.loop_start() 

try:
    while True:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("\n[대기 중] '날씨'라고 말씀해주세요 :")
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source)
            
        try:
            text = r.recognize_google(audio, language='ko-KR')
            print("인식된 음성: [" + text + "]")
            
            if "날씨" in text:
                client.publish("voice_weather", "날씨")
                print("-> 라즈베리파이에 날씨 데이터를 요청했습니다.")
                
                
        except sr.UnknownValueError:
            print("음성을 인식하지 못했습니다.")
        except sr.RequestError as e:
            print(f"네트워크 에러 발생: {e}")

except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()