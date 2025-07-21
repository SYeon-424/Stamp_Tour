import streamlit as st
import pyrebase
import time

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

# 세션 초기화
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.nickname = ""
    st.session_state.phone = ""

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

                # 닉네임, 전화번호 불러오기
                user_info = db.child("users").child(email.replace(".", "_")).get().val()
                if user_info:
                    st.session_state.nickname = user_info.get("nickname", "")
                    st.session_state.phone = user_info.get("phone", "")

                st.success("✅ 로그인 성공!")
                time.sleep(1)
                st.rerun()

            except Exception:
                st.error("❌ 로그인 실패 - 이메일 또는 비밀번호 확인")

class Register:
    def __init__(self, login_page_url: str):
        st.title("📝 회원가입")
        email = st.text_input("이메일", key="signup_email")
        password = st.text_input("비밀번호", type="password", key="signup_pw")
        nickname = st.text_input("닉네임", key="signup_nick")
        phone = st.text_input("휴대전화번호", key="signup_phone")

        if st.button("회원가입", key="signup_btn"):
            try:
                auth.create_user_with_email_and_password(email, password)
                db.child("users").child(email.replace(".", "_")).set({
                    "email": email,
                    "nickname": nickname,
                    "phone": phone
                })
                st.success("🎉 회원가입 성공! 로그인 페이지로 이동합니다.")
                time.sleep(1)
                st.rerun()  # 페이지 전환 대신 rerun 사용

            except Exception:
                st.error("❌ 회원가입 실패 - 이메일 중복 여부 확인")

# 비밀번호 찾기 클래스
class FindPassword:
    def __init__(self):
        st.title("🔑 비밀번호 재설정")
        email = st.text_input("이메일")

        if st.button("비밀번호 재설정 이메일 발송"):
            try:
                auth.send_password_reset_email(email)
                st.success("📩 이메일이 전송되었습니다.")
                time.sleep(1)
                st.rerun()

            except:
                st.error("❌ 이메일 전송 실패")


# 화면 출력 제어 (최종 실행 코드)
if st.session_state.logged_in:
    st.title("🎯 도장판")
    st.write(f"닉네임: {st.session_state.nickname}")
    st.image("static/stampboard.png", width=750)  # 이미지 경로 맞게 수정

    if st.button("로그아웃"):
        st.session_state.logged_in = False
        st.rerun()
else:
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    with tab1:
        Login()
    with tab2:
        Register(login_page_url="")  # 또는 그냥 Register("")
