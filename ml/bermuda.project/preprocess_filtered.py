import pandas as pd
from model_grouping import MODEL_GROUP_MAP

CSV_PATH  = r'C:\Users\Admin\hipython\ml\bermuda.project\data\merged_all_brands_by_my_template (1).csv'
OUT_PATH  = r'C:\Users\Admin\hipython\ml\bermuda.project\data\preprocessed_filtered.xlsx'

# ── 1. 원본 데이터 로드 ──────────────────────────────────────
df = pd.read_csv(CSV_PATH, encoding='utf-8')
print(f"원본 행 수: {len(df):,}  |  컬럼 수: {df.shape[1]}")

# ── 2. 모델 → 그룹명으로 교체 ────────────────────────────────
df['모델'] = df['모델'].map(MODEL_GROUP_MAP).fillna(df['모델'])

# ── 3. 그룹별 frequency 계산 → frequency 20 이하 제거 ─────────
freq = df['모델'].value_counts()
keep_models = freq[freq > 20].index
df = df[df['모델'].isin(keep_models)].reset_index(drop=True)
print(f"frequency > 20 필터 후 행 수: {len(df):,}  |  잔존 모델 수: {df['모델'].nunique()}")

# ── 4. '연료_전기' 컬럼 삭제 ──────────────────────────────────
if '연료_전기' in df.columns:
    df = df.drop(columns=['연료_전기'])
    print("'연료_전기' 컬럼 삭제 완료")
else:
    print("'연료_전기' 컬럼 없음 (스킵)")

print(f"최종 행 수: {len(df):,}  |  최종 컬럼 수: {df.shape[1]}")

# ── 5. 엑셀 저장 ──────────────────────────────────────────────
with pd.ExcelWriter(OUT_PATH, engine='xlsxwriter') as writer:
    # 전처리된 raw data
    df.to_excel(writer, sheet_name='data', index=False)

    # 모델별 frequency 요약
    freq_df = (
        df['모델'].value_counts()
        .reset_index()
        .rename(columns={'모델': '모델', 'count': 'frequency'})
        .reset_index(drop=True)
    )
    freq_df.index += 1
    freq_df.to_excel(writer, sheet_name='모델_frequency', index=True)

    # 컬럼 너비 자동 조정 (data 시트)
    ws = writer.sheets['data']
    for i, col in enumerate(df.columns):
        max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
        ws.set_column(i, i, min(max_len, 40))

print(f"저장 완료: {OUT_PATH}")
