import streamlit as st
from openai import OpenAI
import pygame
import os
from datetime import datetime
import time
import telebot

# 텔레그램 봇 설정
TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
# app_tele.py 파일에서
TELEGRAM_CHAT_ID = st.secrets.get("TELEGRAM_CHAT_ID", "5767743818")  # 기본값 설정

bot = telebot.TeleBot(TELEGRAM_TOKEN)


def send_emergency_alert():
    """텔레그램으로 긴급 알림 전송"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"""🚨 긴급 상황 발생!

발생 시간: {current_time}
상황: 긴급 도움 요청
"""
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        return True
    except Exception as e:
        st.error(f"텔레그램 메시지 전송 실패: {str(e)}")
        return False


# 페이지 설정
st.set_page_config(page_title="실버케어 음성 비서", page_icon="🎤", layout="wide")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets["OPENAI_KEY"])


# 임시 파일 디렉토리 생성
if not os.path.exists("temp_audio"):
    os.makedirs("temp_audio")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

def text_to_speech(text, voice="shimmer"):
    """텍스트를 음성으로 변환"""
    try:
        # OpenAI TTS API 호출만 하고 파일 저장/재생은 하지 않음
        response = client.audio.speech.create(model="tts-1", voice=voice, input=text)
        st.info("🔊 음성이 생성되었습니다. (Cloud 환경에서는 재생이 불가능합니다)")
        return True
    except Exception as e:
        st.error(f"음성 변환 오류: {e}")
        return False

def generate_response(prompt):
    """GPT 응답 생성"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"GPT 응답 생성 오류: {e}")
        return None

# 전역 변수로 mixer 초기화 상태 추적
PYGAME_MIXER_INITIALIZED = False



# 사이드바 설정
with st.sidebar:
    st.title("⚙️ 설정")
    voice_option = st.radio("음성 선택", ["여성 (shimmer)", "남성 (onyx)"], index=0)

    # 볼륨 슬라이더는 유지하되 실제 동작하지 않음을 안내
    volume = st.slider("음량", 0, 100, 50)
    st.info("❗ Cloud 환경에서는 음성 재생이 지원되지 않습니다.")

    st.divider()
    

    # 긴급 연락 섹션
    st.markdown("### ⚠️ 긴급 연락")
    if st.button("🚨 긴급 도움 요청", use_container_width=True):
        with st.spinner("긴급 알림 전송 중..."):
            if send_emergency_alert():
                st.success("긴급 알림이 전송되었습니다!")
                # 음성 안내
                text_to_speech(
                    "긴급 알림이 전송되었습니다. 곧 도움이 도착할 예정입니다."
                )
            else:
                st.error("긴급 알림 전송에 실패했습니다.")

# 메인 화면
st.title("🎤 실버케어 음성 비서")

# 채팅 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("무엇을 도와드릴까요?"):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 로딩 표시
    with st.spinner("응답 생성 중..."):
        # GPT 응답 생성
        response = generate_response(prompt)

        if response:
            # 응답 메시지 추가
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)

            # 음성 변환 및 재생
            voice = "shimmer" if "여성" in voice_option else "onyx"
            text_to_speech(response, voice)

# 하단 정보
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.info("📅 오늘의 일정")
    st.write("- 오후 3시: 병원 예약")
    st.write("- 저녁 6시: 복약 시간")

with col2:
    st.success("💊 복약 관리")
    st.write("- 혈압약: 아침/저녁 식후 30분")
    st.write("- 비타민: 아침 식전")

with col3:
    st.warning("⚡ 긴급 상황 시")
    st.write("1. 긴급 버튼을 눌러주세요")
    st.write("2. 도움 요청이 자동 전송됩니다")
    st.write("3. 침착하게 기다려주세요")
