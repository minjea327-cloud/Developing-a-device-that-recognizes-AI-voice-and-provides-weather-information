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