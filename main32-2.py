import speech_recognition as sr # 음성 인식 라이브러리 import
import requests # HTTP 요청을 보내기 위한 라이브러리 import
import os # 운영체제 명령어 실행을 위한 라이브러리 import
import time # 시간 지연 처리를 위한 라이브러리 import

API_KEY = "Enter your API key here" # OpenWeatherMap API 키 설정
url = f"https://api.openweathermap.org/data/2.5/weather?q=Seoul&appid={API_KEY}&units=metric" # espeak 명령어로 option 설정과 함께 msg를 음성출력

def speak(option, msg): # 텍스트를 음성으로 출력하는 함수 정의
    os.system("espeak {} '{}'".format(option, msg)) # espeak 명령어로 option 설정과 함께 msg를 음성출력

try:
    while True: # 키보드 인터럽트(Crtl+C)가 발생할 때까지 무한 반복
        r = sr.Recognizer() # 음성 인식기 객체 생성
         
        with sr.Microphone() as source: # 기본 마이크를 입력 소스로 사용
            print("Say something!") # 사용자에게 말하도록 안내 메시지 출력
            audio = r.listen(source) # 마이크에서 음성을 녹음하여 audio에 저장
            
        try:
            text = r.recognize_google(audio, language='ko-KR') # 녹음된 음성을 한국어로 텍스트 변환
            print("You said: " + text) # 인식된 텍스트 출력
            if text in "날씨": # text가 "날씨" 문자열 안에 포함되는지 확인
                print("날씨 음성을 인식하였습니다.") # 날씨 관련 음성인식 성공 메시지 출력
                response = requests.get(url) # 날씨 API에 GET 요청을 보내 응답 수신
                data = response.json() # 응답 데이터를 JSON 형식으로 파싱
                temp = data["main"]["temp"] # JSON 데이터에서 현재 기온 추출
                humi = data["main"]["humidity"] # JSON 데이터에서 현재 습도 추출
                
                msg = '    기온은 ' + str(int(temp)) + '도 습도는 ' + str(humi) + '퍼센트 입니다' # 기온과 습도를 포함한 안내 문자열 생성
                
                option = '-s 180 -p 50 -a 200 -v ko+f5'# espeak 옵션 설정
                speak(option, msg) # 설정된 옵션과 메시지로 음성 출력 함수 호출
            
        except sr.UnknownValueError: # 음성은 감지됐지만 내용을 인식하지 못한 경우
            print("Google Speech Recognition could not understand audio") # 인식 실패 메시지 출력
        except sr.RequestError as e: # Google API 서버 요청 자체가 실패한 경우
            print("Could not request results from Google Speech Recognition service; {0}".format(e)) # 오류내용 출력
 
except KeyboardInterrupt: # Ctrl+C 입력시 프로그램 정상 종료
    pass # 아무 처리없이 루프 탈출
