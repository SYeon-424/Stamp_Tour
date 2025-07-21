import streamlit as st
import json
from PIL import Image
import os

# 경로 설정
STAMP_DATA_PATH = "stamp_data.json"
STAMP_IMAGE_FOLDER = "stamps"
STAMP_BASE_IMAGE = "StampPaperSample.png"

def overlay_stamps(nickname):
    # 배경 이미지 불러오기
    try:
        base = Image.open(STAMP_BASE_IMAGE).convert("RGBA")
    except FileNotFoundError:
        st.error("배경 이미지가 없습니다.")
        return None

    # 도장 데이터 불러오기
    try:
        with open(STAMP_DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        st.error("도장 데이터 파일이 없습니다.")
        return None

    user_data = data.get(nickname)
    if not user_data:
        st.error("존재하지 않는 닉네임입니다.")
        return None

    # 도장 오버레이
    for club, stamped in user_data.get("stamps", {}).items():
        if stamped:
            stamp_path = os.path.join(STAMP_IMAGE_FOLDER, f"{club}.png")
            if os.path.exists(stamp_path):
                stamp = Image.open(stamp_path).convert("RGBA")
                base.alpha_composite(stamp)  # 같은 크기, 같은 위치
            else:
                st.warning(f"도장 이미지가 없습니다: {club}.png")

    return base

# Streamlit UI
st.title("🎯 도장 현황 보기")
nickname = st.text_input("닉네임을 입력하세요")

if st.button("도장 확인"):
    result = overlay_stamps(nickname)
    if result:
        st.image(result, use_container_width=True)
