# -*- coding: utf-8 -*-
"""
STEP 6. 하이퍼파라미터 튜닝 (Optuna - LightGBM)
STEP 7. 모델 해석 (SHAP)
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.rcParams["font.family"] = "Malgun Gothic"
matplotlib.rcParams["axes.unicode_minus"] = False
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, KFold, cross_validate
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import xgboost as xgb
import lightgbm as lgb
import optuna
import shap

# ── 경로 설정
DATA_PATH = r"C:\Users\Admin\hipython\ml\bermuda.project\encar_kia_all\output\kia_preprocessed_v2.csv"
OUT_DIR   = r"C:\Users\Admin\hipython\ml\bermuda.project\encar_kia_all\output"
RANDOM_STATE = 42

def eval_metrics(y_true, y_pred, label=""):
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2   = r2_score(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    return {"Model": label, "MAE": round(mae,1), "RMSE": round(rmse,1),
            "R2": round(r2,4), "MAPE(%)": round(mape,2)}

# ── 데이터 재로드 (STEP 1~3 동일 과정)
df = pd.read_csv(DATA_PATH)
y = df["현재가격"].copy()
X_raw = df.drop(columns=["현재가격","매물ID","제조사_기아"])

# 이상치 캡핑
upper_cap = y.quantile(0.99)
lower_cap = max(y.quantile(0.01), 50)
mask = (y >= lower_cap) & (y <= upper_cap)
X_clean = X_raw[mask].reset_index(drop=True)
y_clean = y[mask].reset_index(drop=True)

# Train / Test 분리
X_tr_raw, X_te_raw, y_tr, y_te = train_test_split(
    X_clean, y_clean, test_size=0.2, random_state=RANDOM_STATE
)

# 모델명 Target Encoding
train_model_mean = y_tr.groupby(X_tr_raw["모델"].values).mean().to_dict()
global_mean = y_tr.mean()

def encode_model(X, mapping, gm):
    return X["모델"].map(mapping).fillna(gm)

X_tr = X_tr_raw.copy(); X_te = X_te_raw.copy()
X_tr["모델_enc"] = encode_model(X_tr, train_model_mean, global_mean)
X_te["모델_enc"] = encode_model(X_te, train_model_mean, global_mean)
X_tr = X_tr.drop(columns=["모델"])
X_te = X_te.drop(columns=["모델"])
feat_names = list(X_tr.columns)

kf = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

# ─────────────────────────────────────────────────────────────
# STEP 6. 하이퍼파라미터 튜닝 - LightGBM x Optuna
# ─────────────────────────────────────────────────────────────
print("=" * 60)
print("STEP 6. 하이퍼파라미터 튜닝 (Optuna - LightGBM)")
print("=" * 60)

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
        "random_state": RANDOM_STATE, "verbose": -1, "n_jobs": -1,
    }
    model = lgb.LGBMRegressor(**params)
    scores = cross_validate(model, X_tr, y_tr, cv=kf,
                            scoring="neg_mean_absolute_error", n_jobs=-1)
    return -scores["test_score"].mean()

optuna.logging.set_verbosity(optuna.logging.WARNING)
study = optuna.create_study(direction="minimize",
                            sampler=optuna.samplers.TPESampler(seed=RANDOM_STATE))
study.optimize(objective, n_trials=80, show_progress_bar=True)

best_params = study.best_params
best_mae_cv = study.best_value
print(f"\n  최적 CV MAE : {best_mae_cv:.1f} 만원")
print("  최적 파라미터:")
for k, v in best_params.items():
    print(f"    {k}: {v}")

# ── 최적 모델 재학습
best_lgb = lgb.LGBMRegressor(**best_params, random_state=RANDOM_STATE,
                              verbose=-1, n_jobs=-1)
best_lgb.fit(X_tr, y_tr)
y_pred_best = best_lgb.predict(X_te)
res_best = eval_metrics(y_te, y_pred_best, "LightGBM (Tuned)")

print()
print("── 최적 LightGBM Test 결과 ──")
print(f"  MAE    : {res_best['MAE']:.1f} 만원")
print(f"  RMSE   : {res_best['RMSE']:.1f} 만원")
print(f"  R2     : {res_best['R2']:.4f}")
print(f"  MAPE   : {res_best['MAPE(%)']:.2f} %")

# ── 실제 vs 예측 산점도
fig, ax = plt.subplots(figsize=(7,6))
ax.scatter(y_te, y_pred_best, alpha=0.3, s=15, color="#4C72B0")
mn, mx = y_te.min(), y_te.max()
ax.plot([mn,mx],[mn,mx], "r--", lw=1.5, label="Perfect Fit")
ax.set_xlabel("실제 가격 (만원)")
ax.set_ylabel("예측 가격 (만원)")
ax.set_title(f"실제 vs 예측  |  MAE={res_best['MAE']:.0f}만원  R2={res_best['R2']:.4f}")
ax.legend()
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/03_pred_vs_actual.png", dpi=120, bbox_inches="tight")
plt.close()
print("\n  -> 산점도 저장: 03_pred_vs_actual.png")

# ── Optuna 시각화 (최적화 히스토리 + 파라미터 중요도)
try:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 히스토리
    trials_df = study.trials_dataframe()
    axes[0].plot(trials_df["number"], trials_df["value"], "o-", ms=3, color="#4C72B0", alpha=0.6)
    axes[0].axhline(best_mae_cv, color="red", ls="--", label=f"Best={best_mae_cv:.1f}")
    axes[0].set_xlabel("Trial")
    axes[0].set_ylabel("CV MAE (만원)")
    axes[0].set_title("Optuna 최적화 히스토리")
    axes[0].legend()

    # 파라미터 중요도
    importances = optuna.importance.get_param_importances(study)
    params_sorted = list(importances.keys())[::-1]
    vals_sorted   = [importances[p] for p in params_sorted]
    axes[1].barh(params_sorted, vals_sorted, color="#DD8452")
    axes[1].set_xlabel("중요도")
    axes[1].set_title("하이퍼파라미터 중요도")

    plt.tight_layout()
    plt.savefig(f"{OUT_DIR}/04_optuna_history.png", dpi=120, bbox_inches="tight")
    plt.close()
    print("  -> Optuna 히스토리 저장: 04_optuna_history.png")
except Exception as e:
    print(f"  Optuna 시각화 스킵: {e}")

print()

# ─────────────────────────────────────────────────────────────
# STEP 7. 모델 해석 - SHAP
# ─────────────────────────────────────────────────────────────
print("=" * 60)
print("STEP 7. 모델 해석 (SHAP)")
print("=" * 60)

explainer   = shap.TreeExplainer(best_lgb)
shap_values = explainer(X_te)

# ── 7-1. Feature Importance Bar
plt.figure(figsize=(9, 6))
shap.plots.bar(shap_values, max_display=20, show=False)
plt.title("SHAP Feature Importance (Mean |SHAP|)")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/05_shap_importance.png", dpi=120, bbox_inches="tight")
plt.close()
print("  -> SHAP 중요도 저장: 05_shap_importance.png")

# ── 7-2. Beeswarm
plt.figure(figsize=(10, 7))
shap.plots.beeswarm(shap_values, max_display=20, show=False)
plt.title("SHAP Beeswarm - 피처별 영향 분포")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/06_shap_beeswarm.png", dpi=120, bbox_inches="tight")
plt.close()
print("  -> SHAP Beeswarm 저장: 06_shap_beeswarm.png")

# ── 7-3. Waterfall (가장 고가 차량 1대)
idx_sample = int(y_te.values.argmax())
plt.figure(figsize=(10, 6))
shap.plots.waterfall(shap_values[idx_sample], max_display=15, show=False)
plt.title(f"SHAP Waterfall - 예측 {y_pred_best[idx_sample]:.0f}만원 / 실제 {y_te.values[idx_sample]:.0f}만원")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/07_shap_waterfall_high.png", dpi=120, bbox_inches="tight")
plt.close()
print("  -> SHAP Waterfall(고가) 저장: 07_shap_waterfall_high.png")

# ── 7-4. Waterfall (중간 가격대 차량)
idx_mid = int(np.argsort(np.abs(y_te.values - y_te.median()))[0])
plt.figure(figsize=(10, 6))
shap.plots.waterfall(shap_values[idx_mid], max_display=15, show=False)
plt.title(f"SHAP Waterfall - 예측 {y_pred_best[idx_mid]:.0f}만원 / 실제 {y_te.values[idx_mid]:.0f}만원 (중간가)")
plt.tight_layout()
plt.savefig(f"{OUT_DIR}/08_shap_waterfall_mid.png", dpi=120, bbox_inches="tight")
plt.close()
print("  -> SHAP Waterfall(중간가) 저장: 08_shap_waterfall_mid.png")

# ─────────────────────────────────────────────────────────────
# 최종 결과 요약
# ─────────────────────────────────────────────────────────────
print()
print("=" * 60)
print("최종 결과 요약")
print("=" * 60)
baseline_results = {
    "Linear Regression": {"MAE":269.3,"RMSE":558.7,"R2":0.7910,"MAPE(%)":16.39},
    "Ridge":             {"MAE":268.7,"RMSE":558.7,"R2":0.7910,"MAPE(%)":16.25},
    "Lasso":             {"MAE":269.2,"RMSE":559.7,"R2":0.7903,"MAPE(%)":15.72},
    "Random Forest":     {"MAE":235.6,"RMSE":546.3,"R2":0.8002,"MAPE(%)":11.72},
    "XGBoost":           {"MAE":236.1,"RMSE":562.8,"R2":0.7879,"MAPE(%)":11.54},
    "LightGBM":          {"MAE":249.6,"RMSE":571.0,"R2":0.7817,"MAPE(%)":12.59},
}
rows = [{"Model":k, **v} for k,v in baseline_results.items()]
rows.append({"Model":"LightGBM (Tuned)", **{k:v for k,v in res_best.items() if k!="Model"}})
df_summary = pd.DataFrame(rows)
print(df_summary.to_string(index=False))

df_summary.to_csv(f"{OUT_DIR}/model_results_summary.csv", index=False, encoding="utf-8-sig")
print()
print(f"  [최적 모델] LightGBM (Tuned)")
print(f"     MAE    : {res_best['MAE']:.1f} 만원  (평균 예측 오차)")
print(f"     RMSE   : {res_best['RMSE']:.1f} 만원")
print(f"     R2     : {res_best['R2']:.4f}  (설명력 {res_best['R2']*100:.1f}%)")
print(f"     MAPE   : {res_best['MAPE(%)']:.2f} %  (평균 오차율)")
print()
print("All Done.")
