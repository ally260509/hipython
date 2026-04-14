# -*- coding: utf-8 -*-
"""
중고차 판매가격 예측 모델링 파이프라인
=====================================
STEP 1. 데이터 확인 및 피처/타겟 분리
STEP 2. 이상치 탐색 및 처리
STEP 3. Train / Test 분리
STEP 4. 베이스라인 모델 학습 및 비교
STEP 5. 모델 성능 평가 (CV 포함)
STEP 6. 하이퍼파라미터 튜닝 (Optuna – LightGBM)
STEP 7. 모델 해석 (SHAP)
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.rcParams["font.family"] = "Malgun Gothic"   # 한글 폰트
matplotlib.rcParams["axes.unicode_minus"] = False
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, KFold, cross_validate
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

import xgboost as xgb
import lightgbm as lgb
import optuna
import shap

# ──────────────────────────────────────────
# 공통 경로 설정
# ──────────────────────────────────────────
DATA_PATH = r"C:\Users\Admin\hipython\ml\bermuda.project\encar_kia_all\output\kia_preprocessed_v2.csv"
OUT_DIR   = r"C:\Users\Admin\hipython\ml\bermuda.project\encar_kia_all\output"
RANDOM_STATE = 42

# ──────────────────────────────────────────────────────────────
# STEP 1. 데이터 확인 및 피처/타겟 분리
# ──────────────────────────────────────────────────────────────
print("=" * 60)
print("STEP 1. 데이터 확인 및 피처/타겟 분리")
print("=" * 60)

df = pd.read_csv(DATA_PATH)
print(f"  원본 shape : {df.shape}")

# ── 타겟 분리
target = "현재가격"
y = df[target].copy()

# ── 불필요 컬럼 제거 (매물ID, 제조사_기아 – 단일 값)
drop_cols = ["매물ID", "제조사_기아"]
X_raw = df.drop(columns=[target] + drop_cols)

# ── 모델명: Target Encoding (학습 데이터 기준) → 이름 보존을 위해 별도 열 유지
#    (object 그대로 저장된 '모델' 열을 숫자로 변환, leakage 방지는 STEP 3 이후 적용)
print(f"  피처 수    : {X_raw.shape[1]}  (모델명 포함)")
print(f"  타겟 수    : {y.shape[0]}")
print()

# ──────────────────────────────────────────────────────────────
# STEP 2. 이상치 탐색 및 처리
# ──────────────────────────────────────────────────────────────
print("=" * 60)
print("STEP 2. 이상치 탐색 및 처리")
print("=" * 60)

# ── 2-1. 타겟 분포 시각화
fig, axes = plt.subplots(1, 2, figsize=(13, 4))
axes[0].hist(y, bins=60, color="#4C72B0", edgecolor="white")
axes[0].set_title("현재가격 분포 (원본)")
axes[0].set_xlabel("가격 (만원)")
axes[1].hist(np.log1p(y), bins=60, color="#DD8452", edgecolor="white")
axes[1].set_title("현재가격 분포 (log 변환)")
axes[1].set_xlabel("log(가격+1)")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/01_price_distribution.png", dpi=120, bbox_inches="tight")
plt.close()
print("  → 분포 저장: 01_price_distribution.png")

# ── 2-2. IQR 기반 상·하위 극단값 탐색
Q1, Q3 = y.quantile(0.25), y.quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR
outliers = y[(y < lower) | (y > upper)]
print(f"  IQR 범위   : {lower:.0f} ~ {upper:.0f} 만원")
print(f"  이상치 건수 : {len(outliers)}건 ({len(outliers)/len(y)*100:.1f}%)")

# ── 2-3. 극단값 캡핑 (상위 1% 제거 대신 캡핑으로 정보 보존)
upper_cap = y.quantile(0.99)
lower_cap = max(y.quantile(0.01), 50)   # 50만원 미만은 데이터 오류 가능성
mask = (y >= lower_cap) & (y <= upper_cap)
X_clean = X_raw[mask].reset_index(drop=True)
y_clean = y[mask].reset_index(drop=True)
print(f"  캡핑 후 데이터: {y_clean.shape[0]}건  "
      f"(제거 {len(y) - y_clean.shape[0]}건, "
      f"가격 범위 {lower_cap:.0f}~{upper_cap:.0f} 만원)")
print()

# ──────────────────────────────────────────────────────────────
# STEP 3. Train / Test 분리 + 모델명 인코딩
# ──────────────────────────────────────────────────────────────
print("=" * 60)
print("STEP 3. Train / Test 분리")
print("=" * 60)

X_tr_raw, X_te_raw, y_tr, y_te = train_test_split(
    X_clean, y_clean, test_size=0.2, random_state=RANDOM_STATE
)
print(f"  Train : {X_tr_raw.shape[0]}건 | Test : {X_te_raw.shape[0]}건")

# ── 모델명 Target Encoding (학습 데이터 평균가격 기준 → 리크 방지)
train_model_mean = y_tr.groupby(X_tr_raw["모델"].values).mean().to_dict()
global_mean = y_tr.mean()

def encode_model(X, mapping, global_mean):
    return X["모델"].map(mapping).fillna(global_mean)

X_tr = X_tr_raw.copy()
X_te = X_te_raw.copy()
X_tr["모델_enc"] = encode_model(X_tr, train_model_mean, global_mean)
X_te["모델_enc"] = encode_model(X_te, train_model_mean, global_mean)
X_tr = X_tr.drop(columns=["모델"])
X_te = X_te.drop(columns=["모델"])

feat_names = list(X_tr.columns)
print(f"  최종 피처 수 : {len(feat_names)}")
print(f"  피처 목록 : {feat_names}")
print()

# ──────────────────────────────────────────────────────────────
# STEP 4 & 5. 베이스라인 모델 학습 + 성능 평가 (5-Fold CV)
# ──────────────────────────────────────────────────────────────
print("=" * 60)
print("STEP 4 & 5. 베이스라인 모델 학습 + 성능 평가")
print("=" * 60)

def eval_metrics(y_true, y_pred, label=""):
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2   = r2_score(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    return {"Model": label, "MAE": round(mae,1), "RMSE": round(rmse,1),
            "R²": round(r2,4), "MAPE(%)": round(mape,2)}

kf = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

models = {
    "Linear Regression": LinearRegression(),
    "Ridge":             Ridge(alpha=10),
    "Lasso":             Lasso(alpha=10),
    "Random Forest":     RandomForestRegressor(n_estimators=200, n_jobs=-1,
                                               random_state=RANDOM_STATE),
    "XGBoost":           xgb.XGBRegressor(n_estimators=400, learning_rate=0.05,
                                          max_depth=6, subsample=0.8,
                                          colsample_bytree=0.8,
                                          random_state=RANDOM_STATE,
                                          verbosity=0),
    "LightGBM":          lgb.LGBMRegressor(n_estimators=400, learning_rate=0.05,
                                            num_leaves=63, subsample=0.8,
                                            colsample_bytree=0.8,
                                            random_state=RANDOM_STATE,
                                            verbose=-1),
}

results_cv  = []   # CV 결과
results_test= []   # Test 결과
trained_models = {}

for name, model in models.items():
    # ── 5-Fold CV (학습 데이터)
    cv_res = cross_validate(
        model, X_tr, y_tr, cv=kf,
        scoring={"mae":  "neg_mean_absolute_error",
                 "rmse": "neg_root_mean_squared_error",
                 "r2":   "r2"},
        n_jobs=-1, return_train_score=False
    )
    cv_mae  = -cv_res["test_mae"].mean()
    cv_rmse = -cv_res["test_rmse"].mean()
    cv_r2   =  cv_res["test_r2"].mean()
    results_cv.append({"Model": name,
                        "CV_MAE": round(cv_mae,1),
                        "CV_RMSE": round(cv_rmse,1),
                        "CV_R²": round(cv_r2,4)})

    # ── Test 세트 평가
    model.fit(X_tr, y_tr)
    y_pred = model.predict(X_te)
    results_test.append(eval_metrics(y_te, y_pred, name))
    trained_models[name] = model
    print(f"  [{name:20s}]  MAE={cv_mae:6.1f}  RMSE={cv_rmse:7.1f}  R²={cv_r2:.4f}")

df_cv   = pd.DataFrame(results_cv)
df_test = pd.DataFrame(results_test)
print()
print("── 5-Fold CV 결과 ──")
print(df_cv.to_string(index=False))
print()
print("── Test 세트 결과 ──")
print(df_test.to_string(index=False))
print()

# ── 성능 비교 차트 (MAE / R²)
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
order = df_cv.sort_values("CV_MAE")["Model"]

axes[0].barh(order, df_cv.set_index("Model").loc[order,"CV_MAE"],
             color="#4C72B0")
axes[0].set_xlabel("CV MAE (만원)  ← 낮을수록 좋음")
axes[0].set_title("모델별 CV MAE 비교")

axes[1].barh(order, df_cv.set_index("Model").loc[order,"CV_R²"],
             color="#55A868")
axes[1].set_xlabel("CV R²  → 높을수록 좋음")
axes[1].set_title("모델별 CV R² 비교")

plt.tight_layout()
plt.savefig(f"{OUT_DIR}/02_baseline_comparison.png", dpi=120, bbox_inches="tight")
plt.close()
print("  → 비교 차트 저장: 02_baseline_comparison.png")
print()

# ──────────────────────────────────────────────────────────────
# STEP 6. 하이퍼파라미터 튜닝 – LightGBM × Optuna
# ──────────────────────────────────────────────────────────────
print("=" * 60)
print("STEP 6. 하이퍼파라미터 튜닝 (Optuna - LightGBM)")
print("=" * 60)

X_tr_np = np.array(X_tr)
X_te_np = np.array(X_te)

def objective(trial):
    params = {
        "n_estimators":      trial.suggest_int("n_estimators", 300, 1500),
        "learning_rate":     trial.suggest_float("learning_rate", 0.01, 0.15, log=True),
        "num_leaves":        trial.suggest_int("num_leaves", 31, 255),
        "max_depth":         trial.suggest_int("max_depth", 4, 12),
        "min_child_samples": trial.suggest_int("min_child_samples", 5, 50),
        "subsample":         trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree":  trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "reg_alpha":         trial.suggest_float("reg_alpha", 1e-3, 10.0, log=True),
        "reg_lambda":        trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
        "random_state": RANDOM_STATE,
        "verbose": -1,
        "n_jobs": -1,
    }
    model = lgb.LGBMRegressor(**params)
    scores = cross_validate(model, X_tr, y_tr, cv=kf,
                            scoring="neg_mean_absolute_error",
                            n_jobs=-1)
    return -scores["test_score"].mean()

optuna.logging.set_verbosity(optuna.logging.WARNING)
study = optuna.create_study(direction="minimize",
                            sampler=optuna.samplers.TPESampler(seed=RANDOM_STATE))
study.optimize(objective, n_trials=80, show_progress_bar=True)

best_params = study.best_params
best_mae    = study.best_value
print(f"\n  최적 CV MAE : {best_mae:.1f} 만원")
print(f"  최적 파라미터 :")
for k, v in best_params.items():
    print(f"    {k}: {v}")

# ── 최적 모델 재학습 및 테스트 평가
best_lgb = lgb.LGBMRegressor(**best_params, random_state=RANDOM_STATE,
                              verbose=-1, n_jobs=-1)
best_lgb.fit(X_tr, y_tr)
y_pred_best = best_lgb.predict(X_te)
res_best = eval_metrics(y_te, y_pred_best, "LightGBM (Tuned)")
print()
print("── 최적 LightGBM Test 결과 ──")
for k, v in res_best.items():
    print(f"  {k}: {v}")

# ── 실제 vs 예측 산점도
fig, ax = plt.subplots(figsize=(7,6))
ax.scatter(y_te, y_pred_best, alpha=0.3, s=15, color="#4C72B0")
mn, mx = y_te.min(), y_te.max()
ax.plot([mn,mx],[mn,mx], "r--", lw=1.5, label="Perfect Fit")
ax.set_xlabel("실제 가격 (만원)")
ax.set_ylabel("예측 가격 (만원)")
ax.set_title(f"실제 vs 예측  |  MAE={res_best['MAE']:.0f}만원  R²={res_best['R²']:.4f}")
ax.legend()
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/03_pred_vs_actual.png", dpi=120, bbox_inches="tight")
plt.close()
print("\n  → 산점도 저장: 03_pred_vs_actual.png")
print()

# ── Optuna 최적화 히스토리
try:
    from optuna.visualization.matplotlib import plot_optimization_history, plot_param_importances
    fig = plot_optimization_history(study)
    fig.savefig(f"{OUT_DIR}/04_optuna_history.png", dpi=120, bbox_inches="tight")
    plt.close()
    print("  → Optuna 히스토리 저장: 04_optuna_history.png")
except Exception:
    pass
print()

# ──────────────────────────────────────────────────────────────
# STEP 7. 모델 해석 – SHAP
# ──────────────────────────────────────────────────────────────
print("=" * 60)
print("STEP 7. 모델 해석 (SHAP)")
print("=" * 60)

explainer  = shap.TreeExplainer(best_lgb)
shap_values = explainer(X_te)

# ── 7-1. Feature Importance (Bar)
fig, ax = plt.subplots(figsize=(9, 6))
shap.plots.bar(shap_values, max_display=20, show=False, ax=ax)
ax.set_title("SHAP Feature Importance (Mean |SHAP|)")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/05_shap_importance.png", dpi=120, bbox_inches="tight")
plt.close()
print("  → SHAP 중요도 저장: 05_shap_importance.png")

# ── 7-2. Beeswarm (분포 전체)
fig, ax = plt.subplots(figsize=(10, 7))
shap.plots.beeswarm(shap_values, max_display=20, show=False)
plt.title("SHAP Beeswarm – 피처별 영향 분포")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/06_shap_beeswarm.png", dpi=120, bbox_inches="tight")
plt.close()
print("  → SHAP Beeswarm 저장: 06_shap_beeswarm.png")

# ── 7-3. Waterfall (개별 예측 설명 – 가장 비싼 차 1대)
idx_sample = y_te.values.argmax()
fig, ax = plt.subplots(figsize=(10, 6))
shap.plots.waterfall(shap_values[idx_sample], max_display=15, show=False)
plt.title(f"SHAP Waterfall – 예측 가격 {y_pred_best[idx_sample]:.0f}만원 (실제 {y_te.values[idx_sample]:.0f}만원)")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/07_shap_waterfall.png", dpi=120, bbox_inches="tight")
plt.close()
print("  → SHAP Waterfall 저장: 07_shap_waterfall.png")

# ──────────────────────────────────────────────────────────────
# 최종 결과 요약
# ──────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("최종 결과 요약")
print("=" * 60)
print()

all_results = df_test.copy()
all_results.loc[len(all_results)] = res_best
print(all_results.to_string(index=False))
print()
print(f"  ★ 최적 모델 : LightGBM (Tuned)")
print(f"     MAE    : {res_best['MAE']:.1f} 만원")
print(f"     RMSE   : {res_best['RMSE']:.1f} 만원")
print(f"     R²     : {res_best['R²']:.4f}")
print(f"     MAPE   : {res_best['MAPE(%)']:.2f} %")
print()

# ── 결과 CSV 저장
all_results.to_csv(f"{OUT_DIR}/model_results_summary.csv", index=False, encoding="utf-8-sig")
print("  → 결과 CSV 저장: model_results_summary.csv")
print()
print("All Done.")
