# -*- coding: utf-8 -*-
"""
Hybrid Quantile LightGBM (CV TE 버전)
=====================================
STEP 1. 데이터 로드 및 피처 확인
STEP 2. 저가/고가 분할
STEP 3. 저가 모델 (q10/q50/q90) 훈련
STEP 4. 고가 모델 (q05/q50/q95) Optuna 튜닝
STEP 5. Hybrid 예측 및 성능 평가
STEP 6. 모델 저장
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.rcParams["font.family"] = "Malgun Gothic"
matplotlib.rcParams["axes.unicode_minus"] = False
import matplotlib.pyplot as plt
import lightgbm as lgb
import optuna
import pickle
from sklearn.model_selection import KFold

OUT_DIR   = r"C:\Users\Admin\hipython\ml\bermuda.project\encar_kia_all\output"
MODEL_DIR = r"C:\Users\Admin\hipython\ml\bermuda.project\encar_kia_all\output\model"
RANDOM_STATE = 42
THRESHOLD    = 1700   # 저가/고가 분기점 (만원)

# ──────────────────────────────────────────────────────────────
# STEP 1. 데이터 로드 및 피처 확인
# ──────────────────────────────────────────────────────────────
print("=" * 60)
print("STEP 1. 데이터 로드 및 피처 확인")
print("=" * 60)

train_df = pd.read_csv(f"{OUT_DIR}/train_cv_te.csv", encoding='utf-8-sig')
test_df  = pd.read_csv(f"{OUT_DIR}/test_cv_te.csv",  encoding='utf-8-sig')

print(f"  Train shape : {train_df.shape}")
print(f"  Test  shape : {test_df.shape}")

# 피처 / 타겟 분리
DROP_COLS = ['매물ID', '현재가격_만원']
FEAT_COLS = [c for c in train_df.columns if c not in DROP_COLS]

X_train = train_df[FEAT_COLS].copy()
y_train = train_df['현재가격_만원'].copy()
X_test  = test_df[FEAT_COLS].copy()
y_test  = test_df['현재가격_만원'].copy()

# log1p 변환 (모델 학습용)
y_train_log = np.log1p(y_train)
y_test_log  = np.log1p(y_test)

print(f"\n  사용 피처 수 : {len(FEAT_COLS)}개")
print(f"  피처 목록 : {FEAT_COLS}")
print(f"\n  타겟 통계 (원본 만원)")
print(f"    Train  mean={y_train.mean():.0f}  std={y_train.std():.0f}  min={y_train.min():.0f}  max={y_train.max():.0f}")
print(f"    Test   mean={y_test.mean():.0f}   std={y_test.std():.0f}   min={y_test.min():.0f}   max={y_test.max():.0f}")

# ──────────────────────────────────────────────────────────────
# STEP 2. 저가/고가 분할 (Threshold = 1700만원)
# ──────────────────────────────────────────────────────────────
print()
print("=" * 60)
print(f"STEP 2. 저가/고가 분할 (Threshold={THRESHOLD}만원)")
print("=" * 60)

# Train 분할
low_tr_mask  = y_train <= THRESHOLD
high_tr_mask = y_train > THRESHOLD

X_tr_low  = X_train[low_tr_mask].reset_index(drop=True)
y_tr_low  = y_train[low_tr_mask].reset_index(drop=True)
X_tr_high = X_train[high_tr_mask].reset_index(drop=True)
y_tr_high = y_train[high_tr_mask].reset_index(drop=True)

# Test 분할 (평가 시에는 전체 사용, 예측은 Threshold 기준 라우팅)
low_te_mask  = y_test <= THRESHOLD
high_te_mask = y_test > THRESHOLD

print(f"  Train 저가 (≤{THRESHOLD}) : {low_tr_mask.sum()}건 ({low_tr_mask.mean()*100:.1f}%)")
print(f"  Train 고가 (>{THRESHOLD}) : {high_tr_mask.sum()}건 ({high_tr_mask.mean()*100:.1f}%)")
print(f"  Test  저가 (≤{THRESHOLD}) : {low_te_mask.sum()}건 ({low_te_mask.mean()*100:.1f}%)")
print(f"  Test  고가 (>{THRESHOLD}) : {high_te_mask.sum()}건 ({high_te_mask.mean()*100:.1f}%)")

# log1p 변환
y_tr_low_log  = np.log1p(y_tr_low)
y_tr_high_log = np.log1p(y_tr_high)

# ──────────────────────────────────────────────────────────────
# STEP 3. 저가 모델 (q10 / q50 / q90) 훈련
# ──────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("STEP 3. 저가 모델 Optuna 튜닝 (q10 / q50 / q90, 30 trials × 3-Fold)")
print("=" * 60)

kf_low = KFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE)

def make_objective_low(quantile):
    def objective(trial):
        params = {
            "objective":         "quantile",
            "alpha":             quantile,
            "n_estimators":      trial.suggest_int("n_estimators", 300, 1500),
            "learning_rate":     trial.suggest_float("learning_rate", 0.01, 0.15, log=True),
            "num_leaves":        trial.suggest_int("num_leaves", 31, 255),
            "max_depth":         trial.suggest_int("max_depth", 4, 12),
            "min_child_samples": trial.suggest_int("min_child_samples", 5, 50),
            "subsample":         trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree":  trial.suggest_float("colsample_bytree", 0.5, 1.0),
            "reg_alpha":         trial.suggest_float("reg_alpha", 1e-3, 10.0, log=True),
            "reg_lambda":        trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
            "random_state":      RANDOM_STATE,
            "verbose":           -1,
            "n_jobs":            -1,
        }
        oof_losses = []
        for tr_idx, val_idx in kf_low.split(X_tr_low):
            X_tr_f = X_tr_low.iloc[tr_idx]
            y_tr_f = y_tr_low_log.iloc[tr_idx]
            X_val  = X_tr_low.iloc[val_idx]
            y_val  = y_tr_low_log.iloc[val_idx]

            m = lgb.LGBMRegressor(**params)
            m.fit(X_tr_f, y_tr_f)
            pred  = m.predict(X_val)
            err   = y_val.values - pred
            loss  = np.mean(np.where(err >= 0, quantile * err, (quantile - 1) * err))
            oof_losses.append(loss)
        return np.mean(oof_losses)
    return objective

low_quantiles    = [0.10, 0.50, 0.90]
low_models       = {}
best_params_low  = {}

for q in low_quantiles:
    print(f"  q{int(q*100):02d} Optuna 튜닝 중...", end=" ", flush=True)
    study = optuna.create_study(
        direction="minimize",
        sampler=optuna.samplers.TPESampler(seed=RANDOM_STATE)
    )
    study.optimize(make_objective_low(q), n_trials=30, show_progress_bar=False)

    best_p = {**study.best_params,
              "objective": "quantile", "alpha": q,
              "random_state": RANDOM_STATE, "verbose": -1, "n_jobs": -1}
    model = lgb.LGBMRegressor(**best_p)
    model.fit(X_tr_low, y_tr_low_log)
    low_models[q]      = model
    best_params_low[q] = study.best_params
    print(f"완료  (best pinball={study.best_value:.5f})")

# 저가 Test 예측
X_te_low = X_test[low_te_mask]
y_te_low  = y_test[low_te_mask]

preds_low = {
    q: np.expm1(low_models[q].predict(X_te_low))
    for q in low_quantiles
}

# 저가 구간 성능 확인
low_coverage = ((preds_low[0.10] <= y_te_low) & (y_te_low <= preds_low[0.90])).mean()
low_width    = (preds_low[0.90] - preds_low[0.10]).mean()
low_mae      = np.abs(preds_low[0.50] - y_te_low).mean()

print(f"\n  [저가 구간 성능]")
print(f"    Coverage (q10~q90) : {low_coverage*100:.1f}%")
print(f"    Width 평균         : {low_width:.0f}만원")
print(f"    MAE (q50)          : {low_mae:.1f}만원")

# ──────────────────────────────────────────────────────────────
# STEP 4. 고가 모델 (q05 / q50 / q95) Optuna 튜닝
# ──────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("STEP 4. 고가 모델 Optuna 튜닝 (q05 / q50 / q95, 30 trials × 3-Fold)")
print("=" * 60)

kf_high = KFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE)

def make_objective(quantile):
    def objective(trial):
        params = {
            "objective":         "quantile",
            "alpha":             quantile,
            "n_estimators":      trial.suggest_int("n_estimators", 300, 1500),
            "learning_rate":     trial.suggest_float("learning_rate", 0.01, 0.15, log=True),
            "num_leaves":        trial.suggest_int("num_leaves", 31, 255),
            "max_depth":         trial.suggest_int("max_depth", 4, 12),
            "min_child_samples": trial.suggest_int("min_child_samples", 5, 50),
            "subsample":         trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree":  trial.suggest_float("colsample_bytree", 0.5, 1.0),
            "reg_alpha":         trial.suggest_float("reg_alpha", 1e-3, 10.0, log=True),
            "reg_lambda":        trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
            "random_state":      RANDOM_STATE,
            "verbose":           -1,
            "n_jobs":            -1,
        }
        oof_losses = []
        for tr_idx, val_idx in kf_high.split(X_tr_high):
            X_tr_f = X_tr_high.iloc[tr_idx]
            y_tr_f = y_tr_high_log.iloc[tr_idx]
            X_val  = X_tr_high.iloc[val_idx]
            y_val  = y_tr_high_log.iloc[val_idx]

            m = lgb.LGBMRegressor(**params)
            m.fit(X_tr_f, y_tr_f)
            pred   = m.predict(X_val)
            # Pinball loss
            err    = y_val.values - pred
            loss   = np.mean(np.where(err >= 0, quantile * err, (quantile - 1) * err))
            oof_losses.append(loss)
        return np.mean(oof_losses)
    return objective

optuna.logging.set_verbosity(optuna.logging.WARNING)

high_quantiles  = [0.05, 0.50, 0.95]
high_models     = {}
best_params_log = {}

for q in high_quantiles:
    print(f"  q{int(q*100):02d} Optuna 튜닝 중...", end=" ", flush=True)
    study = optuna.create_study(
        direction="minimize",
        sampler=optuna.samplers.TPESampler(seed=RANDOM_STATE)
    )
    study.optimize(make_objective(q), n_trials=30, show_progress_bar=False)

    best_p = {**study.best_params,
              "objective": "quantile", "alpha": q,
              "random_state": RANDOM_STATE, "verbose": -1, "n_jobs": -1}
    model  = lgb.LGBMRegressor(**best_p)
    model.fit(X_tr_high, y_tr_high_log)
    high_models[q]     = model
    best_params_log[q] = study.best_params
    print(f"완료  (best pinball={study.best_value:.5f})")

# 고가 Test 예측
X_te_high = X_test[high_te_mask]
y_te_high  = y_test[high_te_mask]

preds_high = {
    q: np.expm1(high_models[q].predict(X_te_high))
    for q in high_quantiles
}

high_coverage = ((preds_high[0.05] <= y_te_high) & (y_te_high <= preds_high[0.95])).mean()
high_width    = (preds_high[0.95] - preds_high[0.05]).mean()
high_mae      = np.abs(preds_high[0.50] - y_te_high).mean()

print(f"\n  [고가 구간 성능]")
print(f"    Coverage (q05~q95) : {high_coverage*100:.1f}%")
print(f"    Width 평균         : {high_width:.0f}만원")
print(f"    MAE (q50)          : {high_mae:.1f}만원")

# ──────────────────────────────────────────────────────────────
# STEP 5. Hybrid 전체 예측 및 성능 평가
# ──────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("STEP 5. Hybrid 전체 성능 평가")
print("=" * 60)

# 전체 Test에 대해 Threshold 기준으로 라우팅
q_lo = np.full(len(y_test), np.nan)
q_mid= np.full(len(y_test), np.nan)
q_hi = np.full(len(y_test), np.nan)

low_idx  = np.where(low_te_mask.values)[0]
high_idx = np.where(high_te_mask.values)[0]

# 저가 구간 채우기 (q10/q50/q90)
q_lo[low_idx]  = preds_low[0.10]
q_mid[low_idx] = preds_low[0.50]
q_hi[low_idx]  = preds_low[0.90]

# 고가 구간 채우기 (q05/q50/q95)
q_lo[high_idx]  = preds_high[0.05]
q_mid[high_idx] = preds_high[0.50]
q_hi[high_idx]  = preds_high[0.95]

y_te_arr = y_test.values
hybrid_coverage = ((q_lo <= y_te_arr) & (y_te_arr <= q_hi)).mean()
hybrid_width    = (q_hi - q_lo).mean()
hybrid_mae      = np.abs(q_mid - y_te_arr).mean()

print(f"\n  {'지표':<20} {'기존 모델':>12} {'CV TE 모델':>12}")
print(f"  {'-'*46}")
print(f"  {'Coverage':<20} {'80.4%':>12} {hybrid_coverage*100:>11.1f}%")
print(f"  {'Width 평균(만원)':<20} {'956':>12} {hybrid_width:>12.0f}")
print(f"  {'MAE (만원)':<20} {'280.4':>12} {hybrid_mae:>12.1f}")

# 저가/고가 세부 성능
print(f"\n  [저가 구간 (≤{THRESHOLD}만원)]")
print(f"    Coverage : {low_coverage*100:.1f}%  |  Width : {low_width:.0f}만원  |  MAE : {low_mae:.1f}만원")
print(f"  [고가 구간 (>{THRESHOLD}만원)]")
print(f"    Coverage : {high_coverage*100:.1f}%  |  Width : {high_width:.0f}만원  |  MAE : {high_mae:.1f}만원")

# ── 시각화: 실제 vs 예측 중간값 산점도
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 전체
axes[0].scatter(y_te_arr[low_idx],  q_mid[low_idx],  alpha=0.3, s=10, label=f'저가(≤{THRESHOLD})', color='#4C72B0')
axes[0].scatter(y_te_arr[high_idx], q_mid[high_idx], alpha=0.3, s=10, label=f'고가(>{THRESHOLD})', color='#DD8452')
mn, mx = y_te_arr.min(), y_te_arr.max()
axes[0].plot([mn,mx],[mn,mx], 'r--', lw=1.5, label='Perfect Fit')
axes[0].set_xlabel('실제 가격 (만원)'); axes[0].set_ylabel('예측 중간값 (만원)')
axes[0].set_title(f'실제 vs 예측  |  MAE={hybrid_mae:.0f}만원')
axes[0].legend(fontsize=8)

# 예측 구간 폭 분포
axes[1].hist(q_hi[low_idx]  - q_lo[low_idx],  bins=40, alpha=0.6, label=f'저가', color='#4C72B0')
axes[1].hist(q_hi[high_idx] - q_lo[high_idx], bins=40, alpha=0.6, label=f'고가', color='#DD8452')
axes[1].set_xlabel('예측 구간 폭 (만원)'); axes[1].set_ylabel('빈도')
axes[1].set_title(f'예측 구간 폭 분포  |  평균 {hybrid_width:.0f}만원')
axes[1].legend()

plt.tight_layout()
plt.savefig(f"{OUT_DIR}/hybrid_cv_te_performance.png", dpi=120, bbox_inches="tight")
plt.close()
print(f"\n  → 시각화 저장: hybrid_cv_te_performance.png")

# ──────────────────────────────────────────────────────────────
# STEP 6. 모델 저장
# ──────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("STEP 6. 모델 저장")
print("=" * 60)

import os
os.makedirs(MODEL_DIR, exist_ok=True)

# 저가 모델
with open(f"{MODEL_DIR}/lgb_low_models_cvte.pkl", "wb") as f:
    pickle.dump(low_models, f)

# 고가 모델
with open(f"{MODEL_DIR}/lgb_high_models_cvte.pkl", "wb") as f:
    pickle.dump(high_models, f)

# 메타 정보
meta = {
    "threshold":    THRESHOLD,
    "feat_cols":    FEAT_COLS,
    "low_quantiles":  low_quantiles,
    "high_quantiles": high_quantiles,
    "performance": {
        "coverage": round(hybrid_coverage, 4),
        "width":    round(hybrid_width, 1),
        "mae":      round(hybrid_mae, 1),
    },
    "best_params_low":  best_params_low,
    "best_params_high": best_params_log,
}
with open(f"{MODEL_DIR}/hybrid_quantile_lgb_cvte.pkl", "wb") as f:
    pickle.dump(meta, f)

print(f"  저장 완료: {MODEL_DIR}/")
print(f"    lgb_low_models_cvte.pkl")
print(f"    lgb_high_models_cvte.pkl")
print(f"    hybrid_quantile_lgb_cvte.pkl")
print()
print("All Done.")
