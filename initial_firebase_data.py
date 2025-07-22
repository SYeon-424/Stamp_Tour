import pyrebase

firebase_config = {
    "apiKey": "AIzaSyAnQEAGW1Of4_H1GqDU0YLum5BPHCA4o6s",
    "authDomain": "stamp-tour-syeon02424.firebaseapp.com",
    "databaseURL": "https://stamp-tour-syeon02424-default-rtdb.firebaseio.com",
    "projectId": "stamp-tour-syeon02424",
    "storageBucket": "stamp-tour-syeon02424.appspot.com",
    "messagingSenderId": "243251650008",
    "appId": "1:243251650008:web:d37c89919c821a7bcae6ad"
}

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()

db.child("stamp_data").set({})
db.child("reservation_status").set({
    "Static": False,
    "인포메티카": False,
    "배째미": False,
    "생동감": False,
    "셈터": False,
    "시그너스": False,
    "마스터": False,
    "플럭스": False,
    "제트원": False,
    "오토메틱": False,
    "스팀": False,
    "넛츠": False,
    "케미어스": False
})
db.child("reservations").set({})

print("✅ Firebase 초기화 완료")
