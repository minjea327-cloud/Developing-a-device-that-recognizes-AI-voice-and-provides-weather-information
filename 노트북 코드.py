import speech_recognition as sr # 마이크 음성을 텍스트로 변환하기 위한 라이브러리
import paho.mqtt.client as mqtt # 라즈베리파이와 기기간 통신(MQTT)을 위한 라이브러리
import pyttsx3 # 텍스트를 음성으로 읽어주는(TTS) 라이브러리

# TTS (음성 출력) 엔진 초기화
engine = pyttsx3.init()

# 라즈베리파이에서 보낸 날씨 데이터를 받았을 때 실행되는 함수
def on_message(client, userdata, msg):
    # 라즈베리파이가 보낸 바이너리 데이터를 유니코드(UTF-8) 문자열로 디코딩
    weather_text = msg.payload.decode('utf-8')
    print("\n[라즈베리파이 응답]: " + weather_text)
    # 노트북 스피커로 텍스트 읽기
    engine.say(weather_text)
    # 음성 출력이 완료될 때까지 프로그램 대기
    engine.runAndWait()

# MQTT 설정
broker_address = "10.60.7.169"  # MQTT 브로커(서버) 역할을 하는 IP 주소 (일반적으로 라즈베리파이 IP)
client = mqtt.Client(client_id="Laptop_Node") # 'Laptop_Node'라는 고유 식별자 이름으로 MQTT 클라이언트 생성
client.on_message = on_message # 메시지가 도착했을 때 실행할 콜백 함수 지정
client.connect(broker_address) # 설정한 IP 주소의 MQTT 브로커에 연결 시도

# 라즈베리파이가 보내는 'weather_info' 토픽을 구독
client.subscribe("weather_info", 1)
# 마이크 대기와 별개로 백그라운드에서 계속 메시지를 수신하도록 설정
client.loop_start() 

try:
    while True:
        r = sr.Recognizer() # 구글 음성 인식을 담당하는 객체 생성
        
        # 컴퓨터의 기본 마이크를 음성 입력 소스로 사용
        with sr.Microphone() as source:
            print("\n[대기 중] '날씨'라고 말씀해주세요 :")
            # 주변 소음 상태를 0.5초간 측정하여 음성 인식률을 높이도록 임계값 자동 조절
            r.adjust_for_ambient_noise(source, duration=0.5)
            # 사용자가 말할 때까지 기다린 후 오디오 녹음
            audio = r.listen(source)
            
        try:
            # 구글 웹 음성 인식 API를 이용해 녹음된 오디오를 한국어('ko-KR') 텍스트로 변환
            text = r.recognize_google(audio, language='ko-KR')
            print("인식된 음성: [" + text + "]")

            # 구글이 인식한 문자열 안에 "날씨"라는 키워드가 포함되어 있다면
            if "날씨" in text:
                # 라즈베리파이가 수신 대기 중인 "voice_weather" 토픽으로 "날씨"라는 문자열 데이터 발행(전송)
                client.publish("voice_weather", "날씨")
                print("-> 라즈베리파이에 날씨 데이터를 요청했습니다.")
                
        # 목소리가 너무 작거나 주변 소음으로 인해 음성 판별을 실패했을 때의 예외 처리        
        except sr.UnknownValueError:
            print("음성을 인식하지 못했습니다.")
        # 인터넷 끊김 등 구글 음성 서버와 통신할 수 없는 상황일 때의 예외 처리
        except sr.RequestError as e:
            print(f"네트워크 에러 발생: {e}")

# 사용자가 키보드로 Ctrl + C를 눌러 프로그램을 강제 종료했을 때 안전하게 통신을 닫는 처리
except KeyboardInterrupt:
    client.loop_stop() # 백그라운드 MQTT 루프 스레드 정지
    client.disconnect() # MQTT 브로커와의 연결 해제
