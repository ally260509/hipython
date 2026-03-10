import os
import joblib
import pandas as pd

# ── 파이프라인 로드 ──────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'service_pipeline.pkl')

pipeline = joblib.load(MODEL_PATH)

# ── 피처 정의 ────────────────────────────────────────────────
FEATURE_COLS = [
    'LIMIT_BAL',
    'SEX', 'EDUCATION', 'MARRIAGE', 'AGE',
    'PAY_0', 'PAY_2', 'PAY_3', 'PAY_4', 'PAY_5', 'PAY_6',
    'BILL_AMT1', 'BILL_AMT2', 'BILL_AMT3',
    'BILL_AMT4', 'BILL_AMT5', 'BILL_AMT6',
    'PAY_AMT1', 'PAY_AMT2', 'PAY_AMT3',
    'PAY_AMT4', 'PAY_AMT5', 'PAY_AMT6',
]

# ── 예측 함수 ────────────────────────────────────────────────
def predict(input_data: dict) -> dict:
    """
    Parameters
    ----------
    input_data : dict
        FEATURE_COLS 에 해당하는 키-값 쌍

    Returns
    -------
    dict
        {
          'prediction'      : int   (0=정상, 1=채무불이행),
          'probability_ok'  : float (정상 확률),
          'probability_default' : float (채무불이행 확률),
          'label'           : str
        }
    """
    df = pd.DataFrame([input_data], columns=FEATURE_COLS)

    pred  = int(pipeline.predict(df)[0])
    proba = pipeline.predict_proba(df)[0]

    return {
        'prediction'          : pred,
        'probability_ok'      : round(float(proba[0]), 4),
        'probability_default' : round(float(proba[1]), 4),
        'label'               : '채무불이행' if pred == 1 else '정상',
    }


# ── 단독 실행 시 샘플 테스트 ─────────────────────────────────
if __name__ == '__main__':
    sample = {
        'LIMIT_BAL': 200000,
        'SEX': 2, 'EDUCATION': 2, 'MARRIAGE': 1, 'AGE': 35,
        'PAY_0': 0, 'PAY_2': 0, 'PAY_3': 0,
        'PAY_4': 0, 'PAY_5': 0, 'PAY_6': 0,
        'BILL_AMT1': 50000, 'BILL_AMT2': 48000, 'BILL_AMT3': 46000,
        'BILL_AMT4': 44000, 'BILL_AMT5': 42000, 'BILL_AMT6': 40000,
        'PAY_AMT1': 5000,  'PAY_AMT2': 5000,  'PAY_AMT3': 5000,
        'PAY_AMT4': 5000,  'PAY_AMT5': 5000,  'PAY_AMT6': 5000,
    }

    result = predict(sample)

    print('=== 예측 결과 ===')
    print(f"판정        : {result['label']}")
    print(f"정상 확률   : {result['probability_ok']*100:.1f}%")
    print(f"불이행 확률 : {result['probability_default']*100:.1f}%")
