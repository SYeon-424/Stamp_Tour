...

# (위 코드는 생략된 상태이며 이어지는 파트입니다)

# 도장판 출력 함수
def show_stamp_board():
    st.title("🎯 도장판")
    st.write(f"닉네임: {st.session_state.nickname}")

    stamp_data = load_data("stamp_data")
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

# 부스 소개
if st.session_state.page == "club_intro":
    club = st.session_state.selected_club
    st.title(f"📑 {club} 부스 소개")
    club_info = club_infos.get(club, {"description": "소개 정보가 없습니다.", "image": "club_default.png"})
    st.write(club_info["description"])
    st.image(club_info["image"], caption=f"{club} 활동 소개", use_container_width=True)
    if st.button("🔙 메인으로"):
        st.session_state.page = "main"
        st.rerun()

# 예약 페이지
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
            if any(r["time"] == selected_time for r in club_reservations):
                st.error("❌ 이미 해당 시간에 예약이 있습니다.")
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

# 관리자 로그인
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
    if st.button("🔙 메인으로"):
        st.session_state.page = "main"
        st.rerun()

# 관리자 페이지
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
                    st.info("✅ 이미 도장이 찍혀 있습니다.")

    with tab2:
        reservation_status = load_data("reservation_status")
        reservations = load_data("reservations")
        club = st.session_state.admin_club
        is_enabled = reservation_status.get(club, False)
        new_status = st.checkbox("예약 기능 활성화", value=is_enabled)
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

# 진입점
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    with tab1:
        Login()
    with tab2:
        Register()
elif st.session_state.logged_in and st.session_state.page == "main":
    show_stamp_board()
