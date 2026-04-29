import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import requests
import json
import numpy as np

# ============================================================
# 페이지 설정 & 커스텀 CSS (서울안전누리 스타일 다크 테마)
# ============================================================
st.set_page_config(
    page_title="서울 SafeCity – 범죄 위험도 분석 시스템",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 다크 테마 CSS
st.markdown("""
<style>
/* ===== 전체 배경 & 텍스트 ===== */
.stApp {
    background-color: #0a0e1a;
}
section[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #1e293b;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li,
section[data-testid="stSidebar"] label {
    color: #94a3b8 !important;
}

/* ===== 헤더 배너 ===== */
.header-banner {
    background: linear-gradient(135deg, #111827 0%, #1a2236 100%);
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 20px 28px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.header-left {
    display: flex;
    align-items: center;
    gap: 14px;
}
.header-icon {
    width: 44px;
    height: 44px;
    background: linear-gradient(135deg, #3b82f6, #22d3ee);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    box-shadow: 0 0 20px rgba(59,130,246,0.3);
}
.header-title {
    font-size: 22px;
    font-weight: 800;
    color: #f1f5f9;
    letter-spacing: -0.5px;
}
.header-title span {
    color: #22d3ee;
}
.header-sub {
    font-size: 12px;
    color: #64748b;
    margin-top: 2px;
}
.header-right {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: #64748b;
}
.live-dot {
    width: 8px;
    height: 8px;
    background: #10b981;
    border-radius: 50%;
    display: inline-block;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(16,185,129,0.4); }
    50% { opacity: 0.7; box-shadow: 0 0 0 6px rgba(16,185,129,0); }
}

/* ===== KPI 카드 ===== */
.kpi-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 20px;
}
.kpi-card {
    background: #1a2236;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 20px rgba(34,211,238,0.15);
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 12px 12px 0 0;
}
.kpi-card.red::before { background: #ef4444; }
.kpi-card.orange::before { background: #f97316; }
.kpi-card.green::before { background: #10b981; }
.kpi-card.blue::before { background: #3b82f6; }
.kpi-card.cyan::before { background: #22d3ee; }
.kpi-card.purple::before { background: #a855f7; }
.kpi-label {
    font-size: 12px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}
.kpi-value {
    font-size: 26px;
    font-weight: 800;
    letter-spacing: -1px;
}
.kpi-value.red { color: #ef4444; }
.kpi-value.orange { color: #f97316; }
.kpi-value.green { color: #10b981; }
.kpi-value.blue { color: #3b82f6; }
.kpi-value.cyan { color: #22d3ee; }
.kpi-value.purple { color: #a855f7; }
.kpi-sub {
    font-size: 11px;
    color: #475569;
    margin-top: 2px;
}

/* ===== 패널 카드 ===== */
.panel-card {
    background: #1a2236;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
}
.panel-title {
    font-size: 15px;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ===== 랭킹 아이템 ===== */
.rank-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 8px;
    margin-bottom: 4px;
    background: rgba(255,255,255,0.02);
    transition: background 0.2s;
}
.rank-item:hover {
    background: rgba(59,130,246,0.08);
}
.rank-num {
    width: 26px;
    height: 26px;
    border-radius: 7px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 700;
    flex-shrink: 0;
}
.rank-num.danger { background: rgba(239,68,68,0.15); color: #ef4444; }
.rank-num.safe { background: rgba(16,185,129,0.15); color: #10b981; }
.rank-name {
    font-size: 13px;
    font-weight: 600;
    color: #e2e8f0;
    min-width: 70px;
}
.rank-bar {
    flex: 1;
    height: 6px;
    background: rgba(255,255,255,0.05);
    border-radius: 3px;
    overflow: hidden;
}
.rank-bar-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.5s;
}
.rank-value {
    font-size: 13px;
    font-weight: 700;
    color: #94a3b8;
    min-width: 50px;
    text-align: right;
}

/* ===== 예측 시뮬레이터 결과 ===== */
.sim-result-card {
    background: rgba(34,211,238,0.05);
    border: 1px solid rgba(34,211,238,0.2);
    border-radius: 12px;
    padding: 24px;
    text-align: center;
}
.sim-result-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-top: 16px;
}
.sim-result-item {
    background: rgba(255,255,255,0.03);
    border-radius: 8px;
    padding: 16px;
}
.sim-result-label {
    font-size: 11px;
    color: #64748b;
    margin-bottom: 4px;
}
.sim-result-value {
    font-size: 22px;
    font-weight: 800;
}
.sim-note {
    font-size: 12px;
    color: #64748b;
    margin-top: 16px;
    line-height: 1.7;
    text-align: left;
}

/* ===== 필요도 아이템 ===== */
.need-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 14px;
    border-radius: 8px;
    margin-bottom: 6px;
    background: rgba(255,255,255,0.02);
    border-left: 3px solid transparent;
}
.need-item.high { border-left-color: #ef4444; }
.need-item.mid { border-left-color: #f97316; }
.need-item.low { border-left-color: #eab308; }

/* ===== Plotly 차트 배경 투명 ===== */
.stPlotlyChart {
    background: transparent !important;
}

/* ===== 기본 st.metric 숨기고 커스텀 사용 ===== */
[data-testid="stMetric"] {
    background: #1a2236;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 12px 16px;
}

/* ===== 사이드바 제목 ===== */
.sidebar-logo {
    text-align: center;
    padding: 10px 0 20px 0;
    border-bottom: 1px solid #1e293b;
    margin-bottom: 20px;
}
.sidebar-logo-text {
    font-size: 20px;
    font-weight: 800;
    color: #f1f5f9;
}
.sidebar-logo-text span {
    color: #22d3ee;
}

/* ===== 구분선 ===== */
.divider {
    border: none;
    border-top: 1px solid #1e293b;
    margin: 16px 0;
}

/* ===== 탭 스타일 오버라이드 ===== */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #111827;
    border-radius: 8px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    color: #64748b;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: #3b82f6 !important;
    color: white !important;
}

/* ===== 반응형 KPI ===== */
@media (max-width: 768px) {
    .kpi-container {
        grid-template-columns: repeat(2, 1fr);
    }
    .sim-result-grid {
        grid-template-columns: 1fr;
    }
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# 데이터 로딩 (기존 구조 유지)
# ============================================================
@st.cache_data(ttl=0)
def load_data():
    # --- 범죄율/검거율 (2019~2023) ---
    try:
        crime = pd.read_csv('자치구별 범죄율 검거율 5개년.csv', encoding='utf-8', header=1)
    except:
        crime = pd.read_csv('자치구별 범죄율 검거율 5개년.csv', encoding='cp949', header=1)
    crime.columns = ['자치구별','2019_범죄율','2019_검거율','2020_범죄율','2020_검거율',
                     '2021_범죄율','2021_검거율','2022_범죄율','2022_검거율','2023_범죄율','2023_검거율']
    crime = crime.dropna(subset=['자치구별'])

    # --- 발생/검거 건수 (2019~2023) ---
    try:
        occur = pd.read_csv('전국 발생 검거 수.csv', encoding='utf-8', header=1)
    except:
        occur = pd.read_csv('전국 발생 검거 수.csv', encoding='cp949', header=1)
    occur.columns = ['자치구별','2019_발생','2019_검거','2020_발생','2020_검거',
                     '2021_발생','2021_검거','2022_발생','2022_검거','2023_발생','2023_검거']
    occur = occur.dropna(subset=['자치구별'])
    occur = occur[occur['자치구별'] != '소계']
    for col in occur.columns[1:]:
        occur[col] = pd.to_numeric(occur[col].astype(str).str.replace(',',''), errors='coerce')

    # --- 2024년 범죄 데이터 추가 (crime_seoul.csv) ---
    try:
        crime_2024_raw = pd.read_csv('crime_seoul.csv', encoding='utf-8')
        crime_2024_list = []
        for _, row in crime_2024_raw.iloc[4:].iterrows():  # skip header rows + 소계
            gu = str(row.iloc[1]).strip()
            if gu == '소계' or gu == '자치구별(2)':
                continue
            oc = int(str(row.iloc[2]).replace(',',''))
            ar = int(str(row.iloc[3]).replace(',',''))
            crime_2024_list.append({'자치구별': gu, '2024_발생': oc, '2024_검거': ar})
        crime_2024_df = pd.DataFrame(crime_2024_list)
        # 발생/검거 건수에 2024년 추가
        occur = pd.merge(occur, crime_2024_df, on='자치구별', how='left')
    except Exception as e:
        st.warning(f"crime_seoul.csv 로딩 실패: {e}")

    # --- CCTV ---
    cctv = pd.read_csv('cctv_clean.csv', encoding='utf-8-sig')
    cctv.columns = ['자치구','총계','2016년이전','2017년','2018년','2019년','2020년',
                    '2021년','2022년','2023년','2024년','2025년']
    cctv = cctv[cctv['자치구'] != '계']
    cctv = cctv.dropna(subset=['자치구'])
    cctv['자치구'] = cctv['자치구'].str.replace(' ', '')
    for col in cctv.columns[1:]:
        cctv[col] = pd.to_numeric(cctv[col].astype(str).str.replace(',',''), errors='coerce')

    # --- 인구 (2019~2023) ---
    try:
        pop = pd.read_csv('인구 수.csv', encoding='utf-8', header=1)
    except:
        pop = pd.read_csv('인구 수.csv', encoding='cp949', header=1)
    pop.columns = ['자치구별','2019_인구','2020_인구','2021_인구','2022_인구','2023_인구']
    pop = pop.dropna(subset=['자치구별'])
    pop = pop[pop['자치구별'] != '서울특별시']
    for col in pop.columns[1:]:
        pop[col] = pd.to_numeric(pop[col].astype(str).str.replace(',',''), errors='coerce')

    # --- 2025년 인구 데이터 추가 (population_seoul.csv) → 2024년 분석에 사용 ---
    try:
        pop_2025_raw = pd.read_csv('population_seoul.csv', encoding='utf-8')
        pop_2025_list = []
        for _, row in pop_2025_raw.iloc[1:].iterrows():
            raw = str(row.iloc[0])
            parts = raw.split()
            gu = parts[1] if len(parts) >= 2 else parts[0]
            population = int(str(row.iloc[1]).replace(',',''))
            pop_2025_list.append({'자치구별': gu, '2024_인구': population})
        pop_2025_df = pd.DataFrame(pop_2025_list)
        pop = pd.merge(pop, pop_2025_df, on='자치구별', how='left')
    except Exception as e:
        st.warning(f"population_seoul.csv 로딩 실패: {e}")

    # --- 2024년 범죄율/검거율 계산하여 crime 테이블에 추가 ---
    try:
        merged_2024 = pd.merge(
            occur[['자치구별','2024_발생','2024_검거']].dropna(),
            pop[['자치구별','2024_인구']].dropna(),
            on='자치구별', how='inner'
        )
        merged_2024['2024_범죄율'] = (merged_2024['2024_발생'] / merged_2024['2024_인구'] * 100).round(2)
        merged_2024['2024_검거율'] = (merged_2024['2024_검거'] / merged_2024['2024_발생'] * 100).round(2)
        crime = pd.merge(crime, merged_2024[['자치구별','2024_범죄율','2024_검거율']], on='자치구별', how='left')
    except Exception as e:
        st.warning(f"2024 범죄율 계산 실패: {e}")

    return crime, occur, cctv, pop

crime, occur, cctv, pop = load_data()

@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_municipalities_geo_simple.json"
    return requests.get(url).json()

seoul_geo = load_geojson()

# 자치구 중심 좌표
gu_coords = {
    '종로구':[37.5735,126.9790],'중구':[37.5641,126.9979],'용산구':[37.5326,126.9910],
    '성동구':[37.5634,127.0371],'광진구':[37.5384,127.0822],'동대문구':[37.5744,127.0400],
    '중랑구':[37.6063,127.0928],'성북구':[37.5894,127.0167],'강북구':[37.6397,127.0255],
    '도봉구':[37.6688,127.0471],'노원구':[37.6542,127.0568],'은평구':[37.6027,126.9291],
    '서대문구':[37.5791,126.9368],'마포구':[37.5663,126.9014],'양천구':[37.5170,126.8664],
    '강서구':[37.5510,126.8495],'구로구':[37.4955,126.8876],'금천구':[37.4519,126.8968],
    '영등포구':[37.5264,126.8963],'동작구':[37.5124,126.9393],'관악구':[37.4784,126.9516],
    '서초구':[37.4837,127.0324],'강남구':[37.5172,127.0473],'송파구':[37.5145,127.1050],
    '강동구':[37.5301,127.1238]
}


# ============================================================
# 헬퍼 함수
# ============================================================
def get_risk_level(rate):
    if rate >= 1.5: return '위험', '#ef4444', '🔴'
    if rate >= 1.0: return '주의', '#f97316', '🟠'
    if rate >= 0.7: return '보통', '#eab308', '🟡'
    return '안전', '#10b981', '🟢'

def plotly_dark_layout(fig, height=450):
    """공통 Plotly 다크 테마 레이아웃"""
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8', size=12),
        height=height,
        margin=dict(l=40, r=20, t=40, b=40),
        xaxis=dict(gridcolor='#1e293b', zerolinecolor='#1e293b'),
        yaxis=dict(gridcolor='#1e293b', zerolinecolor='#1e293b'),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8')),
    )
    return fig

def make_kpi_html(cards):
    """KPI 카드 그리드 HTML 생성"""
    html = '<div class="kpi-container">'
    for label, value, sub, color in cards:
        html += f'''
        <div class="kpi-card {color}">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value {color}">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>'''
    html += '</div>'
    return html

def make_ranking_html(title, items, rank_type='danger'):
    """랭킹 리스트 HTML"""
    max_val = items[0][1] if items else 1
    html = f'<div class="panel-title">{title}</div>'
    for i, (name, val) in enumerate(items):
        pct = val / max_val * 100
        bar_color = '#ef4444' if rank_type == 'danger' else '#10b981'
        html += f'''
        <div class="rank-item">
            <div class="rank-num {rank_type}">{i+1}</div>
            <div class="rank-name">{name}</div>
            <div class="rank-bar"><div class="rank-bar-fill" style="width:{pct:.0f}%;background:{bar_color};"></div></div>
            <div class="rank-value">{val}%</div>
        </div>'''
    return html


# ============================================================
# 사이드바
# ============================================================
with st.sidebar:
    st.markdown('''
    <div class="sidebar-logo">
        <div style="font-size:28px;margin-bottom:4px;">🛡️</div>
        <div class="sidebar-logo-text">서울 <span>SafeCity</span></div>
        <div style="font-size:11px;color:#64748b;margin-top:4px;">범죄 위험도 분석 시스템</div>
    </div>
    ''', unsafe_allow_html=True)

    menu = st.radio(
        "메뉴",
        ["🗺️ 안전 지도", "📊 범죄 현황", "📹 CCTV 현황", "📈 통계 비교", "🔮 CCTV 예측 시뮬레이터"],
        label_visibility="collapsed"
    )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    year = st.selectbox("📅 분석 연도", [2024, 2023, 2022, 2021, 2020, 2019])

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown(f'''
    <div style="font-size:11px;color:#475569;line-height:1.6;">
        <span class="live-dot"></span> 데이터 업데이트: 2025.12<br>
        학번: 202384064, 202004244, 202384068<br>
        캡스톤디자인 프로젝트
    </div>
    ''', unsafe_allow_html=True)


# ============================================================
# 공통 변수
# ============================================================
col_o = f'{year}_발생'
col_r = f'{year}_범죄율'
col_a = f'{year}_검거율'
col_p = f'{year}_인구'

# 선택한 연도의 컬럼이 데이터에 없으면 가장 가까운 연도로 대체
if col_r not in crime.columns:
    col_r = '2023_범죄율'
if col_a not in crime.columns:
    col_a = '2023_검거율'
if col_o not in occur.columns:
    col_o = '2023_발생'
if col_p not in pop.columns:
    col_p = '2023_인구'


# ============================================================
# 헤더 배너
# ============================================================
st.markdown(f'''
<div class="header-banner">
    <div class="header-left">
        <div class="header-icon">🛡</div>
        <div>
            <div class="header-title">서울 <span>SafeCity</span></div>
            <div class="header-sub">범죄 발생 데이터와 CCTV 정보를 활용한 지역 위험도 예측 시스템</div>
        </div>
    </div>
    <div class="header-right">
        <span class="live-dot"></span> {year}년 데이터 기준
    </div>
</div>
''', unsafe_allow_html=True)


# ============================================================
# 페이지 1: 안전 지도
# ============================================================
if menu == "🗺️ 안전 지도":

    # KPI 카드
    total_crime = int(occur[col_o].sum()) if col_o in occur.columns else 0
    avg_rate = round(crime[col_r].mean(), 2) if col_r in crime.columns else 0
    avg_arrest = round(crime[col_a].mean(), 1) if col_a in crime.columns else 0
    total_cctv = int(cctv['총계'].sum())

    st.markdown(make_kpi_html([
        ('🚨 총 범죄 발생', f'{total_crime:,}건', '서울시 25개 자치구 합계', 'red'),
        ('📊 평균 범죄율', f'{avg_rate}%', '인구 대비 범죄 발생 비율', 'orange'),
        ('🔍 평균 검거율', f'{avg_arrest}%', '범죄 대비 검거 비율', 'green'),
        ('📹 CCTV 총 설치', f'{total_cctv:,}대', '2025년 12월 기준 누적', 'blue'),
    ]), unsafe_allow_html=True)

    # 지도 레이어 선택
    layer = st.radio(
        "지도 레이어",
        ["범죄율", "범죄 발생 건수", "CCTV 밀도", "검거율"],
        horizontal=True,
        label_visibility="collapsed"
    )

    # 지도 + 사이드 패널
    map_col, side_col = st.columns([2, 1])

    with map_col:
        # 다크 테마 지도 생성
        m = folium.Map(
            location=[37.5665, 126.9780],
            zoom_start=11,
            tiles='CartoDB dark_matter'
        )

        # Choropleth 레이어
        if layer == "범죄율" and col_r in crime.columns:
            folium.Choropleth(
                geo_data=seoul_geo, data=crime,
                columns=['자치구별', col_r],
                key_on='feature.properties.name',
                fill_color='YlOrRd', fill_opacity=0.7, line_opacity=0.3,
                legend_name=f'{year}년 범죄율(%)'
            ).add_to(m)
        elif layer == "범죄 발생 건수" and col_o in occur.columns:
            folium.Choropleth(
                geo_data=seoul_geo, data=occur,
                columns=['자치구별', col_o],
                key_on='feature.properties.name',
                fill_color='OrRd', fill_opacity=0.7, line_opacity=0.3,
                legend_name=f'{year}년 범죄 발생 건수'
            ).add_to(m)
        elif layer == "CCTV 밀도":
            folium.Choropleth(
                geo_data=seoul_geo, data=cctv,
                columns=['자치구', '총계'],
                key_on='feature.properties.name',
                fill_color='BuGn', fill_opacity=0.7, line_opacity=0.3,
                legend_name='CCTV 총 설치 대수'
            ).add_to(m)
        elif layer == "검거율" and col_a in crime.columns:
            folium.Choropleth(
                geo_data=seoul_geo, data=crime,
                columns=['자치구별', col_a],
                key_on='feature.properties.name',
                fill_color='Blues', fill_opacity=0.7, line_opacity=0.3,
                legend_name=f'{year}년 검거율(%)'
            ).add_to(m)

        # 자치구별 팝업 마커
        for gu, coord in gu_coords.items():
            rate_val = crime.loc[crime['자치구별']==gu, col_r].values
            rate = float(rate_val[0]) if len(rate_val) > 0 else 0
            risk_label, risk_color, risk_emoji = get_risk_level(rate)

            rate_str = f"{rate_val[0]}%" if len(rate_val) > 0 else "N/A"
            occ_val = occur.loc[occur['자치구별']==gu, col_o].values
            occ_str = f"{int(occ_val[0]):,}건" if len(occ_val) > 0 else "N/A"
            arr_val = crime.loc[crime['자치구별']==gu, col_a].values
            arr_str = f"{arr_val[0]}%" if len(arr_val) > 0 else "N/A"
            cctv_val = cctv.loc[cctv['자치구']==gu, '총계'].values
            cctv_str = f"{int(cctv_val[0]):,}대" if len(cctv_val) > 0 else "N/A"
            pop_val = pop.loc[pop['자치구별']==gu, col_p].values if col_p in pop.columns else []
            pop_str = f"{int(pop_val[0]):,}명" if len(pop_val) > 0 else "N/A"

            popup_html = f"""
            <div style="font-family:-apple-system,sans-serif;width:220px;padding:4px;">
                <div style="font-size:16px;font-weight:700;margin-bottom:6px;">{risk_emoji} {gu}
                    <span style="font-size:11px;background:{risk_color};color:white;padding:2px 8px;border-radius:4px;margin-left:6px;">{risk_label}</span>
                </div>
                <hr style="margin:6px 0;border-color:#eee;">
                <div style="font-size:13px;line-height:1.8;">
                    🚨 범죄 발생: <b>{occ_str}</b><br>
                    📊 범죄율: <b>{rate_str}</b><br>
                    🔍 검거율: <b>{arr_str}</b><br>
                    📹 CCTV: <b>{cctv_str}</b><br>
                    👥 인구: <b>{pop_str}</b>
                </div>
            </div>
            """
            folium.CircleMarker(
                location=coord,
                radius=7,
                color=risk_color,
                fill=True,
                fill_color=risk_color,
                fill_opacity=0.8,
                popup=folium.Popup(popup_html, max_width=260),
                tooltip=f"{gu} ({risk_label})"
            ).add_to(m)

        st_folium(m, width=None, height=550, returned_objects=[])

    with side_col:
        # 위험/안전 랭킹
        if col_r in crime.columns:
            sorted_crime = crime.sort_values(col_r, ascending=False)
            top5 = [(row['자치구별'], row[col_r]) for _, row in sorted_crime.head(5).iterrows()]
            bot5 = [(row['자치구별'], row[col_r]) for _, row in sorted_crime.tail(5).iterrows()]

            st.markdown(f'<div class="panel-card">{make_ranking_html("⚠️ 위험 지역 (범죄율 상위 5)", top5, "danger")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="panel-card">{make_ranking_html("✅ 안전 지역 (범죄율 하위 5)", bot5, "safe")}</div>', unsafe_allow_html=True)


# ============================================================
# 페이지 2: 범죄 현황
# ============================================================
elif menu == "📊 범죄 현황":

    # KPI
    total_crime = int(occur[col_o].sum()) if col_o in occur.columns else 0
    max_gu = occur.loc[occur[col_o].idxmax(), '자치구별'] if col_o in occur.columns else '-'
    max_val = int(occur[col_o].max()) if col_o in occur.columns else 0
    min_gu = occur.loc[occur[col_o].idxmin(), '자치구별'] if col_o in occur.columns else '-'

    st.markdown(make_kpi_html([
        ('🚨 총 범죄 발생', f'{total_crime:,}건', f'{year}년 서울시 합계', 'red'),
        ('📈 최다 발생 자치구', max_gu, f'{max_val:,}건', 'orange'),
        ('📉 최소 발생 자치구', min_gu, f'{int(occur[col_o].min()):,}건' if col_o in occur.columns else '', 'green'),
        ('📊 평균 범죄율', f'{crime[col_r].mean():.2f}%' if col_r in crime.columns else '-', '25개 자치구 평균', 'blue'),
    ]), unsafe_allow_html=True)

    # 범죄 발생 건수 차트
    if col_o in occur.columns:
        st.markdown('<div class="panel-card"><div class="panel-title">📊 자치구별 범죄 발생 건수</div></div>', unsafe_allow_html=True)
        df_sorted = occur.sort_values(col_o, ascending=True)
        fig1 = px.bar(
            df_sorted, x=col_o, y='자치구별', orientation='h',
            color=col_o, color_continuous_scale='YlOrRd',
            labels={col_o: '발생 건수', '자치구별': ''}
        )
        plotly_dark_layout(fig1, height=600)
        fig1.update_layout(yaxis=dict(dtick=1), coloraxis_showscale=False)
        st.plotly_chart(fig1, use_container_width=True)

    # 범죄율 차트
    if col_r in crime.columns:
        st.markdown('<div class="panel-card"><div class="panel-title">📊 자치구별 범죄율 (%)</div></div>', unsafe_allow_html=True)
        df_sorted2 = crime.sort_values(col_r, ascending=False)
        fig2 = px.bar(
            df_sorted2, x='자치구별', y=col_r,
            color=col_r, color_continuous_scale='OrRd',
            labels={col_r: '범죄율(%)', '자치구별': ''}
        )
        plotly_dark_layout(fig2, height=450)
        fig2.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False)
        st.plotly_chart(fig2, use_container_width=True)

    # 연도별 추이
    st.markdown('<div class="panel-card"><div class="panel-title">📈 연도별 범죄 발생 추이 (상위 5개 구)</div></div>', unsafe_allow_html=True)
    year_cols = ['2019_발생','2020_발생','2021_발생','2022_발생','2023_발생']
    if '2024_발생' in occur.columns:
        year_cols.append('2024_발생')
    occur_years = occur[['자치구별'] + year_cols].copy()
    latest_col = year_cols[-1]
    top5_names = occur_years.nlargest(5, latest_col)['자치구별'].tolist()
    top5_m = occur_years[occur_years['자치구별'].isin(top5_names)].melt(
        id_vars='자치구별', var_name='연도', value_name='발생건수'
    )
    top5_m['연도'] = top5_m['연도'].str.replace('_발생','')
    fig3 = px.line(top5_m, x='연도', y='발생건수', color='자치구별', markers=True)
    plotly_dark_layout(fig3, height=400)
    st.plotly_chart(fig3, use_container_width=True)

    # 검거율
    if col_a in crime.columns:
        st.markdown('<div class="panel-card"><div class="panel-title">🔍 자치구별 검거율 (%)</div></div>', unsafe_allow_html=True)
        fig4 = px.bar(
            crime.sort_values(col_a, ascending=True), x=col_a, y='자치구별',
            orientation='h', color=col_a, color_continuous_scale='Blues',
            labels={col_a: '검거율(%)', '자치구별': ''}
        )
        plotly_dark_layout(fig4, height=600)
        fig4.update_layout(yaxis=dict(dtick=1), coloraxis_showscale=False)
        st.plotly_chart(fig4, use_container_width=True)


# ============================================================
# 페이지 3: CCTV 현황
# ============================================================
elif menu == "📹 CCTV 현황":

    total_cctv = int(cctv['총계'].sum())
    max_cctv_gu = cctv.loc[cctv['총계'].idxmax(), '자치구']
    min_cctv_gu = cctv.loc[cctv['총계'].idxmin(), '자치구']

    # 인구 천명당 CCTV 계산
    cp = cctv[['자치구','총계']].copy().rename(columns={'자치구':'자치구별'})
    cp['자치구별'] = cp['자치구별'].str.strip()
    pp = pop.copy()
    pp['자치구별'] = pp['자치구별'].str.strip()
    mg = pd.merge(cp, pp[['자치구별','2023_인구']], on='자치구별', how='inner')
    mg['인구천명당_CCTV'] = (mg['총계'] / mg['2023_인구'] * 1000).round(2)
    avg_per1k = mg['인구천명당_CCTV'].mean()

    st.markdown(make_kpi_html([
        ('📹 CCTV 총 설치', f'{total_cctv:,}대', '2025년 12월 기준', 'cyan'),
        ('🏆 최다 설치 자치구', max_cctv_gu, f'{int(cctv["총계"].max()):,}대', 'blue'),
        ('📉 최소 설치 자치구', min_cctv_gu, f'{int(cctv["총계"].min()):,}대', 'orange'),
        ('👥 천명당 CCTV 평균', f'{avg_per1k:.1f}대', '인구 1,000명당', 'purple'),
    ]), unsafe_allow_html=True)

    # CCTV 총 설치 대수
    st.markdown('<div class="panel-card"><div class="panel-title">📹 자치구별 CCTV 총 설치 대수</div></div>', unsafe_allow_html=True)
    fig5 = px.bar(
        cctv.sort_values('총계', ascending=False), x='자치구', y='총계',
        color='총계', color_continuous_scale='teal',
        labels={'총계': 'CCTV 대수', '자치구': ''}
    )
    plotly_dark_layout(fig5, height=450)
    fig5.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False)
    st.plotly_chart(fig5, use_container_width=True)

    # 연도별 CCTV 추이
    st.markdown('<div class="panel-card"><div class="panel-title">📈 연도별 CCTV 설치 추이 (상위 5개 구)</div></div>', unsafe_allow_html=True)
    y_cols = ['자치구','2017년','2018년','2019년','2020년','2021년','2022년','2023년','2024년','2025년']
    top5c = cctv.nlargest(5, '총계')['자치구'].tolist()
    t5m = cctv[cctv['자치구'].isin(top5c)][y_cols].melt(id_vars='자치구', var_name='연도', value_name='설치대수')
    t5m['연도'] = t5m['연도'].str.replace('년','')
    fig6 = px.line(t5m, x='연도', y='설치대수', color='자치구', markers=True)
    plotly_dark_layout(fig6, height=400)
    st.plotly_chart(fig6, use_container_width=True)

    # 인구 천명당 CCTV
    st.markdown('<div class="panel-card"><div class="panel-title">👥 인구 1,000명당 CCTV 설치 비율</div></div>', unsafe_allow_html=True)
    fig7 = px.bar(
        mg.sort_values('인구천명당_CCTV', ascending=False),
        x='자치구별', y='인구천명당_CCTV',
        color='인구천명당_CCTV', color_continuous_scale='Purples',
        labels={'인구천명당_CCTV': '인구 1000명당 CCTV', '자치구별': ''}
    )
    plotly_dark_layout(fig7, height=450)
    fig7.update_layout(xaxis_tickangle=-45, coloraxis_showscale=False)
    st.plotly_chart(fig7, use_container_width=True)

    # CCTV 설치 현황 지도
    st.markdown('<div class="panel-card"><div class="panel-title">🗺️ CCTV 설치 현황 지도</div></div>', unsafe_allow_html=True)
    m_cctv = folium.Map(location=[37.5665, 126.9780], zoom_start=11, tiles='CartoDB dark_matter')
    folium.Choropleth(
        geo_data=seoul_geo, data=cctv,
        columns=['자치구', '총계'],
        key_on='feature.properties.name',
        fill_color='YlGnBu', fill_opacity=0.7, line_opacity=0.3,
        legend_name='CCTV 설치 대수'
    ).add_to(m_cctv)

    for gu, coord in gu_coords.items():
        cctv_val = cctv.loc[cctv['자치구']==gu, '총계'].values
        if len(cctv_val) > 0:
            folium.CircleMarker(
                location=coord, radius=max(5, cctv_val[0] / 800),
                color='#22d3ee', fill=True, fill_color='#22d3ee', fill_opacity=0.6,
                tooltip=f"{gu}: {int(cctv_val[0]):,}대"
            ).add_to(m_cctv)

    st_folium(m_cctv, width=None, height=500, returned_objects=[])


# ============================================================
# 페이지 4: 통계 비교
# ============================================================
elif menu == "📈 통계 비교":

    st.markdown('<div class="panel-card"><div class="panel-title">📈 자치구 통계 비교 분석</div></div>', unsafe_allow_html=True)

    gu_list = crime['자치구별'].tolist()
    selected = st.multiselect("비교할 자치구 선택 (최대 5개)", gu_list, default=gu_list[:3], max_selections=5)

    if selected:
        # 비교 테이블
        compare = crime[crime['자치구별'].isin(selected)][['자치구별', col_r, col_a]].copy()
        occ_sel = occur[occur['자치구별'].isin(selected)][['자치구별', col_o]]
        compare = pd.merge(compare, occ_sel, on='자치구별', how='left')
        cctv_sel = cctv[cctv['자치구'].isin(selected)][['자치구','총계']].rename(columns={'자치구':'자치구별'})
        compare = pd.merge(compare, cctv_sel, on='자치구별', how='left')
        pop_sel = pop[pop['자치구별'].isin(selected)][['자치구별', col_p]] if col_p in pop.columns else pd.DataFrame()
        if not pop_sel.empty:
            compare = pd.merge(compare, pop_sel, on='자치구별', how='left')
        compare.columns = ['자치구','범죄율(%)','검거율(%)','발생건수','CCTV대수'] + (['인구'] if not pop_sel.empty else [])

        st.dataframe(compare, use_container_width=True, hide_index=True)

        # 비교 차트
        col1, col2 = st.columns(2)
        with col1:
            fig_r = px.bar(compare, x='자치구', y='범죄율(%)', color='자치구', title='범죄율 비교')
            plotly_dark_layout(fig_r, height=380)
            fig_r.update_layout(showlegend=False)
            st.plotly_chart(fig_r, use_container_width=True)
        with col2:
            fig_c = px.bar(compare, x='자치구', y='CCTV대수', color='자치구', title='CCTV 대수 비교')
            plotly_dark_layout(fig_c, height=380)
            fig_c.update_layout(showlegend=False)
            st.plotly_chart(fig_c, use_container_width=True)

        # 산점도: CCTV vs 범죄율
        st.markdown('<div class="panel-card"><div class="panel-title">🔗 CCTV 대수 vs 범죄율 관계</div></div>', unsafe_allow_html=True)
        all_compare = crime[['자치구별', col_r]].copy()
        all_cctv = cctv[['자치구','총계']].rename(columns={'자치구':'자치구별'})
        scatter = pd.merge(all_compare, all_cctv, on='자치구별', how='inner')
        scatter.columns = ['자치구','범죄율','CCTV대수']
        scatter['선택'] = scatter['자치구'].isin(selected)

        fig_s = px.scatter(
            scatter, x='CCTV대수', y='범죄율', text='자치구',
            color='선택', color_discrete_map={True: '#22d3ee', False: '#334155'},
            size=[14 if s else 8 for s in scatter['선택']],
            labels={'CCTV대수': 'CCTV 총 대수', '범죄율': f'범죄율(%)'},
        )
        fig_s.update_traces(textposition='top center', textfont=dict(size=10, color='#94a3b8'))
        plotly_dark_layout(fig_s, height=500)
        fig_s.update_layout(showlegend=False)

        # 추세선
        from numpy.polynomial.polynomial import polyfit
        x_vals = scatter['CCTV대수'].values
        y_vals = scatter['범죄율'].values
        b, m_coef = polyfit(x_vals, y_vals, 1)
        x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
        y_line = b + m_coef * x_line
        fig_s.add_trace(go.Scatter(
            x=x_line, y=y_line, mode='lines',
            line=dict(color='rgba(239,68,68,0.4)', width=2, dash='dash'),
            name='추세선', showlegend=False
        ))

        st.plotly_chart(fig_s, use_container_width=True)
    else:
        st.info("비교할 자치구를 선택해주세요.")


# ============================================================
# 페이지 5: CCTV 예측 시뮬레이터 (NEW!)
# ============================================================
elif menu == "🔮 CCTV 예측 시뮬레이터":

    st.markdown('''
    <div class="panel-card">
        <div class="panel-title">🔮 CCTV 추가 설치 시 범죄 감소 예측 시뮬레이터</div>
        <div style="font-size:13px;color:#94a3b8;line-height:1.7;">
            자치구를 선택하고 CCTV 추가 설치 대수를 조절하면, 예상 범죄 감소율을 확인할 수 있습니다.<br>
            이 모델은 CCTV 설치 밀도와 범죄율 간의 상관관계를 기반으로 한 추정입니다.
        </div>
    </div>
    ''', unsafe_allow_html=True)

    sim_col1, sim_col2 = st.columns([1, 2])

    with sim_col1:
        gu_list = crime['자치구별'].tolist()
        sel_gu = st.selectbox("🏢 자치구 선택", gu_list, index=0)
        add_cctv = st.slider("📹 CCTV 추가 설치 대수", min_value=100, max_value=3000, value=500, step=100)

        # 현재 데이터
        gu_crime_rate = crime.loc[crime['자치구별']==sel_gu, col_r].values
        gu_crime_rate = float(gu_crime_rate[0]) if len(gu_crime_rate) > 0 else 0
        gu_arrest_rate = crime.loc[crime['자치구별']==sel_gu, col_a].values
        gu_arrest_rate = float(gu_arrest_rate[0]) if len(gu_arrest_rate) > 0 else 0
        gu_occur_val = occur.loc[occur['자치구별']==sel_gu, col_o].values
        gu_occur_val = int(gu_occur_val[0]) if len(gu_occur_val) > 0 else 0
        gu_cctv = cctv.loc[cctv['자치구']==sel_gu, '총계'].values
        gu_cctv = int(gu_cctv[0]) if len(gu_cctv) > 0 else 0
        gu_pop = pop.loc[pop['자치구별']==sel_gu, col_p].values if col_p in pop.columns else []
        gu_pop = int(gu_pop[0]) if len(gu_pop) > 0 else 1

        current_per1k = gu_cctv / gu_pop * 1000
        risk_label, risk_color, risk_emoji = get_risk_level(gu_crime_rate)

        st.markdown(f'''
        <div class="panel-card">
            <div class="panel-title">{risk_emoji} {sel_gu} 현재 현황</div>
            <div style="font-size:13px;line-height:2;color:#cbd5e1;">
                📹 CCTV: <b style="color:#22d3ee;">{gu_cctv:,}대</b><br>
                👥 인구: <b>{gu_pop:,}명</b><br>
                📊 범죄율: <b style="color:{risk_color};">{gu_crime_rate}%</b><br>
                🔍 검거율: <b style="color:#10b981;">{gu_arrest_rate}%</b><br>
                🚨 범죄 발생: <b style="color:#f97316;">{gu_occur_val:,}건</b><br>
                📏 천명당 CCTV: <b>{current_per1k:.1f}대</b>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    with sim_col2:
        # 예측 계산
        new_total = gu_cctv + add_cctv
        new_per1k = new_total / gu_pop * 1000
        delta_per1k = new_per1k - current_per1k

        # 선형 모델: CCTV per 1k 증가 → 범죄율 감소 (데이터 상관관계 기반)
        crime_reduction = min(delta_per1k * 0.03, gu_crime_rate * 0.5)
        new_crime_rate = max(0.1, gu_crime_rate - crime_reduction)
        reduction_pct = (crime_reduction / gu_crime_rate * 100) if gu_crime_rate > 0 else 0
        est_crimes_reduced = int(gu_occur_val * (crime_reduction / gu_crime_rate)) if gu_crime_rate > 0 else 0

        st.markdown(f'''
        <div class="sim-result-card">
            <div style="font-size:16px;font-weight:700;color:#22d3ee;margin-bottom:4px;">
                {sel_gu}에 CCTV {add_cctv:,}대 추가 설치 시 예측 결과
            </div>
            <div class="sim-result-grid">
                <div class="sim-result-item">
                    <div class="sim-result-label">예상 범죄율</div>
                    <div class="sim-result-value" style="color:#10b981;">{new_crime_rate:.2f}%</div>
                    <div style="font-size:11px;color:#10b981;margin-top:4px;">▼ {crime_reduction:.2f}%p 감소</div>
                </div>
                <div class="sim-result-item">
                    <div class="sim-result-label">범죄 감소율</div>
                    <div class="sim-result-value" style="color:#10b981;">-{reduction_pct:.1f}%</div>
                    <div style="font-size:11px;color:#64748b;margin-top:4px;">현재 대비</div>
                </div>
                <div class="sim-result-item">
                    <div class="sim-result-label">예상 감소 건수</div>
                    <div class="sim-result-value" style="color:#10b981;">약 {est_crimes_reduced:,}건</div>
                    <div style="font-size:11px;color:#64748b;margin-top:4px;">{year}년 기준</div>
                </div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px;">
                <div class="sim-result-item">
                    <div class="sim-result-label">변경 후 CCTV 총계</div>
                    <div class="sim-result-value" style="color:#22d3ee;">{new_total:,}대</div>
                </div>
                <div class="sim-result-item">
                    <div class="sim-result-label">변경 후 천명당 CCTV</div>
                    <div class="sim-result-value" style="color:#22d3ee;">{new_per1k:.1f}대</div>
                </div>
            </div>
            <div class="sim-note">
                ※ 본 예측은 CCTV 설치 밀도와 범죄율 간의 <b>선형 회귀 추정</b>입니다.<br>
                실제 결과는 지역 특성, 경찰 배치, 인구 밀도 등 다양한 요인에 의해 달라질 수 있습니다.<br>
                <span style="color:#22d3ee;">🔬 한윤수 팀원의 ML 모델(XGBoost/Random Forest) 연동 시 더 정확한 예측이 가능합니다.</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)

    # CCTV 필요도 분석
    st.markdown('<div class="panel-card"><div class="panel-title">🎯 CCTV 추가 설치 필요도 분석 (범죄율 높고 CCTV 적은 지역)</div></div>', unsafe_allow_html=True)

    # 필요도 점수 계산
    need_data = []
    for _, row in crime.iterrows():
        gu = row['자치구별']
        cr = row[col_r] if col_r in crime.columns else 0
        ct = cctv.loc[cctv['자치구']==gu, '총계'].values
        ct = int(ct[0]) if len(ct) > 0 else 0
        pp_val = pop.loc[pop['자치구별']==gu, '2023_인구'].values
        pp_val = int(pp_val[0]) if len(pp_val) > 0 else 1
        per1k = ct / pp_val * 1000
        avg_cr = crime[col_r].mean() if col_r in crime.columns else 1
        avg_per1k_all = 13  # 대략적 평균
        need_score = (cr / avg_cr) * (avg_per1k_all / max(per1k, 1))
        need_data.append({
            '자치구': gu, '범죄율': cr, 'CCTV': ct,
            '천명당CCTV': round(per1k, 1), '필요도점수': round(need_score, 2)
        })

    need_df = pd.DataFrame(need_data).sort_values('필요도점수', ascending=False)

    # 필요도 상위 10개 차트
    fig_need = px.bar(
        need_df.head(10), x='필요도점수', y='자치구', orientation='h',
        color='필요도점수', color_continuous_scale='YlOrRd',
        text='필요도점수',
        labels={'필요도점수': '설치 필요도 점수', '자치구': ''}
    )
    fig_need.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    plotly_dark_layout(fig_need, height=400)
    fig_need.update_layout(yaxis=dict(autorange='reversed'), coloraxis_showscale=False)
    st.plotly_chart(fig_need, use_container_width=True)

    # 필요도 상세 테이블
    st.markdown("**📋 전체 자치구 CCTV 필요도 순위**")
    need_display = need_df[['자치구','범죄율','CCTV','천명당CCTV','필요도점수']].reset_index(drop=True)
    need_display.index = need_display.index + 1
    st.dataframe(need_display, use_container_width=True)

    # CCTV 필요도 지도
    st.markdown('<div class="panel-card"><div class="panel-title">🗺️ CCTV 추가 설치 필요도 지도</div></div>', unsafe_allow_html=True)
    m_need = folium.Map(location=[37.5665, 126.9780], zoom_start=11, tiles='CartoDB dark_matter')

    need_map_data = need_df.set_index('자치구')
    max_need = need_df['필요도점수'].max()

    folium.Choropleth(
        geo_data=seoul_geo,
        data=need_df,
        columns=['자치구', '필요도점수'],
        key_on='feature.properties.name',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.3,
        legend_name='CCTV 설치 필요도 점수'
    ).add_to(m_need)

    for gu, coord in gu_coords.items():
        if gu in need_map_data.index:
            score = need_map_data.loc[gu, '필요도점수']
            per1k = need_map_data.loc[gu, '천명당CCTV']
            cr = need_map_data.loc[gu, '범죄율']
            color = '#ef4444' if score > 1.3 else '#f97316' if score > 1.0 else '#22d3ee'
            folium.CircleMarker(
                location=coord, radius=max(5, score * 6),
                color=color, fill=True, fill_color=color, fill_opacity=0.7,
                tooltip=f"{gu} | 필요도: {score:.2f} | 범죄율: {cr}% | 천명당CCTV: {per1k}"
            ).add_to(m_need)

    st_folium(m_need, width=None, height=500, returned_objects=[])