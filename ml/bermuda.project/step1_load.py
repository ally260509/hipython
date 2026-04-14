# ============================================================
# Step 1 : 라이브러리 & 데이터 불러오기
# ============================================================

# ── 기본 라이브러리 ──────────────────────────────────────────
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ── 시각화 ───────────────────────────────────────────────────
import matplotlib.pyplot as plt
import seaborn as sns

# ── 전처리 / 평가 ─────────────────────────────────────────────
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

# ── 모델 ─────────────────────────────────────────────────────
from sklearn.ensemble import RandomForestRegressor
import lightgbm as lgb
from catboost import CatBoostRegressor

# ── 한글 폰트 설정 (Windows) ───────────────────────────────────
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


# ============================================================
# 데이터 로드
# ============================================================
DATA_PATH = r'C:\Users\Admin\hipython\ml\bermuda.project\data\encar_feature_processed_model_brand_labelencoded.csv'

df = pd.read_csv(DATA_PATH)

print("=" * 55)
print(f"데이터 shape : {df.shape}")
print("=" * 55)
print("\n[컬럼 목록]")
print(df.columns.tolist())
print("\n[데이터 타입]")
print(df.dtypes)
print("\n[결측치]")
print(df.isnull().sum()[df.isnull().sum() > 0])
print("\n[기초 통계 - 타겟 포함 주요 수치형]")
print(df[['현재가격_만원', '주행거리_km', '배기량_cc', '차량연령', '사고강도점수']].describe())
print("\n[샘플 5행]")
print(df.head())
