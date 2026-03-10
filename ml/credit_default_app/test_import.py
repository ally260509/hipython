import sys
print("Python:", sys.version)
print("Path:", sys.executable)

try:
    import joblib
    print("joblib OK:", joblib.__version__)
except Exception as e:
    print("joblib ERROR:", e)

try:
    import pandas as pd
    print("pandas OK:", pd.__version__)
except Exception as e:
    print("pandas ERROR:", e)

try:
    import xgboost
    print("xgboost OK:", xgboost.__version__)
except Exception as e:
    print("xgboost ERROR:", e)

try:
    import sklearn
    print("sklearn OK:", sklearn.__version__)
except Exception as e:
    print("sklearn ERROR:", e)
