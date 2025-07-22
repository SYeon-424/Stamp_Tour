import streamlit as st
import pyrebase
import time
import json
import os
from PIL import Image

# Firebase 설정
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

# 부스 목록과 비밀번호
club_passwords = {
    "Static": "pw1",
    "인포메티카": "pw2",
    "배째미": "pw3",
    "생동감": "pw4",
    "셈터": "pw5",
    "시그너스": "pw6",
    "마스터": "pw7",
    "플럭스": "pw8",
    "제트온": "pw9",
    "오토메틱": "pw10",
    "스팀": "pw11",
    "넛츠": "pw12",
    "케미어스": "pw13"
}

clubs = list(club_passwords.keys())

club_infos = {
    "Static": {
        "description": "Static은 하드웨어와 소프트웨어를 융합한 프로젝트를 진행하는 동아리입니다.",
        "image": "club_images/Static.png"
    },
    "인포메티카": {
        "description": "인포메티카는 데이터 분석과 AI를 다루는 정보동아리입니다.",
        "image": "club_images/infomatica.png"
    },
    "배째미": {
        "description": "시현이는 천재야",
        "image": "club_images/bajjami.png"
    }
    # ... 나머지 부스도 추가
}


# 세션 초기화
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.nickname = ""
    st.session_state.phone = ""
    st.session_state.page = "main"
    st.session_state.selected_club = ""
    st.session_state.admin_club = None
    st.session_state.admin_mode = False

# JSON 파일 경로
data_file = "stamp_data.json"

# JSON 초기화 함수
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

# 로그인 클래스
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
                time.sleep(0.5)
                st.rerun()
                st.stop()  # 💡 추가: rerun 후 남은 코드 실행 막기
            except:
                st.error("❌ 로그인 실패 - 이메일 또는 비밀번호 확인")

# 회원가입 클래스
class Register:
    def __init__(self):
        st.title("📝 회원가입")
        email = st.text_input("이메일", key="signup_email")
        password = st.text_input("비밀번호", type="password", key="signup_pw")
        nickname = st.text_input("닉네임", key="signup_nick")
        phone = st.text_input("휴대전화번호", key="signup_phone")
        if st.button("회원가입"):
            try:
                auth.create_user_with_email_and_password(email, password)
                db.child("users").child(email.replace(".", "_")).set({
                    "email": email,
                    "nickname": nickname,
                    "phone": phone
                })
                stamp_data[nickname] = []
                save_stamp_data(stamp_data)
                st.success("🎉 회원가입 성공!")
                time.sleep(1)
                st.rerun()
            except:
                st.error("❌ 회원가입 실패 - 이메일 중복 여부 확인")

# 도장판 페이지
def show_stamp_board():
    st.title("🎯 도장판")
    st.write(f"닉네임: {st.session_state.nickname}")

    # 최신 데이터 다시 로드
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
    st.subheader("🔍 동아리 체험 부스")
    for i, club in enumerate(clubs):
        if st.button(f"{club} 부스 소개 보기", key=f"club_button_{i}"):
            st.session_state.page = "club_intro"
            st.session_state.selected_club = club
            st.rerun()

    st.markdown("---")
    if st.button("관리자 모드"):
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
    st.title(f"📘 {club} 부스 소개")

    # club_infos에서 정보 불러오기
    club_info = club_infos.get(club, {
        "description": "소개 정보가 없습니다.",
        "image": "club_default.png"
    })

    st.write(club_info["description"])
    st.image(club_info["image"], caption=f"{club} 활동 사진", use_container_width=True)

    if st.button("⬅ 도장판으로", key="back_to_main"):
        st.session_state.page = "main"
        st.rerun()


elif st.session_state.page == "admin_login":
    st.title("🔑 관리자 모드 비밀번호 입력")

    admin_pw = st.text_input("부스용 비밀번호 입력", type="password")
    
    if st.button("입장"):
        for club, pw in club_passwords.items():
            if admin_pw == pw:
                st.session_state.admin_club = club
                st.session_state.page = "admin_panel"
                st.session_state.admin_mode = True
                st.rerun()
                st.stop()
        st.error("❌ 올바르지 않은 비밀번호")

    st.markdown("---")
    if st.button("⬅ 도장판으로 돌아가기"):
        st.session_state.page = "main"
        st.rerun()



elif st.session_state.page == "admin_panel":
    st.title(f"✅ {st.session_state.admin_club} 도장 찍기")
    nickname = st.text_input("닉네임 입력")
    if st.button("도장 찍기"):
        stamp_data = load_stamp_data()
        if nickname not in stamp_data:
            st.error("❌ 존재하지 않는 닉네임입니다.")
        else:
            if st.session_state.admin_club not in stamp_data[nickname]:
                stamp_data[nickname].append(st.session_state.admin_club)
                save_stamp_data(stamp_data)
                st.success("📌 도장 찍기 성공!")
            else:
                st.info("✅ 이미 도장이 찍혀 있습니다.")
    if st.button("⬅ 도장판으로 돌아가기"):
        st.session_state.page = "main"
        st.session_state.admin_mode = False
        st.rerun()
