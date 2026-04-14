from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import numpy as np
import pandas as pd
import joblib
import os

app = FastAPI()

# Next.js 앱에서 호출 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 모델 & 피처 로드 ───────────────────────────────────────
BASE_DIR = os.path.dirname(__file__)
models   = joblib.load(os.path.join(BASE_DIR, "data", "xgb_quantile_models.pkl"))
features = joblib.load(os.path.join(BASE_DIR, "data", "model_features.pkl"))

# ── 라벨 인코딩 매핑 ───────────────────────────────────────
제조사_map = {
    "KG모빌리티(쌍용)": 0, "기아": 1, "르노코리아(삼성)": 2,
    "쉐보레(GM대우)": 3, "제네시스": 4, "현대": 5,
}
연료_map = {
    "LPG": 0, "가솔린": 1, "디젤": 2, "수소": 3, "하이브리드": 5,
}
색상_map = {
    "검정색": 0, "기타": 1, "은색": 2, "흰색": 3,
}
변속기_map = {
    "수동": 0, "자동": 1,
}
차급_map = {
    "SUV": 0, "세단": 1,
}

# ── 앱 옵션명 → 모델 피처명 매핑 ──────────────────────────
옵션_map = {
    "선루프":   "주요옵션_선루프",
    "헤드램프": "주요옵션_헤드램프 (LED)",
    "주차감지": "주요옵션_주차감지센서",
    "후방카메라": "주요옵션_후방카메라",
    "자동에어컨": "주요옵션_자동에어컨",
    "스마트키": "주요옵션_스마트키",
    "네비게이션": "주요옵션_내비게이션",
    "열선시트": "주요옵션_열선시트",
    "통풍시트": "주요옵션_통풍시트",
    "가죽시트": "주요옵션_가죽시트",
}

# ── 입력 데이터 스키마 ─────────────────────────────────────
class CarInput(BaseModel):
    제조사: str          # 예: "현대"
    모델: str            # 예: "아반떼"
    연식: int            # 예: 2021
    주행거리: int        # 예: 52000 (km)
    배기량: int          # 예: 1600 (cc)
    좌석수: int          # 예: 5
    연료: str            # 예: "가솔린"
    변속기: str          # 예: "자동"
    색상: str            # 예: "흰색"
    차급: str            # 예: "세단"
    옵션: List[str]      # 예: ["후방카메라", "스마트키"]
    사고여부: bool       # True / False
    교환개수: int        # 예: 1
    판금개수: int        # 예: 0
    보험이력건수: int    # 예: 0
    부식여부: bool       # True / False


def 사고강도점수_계산(교환개수, 판금개수, 보험이력건수, 부식여부):
    return 교환개수 * 2 + 판금개수 * 1 + 보험이력건수 * 1 + (1 if 부식여부 else 0)


def 전처리(car: CarInput) -> pd.DataFrame:
    현재연도 = 2026
    차량연령 = 현재연도 - car.연식
    연간_주행거리 = car.주행거리 / (차량연령 + 1)
    사고점수 = 사고강도점수_계산(car.교환개수, car.판금개수, car.보험이력건수, car.부식여부)

    # 기본값 0으로 모든 피처 초기화
    row = {f: 0 for f in features}

    # 수치형 (로그 변환)
    row["주행거리_km_log"]    = np.log1p(car.주행거리)
    row["배기량_cc_log"]      = np.log1p(car.배기량)
    row["연간_주행거리_log"]  = np.log1p(연간_주행거리)
    row["차량연령_log"]       = np.log1p(차량연령)
    row["좌석수"]             = car.좌석수
    row["사고강도점수"]       = 사고점수

    # 라벨 인코딩
    row["제조사_라벨"] = 제조사_map.get(car.제조사, 5)
    row["연료_라벨"]   = 연료_map.get(car.연료, 1)
    row["색상_라벨"]   = 색상_map.get(car.색상, 1)
    row["변속기_라벨"] = 변속기_map.get(car.변속기, 1)
    row["차급_라벨"]   = 차급_map.get(car.차급, 1)

    # 모델 원-핫
    모델_컬럼 = f"모델_{car.모델}"
    if 모델_컬럼 in row:
        row[모델_컬럼] = 1

    # 옵션 원-핫
    for 앱_옵션 in car.옵션:
        피처명 = 옵션_map.get(앱_옵션)
        if 피처명 and 피처명 in row:
            row[피처명] = 1

    return pd.DataFrame([row])[features]


@app.post("/predict")
def predict(car: CarInput):
    X = 전처리(car)

    # 분위수별 예측 (로그 역변환)
    preds = {q: float(np.expm1(m.predict(X)[0])) for q, m in models.items()}

    # 분위수 키 정렬 (0.05 → 빠른판매, 0.5 → 적정, 0.95 → 최대수익)
    keys = sorted(preds.keys())
    low, mid, high = preds[keys[0]], preds[keys[1]], preds[keys[2]]

    return {
        "추천_적정가":     round(mid),
        "빠른판매_가격":   round(low),
        "적정판매_가격":   round(mid),
        "최대수익_가격":   round(high),
        "유사차량_최저가": round(low * 0.85),
        "유사차량_평균가": round(mid * 0.98),
        "유사차량_최고가": round(high * 1.10),
    }


@app.get("/health")
def health():
    return {"status": "ok"}
