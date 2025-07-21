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

# 부스별 관리자 비밀번호 매핑
admin_passwords = {
    "Static": "pw1",
    "인포메티카": "pw2",
    "배째미": "pw3",
    # ... 필요한 만큼 추가 가능
}

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
if "admin_club" not in st.session_state:
    st.session_state.admin_club = None

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
    def __init__(self):
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

# 관리자 모드 진입
if st.session_state.logged_in and st.session_state.page == "main":
    st.title("🎯 도장판")
    st.write(f"닉네임: {st.session_state.nickname}")
    st.image("StampPaperSample.png", use_container_width=True)

    st.markdown("---")
    st.subheader("🔍 동아리 체험 부스")

    clubs = list(admin_passwords.keys())
    for i, club in enumerate(clubs):
        if st.button(f"{club} 부스 소개 보기", key=f"club_button_{i}"):
            st.session_state.page = "club_intro"
            st.session_state.selected_club = club
            st.rerun()

        st.markdown("---")

    if st.button("🔑 관리자 모드"):
        st.session_state.page = "admin_login"
        st.rerun()

    if st.button("로그아웃"):
        st.session_state.logged_in = False
        st.session_state.page = "main"
        st.rerun()

# 관리자 비밀번호 입력
elif st.session_state.page == "admin_login":
    st.title("🔐 관리자 모드 로그인")
    pw = st.text_input("부스별 비밀번호를 입력하세요", type="password")
    if st.button("확인"):
        found = False
        for club, password in admin_passwords.items():
            if pw == password:
                st.session_state.admin_club = club
                st.session_state.page = "admin_panel"
                st.success(f"✅ {club} 관리자 모드 진입 완료!")
                time.sleep(1)
                st.rerun()
                found = True
                break
        if not found:
            st.error("❌ 비밀번호가 올바르지 않습니다.")

# 관리자 패널
elif st.session_state.page == "admin_panel" and st.session_state.admin_club:
    club = st.session_state.admin_club
    st.title(f"🔧 {club} 부스 도장 찍기")
    nickname = st.text_input("닉네임 입력")
    if st.button("✅ 도장 찍기"):
        all_users = db.child("users").get().val()
        target_key = None
        for key, val in all_users.items():
            if val.get("nickname") == nickname:
                target_key = key
                break
        if target_key:
            db.child("stamps").child(target_key).update({club: True})
            st.success(f"🎉 {nickname}님께 {club} 도장을 찍었습니다!")
        else:
            st.error("❌ 해당 닉네임을 가진 사용자가 없습니다.")
    if st.button("⬅ 뒤로 가기"):
        st.session_state.page = "main"
        st.rerun()

# 동아리 소개 페이지
elif st.session_state.page == "club_intro":
    club = st.session_state.selected_club
    st.title(f"📘 {club} 부스 소개")
    st.write(f"여기에 **{club}** 동아리에 대한 자세한 소개를 입력하세요.")
    st.image("club_default.png", caption=f"{club} 활동 사진", use_container_width=True)

    if st.button("⬅ 도장판으로 돌아가기", key="back_to_main"):
        st.session_state.page = "main"
        st.rerun()

# 로그인/회원가입 탭
elif not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    with tab1:
        Login()
    with tab2:
        Register()

