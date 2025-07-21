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
if "page" not in st.session_state:
    st.session_state.page = "main"
if "selected_club" not in st.session_state:
    st.session_state.selected_club = ""

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
                time.sleep(1)
                st.rerun()

            except Exception:
                st.error("❌ 로그인 실패 - 이메일 또는 비밀번호 확인")

# 회원가입 클래스
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
                st.rerun()
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

# 로그인 상태이고 메인 페이지일 경우
if st.session_state.logged_in and st.session_state.page == "main":
    st.title("🎯 도장판")
    st.write(f"닉네임: {st.session_state.nickname}")
    st.image("StampPaperSample.png", use_container_width=True)

    st.markdown("---")
    st.subheader("🔍 동아리 체험 부스")

    clubs = [
        "로보틱스", "인공지능", "바이오", "천문", "화학", "지구과학", "수학연구",
        "전산", "전기전자", "기계", "물리실험", "에너지", "디자인사이언스"
    ]

    for club in clubs:
        if st.button(f"{club} 부스 소개 보기", key=f"club_{club}"):
            st.session_state.page = "club_intro"
            st.session_state.selected_club = club
            st.rerun()

    st.markdown("---")

    if st.button("로그아웃"):
        st.session_state.logged_in = False
        st.session_state.page = "main"
        st.rerun()

# 동아리 소개 페이지
elif st.session_state.page == "club_intro":
    club = st.session_state.selected_club
    st.title(f"📘 {club} 부스 소개")
    st.write(f"여기에 **{club}** 동아리에 대한 자세한 소개를 입력하세요.")
    st.image("club_default.png", caption=f"{club} 활동 사진", use_column_width=True)

    if st.button("⬅ 도장판으로 돌아가기"):
        st.session_state.page = "main"
        st.rerun()

# 로그인 안 된 경우: 로그인/회원가입 탭 표시
elif not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    with tab1:
        Login()
    with tab2:
        Register(login_page_url="")
