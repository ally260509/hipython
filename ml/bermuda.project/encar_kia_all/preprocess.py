"""
중고차 판매가격 예측 모델 - 데이터 전처리 스크립트
Feature 목록 (1).xlsx (최종선택피처요약 + 인코딩전략상세) 기준
"""

import pandas as pd
import os

INPUT_PATH  = os.path.join(os.path.dirname(__file__), 'output', 'kia_detail_batch.csv')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'output', 'kia_preprocessed_v2.csv')

# ── 1. 원본 로드 ───────────────────────────────────────────────
df_raw = pd.read_csv(INPUT_PATH)
print(f"원본: {df_raw.shape[0]}행 × {df_raw.shape[1]}열")

# ── 2. 필요 컬럼만 선택 (피처 + 파생변수 재료) ────────────────
MAJOR_OPT_COLS = [
    '주요옵션_선루프', '주요옵션_헤드램프 (LED)', '주요옵션_주차감지센서',
    '주요옵션_후방카메라', '주요옵션_자동에어컨', '주요옵션_스마트키',
    '주요옵션_내비게이션', '주요옵션_열선시트', '주요옵션_통풍시트', '주요옵션_가죽시트',
]

needed = [
    '매물ID', '제조사', '모델', '현재가격_만원', '연식', '주행거리_km',
    '연료', '색상', '변속기', '배기량_cc', '차급', '좌석수',
    # 파생변수 사고강도점수 재료
    '교환_개수', '판금_개수', '보험이력건수', '부식_여부',
] + MAJOR_OPT_COLS

df = df_raw[needed].copy()

# ── 3. 결측값 처리 ────────────────────────────────────────────
# 좌석수: 최빈값
df['좌석수'] = df['좌석수'].fillna(df['좌석수'].mode()[0]).astype(int)

# 사고강도점수 재료: 결측 → 0
for col in ['교환_개수', '판금_개수', '보험이력건수', '부식_여부']:
    df[col] = df[col].fillna(0)

# 주요옵션 10개: 결측 → 0 (헤드램프 LED 39.6% 포함)
df[MAJOR_OPT_COLS] = df[MAJOR_OPT_COLS].fillna(0).astype(int)

# ── 4. 파생변수 생성 ──────────────────────────────────────────
# 차량연령
df['차량연령'] = (2026 - df['연식']).astype(int)

# 사고강도점수 = (교환개수×2) + (판금개수×1) + (보험이력건수×1) + (부식여부×1)
df['사고강도점수'] = (
    df['교환_개수'].astype(int) * 2
    + df['판금_개수'].astype(int) * 1
    + df['보험이력건수'].astype(int) * 1
    + df['부식_여부'].astype(int) * 1
).astype(int)

# ── 5. 변속기 Binary Encoding (오토=1, 수동=0) ───────────────
df['변속기'] = (df['변속기'] == '오토').astype(int)

# ── 6. 연료 One-Hot Encoding (6→5 그룹) ──────────────────────
fuel_map = {
    'LPG(일반인 구입)': '연료_LPG',
    '가솔린':          '연료_가솔린',
    '가솔린+전기':     '연료_하이브리드',
    '가솔린+LPG':     '연료_하이브리드',
    '디젤':            '연료_디젤',
    '전기':            '연료_전기',
}
df['연료_그룹'] = df['연료'].map(fuel_map)
fuel_dummies = pd.get_dummies(df['연료_그룹'], prefix='', prefix_sep='').astype(int)
# 순서 고정
fuel_cols_ordered = ['연료_LPG', '연료_가솔린', '연료_하이브리드', '연료_디젤', '연료_전기']
fuel_dummies = fuel_dummies.reindex(columns=fuel_cols_ordered, fill_value=0)

# ── 7. 색상 One-Hot Encoding (24→4 그룹) ─────────────────────
def map_color(c):
    if c in ('흰색', '진주색', '흰색투톤'):
        return '색상_흰색'
    elif c == '검정색':
        return '색상_검정색'
    elif c in ('은색', '은회색', '쥐색'):
        return '색상_은색'
    else:
        return '색상_기타'

df['색상_그룹'] = df['색상'].apply(map_color)
color_dummies = pd.get_dummies(df['색상_그룹'], prefix='', prefix_sep='').astype(int)
color_cols_ordered = ['색상_흰색', '색상_검정색', '색상_은색', '색상_기타']
color_dummies = color_dummies.reindex(columns=color_cols_ordered, fill_value=0)

# ── 8. 차급 Binary Grouping (9→2) ────────────────────────────
# SUV 그룹: SUV / RV / 화물차 / 승합차 / 경승합차
suv_set = {'SUV', 'RV', '화물차', '승합차', '경승합차'}
grade_dummies = pd.DataFrame({
    '차급_SUV':  df['차급'].isin(suv_set).astype(int),
    '차급_세단': (~df['차급'].isin(suv_set)).astype(int),
})

# ── 9. 제조사 One-Hot Encoding (기아 단일 → 상수 컬럼) ─────────
maker_dummies = pd.get_dummies(df['제조사'], prefix='제조사').astype(int)

# ── 10. 컬럼 이름 정리 ────────────────────────────────────────
df = df.rename(columns={'현재가격_만원': '현재가격', '배기량_cc': '배기량'})

# ── 11. 최종 데이터프레임 조립 ────────────────────────────────
result = pd.concat([
    df[['매물ID', '모델', '현재가격']],          # ID, 타겟 (모델은 object 유지)
    maker_dummies,                               # 제조사 OHE (1열)
    df[['주행거리_km', '배기량', '좌석수', '차량연령', '사고강도점수']],  # 수치형
    df['변속기'],                                # binary
    fuel_dummies,                                # 연료 OHE (5열)
    color_dummies,                               # 색상 OHE (4열)
    grade_dummies,                               # 차급 OHE (9열)
    df[MAJOR_OPT_COLS],                          # 주요옵션 10개 boolean
], axis=1)

# ── 12. 저장 ──────────────────────────────────────────────────
result.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')

# ── 13. 검증 출력 ─────────────────────────────────────────────
print(f"\n전처리 완료: {result.shape[0]}행 × {result.shape[1]}열")
print(f"저장: {OUTPUT_PATH}")
print("\n--- 컬럼 목록 ---")
for i, col in enumerate(result.columns, 1):
    print(f"  {i:2d}. {col} ({result[col].dtype})")
print(f"\n결측값: {result.isnull().sum().sum()}건")
print("\n--- 샘플 (첫 2행) ---")
print(result.head(2).to_string())
