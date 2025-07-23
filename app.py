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
        "admin_mode": False,
        "viewing_profile": ""
    })

def initialize_firebase_data():
    if not db.child("reservation_status").get().val():
        db.child("reservation_status").set({club: False for club in clubs})
    if not db.child("stamp_data").get().val():
        db.child("stamp_data").set({})
    if not db.child("max_reservations").get().val():
        db.child("max_reservations").set({club: 2 for club in clubs})
    if not db.child("available_times").get().val():
        default_times = [
            "10:00", "10:30", "11:00", "11:30",
            "13:00", "13:30", "14:00", "14:30"
        ]
        db.child("available_times").set({club: default_times for club in clubs})
        
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
def refresh_login():
    try:
        if not st.session_state.get("logged_in", False) and "refresh_token" in st.session_state:
            user = auth.refresh(st.session_state["refresh_token"])
            st.session_state.id_token = user["idToken"]
            st.session_state.logged_in = True
            st.session_state.user_email = user["userId"]
            st.session_state.page = "main"
    except Exception as e:
        print("자동 로그인 실패:", e)
        st.session_state.logged_in = False

class Login:
    def __init__(self):
        st.title("🔐 로그인")
        st.subheader("로그인이 안되면 회원가입을 다시해주세요. 데이터 리셋기능 테스트로 데이터가 날아갔을 수 있습니다... :(")

        email = st.text_input("이메일", key="login_email")
        password = st.text_input("비밀번호", type="password", key="login_pw")

        if st.button("로그인"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                user_info = db.child("users").child(email.replace(".", "_")).get().val()
                if user_info:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.session_state.nickname = user_info.get("nickname", "")
                    st.session_state.phone = user_info.get("phone", "")

                    st.session_state.id_token = user['idToken']
                    st.session_state.refresh_token = user['refreshToken']
                    st.session_state.local_id = user['localId']
                    st.session_state.page = "main"

                    st.success("✅ 로그인 성공!")
                    st.rerun()
                else:
                    st.error("❌ 사용자 정보가 존재하지 않습니다.")
            except Exception as e:
                print("로그인 실패:", e)
                st.error("❌ 로그인 실패. 이메일 또는 비밀번호를 확인하세요.")

class Register:
    def __init__(self):
        st.title("📝 회원가입")
        email = st.text_input("이메일", key="signup_email")
        password = st.text_input("비밀번호", type="password", key="signup_pw")
        nickname = st.text_input("닉네임", key="signup_nick")
        phone = st.text_input("휴대전화번호", key="signup_phone")
        
        if st.button("회원가입"):
            if any(c in nickname for c in ".#$[]/ ") or nickname.strip() == "":
                st.error("❌ 닉네임에 공백이나 '.', '#', '$', '[', ']', '/' 는 사용할 수 없습니다.")
                st.stop()
                
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
    users_data = load_data("users")
    my_nick = st.session_state.nickname
    my_email_key = st.session_state.user_email.replace(".", "_")
    my_data = users_data.get(my_email_key, {})
    my_friends = my_data.get("friends", [])

    if my_data.get("pending_requests"):
        st.subheader("📬 친구 요청 수락")
        for requester in my_data["pending_requests"]:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"👉 {requester}")
            with col2:
                if st.button("수락", key=f"accept_{requester}"):
                    if requester not in my_friends:
                        my_friends.append(requester)
                        db.child("users").child(my_email_key).update({"friends": my_friends})
    
                    requester_email_key = next((k for k, v in users_data.items() if v.get("nickname") == requester), None)
                    if requester_email_key:
                        requester_data = users_data[requester_email_key]
                        requester_friends = requester_data.get("friends", [])
                        if my_nick not in requester_friends:
                            requester_friends.append(my_nick)
                            db.child("users").child(requester_email_key).update({"friends": requester_friends})
    
                        requester_sent = requester_data.get("sent_requests", [])
                        if my_nick in requester_sent:
                            requester_sent.remove(my_nick)
                            db.child("users").child(requester_email_key).update({"sent_requests": requester_sent})
    
                    my_pending = my_data.get("pending_requests", [])
                    my_pending.remove(requester)
                    db.child("users").child(my_email_key).update({"pending_requests": my_pending})
    
                    st.success(f"{requester}님을 친구로 추가했습니다.")
                    st.rerun()
    
            with col3:
                if st.button("거절", key=f"reject_{requester}"):
                    my_pending = my_data.get("pending_requests", [])
                    if requester in my_pending:
                        my_pending.remove(requester)
                        db.child("users").child(my_email_key).update({"pending_requests": my_pending})
                    requester_email_key = next((k for k, v in users_data.items() if v.get("nickname") == requester), None)
                    if requester_email_key:
                        requester_data = users_data[requester_email_key]
                        requester_sent = requester_data.get("sent_requests", [])
                        if my_nick in requester_sent:
                            requester_sent.remove(my_nick)
                            db.child("users").child(requester_email_key).update({"sent_requests": requester_sent})
                    st.info(f"{requester}님의 친구 요청을 거절했습니다.")
                    st.rerun()


    st.title("🎯 도장판")
    st.write(f"닉네임: {st.session_state.nickname}")

    if st.button("🔄 새로고침"):
        st.rerun()
    if st.button("친구 관리"):
        st.session_state.page = "friends"
        st.rerun()

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

    if st.button("⚙️ 설정"):
        st.session_state.page = "setting"
        st.rerun()
    if st.button("로그아웃"):
        st.session_state.logged_in = False
        st.session_state.page = "main"
        st.rerun()
    st.markdown("---")
    if st.button("Staff only"):
        st.session_state.page = "admin_login"
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
        sorted_reservations = sorted(club_reservations, key=lambda r: r["time"])
        st.table([{"시간": r["time"], "닉네임": r["nickname"]} for r in sorted_reservations])
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
        
        max_reservations = load_data("max_reservations")
        limit = max_reservations.get(club, 2)
        st.markdown(f"**시간당 최대 {limit}명까지 예약할 수 있습니다.**")
        
        available_times = load_data("available_times").get(club, [])
        selected_time = st.selectbox("시간 선택", available_times)

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

elif st.session_state.page == "friends":
    st.title("👥 친구 관리")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🌍 둘러보기", "📜 친구 목록", "🏆 도장판 완성 순위", "🏆 방명록 순위"])

    users_data = load_data("users")
    my_nick = st.session_state.nickname
    my_email_key = st.session_state.user_email.replace(".", "_")
    my_data = users_data.get(my_email_key, {})
    my_friends = my_data.get("friends", [])
    with tab1:
        st.subheader("닉네임 검색")
        query = st.text_input("닉네임 입력")

        if query:
            matched = [
                user["nickname"] for user in users_data.values()
                if query.lower() in user["nickname"].lower()
                and user.get("searchable", True)
                and user["nickname"] != my_nick
            ]
            for nick in matched:
                if st.button(nick, key=f"search_{nick}"):
                    st.session_state.page = "profile"
                    st.session_state.viewing_profile = nick
                    st.rerun()

    with tab2:
        if not my_friends:
            st.info("🙁 아직 친구가 없습니다.")
        else:
            for friend in my_friends:
                if st.button(friend, key=f"friend_{friend}"):
                    st.session_state.page = "profile"
                    st.session_state.viewing_profile = friend
                    st.rerun()

    with tab3:
        st.subheader("🏆 도장판 완성 순위")
    
        stamp_data = load_data("stamp_data")
    
        finish_times = []
        for nick, data in stamp_data.items():
            if isinstance(data, dict) and data.get("finished_at"):
                finish_times.append((nick, data["finished_at"]))
    
        if not finish_times:
            st.info("아직 도장판을 완성한 사람이 없습니다.")
        else:
            finish_times.sort(key=lambda x: x[1]) 
    
            badges = ["🥇", "🥈", "🥉"]
            for i, (nick, ts) in enumerate(finish_times, start=1):
                badge = badges[i-1] if i <= 3 else ""
                nick_display = f"**{badge} {nick}**" if i <= 3 else f"{badge} {nick}"
                tstr = time.strftime("%m월 %d일 %H:%M", time.localtime(ts))
                col1, col2 = st.columns([4, 2])
                with col1:
                    st.markdown(nick_display)
                with col2:
                    st.markdown(f"🏁 {tstr}")


    with tab4:
        st.subheader("🏆 방명록 순위")
    
        emojis = load_data("emojis")
        if not emojis:
            st.info("아직 아무도 방명록을 남기지 않았습니다.")
        else:
            emoji_counts = [(nickname, len(emojis[nickname])) for nickname in emojis]
            emoji_counts.sort(key=lambda x: x[1], reverse=True)
    
            badges = ["🥇", "🥈", "🥉"]
            for i, (nick, count) in enumerate(emoji_counts, start=1):
                badge = badges[i-1] if i <= 3 else ""
                nick_display = f"**{badge} {nick}**" if i <= 3 else f"{badge} {nick}"
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(nick_display)
                with col2:
                    st.markdown(f"**{count}개**")

    if st.button("🔙 메인으로"):
        st.session_state.page = "main"
        st.rerun()

elif st.session_state.page == "profile":
    nickname = st.session_state.viewing_profile
    st.title(f"📄 {nickname}의 프로필")

    users_data = load_data("users")
    my_nick = st.session_state.nickname
    my_email_key = st.session_state.user_email.replace(".", "_")
    my_data = users_data.get(my_email_key, {})
    my_friends = my_data.get("friends", [])
    emojis = load_data("emojis")
    stamp_data = load_data("stamp_data")

    target_user = next((u for u in users_data.values() if u.get("nickname") == nickname), None)

    if not target_user:
        st.error("❌ 존재하지 않는 사용자입니다.")
    else:
        is_visible = target_user.get("public_stamp", True) or (my_nick in target_user.get("friends", []))
        is_mutual_friend = (nickname in my_friends) and (my_nick in target_user.get("friends", []))

        if is_visible:
            base = Image.open("StampPaperSample.png").convert("RGBA")
            overlay = Image.new("RGBA", base.size, (255, 255, 255, 0))
            user_stamps = stamp_data.get(nickname, {})
            for club, stamped in user_stamps.items():
                if stamped:
                    try:
                        stamp = Image.open(f"stamps/{club}.png").convert("RGBA")
                        overlay = Image.alpha_composite(overlay, stamp)
                    except Exception as e:
                        print(f"⚠️ Stamp image not found for {club}: {e}")
            result = Image.alpha_composite(base, overlay)
            st.image(result, use_container_width=True)
    
        else:
            st.warning("🔒 도장판이 비공개로 설정되어 있습니다.")

        if is_visible:
            st.markdown("방명록")
            emoji_data = emojis.get(nickname, {})
            if not emoji_data:
                st.info("아직 아무도 방문하지 않았습니다.")
            else:
                for sender, emoji in emoji_data.items():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"- **{sender}**: {emoji}")
                    with col2:
                        if sender == my_nick:
                            if st.button("❌ 삭제", key=f"del_emoji_{sender}"):
                                del emojis[nickname][sender]
                                save_data("emojis", emojis)
                                st.success("방명록이 삭제되었습니다.")
                                time.sleep(1)
                                st.rerun()

        ALLOWED_EMOJIS = ["❤️", "💕", "🎉", "🔥", "🌟", "👏", "😎", "😊", "🙃", "🎉", "👍", "🤝"]
        if is_mutual_friend and is_visible:
            st.markdown("### 😎 방명록 남기기")
            emoji_input = st.selectbox("이모티콘 선택", [""] + ALLOWED_EMOJIS, key="emoji_select")
        
            if st.button("📌 방명록 남기기"):
                if emoji_input == "":
                    st.warning("이모티콘을 선택해주세요!")
                else:
                    if nickname not in emojis:
                        emojis[nickname] = {}
                    emojis[nickname][my_nick] = emoji_input
                    save_data("emojis", emojis)
                    st.success("방명록을 남겼습니다!")
                    time.sleep(1)
                    st.rerun()

        if nickname in my_friends:
            st.info("✅ 이미 친구추가된 사용자입니다.")
        else:
            if st.button("➕ 친구 요청"):
                if nickname not in my_data.get("sent_requests", []):
                    my_sent = my_data.get("sent_requests", [])
                    my_sent.append(nickname)
                    db.child("users").child(my_email_key).update({"sent_requests": my_sent})
                    target_email_key = next((k for k, v in users_data.items() if v.get("nickname") == nickname), None)
                if target_email_key:
                    target_pending = users_data[target_email_key].get("pending_requests", [])
                    target_pending.append(my_nick)
                    db.child("users").child(target_email_key).update({"pending_requests": target_pending})
    
                st.success("🎉 친구 요청을 보냈습니다!")
                st.rerun()
            else:
                st.info("이미 친구 요청을 보낸 상태입니다.")

    if st.button("🔙 돌아가기"):
        st.session_state.page = "friends"
        st.rerun()

elif st.session_state.page == "setting":
    st.title("⚙️ 설정")
    tab1, tab2 = st.tabs(["👤 개인정보 수정", "🧑‍🤝‍🧑 친구 설정"])

    with tab1:
        st.subheader("👤 개인정보 수정")
        current_nick = st.session_state.nickname
        current_phone = st.session_state.phone

        new_nick = st.text_input("새 닉네임", value=current_nick, key="edit_nick")
        new_phone = st.text_input("새 전화번호", value=current_phone, key="edit_phone")
        msg_area = st.empty()

    with tab2:
        st.subheader("🧑‍🤝‍🧑 친구 설정")
        
        email_key = st.session_state.user_email.replace(".", "_")
        users_data = load_data("users")
        user_data = users_data.get(email_key, {})
    
        public_default = user_data.get("public_stamp", True)
        search_default = user_data.get("searchable", True)
    
        public_checkbox = st.checkbox("📢 내 도장판 전체 공개", value=public_default)
        search_checkbox = st.checkbox("🔍 닉네임으로 나를 검색 가능하게 하기", value=search_default)

    if st.button("✅ 저장"):
        updated = False
        reservations = load_data("reservations")

        if any(c in new_nick for c in ".#$[]/ ") or new_nick.strip() == "":
            msg_area.error("❌ 닉네임에 공백이나 '.', '#', '$', '[', ']', '/' 는 사용할 수 없습니다.")
        else:
            if new_nick != current_nick:
                stamp_data = load_data("stamp_data")
                if new_nick in stamp_data:
                    msg_area.error("❌ 이미 존재하는 닉네임입니다.")
                else:
                    stamp_data[new_nick] = stamp_data.pop(current_nick)
                    save_data("stamp_data", stamp_data)

                    for club, lst in reservations.items():
                        for r in lst:
                            if r["nickname"] == current_nick:
                                r["nickname"] = new_nick
                    save_data("reservations", reservations)

                    email_key = st.session_state.user_email.replace(".", "_")
                    db.child("users").child(email_key).update({"nickname": new_nick})

                    st.session_state.nickname = new_nick
                    current_nick = new_nick
                    updated = True

            if new_phone != current_phone:
                email_key = st.session_state.user_email.replace(".", "_")
                db.child("users").child(email_key).update({"phone": new_phone})
                st.session_state.phone = new_phone
                current_phone = new_phone
                for club, lst in reservations.items():
                    for r in lst:
                        if r["nickname"] == current_nick:
                            r["phone"] = new_phone
                save_data("reservations", reservations)
                updated = True

            if updated:
                msg_area.success("✅ 변경사항이 저장되었습니다.")
            db.child("users").child(email_key).update({
                "public_stamp": public_checkbox,
                "searchable": search_checkbox
            })

    st.markdown("---")
    if st.button("🔙 돌아가기"):
        st.session_state.page = "main"
        st.rerun()

elif st.session_state.page == "admin_login":
    st.title("🗝️ 인증")
    admin_pw = st.text_input("비밀번호 입력", type="password")
    if st.button("Enter"):
        if admin_pw == "dshs37lsy":
            st.session_state.page = "super_admin_panel"
            st.rerun()
            st.stop()
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
                    if all(stamp_data[nickname].values()):
                        if "finished_at" not in stamp_data[nickname]:
                            stamp_data[nickname]["finished_at"] = time.time()
                
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
        
        if new_status:
            max_num = max_reservations.get(club, 2)
            new_max = st.number_input("시간당 최대 예약 인원 수", min_value=1, max_value=20, value=max_num, key=f"{club}_max")
        else:
            new_max = max_reservations.get(club, 2)

        if new_status != is_enabled or new_max != max_reservations.get(club, 3):
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
            if st.button("🔄 새로고침"):
                st.rerun()
            st.markdown("#### 📋 예약 목록")
            club_reservations = reservations.get(club, [])
            if not club_reservations:
                st.info("예약된 항목이 없습니다.")
            else:
                sorted_admin_reservations = sorted(club_reservations, key=lambda r: r["time"])
                st.table([{ "시간": r["time"], "닉네임": r["nickname"], "전화번호": r["phone"] } for r in sorted_admin_reservations])
            st.markdown("#### ⏰ 예약 시간 관리")
            
            available_times = load_data("available_times").get(club, [])
            new_time = st.text_input("새로운 시간 추가 (24시간 단위로 적어주세요 -> 1시(x), 13시(o))", key=f"{club}_new_time")
            if st.button("➕ 시간 추가"):
                if new_time and new_time not in available_times:
                    available_times.append(new_time)
                    available_times.sort()
                    db.child("available_times").child(club).set(available_times)
                    st.success("새로운 시간이 추가되었습니다.")
                    st.rerun()
                else:
                    st.warning("시간이 비어있거나 이미 존재합니다.")
            delete_time = st.selectbox("삭제할 시간 선택", available_times, key=f"{club}_del_time")
            if st.button("🗑️ 시간 삭제"):
                available_times.remove(delete_time)
                db.child("available_times").child(club).set(available_times)
                st.success("시간이 삭제되었습니다.")
                st.rerun()

    if st.button("🔙 메인으로"):
        st.session_state.page = "main"
        st.session_state.admin_mode = False
        st.rerun()

elif st.session_state.page == "super_admin_panel":
    st.title("🧙‍♂️ 총괄 관리자 페이지")

    tab1, tab2 = st.tabs(["🧹 데이터 초기화", "📊 통계 보기 (준비 중)"])

    with tab1:
        st.warning("⚠️ 모든 데이터를 초기값으로 되돌립니다. 정말로 진행하시겠습니까?")
        if st.button("🚨 전체 초기화 실행"):
            try:
                # 초기화 로직
                db.child("reservation_status").set({club: False for club in clubs})
                db.child("stamp_data").set({})
                db.child("max_reservations").set({club: 2 for club in clubs})
                default_times = [
                    "10:00", "10:30", "11:00", "11:30",
                    "13:00", "13:30", "14:00", "14:30"
                ]
                db.child("available_times").set({club: default_times for club in clubs})
                db.child("reservations").set({})
                db.child("emojis").set({})
                db.child("users").set({})

                st.success("✅ 모든 데이터가 초기화되었습니다.")
            except Exception as e:
                st.error(f"🔥 초기화 실패: {e}")

    with tab2:
        st.info("🚧 추후 통계 페이지 추가 예정입니다.")

    if st.button("🔙 메인으로"):
        st.session_state.page = "main"
        st.rerun()

refresh_login()

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    with tab1:
        Login()
    with tab2:
        Register()
elif st.session_state.logged_in and st.session_state.page == "main":
    show_stamp_board()
