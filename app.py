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
        st.title("\U0001F510 로그인")
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

                st.success("\u2705 로그인 성공!")
                time.sleep(1)
                st.rerun()

            except Exception:
                st.error("\u274C 로그인 실패 - 이메일 또는 비밀번호 확인")

# 회원가입 클래스
class Register:
    def __init__(self, login_page_url: str):
        st.title("\U0001F4DD 회원가입")
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
                st.success("\U0001F389 회원가입 성공! 로그인 페이지로 이동합니다.")
                time.sleep(1)
                st.rerun()
            except Exception:
                st.error("\u274C 회원가입 실패 - 이메일 중복 여부 확인")

# 비밀번호 찾기 클래스
class FindPassword:
    def __init__(self):
        st.title("\U0001F511 비밀번호 재설정")
        email = st.text_input("이메일")
        if st.button("비밀번호 재설정 이메일 발송"):
            try:
                auth.send_password_reset_email(email)
                st.success("\U0001F4E9 이메일이 전송되었습니다.")
                time.sleep(1)
                st.rerun()
            except:
                st.error("\u274C 이메일 전송 실패")

# 로그인 후 도장판과 관리자 탭
if st.session_state.logged_in and st.session_state.page == "main":
    tab1, tab2 = st.tabs(["도장판", "관리자 모드"])

    with tab1:
        st.title("\U0001F3AF 도장판")
        st.write(f"닉네임: {st.session_state.nickname}")
        st.image("StampPaperSample.png", use_container_width=True)

        st.markdown("---")
        st.subheader("\U0001F50D 동아리 체험 부스")

        clubs = [
            "Static", "인포메티카", "배째미", "생동감", "셈터", "시그너스", "마스터",
            "플럭스", "제트온", "오토메틱", "스팀", "넛츠", "케미어스"
        ]

        for i, club in enumerate(clubs):
            if st.button(f"{club} 부스 소개 보기", key=f"club_button_{i}"):
                st.session_state.page = "club_intro"
                st.session_state.selected_club = club
                st.rerun()

        if st.button("로그아웃", key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.page = "main"
            st.rerun()

    with tab2:
        st.title("\U0001F512 관리자 모드")

        if "admin_authenticated" not in st.session_state:
            st.session_state.admin_authenticated = False

        if not st.session_state.admin_authenticated:
            password = st.text_input("비밀번호 입력", type="password", key="admin_pw")
            if st.button("입장", key="admin_enter_btn"):
                if password == "dshs37":
                    st.session_state.admin_authenticated = True
                    st.success("\u2705 인증 성공!")
                    st.rerun()
                else:
                    st.error("\u274C 비밀번호 틀림")
        else:
            st.success("\U0001F451 관리자 인증 완료")
            club = st.selectbox("✅ 도장 찍을 부스 선택", clubs)
            nickname = st.text_input("닉네임 입력", key="admin_nick_input")

            if st.button("도장 찍기", key="admin_stamp_btn"):
                try:
                    user_ref = db.child("users").get()
                    user_found = False
                    for u in user_ref.each():
                        data = u.val()
                        if data.get("nickname", "") == nickname:
                            user_found = True
                            user_key = u.key()
                            db.child("users").child(user_key).child("stamps").update({club: True})
                            st.success(f"✅ {nickname}님에게 {club} 도장 찍음!")
                            break
                    if not user_found:
                        st.warning("해당 닉네임을 가진 유저가 없습니다.")
                except Exception as e:
                    st.error(f"에러 발생: {str(e)}")

            if st.button("\U0001F513 관리자 인증 해제", key="admin_logout_btn"):
                st.session_state.admin_authenticated = False
                st.rerun()

# 동아리 소개 페이지
elif st.session_state.page == "club_intro":
    club = st.session_state.selected_club
    st.title(f"\U0001F4D8 {club} 부스 소개")
    st.write(f"여기에 **{club}** 동아리에 대한 자세한 소개를 입력하세요.")
    st.image("club_default.png", caption=f"{club} 활동 사진", use_container_width=True)

    if st.button("\u2B05 도장판으로 돌아가기", key="back_to_main"):
        st.session_state.page = "main"
        st.rerun()

# 로그인 안 된 경우
elif not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    with tab1:
        Login()
    with tab2:
        Register(login_page_url="")

