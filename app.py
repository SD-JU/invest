import streamlit as st
import pandas as pd

st.set_page_config(page_title="투자 금액 분배기", layout="centered")

st.title("📊 투자 금액 자동 분배 앱")

# 1. 총 투자 금액 입력
total_amount = st.number_input("총 투자 금액 (원)", min_value=0, step=100000)

# 2. 자산군 비율 입력
st.subheader("자산군별 비율 입력 (%)")
col1, col2, col3 = st.columns(3)

with col1:
    div_yield = st.number_input("배당주 (%)", min_value=0, max_value=100, value=30, step=1)
    gold = st.number_input("금 (%)", min_value=0, max_value=100, value=15, step=1)

with col2:
    dollar_bond = st.number_input("달러 단기채 (%)", min_value=0, max_value=100, value=15, step=1)
    growth_etf = st.number_input("성장형 ETF (%)", min_value=0, max_value=100, value=30, step=1)

with col3:
    crypto = st.number_input("크립토 (%)", min_value=0, max_value=100, value=10, step=1)

# 3. 총합 체크
total_percent = div_yield + gold + dollar_bond + growth_etf + crypto
st.write(f"👉 현재 비율 합계: **{total_percent}%**")

if total_percent != 100:
    st.error("총합이 100%가 되어야 합니다.")
else:
    if total_amount > 0:
        # 금액 분배 계산
        data = {
            "자산군": ["배당주", "금", "달러 단기채", "성장형 ETF", "크립토"],
            "비율(%)": [div_yield, gold, dollar_bond, growth_etf, crypto],
            "투자 금액(원)": [
                total_amount * div_yield / 100,
                total_amount * gold / 100,
                total_amount * dollar_bond / 100,
                total_amount * growth_etf / 100,
                total_amount * crypto / 100
            ]
        }
        df = pd.DataFrame(data)

        # 결과 출력
        st.subheader("📌 투자 분배 결과")
        st.table(df)

        # 원형 차트 시각화
        st.subheader("📊 비율 시각화")
        st.pyplot(df.set_index("자산군")["비율(%)"].plot.pie(autopct="%.1f%%").figure)
