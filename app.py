# app.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams, font_manager
import streamlit as st

# -----------------------
# 0) 전역 설정
# -----------------------
st.set_page_config(page_title="투자 금액 분배기", layout="centered")

# (A) 운영체제 기본 한글 폰트 자동 사용 (추가 다운로드/동봉 불필요)
default_fonts = ["Malgun Gothic", "Apple SD Gothic Neo", "NanumGothic"]
available_fonts = set(f.name for f in font_manager.fontManager.ttflist)
for f in default_fonts:
    if f in available_fonts:
        rcParams["font.family"] = f
        break
rcParams["axes.unicode_minus"] = False  # 한글 폰트 사용 시 마이너스 문자 깨짐 방지

# -----------------------
# 1) UI 헤더
# -----------------------
st.title("📊 투자 금액 자동 분배 앱")

# -----------------------
# 2) 입력 섹션
# -----------------------
total_amount = st.number_input("총 투자 금액 (원)", min_value=0, step=100000, format="%d")

st.subheader("자산군별 비율 입력 (%)")
col1, col2, col3 = st.columns(3)

with col1:
    div_yield = st.number_input("배당주 ETF (%)", min_value=0, max_value=100, value=30, step=1)
    gold = st.number_input("금 (%)", min_value=0, max_value=100, value=15, step=1)

with col2:
    dollar_bond = st.number_input("달러 단기채 (%)", min_value=0, max_value=100, value=15, step=1)
    growth_etf = st.number_input("성장주 ETF (%)", min_value=0, max_value=100, value=30, step=1)

with col3:
    crypto = st.number_input("크립토 (%)", min_value=0, max_value=100, value=10, step=1)

# 한글 라벨(표/CSV/입력용)
labels = np.array(["배당주 ETF", "금", "달러 단기채", "성장주 ETF", "크립토"])
# 파이 차트 전용 영문 라벨(웹 폰트 이슈 회피)
labels_en = np.array(["Dividend ETF", "Gold", "USD Short-Term Bonds", "Growth ETF", "Crypto"])

weights = np.array([div_yield, gold, dollar_bond, growth_etf, crypto], dtype=float)
total_percent = float(weights.sum())
st.write(f"👉 현재 비율 합계: **{total_percent:.0f}%**")

# 합계 자동 정규화 토글 (모바일 UX 개선용)
auto_normalize = st.toggle("합계가 100%가 아니면 자동 정규화(미리보기)", value=True)

# -----------------------
# 3) 결과 테이블 섹션 (항상 렌더)
# -----------------------
st.subheader("📌 투자 분배 결과")

def render_table(df: pd.DataFrame):
    styled = df.style.format({"비율(%)": "{:.2f}", "투자 금액(원)": "{:,}"})
    st.dataframe(styled, use_container_width=True)

if total_amount <= 0:
    # 금액이 0일 때도 섹션은 유지하고 안내 제공
    st.info("총 투자 금액을 1원 이상 입력하면 금액 분배 결과가 표시됩니다.")
    df_placeholder = pd.DataFrame({"자산군": labels, "비율(%)": weights, "투자 금액(원)": [0]*len(labels)})
    render_table(df_placeholder)
else:
    if total_percent == 100:
        norm_weights = weights / 100.0
        normalized = False
    else:
        if auto_normalize and total_percent > 0:
            norm_weights = weights / total_percent
            normalized = True
        else:
            norm_weights = None
            normalized = False

    if norm_weights is None:
        st.warning("합계가 100%가 아니어서 금액 계산을 할 수 없습니다. 합계를 100%로 맞추거나 '자동 정규화'를 켜세요.")
        df_placeholder = pd.DataFrame({"자산군": labels, "비율(%)": weights, "투자 금액(원)": [0]*len(labels)})
        render_table(df_placeholder)
    else:
        alloc_amounts = (total_amount * norm_weights).round(0).astype(int)
        df = pd.DataFrame({
            "자산군": labels,                          # 표/CSV는 한글 유지
            "비율(%)": (norm_weights * 100).round(2),
            "투자 금액(원)": alloc_amounts
        })
        if normalized:
            st.warning(f"합계 {total_percent:.0f}% → **자동 정규화**로 환산해 미리보기를 표시합니다.")
        render_table(df)

        # CSV 다운로드 (한글 라벨 유지)
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "CSV 다운로드",
            data=csv,
            file_name="투자_분배_결과.csv",
            mime="text/csv",
            use_container_width=True
        )

# -----------------------
# 4) 파이 차트 섹션 (항상 렌더)
# -----------------------
st.subheader("📊 비율 시각화")

if total_percent == 100 or (auto_normalize and total_percent > 0):
    pie_weights = (weights / 100.0) if total_percent == 100 else (weights / total_percent)
    fig, ax = plt.subplots()
    ax.pie(
        pie_weights,
        labels=labels_en,   # 차트에만 영문 라벨 사용 (폰트 깨짐 회피)
        autopct="%.1f%%",
        startangle=90
    )
    ax.axis("equal")
    st.pyplot(fig, use_container_width=True)
else:
    st.info("차트를 보려면 합계를 100%로 맞추거나 '자동 정규화'를 켜세요.")
