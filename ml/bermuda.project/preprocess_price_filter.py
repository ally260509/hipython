import pandas as pd
from model_grouping import MODEL_GROUP_MAP

CSV_PATH = r'C:\Users\Admin\hipython\ml\bermuda.project\data\merged_all_brands_by_my_template (1).csv'
OUT_PATH = r'C:\Users\Admin\hipython\ml\bermuda.project\data\bermuda_data_v2.xlsx'

df = pd.read_csv(CSV_PATH, encoding='utf-8')
print(f"[1] 원본: {len(df):,}행")

# 모델 그룹명으로 교체
df['모델'] = df['모델'].map(MODEL_GROUP_MAP).fillna(df['모델'])

# 모델 frequency > 20 필터
freq = df['모델'].value_counts()
df = df[df['모델'].isin(freq[freq > 20].index)].reset_index(drop=True)
print(f"[2] frequency>20 필터 후: {len(df):,}행")

# 연료_전기 컬럼 삭제
if '연료_전기' in df.columns:
    df = df.drop(columns=['연료_전기'])

# 현재가격_만원 필터 ─ 100 이하 / 10000 이상 제거
col = '현재가격_만원'
before = len(df)
df = df[(df[col] > 100) & (df[col] < 10000)].reset_index(drop=True)
print(f"[3] 가격범위(100<x<10000) 필터 후: {len(df):,}행  (제거: {before - len(df):,}행)")

# 동일 자릿수 3회 이상 반복값 제거 (예: 999, 888, 9999, 7777)
def is_repeated_digit(v):
    s = str(int(v))
    return len(s) >= 3 and len(set(s)) == 1

before = len(df)
repeated_vals = df[col].dropna().apply(is_repeated_digit)
removed_vals = sorted(df.loc[repeated_vals[repeated_vals].index, col].unique().tolist())
df = df[~repeated_vals].reset_index(drop=True)
print(f"[4] 반복자릿수 필터 후: {len(df):,}행  (제거: {before - len(df):,}행, 해당값: {removed_vals})")

# 연료 피쳐 전체 0인 행 삭제
fuel_cols = ['연료_LPG', '연료_가솔린', '연료_하이브리드', '연료_디젤', '연료_수소']
existing_fuel = [c for c in fuel_cols if c in df.columns]
before = len(df)
df = df[df[existing_fuel].sum(axis=1) > 0].reset_index(drop=True)
print(f"[5] 연료 전체 0 행 제거 후: {len(df):,}행  (제거: {before - len(df):,}행)")

# 변속기_오토계열 결측값 → 0
if '변속기_오토계열' in df.columns:
    null_cnt = df['변속기_오토계열'].isna().sum()
    df['변속기_오토계열'] = df['변속기_오토계열'].fillna(0)
    print(f"[6] 변속기_오토계열 결측 {null_cnt:,}건 → 0 으로 변경")

print(f"[최종] {len(df):,}행 x {df.shape[1]}컬럼  |  모델수: {df['모델'].nunique()}")

# 저장
with pd.ExcelWriter(OUT_PATH, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='data', index=False)

    freq_df = (
        df['모델'].value_counts()
        .reset_index()
        .rename(columns={'모델': '모델', 'count': 'frequency'})
    )
    freq_df.index += 1
    freq_df.to_excel(writer, sheet_name='모델_frequency', index=True)

    ws = writer.sheets['data']
    for i, c in enumerate(df.columns):
        max_len = max(df[c].astype(str).map(len).max(), len(c)) + 2
        ws.set_column(i, i, min(max_len, 40))

print(f"저장 완료: {OUT_PATH}")
