"""
저가/고가 파일 → Train/Test 분리 + CV Target Encoding
모델_CV_TE: 5-Fold OOF (train) / 전체 train 기준 (test)
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, KFold

DATA_DIR = r'C:\Users\Admin\hipython\ml\bermuda.project\data'

# ── CV TE 함수 ────────────────────────────────────────────────
def cv_target_encoding(train_df, test_df, col, target, n_splits=5, smooth_k=10, random_state=42):
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    global_mean = train_df[target].mean()
    train_encoded = np.zeros(len(train_df))

    for fold, (tr_idx, val_idx) in enumerate(kf.split(train_df)):
        tr_fold  = train_df.iloc[tr_idx]
        val_fold = train_df.iloc[val_idx]

        fold_mean  = tr_fold.groupby(col)[target].mean()
        fold_count = tr_fold.groupby(col)[target].count()
        smoothed   = (fold_count * fold_mean + smooth_k * global_mean) / (fold_count + smooth_k)

        train_encoded[val_idx] = val_fold[col].map(smoothed).fillna(global_mean).values

    # Test: 전체 train 기준 (test 정보 미포함)
    final_mean    = train_df.groupby(col)[target].mean()
    final_count   = train_df.groupby(col)[target].count()
    final_smoothed = (final_count * final_mean + smooth_k * global_mean) / (final_count + smooth_k)
    test_encoded  = test_df[col].map(final_smoothed).fillna(global_mean).values

    return train_encoded, test_encoded


# ── 처리 함수 ─────────────────────────────────────────────────
def process(label, filename):
    df = pd.read_csv(f'{DATA_DIR}/{filename}', encoding='utf-8-sig')
    price_col = df.columns[4]   # 현재가격_만원
    model_col = df.columns[1]   # 모델

    print(f'\n{"="*50}')
    print(f'[{label}] {df.shape}  |  가격 범위: {df[price_col].min():.0f} ~ {df[price_col].max():.0f}만원')

    # ── 3단계: Train / Test 분리 (80:20) ─────────────────────
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    train_df = train_df.copy().reset_index(drop=True)
    test_df  = test_df.copy().reset_index(drop=True)
    print(f'  Train: {len(train_df)}행  |  Test: {len(test_df)}행')

    # ── 4단계: CV Target Encoding ────────────────────────────
    train_te, test_te = cv_target_encoding(
        train_df, test_df,
        col=model_col,
        target=price_col,
        n_splits=5,
        smooth_k=10,
    )
    train_df['모델_CV_TE'] = train_te
    test_df['모델_CV_TE']  = test_te

    # 누출 감소 확인
    corr_train = train_df['모델_CV_TE'].corr(train_df[price_col])
    corr_test  = test_df['모델_CV_TE'].corr(test_df[price_col])
    print(f'  CV TE 상관관계  →  Train(OOF): {corr_train:.4f}  |  Test: {corr_test:.4f}')

    # 모델_CV_TE를 앞쪽 배치 (매물ID 바로 뒤)
    id_col = df.columns[0]
    front  = [id_col, '모델_CV_TE', price_col]
    rest   = [c for c in train_df.columns if c not in front]
    col_order = front + rest
    train_df = train_df[col_order]
    test_df  = test_df[col_order]

    # 저장
    prefix = 'low' if label == '저가' else 'high'
    train_path = f'{DATA_DIR}/{prefix}_train.csv'
    test_path  = f'{DATA_DIR}/{prefix}_test.csv'
    train_df.to_csv(train_path, index=False, encoding='utf-8-sig')
    test_df.to_csv(test_path,  index=False, encoding='utf-8-sig')

    print(f'  저장: {prefix}_train.csv ({train_df.shape})  |  {prefix}_test.csv ({test_df.shape})')
    print(f'  컬럼 수: {train_df.shape[1]}개')
    return train_df, test_df


# ── 실행 ──────────────────────────────────────────────────────
low_train, low_test   = process('저가', 'encar_low_price.csv')
high_train, high_test = process('고가', 'encar_high_price.csv')

print('\n\n완료 요약')
print(f'  low_train : {low_train.shape}   low_test : {low_test.shape}')
print(f'  high_train: {high_train.shape}  high_test: {high_test.shape}')
