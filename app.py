import streamlit as st
import pyrebase
import time
import os
from PIL import Image

firebase_config = {
    "apiKey": "AIzaSyAnQEAGW1Of4_H1GqDU0YLum5BPHCA4o6s",
    "authDomain": "stamp-tour-syeon02424.firebaseapp.com",
    "databaseURL": "https://stamp-tour-syeon02424-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "stamp-tour-syeon02424",
    "storageBucket": "stamp-tour-syeon02424.appspot.com",
    "messagingSenderId": "243251650008",
    "appId": "1:243251650008:web:d37c89919c821a7bcae6ad"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()

club_passwords = {
    "Static": "pw1", 
    "인포메티카": "pw2",
    "배째미": "pw3", 
    "생동감": "pw4",
    "셈터": "pw5", 
    "시그너스": "pw6", 
    "마스터": "pw7", 
    "플럭스": "pw8",
    "제트원": "pw9", 
    "오토메틱": "pw10", 
    "스팀": "pw11", 
    "넛츠": "pw12", 
    "케미어스": "pw13"
}
clubs = list(club_passwords.keys())

club_infos = {
    "Static": {"description": "Static 소개... 유지원은 일해라아!!", "image": "club_images/Static.png"},
    "인포메티카": {"description": "인포메티카 소개", "image": "club_images/infomatica.png"},
    "배째미": {"description": "시현이는 천재야", "image": "club_images/bajjami.png"}
}

if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False,
        "user_email": "",
        "nickname": "",
        "phone": "",
        "page": "main",
        "selected_club": "",
        "admin_club": None,
        "admin_mode": False
    })

def initialize_firebase_data():
    if not db.child("reservation_status").get().val():
        db.child("reservation_status").set({club: False for club in clubs})
    if not db.child("stamp_data").get().val():
        db.child("stamp_data").set({})
    if not db.child("max_reservations").get().val():
        db.child("max_reservations").set({club: 2 for club in clubs})
        
    try:
        existing = db.child("stamp_data").get().val()
        if existing is None:
            db.child("stamp_data").set({})
    except Exception as e:
        st.error(f"🔥 stamp_data 초기화 중 오류 발생: {e}")

initialize_firebase_data()

def load_data(path):
    data = db.child(path).get().val()
    return data if data else {}

def save_data(path, data):
    db.child(path).set(data)

initialize_firebase_data()

class Login:
    def __init__(self):
        st.title("🔐 로그인")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            try:
                auth.sign_in_with_email_and_password(email, password)
                st.session_state.logged_in = True
                st.session_state.user_email = email
                user_info = db.child("users").child(email.replace(".", "_")).get().val()
                if user_info:
                    st.session_state.nickname = user_info.get("nickname", "")
                    st.session_state.phone = user_info.get("phone", "")
                st.success("✅ 로그인 성공!")
                st.rerun()
            except:
                st.error("❌ 로그인 실패 - 이메일 또는 비밀번호 확인")

class Register:
    def __init__(self):
        st.title("📝 회원가입")
        email = st.text_input("이메일", key="signup_email")
        password = st.text_input("비밀번호", type="password", key="signup_pw")
        nickname = st.text_input("닉네임", key="signup_nick")

        if any(c in nickname for c in ".#$[]/ ") or nickname.strip() == "":
            st.error("❌ 닉네임에 공백이나 '.', '#', '$', '[', ']', '/' 는 사용할 수 없습니다.")
            st.stop()

        phone = st.text_input("휴대전화번호", key="signup_phone")
        if st.button("회원가입"):
            stamp_data = load_data("stamp_data")
            if nickname in stamp_data:
                st.error("❌ 이미 존재하는 닉네임입니다.")
                return
            try:
                auth.create_user_with_email_and_password(email, password)
                db.child("users").child(email.replace(".", "_")).set({
                    "email": email,
                    "nickname": nickname,
                    "phone": phone
                })
                club_status = {club: False for club in clubs}
                stamp_data[nickname] = club_status
                save_data("stamp_data", stamp_data)
                st.success("✅ 회원가입 성공!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 회원가입 실패: {e}")


def show_stamp_board():
    st.title("🎯 도장판")
    st.write(f"닉네임: {st.session_state.nickname}")

    stamp_data = load_data("stamp_data")
    
    if "last_stamp_data" not in st.session_state:
        st.session_state.last_stamp_data = {}

    if stamp_data != st.session_state.last_stamp_data:
        st.session_state.last_stamp_data = stamp_data
        st.rerun() 

    base = Image.open("StampPaperSample.png").convert("RGBA")
    overlay = Image.new("RGBA", base.size, (255, 255, 255, 0))

    user_stamps = stamp_data.get(st.session_state.nickname, {})
    for club, stamped in user_stamps.items():
        if stamped:
            try:
                stamp = Image.open(f"stamps/{club}.png").convert("RGBA")
                overlay = Image.alpha_composite(overlay, stamp)
            except Exception as e:
                print(f"⚠️ Stamp image not found for {club}: {e}")

    result = Image.alpha_composite(base, overlay)
    st.image(result, use_container_width=True)

    st.markdown("---")
    st.subheader("🔬 체험 부스")
    reservation_status = load_data("reservation_status")
    for i, club in enumerate(clubs):
        col1, col2, col3 = st.columns([3, 1.5, 1])
        with col1:
            st.write(f"**{club}**") 
        with col2:
            b1 = st.button("부스 소개", key=f"club_button_{i}")
        with col3:
            b2 = None
            if reservation_status.get(club, False):
                b2 = st.button("예약", key=f"reserve_button_{i}")

        if b1:
            st.session_state.page = "club_intro"
            st.session_state.selected_club = club
            st.rerun()

        if b2:
            st.session_state.page = "reservation_page"
            st.session_state.selected_club = club
            st.rerun()

        st.markdown("---")

    st.markdown("---")
    if st.button("Staff only"):
        st.session_state.page = "admin_login"
        st.rerun()
    if st.button("로그아웃"):
        st.session_state.logged_in = False
        st.session_state.page = "main"
        st.rerun()

if st.session_state.page == "club_intro":
    club = st.session_state.selected_club
    st.title(f"📑 {club}")
    club_info = club_infos.get(club, {"description": "소개 정보가 없습니다.", "image": "club_default.png"})
    st.write(club_info["description"])
    st.image(club_info["image"], caption=f"{club} 활동 소개", use_container_width=True)
    if st.button("🔙 메인으로"):
        st.session_state.page = "main"
        st.rerun()

elif st.session_state.page == "reservation_page":
    club = st.session_state.selected_club
    st.title(f"📅 {club} 예약")

    reservations = load_data("reservations")
    club_reservations = reservations.get(club, [])
    nickname = st.session_state.nickname
    phone = st.session_state.phone

    existing = next((r for r in club_reservations if r["nickname"] == nickname), None)

    st.markdown("#### 📋 예약 현황")
    if club_reservations:
        st.table([{"시간": r["time"], "닉네임": r["nickname"]} for r in club_reservations])
    else:
        st.info("아직 예약된 인원이 없습니다.")

    st.markdown("---")

    if existing:
        st.info(f"⏰ 이미 예약되어 있습니다: {existing['time']}")
        if st.button("❌ 예약 취소"):
            club_reservations.remove(existing)
            reservations[club] = club_reservations
            save_data("reservations", reservations)
            st.success("예약이 취소되었습니다.")
            time.sleep(1)
            st.rerun()
    else:
        st.markdown("#### 🔽 예약 시간 선택")
        selected_time = st.selectbox("시간 선택", [
            "10:00", "10:30", "11:00", "11:30",
            "13:00", "13:30", "14:00", "14:30"
        ])

        if st.button("✅ 예약"):
            max_reservations = load_data("max_reservations")
            limit = max_reservations.get(club, 2)
            
            count = sum(1 for r in club_reservations if r["time"] == selected_time)
            
            if count >= limit:
                st.error("❌ 해당 시간대 예약 인원이 가득 찼습니다.")
            else:
                new_entry = {"time": selected_time, "nickname": nickname, "phone": phone}
                club_reservations.append(new_entry)
                reservations[club] = club_reservations
                save_data("reservations", reservations)
                st.success("예약이 완료되었습니다!")
                time.sleep(1)
                st.rerun()

    st.markdown("---")
    if st.button("🔙 메인으로"):
        st.session_state.page = "main"
        st.rerun()

elif st.session_state.page == "admin_login":
    st.title("🗝️ 인증")
    admin_pw = st.text_input("비밀번호 입력", type="password")
    if st.button("Enter"):
        for club, pw in club_passwords.items():
            if admin_pw == pw:
                st.session_state.admin_club = club
                st.session_state.page = "admin_panel"
                st.session_state.admin_mode = True
                st.rerun()
                st.stop()
        st.error("❌ 잘못된 비밀번호입니다.")
    if st.button("🔙 메인으로"):
        st.session_state.page = "main"
        st.rerun()

elif st.session_state.page == "admin_panel":
    st.title(f"✅ {st.session_state.admin_club} 관리자 페이지")
    tab1, tab2 = st.tabs(["📌 도장 찍기", "📅 예약 관리"])

    with tab1:
        nickname = st.text_input("닉네임 입력")
        if st.button("도장 찍기"):
            stamp_data = load_data("stamp_data")
            if nickname not in stamp_data:
                st.error("❌ 존재하지 않는 닉네임입니다.")
            else:
                if not stamp_data[nickname].get(st.session_state.admin_club, False):
                    stamp_data[nickname][st.session_state.admin_club] = True
                    save_data("stamp_data", stamp_data)
                    st.success("📌 도장을 찍었습니다!")
                else:
                    st.info("❌ 이미 도장이 찍혀 있습니다.")

    with tab2:
        reservation_status = load_data("reservation_status")
        max_reservations = load_data("max_reservations")
        reservations = load_data("reservations")
        club = st.session_state.admin_club
        
        is_enabled = reservation_status.get(club, False)
        new_status = st.checkbox("예약 기능 활성화", value=is_enabled)
        
        max_num = max_reservations.get(club, 3)
        new_max = st.number_input("시간당 최대 예약 인원 수", min_value=1, max_value=20, value=max_num, key=f"{club}_max")
        
        if new_status != is_enabled or new_max != max_num:
            reservation_status[club] = new_status
            max_reservations[club] = new_max
            save_data("reservation_status", reservation_status)
            save_data("max_reservations", max_reservations)
            st.success(f"✅ 설정이 저장되었습니다.")

        if new_status != is_enabled:
            reservation_status[club] = new_status
            save_data("reservation_status", reservation_status)
            st.success(f"예약 기능이 {'활성화' if new_status else '비활성화'}되었습니다.")

        if reservation_status.get(club, False):
            st.markdown("#### 📋 예약 목록")
            club_reservations = reservations.get(club, [])
            if not club_reservations:
                st.info("예약된 항목이 없습니다.")
            else:
                st.table([{ "시간": r["time"], "닉네임": r["nickname"], "전화번호": r["phone"] } for r in club_reservations])

    if st.button("🔙 메인으로"):
        st.session_state.page = "main"
        st.session_state.admin_mode = False
        st.rerun()

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    with tab1:
        Login()
    with tab2:
        Register()
elif st.session_state.logged_in and st.session_state.page == "main":
    show_stamp_board()
