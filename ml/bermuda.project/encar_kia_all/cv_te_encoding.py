"""
모델_평균가_TE (누출 있음) → 모델_CV_TE (Cross-validated TE) 교체
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold, train_test_split

# ── 1. 데이터 로드 ──────────────────────────────────────────────
df = pd.read_csv(
    'C:/Users/Admin/hipython/ml/bermuda.project/encar_kia_all/output/encar_feature_processed_with_model_avg_te.csv',
    encoding='utf-8-sig'
)
print(f'로드 완료: {df.shape}')

# ── 2. 기존 파이프라인과 동일한 Train/Test split ────────────────
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
train_df = train_df.copy().reset_index(drop=True)
test_df  = test_df.copy().reset_index(drop=True)
print(f'Train: {len(train_df)}행 / Test: {len(test_df)}행')

# ── 3. CV Target Encoding 함수 ─────────────────────────────────
def cv_target_encoding(train_df, test_df, col, target, n_splits=5, smooth_k=10, random_state=42):
    """
    Parameters
    ----------
    col      : 인코딩할 컬럼 ('모델')
    target   : 타겟 컬럼 ('현재가격_만원')
    n_splits : KFold 수 (기본 5)
    smooth_k : smoothing 강도 - 값이 클수록 소표본 모델을 전체 평균으로 당김

    Returns
    -------
    train_encoded : Train용 OOF TE 배열
    test_encoded  : Test용 TE 배열 (전체 Train 기준)
    """
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    global_mean = train_df[target].mean()
    train_encoded = np.zeros(len(train_df))

    for fold, (tr_idx, val_idx) in enumerate(kf.split(train_df)):
        tr_fold  = train_df.iloc[tr_idx]
        val_fold = train_df.iloc[val_idx]

        # val 행은 tr_fold 기준으로만 평균/카운트 계산 → 자기 자신 제외
        fold_mean  = tr_fold.groupby(col)[target].mean()
        fold_count = tr_fold.groupby(col)[target].count()

        # Smoothing: n이 작으면 전체 평균 쪽으로 보정
        smoothed = (fold_count * fold_mean + smooth_k * global_mean) / (fold_count + smooth_k)

        # 이 fold에서 처음 등장하는 모델은 global_mean 사용
        train_encoded[val_idx] = val_fold[col].map(smoothed).fillna(global_mean).values

    # Test: 전체 Train 기준 TE (학습에는 사용하지 않으므로 누출 없음)
    final_mean  = train_df.groupby(col)[target].mean()
    final_count = train_df.groupby(col)[target].count()
    final_smoothed = (final_count * final_mean + smooth_k * global_mean) / (final_count + smooth_k)
    test_encoded = test_df[col].map(final_smoothed).fillna(global_mean).values

    return train_encoded, test_encoded

# ── 4. CV TE 계산 ──────────────────────────────────────────────
train_cv_te, test_cv_te = cv_target_encoding(
    train_df, test_df,
    col='모델',
    target='현재가격_만원',
    n_splits=5,
    smooth_k=10
)

train_df['모델_CV_TE'] = train_cv_te
test_df['모델_CV_TE']  = test_cv_te

# ── 5. 누출 감소 확인 ──────────────────────────────────────────
corr_old = df['모델_평균가_TE'].corr(df['현재가격_만원'])
corr_new_train = train_df['모델_CV_TE'].corr(train_df['현재가격_만원'])
corr_new_test  = test_df['모델_CV_TE'].corr(test_df['현재가격_만원'])

print(f'\n[상관관계 비교]')
print(f'기존 TE (전체, 누출):    {corr_old:.4f}')
print(f'CV TE (Train, OOF):     {corr_new_train:.4f}')
print(f'CV TE (Test, 검증용):   {corr_new_test:.4f}')

# ── 6. 기존 TE 제거 후 피처 정리 ──────────────────────────────
# 컬럼 순서: 매물ID, 모델_CV_TE, 현재가격_만원, 나머지 피처들 (모델 object 제거)
drop_cols = ['모델', '모델_평균가_TE']
train_final = train_df.drop(columns=drop_cols)
test_final  = test_df.drop(columns=drop_cols)

# 모델_CV_TE를 앞쪽으로 배치 (가독성)
cols = ['매물ID', '모델_CV_TE', '현재가격_만원'] + \
       [c for c in train_final.columns if c not in ['매물ID', '모델_CV_TE', '현재가격_만원']]
train_final = train_final[cols]
test_final  = test_final[cols]

print(f'\n[최종 피처 수] {train_final.shape[1]}개')
print(f'컬럼 목록: {list(train_final.columns)}')

# ── 7. 저장 ───────────────────────────────────────────────────
out_dir = 'C:/Users/Admin/hipython/ml/bermuda.project/encar_kia_all/output/'
train_final.to_csv(out_dir + 'train_cv_te.csv', index=False, encoding='utf-8-sig')
test_final.to_csv(out_dir  + 'test_cv_te.csv',  index=False, encoding='utf-8-sig')
print(f'\n저장 완료')
print(f'  → {out_dir}train_cv_te.csv  ({train_final.shape})')
print(f'  → {out_dir}test_cv_te.csv   ({test_final.shape})')
