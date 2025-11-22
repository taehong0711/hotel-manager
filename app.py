import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# 페이지 설정
st.set_page_config(page_title="호텔 통합 관리 시스템", page_icon="🏨", layout="wide")

# --- [🔐 로그인 기능 설정] ---
CREDENTIALS = {
    "manager": "admin1234",
    "staff": "hotel5678", 
    "taehong": "1111"
}

# 로그인 상태 관리
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""

# 로그인이 안 된 상태라면 로그인 화면만 보여줌
if not st.session_state['logged_in']:
    st.title("🔒 호텔 관리 시스템 로그인")
    
    with st.form("login_form"):
        input_username = st.text_input("아이디 (ID)")
        input_password = st.text_input("비밀번호 (PW)", type="password")
        submit_button = st.form_submit_button("로그인")

        if submit_button:
            if input_username in CREDENTIALS and CREDENTIALS[input_username] == input_password:
                st.session_state['logged_in'] = True
                # [수정된 부분] 아이디를 기억 장소에 저장합니다!
                st.session_state['username'] = input_username 
                st.success("로그인 성공!")
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 틀렸습니다.")
    
    st.stop()

# --- [로그인 성공 시 보이는 화면] ---

# 사이드바 설정
with st.sidebar:
    # [수정된 부분] 저장된 아이디를 불러옵니다.
    current_user = st.session_state['username']
    st.write(f"환영합니다, **{current_user}**님! 👋")
    
    if st.button("로그아웃"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = "" # 로그아웃 시 이름 지우기
        st.rerun()

st.title("🏨 호텔 매니저 Pro")

# 호텔 설정값
TOTAL_ROOMS = 20 
TARGET_SALES = 1000000

# 1. 엑셀 파일 불러오기
file_name = "hotel_data.xlsx"
try:
    df = pd.read_excel(file_name, engine="openpyxl")
except:
    st.error("엑셀 파일이 없습니다! create_excel.py를 실행해주세요.")
    st.stop()

# 탭 분리
tab1, tab2 = st.tabs(["📊 통계 대시보드", "📝 데이터 관리"])

# --- [탭 1: 통계 대시보드] ---
with tab1:
    if not df.empty:
        total_sales = df['매출'].sum()
        total_days = df['날짜'].nunique()
        total_sold_rooms = len(df)
        occupancy_rate = (total_sold_rooms / (total_days * TOTAL_ROOMS)) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("총 매출", f"¥{total_sales:,}", delta="누적")
        col2.metric("총 판매 객실", f"{total_sold_rooms}건")
        col3.metric("평균 객실 점유율", f"{occupancy_rate:.1f}%")
        col4.metric("목표 달성률", f"{(total_sales/TARGET_SALES)*100:.1f}%")

        st.write(f"🎯 **이번 달 매출 목표 (¥{TARGET_SALES:,}) 달성 현황**")
        progress_val = min(total_sales / TARGET_SALES, 1.0) 
        st.progress(progress_val)

        st.divider()

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.subheader("📅 일별 매출 추이")
            daily_data = df.groupby('날짜')['매출'].sum().reset_index()
            fig1 = px.line(daily_data, x='날짜', y='매출', markers=True)
            st.plotly_chart(fig1, use_container_width=True)

        with chart_col2:
            st.subheader("🛏️ 객실 타입 선호도")
            type_data = df['객실타입'].value_counts().reset_index()
            type_data.columns = ['객실타입', '판매수']
            fig2 = px.pie(type_data, values='판매수', names='객실타입', hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)
            
        st.subheader("📂 리포트 다운로드")
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("데이터 다운로드 (CSV)", csv, 'hotel_report.csv', 'text/csv')
    else:
        st.info("데이터가 없습니다.")

# --- [탭 2: 데이터 관리] ---
with tab2:
    st.subheader("데이터 수정 및 추가")
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    if st.button("💾 변경사항 저장하기"):
        try:
            edited_df.to_excel(file_name, index=False)
            st.success("저장 완료!")
            st.rerun()
        except PermissionError:
            st.error("엑셀 파일을 꺼주세요!")