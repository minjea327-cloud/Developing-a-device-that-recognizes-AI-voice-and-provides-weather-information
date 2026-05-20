## 개요
본 실험은 사물인터넷(IoT) 허브인 Raspberry Pi 5와 웹 API 환경을 연동하여, 사용자의 음성 명령에 맞춰 실시간 서울 날씨 정보를 출력하는 스마트 음성 비서 장치 구현을 목표로 한다.

시스템은 노트북 마이크로 입력된 사용자 음성을 텍스트로 변환하는 STT(Speech-to-Text) 단계를 거쳐, 가벼운 무선 통신인 MQTT 프로토콜을 통해 라즈베리파이로 데이터를 전송한다. 명령을 수신한 라즈베리파이는 OpenWeatherMap API 서버로부터 현재 기온과 습도 데이터를 수집 및 가공하여 다시 노트북으로 송신하며, 최종적으로 노트북 스피커의 TTS(Text-to-Speech) 엔진을 통해 안내 음성을 출력한다.

이를 통해 음성 기반 지능형 시스템의 인터랙션(상호작용) 구조와 분산 데이터 처리 메커니즘을 총체적으로 파악하고자 한다.
## 실험장비
1. 라즈베리파이
2. 노트북 (마이크, 오디오)
## 실험절차

먼저, Python에서 paho-mqtt와 requests 라이브러리를 import하고 OpenWeatherMap 공식웹사이트에 들어가 API를 키를 Python 코드에 넣는다. 노트북에서 사용할 Python 코드는 speechrecognition, paho-mqtt, pyttsx3 라이브러리를 import한다. 그 다음, 노트북 코드에 라즈베리파이의 IP 주소를 적어 서로 통신을 연결하고, 라즈베리파이 프로그램을 먼저 실행해 명령 대기 상태로 만든다. 그 후 노트북 프로그램을 실행하고 마이크에 "날씨"라고 말하면, 노트북이 음성을 텍스트로 바꾸어(STT) 라즈베리파이로 요청 메시지를 보낸다. 메시지를 받은 라즈베리파이는 OpenWeatherMap API에서 서울의 기온과 습도 데이터를 가져와 "현재 서울의 기온은..." 형태의 문장으로 가공한 뒤, 다시 노트북으로 전송한다. 마지막으로 노트북은 이 문장을 받아 스피커를 통해 한글 음성(TTS)으로 최종 출력한다.

## 기존 코드설명
```
import speech_recognition as sr
import requests
import os
import time

API_KEY = "Enter your API key here"
url = f"https://api.openweathermap.org/data/2.5/weather?q=Seoul&appid={API_KEY}&units=metric"

def speak(option, msg):
    os.system("espeak {} '{}'".format(option, msg))

try:
    while True:
        r = sr.Recognizer()
        
        with sr.Microphone() as source:
            print("Say something!")
            audio = r.listen(source)
            
        try:
            text = r.recognize_google(audio, language='ko-KR')
            print("You said: " + text)
            if text in "날씨":
                print("날씨 음성을 인식하였습니다.")
                response = requests.get(url)
                data = response.json()
                temp = data["main"]["temp"]
                humi = data["main"]["humidity"]
                
                msg = '    기온은 ' + str(int(temp)) + '도 습도는 ' + str(humi) + '퍼센트 입니다'
                
                option = '-s 180 -p 50 -a 200 -v ko+f5'
                speak(option, msg)
            
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

except KeyboardInterrupt:
    pass
```
이 코드는 **마이크로 "날씨"라는 말을 인식하면 실시간으로 서울의 현재 기온과 습도를 조회하여 음성으로 안내해 주는 파이썬 프로그램**이다.

전체적인 동작 과정을 살펴보면, 우선 프로그램이 실행된 후 사용자의 입력을 기다리는 무한 루프(`while True`) 상태로 들어간다. 프로그램은 컴퓨터의 마이크를 활성화하고 사용자가 목소리를 낼 때까지 기다렸다가 음성을 녹음한다. 녹음된 오디오 데이터는 구글의 음성 인식 엔진(`recognize_google`)을 통해 한국어 텍스트로 변환된다.

변환된 텍스트에 "날씨"라는 단어가 포함되어 있다면 날씨 정보를 가져오는 단계로 넘어간다. 미리 설정해 둔 OpenWeatherMap API 주소로 인터넷 요청을 보내 서울의 최신 날씨 데이터를 받아온 뒤, 그 안에서 기온과 습도 수치만 쏙 골라낸다. 마지막으로 이 데이터들을 "기온은 X도 습도는 Y퍼센트 입니다"라는 문장으로 만든 다음, 컴퓨터의 시스템 명령어로 작동하는 음성 합성 프로그램인 `espeak`를 호출하여 한국어 음성으로 사용자에게 들려준다.

주변 소음으로 음성을 인식하지 못하거나 인터넷 연결에 문제가 생겨도 프로그램이 갑자기 멈추지 않도록 예외 처리(`try-except`)가 꼼꼼하게 되어 있으며, 사용자가 키보드로 `Ctrl + C`를 누르면 안전하게 종료되도록 설계된 스마트 비서 형태의 코드이다.

## STT 원리

STT는 마이크를 통해 유입된 아날로그 소리 신호(공기의 진동)를 컴퓨터가 처리할 수 있는 문자 데이터로 변환하는 기술이다. 이는 아날로그 신호를 아주 짧은 시간 단위의 디지털 신호로 변환하는 '디지털화' 단계, 소음 제거 후 고유 주파수를 추출하는 '특징 추출' 단계, 그리고 인공지능(AI) 엔진을 통한 '모델 비교 및 매칭' 단계를 거친다. 최종적으로는 음향 모델과 언어 모델을 기반으로 데이터베이스 내 단어들과 비교하여 문맥상 가장 확률이 높은 글자를 판별해 내는 원리로 동작한다. 

## TTS 원리

TTS는 시스템이 보유한 텍스트 정보를 사람이 청취할 수 있는 자연스러운 오디오 신호로 변환하는 기술이다. 입력된 텍스트의 형태소를 분석하여 문장 부호와 문맥에 따른 억양, 어조, 쉼표의 위치를 계산하는 '텍스트 분석'을 먼저 수행한다. 이후 분석된 정보에 맞춰 미리 녹음된 음소(소리 조각)를 자연스럽게 결합하거나, 딥러닝 기반의 AI 모델이 사람의 목소리 파형을 수학적으로 생성하여 스피커로 출력하는 원리를 가진다.

------------
유튜브 데모영상 : https://youtu.be/XRA62GJWX_E 
