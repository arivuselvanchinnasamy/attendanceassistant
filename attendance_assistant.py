from flask import Flask, jsonify
import pandas as pd
import speech_recognition as sr
import pyttsx3

app = Flask(__name__)

def initialize_engine():
    engine = pyttsx3.init('sapi5')
    volume = engine.getProperty('volume')
    engine.setProperty('volume', volume+0.50)
    return engine

def speak(engine, text):
    engine.say(text)
    engine.runAndWait()

def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)

    try:
        command = r.recognize_google(audio)
        print(f"User said: {command}\n")
    except Exception as e:
        print("Sorry, I didn't catch that. Could you please repeat?")
        return "None"

    return command.lower()

def getStudents():
    df = pd.read_csv('students.csv')
    students =df.to_dict(orient='records')
    return students

@app.route('/')
def welcome():
    engine = initialize_engine()
    speak(engine, "Hello, I am your voice assistant to mark your attandence. Say Present once your name is soughted?")
    students = getStudents()
    for student in students:
        studentName = student['Name']
        prompt=f"{studentName}, are you present?"
        speak(engine,prompt)
        user_response=listen()
        if "present" in user_response:
            student['Attendance']='Y'
            print(f"{student} is marked as Present.")
        else:
            student['Attendance']='N'
            print(f"{student} is marked as Absent.")
    total_no_students = int(len(students))
    total_no_students_present =sum(i['Attendance'] == 'Y' for i in students)
    print(total_no_students_present)
    total_absentees = total_no_students - total_no_students_present
    attendance_summary = {}
    attendance_summary['Total No of Students']= total_no_students
    attendance_summary['Total No of Students Present']= total_no_students_present
    attendance_summary['Total No of Absentees']= total_absentees
    message = {
        'status': 200,
        'message': 'OK',
        'attendance_details': students,
        'attendance_summary': attendance_summary
    }
    resp = jsonify(message)
    resp.status_code = 200
    print(resp)
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3030)