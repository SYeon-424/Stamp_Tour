import streamlit as st
import pyrebase
import time
import json
import os
from PIL import Image

firebase_config = {
    "apiKey": "AIzaSyCswFmrOGU3FyLYxwbNPTp7hvQxLfTPIZw",
    "authDomain": "sw-projects-49798.firebaseapp.com",
    "databaseURL": "https://sw-projects-49798-default-rtdb.firebaseio.com",
    "projectId": "sw-projects-49798",
    "storageBucket": "sw-projects-49798.appspot.com",
    "messagingSenderId": "812186368395",
    "appId": "1:812186368395:web:be2f7291ce54396209d78e"
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
    "Static": {
        "description": "Static 소개... 유지원은 일해라아!!",
        "image": "club_images/Static.png"
    },
    "인포메티카": {
        "description": "인포메티카 소개",
        "image": "club_images/infomatica.png"
    },
    "배째미": {
        "description": "시현이는 천재야",
        "image": "club_images/bajjami.png"
    }
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.nickname = ""
    st.session_state.phone = ""
    st.session_state.page = "main"
    st.session_state.selected_club = ""
    st.session_state.admin_club = None
    st.session_state.admin_mode = False

data_file = "stamp_data.json"
reservation_status_file = "reservation_status.json"
reservation_data_file = "reservations.json"

def load_reservation_status():
    if not os.path.exists(reservation_status_file):
        with open(reservation_status_file, "w") as f:
            json.dump({}, f)
    with open(reservation_status_file, "r") as f:
        return json.load(f)

def save_reservation_status(data):
    with open(reservation_status_file, "w") as f:
        json.dump(data, f, indent=2)

def load_reservations():
    if not os.path.exists(reservation_data_file):
        with open(reservation_data_file, "w") as f:
            json.dump({}, f)
    with open(reservation_data_file, "r") as f:
        return json.load(f)

def save_reservations(data):
    with open(reservation_data_file, "w") as f:
        json.dump(data, f, indent=2)

def load_stamp_data():
    if not os.path.exists(data_file):
        with open(data_file, "w") as f:
            json.dump({}, f)
    try:
        with open(data_file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_stamp_data(data):
    with open(data_file, "w") as f:
        json.dump(data, f, indent=2)

stamp_data = load_stamp_data()

class Login:
    def __init__(self):
        st.title("🔐 로그인")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state.logged_in = True
                st.session_state.user_email = email
                user_info = db.child("users").child(email.replace(".", "_")).get().val()
                if user_info:
                    st.session_state.nickname = user_info.get("nickname", "")
                    st.session_state.phone = user_info.get("phone", "")
                st.success("✅ 로그인 성공!")
                st.rerun()
                st.stop() 
            except:
                st.error("❌ 로그인 실패 - 이메일 또는 비밀번호 확인")

class Register:
    def __init__(self):
        st.title("📝 회원가입")
        email = st.text_input("이메일", key="signup_email")
        password = st.text_input("비밀번호", type="password", key="signup_pw")
        nickname = st.text_input("닉네임", key="signup_nick")
        phone = st.text_input("휴대전화번호", key="signup_phone")
        if st.button("회원가입"):
            stamp_data = load_stamp_data()
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
                stamp_data[nickname] = []
                save_stamp_data(stamp_data)
                st.success("✅ 회원가입 성공!")
                st.rerun()
            except:
                st.error("❌ 회원가입 실패 - 이메일 중복 여부 확인")

def show_stamp_board():
    st.title("🎯 도장판")
    st.write(f"닉네임: {st.session_state.nickname}")

    stamp_data = load_stamp_data()

    base = Image.open("StampPaperSample.png").convert("RGBA")
    overlay = Image.new("RGBA", base.size, (255, 255, 255, 0))

    user_stamps = stamp_data.get(st.session_state.nickname, [])
    for club in user_stamps:
        try:
            stamp = Image.open(f"stamps/{club}.png").convert("RGBA")
            overlay = Image.alpha_composite(overlay, stamp)
        except:
            pass

    result = Image.alpha_composite(base, overlay)
    st.image(result, use_container_width=True)

    st.markdown("---")
    st.subheader("🔬 체험 부스")
    for i, club in enumerate(clubs):
        cols = st.columns([2, 1])
        with cols[0]:
            if st.button(f"{club} 부스 소개", key=f"club_button_{i}"):
                st.session_state.page = "club_intro"
                st.session_state.selected_club = club
                st.rerun()
        with cols[1]:
            reservation_status = load_reservation_status()
            if reservation_status.get(club, False):
                if st.button("예약", key=f"reserve_button_{i}"):
                    st.session_state.selected_club = club
                    st.session_state.page = "reservation_page"
                    st.rerun()

    st.markdown("---")
    if st.button("Staff only"):
        st.session_state.page = "admin_login"
        st.rerun()
    if st.button("로그아웃"):
        st.session_state.logged_in = False
        st.session_state.page = "main"
        st.rerun()

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    with tab1:
        Login()
    with tab2:
        Register()

elif st.session_state.logged_in and st.session_state.page == "main":
    show_stamp_board()

elif st.session_state.page == "club_intro":
    club = st.session_state.selected_club
    st.title(f"📑 {club} 부스 소개")

    club_info = club_infos.get(club, {
        "description": "소개 정보가 없습니다.",
        "image": "club_default.png"
    })

    st.write(club_info["description"])
    st.image(club_info["image"], caption=f"{club} 활동 소개", use_container_width=True)

    if st.button("🔙 메인으로", key="back_to_main"):
        st.session_state.page = "main"
        st.rerun()


elif st.session_state.page == "admin_login":
    st.title("🔑 인증")

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

    st.markdown("---")
    if st.button("🔙 메인으로"):
        st.session_state.page = "main"
        st.rerun()

elif st.session_state.page == "reservation_page":
    club = st.session_state.selected_club
    st.title(f"📅 {club} 예약")

    reservations = load_reservations()
    club_reservations = reservations.get(club, [])
    nickname = st.session_state.nickname
    phone = st.session_state.phone

    existing = next((r for r in club_reservations if r["nickname"] == nickname), None)

    st.markdown("#### 📋 예약 현황")
    if club_reservations:
        st.table([
            {"시간": r["time"], "닉네임": r["nickname"]}
            for r in club_reservations
        ])
    else:
        st.info("아직 예약된 인원이 없습니다.")

    st.markdown("---")

    if existing:
        st.info(f"⏰ 이미 예약되어 있습니다: {existing['time']}")
        if st.button("❌ 예약 취소"):
            club_reservations.remove(existing)
            reservations[club] = club_reservations
            save_reservations(reservations)
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
            new_entry = {"time": selected_time, "nickname": nickname, "phone": phone}
            club_reservations.append(new_entry)
            reservations[club] = club_reservations
            save_reservations(reservations)
            st.success("예약이 완료되었습니다!")
            time.sleep(1)
            st.rerun()

    st.markdown("---")
    if st.button("🔙 뒤로 가기"):
        st.session_state.page = "main"
        st.rerun()

elif st.session_state.page == "admin_panel":
    st.title(f"✅ {st.session_state.admin_club} 관리자 페이지")
    tab1, tab2 = st.tabs(["📌 도장 찍기", "📅 예약 관리"])

    with tab1:
        nickname = st.text_input("닉네임 입력")
        if st.button("도장 찍기"):
            stamp_data = load_stamp_data()
            if nickname not in stamp_data:
                st.error("❌ 존재하지 않는 닉네임입니다.")
            else:
                if st.session_state.admin_club not in stamp_data[nickname]:
                    stamp_data[nickname].append(st.session_state.admin_club)
                    save_stamp_data(stamp_data)
                    st.success("📌 도장을 찍었습니다!")
                else:
                    st.info("❌ 이미 도장이 찍혀 있습니다.")

    with tab2:
        reservation_status = load_reservation_status()
        reservations = load_reservations()
        club = st.session_state.admin_club

        is_enabled = reservation_status.get(club, False)
        new_status = st.checkbox("예약 기능 활성화", value=is_enabled)
        if new_status != is_enabled:
            reservation_status[club] = new_status
            save_reservation_status(reservation_status)
            st.success(f"예약 기능이 {'활성화' if new_status else '비활성화'}되었습니다.")

        if reservation_status.get(club, False):
            st.markdown("#### 📋 예약 목록")
            club_reservations = reservations.get(club, [])
            if not club_reservations:
                st.info("예약된 항목이 없습니다.")
            else:
                st.table([
                    {"시간": r["time"], "닉네임": r["nickname"], "전화번호": r["phone"]}
                    for r in club_reservations
                ])

    if st.button("🔙 메인으로"):
        st.session_state.page = "main"
        st.session_state.admin_mode = False
        st.rerun()
