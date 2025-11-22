import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# 페이지 설정
st.set_page_config(page_title="호텔 통합 관리 시스템", page_icon="🏨", layout="wide")

# --- [🔐 구글 시트 연결 설정] ---
@st.cache_resource
def init_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Secrets에 저장된 JSON 문자열을 파싱해서 사용
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json_creds, scope)
    return gspread.authorize(creds)

def load_data():
    try:
        gc = init_connection()
        worksheet = gc.open("hotel_db").sheet1 
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        return pd.DataFrame() # 에러 나면 빈 데이터프레임 반환

def save_data(df):
    gc = init_connection()
    worksheet = gc.open("hotel_db").sheet1
    worksheet.clear()
    # 헤더와 데이터를 리스트로 변환하여 저장
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

# --- [메인 화면 시작] ---
st.title("🏨 호텔 매니저 Pro (Google Cloud)")

# 로그인 (간단 버전)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    with st.form("login"):
        st.write("🔒 로그인이 필요합니다")
        user = st.text_input("ID")
        pw = st.text_input("PW", type="password")
        if st.form_submit_button("로그인"):
            if user == "taehong" and pw == "1111": # 아이디/비번 수정 가능
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("정보가 틀렸습니다.")
    st.stop()

# 데이터 불러오기
df = load_data()

# 탭 구성
tab1, tab2 = st.tabs(["📊 대시보드", "📝 데이터 관리"])

with tab1:
    if not df.empty:
        st.metric("총 매출", f"¥{df['매출'].sum():,}")
        daily = df.groupby('날짜')['매출'].sum().reset_index()
        st.plotly_chart(px.line(daily, x='날짜', y='매출'))
    else:
        st.info("데이터가 없습니다. '데이터 관리' 탭에서 추가해주세요!")

with tab2:
    st.subheader("데이터 입력 및 저장")
    # 데이터가 비어있으면 기본 템플릿 생성
    if df.empty:
        df = pd.DataFrame(columns=["날짜", "객실타입", "매출"])
    
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    if st.button("☁️ 구글 시트에 저장하기"):
        with st.spinner("클라우드에 저장 중..."):
            save_data(edited_df)
        st.success("저장 완료! 구글 스프레드시트를 확인해보세요.")
        st.rerun()

